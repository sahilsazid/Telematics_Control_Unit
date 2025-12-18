#include <iostream>
#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <linux/i2c-dev.h>
#include <cmath>
#include <cstdio> // Required for printf

// Define MPU6050 I2C Address
#define MPU6050_ADDRESS 0x68

// Define Register Addresses
#define MPU6050_ACCEL_XOUT_H 0x3B
#define MPU6050_PWR_MGMT_1   0x6B // Power Management Register 1
#define MPU6050_ACCEL_CONFIG 0x1C // Accel Configuration Register

// Constants
#define GRAVITY_MSS 9.80665 // Earth's gravity in m/s^2

// Full Scale Range (Default is 2g)
// 32768 / 2g = 16384.0
#define ACCEL_SENSITIVITY 16384.0 

// Function to read two consecutive bytes (16-bit value) from a register
short read_word_2c(int file, int reg) {
    // We assume the caller has already set the register pointer.
    // In the main loop, we set it to MPU6050_ACCEL_XOUT_H and then read 6 bytes (X, Y, Z).
    
    // Create a 2-byte buffer to read the high and low bytes
    unsigned char buffer[2];
    
    // Reading 2 bytes from the current register pointer
    if (read(file, buffer, 2) != 2) {
        std::cerr << "Error reading 2 bytes from MPU6050." << std::endl;
        return 0;
    }

    // Combine bytes into a 16-bit signed integer
    short val = (buffer[0] << 8) | buffer[1];
    return val;
}

// Function to write a single byte to a register
void write_byte(int file, unsigned char reg, unsigned char value) {
    unsigned char buf[2] = {reg, value};
    if (write(file, buf, 2) != 2) {
        std::cerr << "Error writing to register " << std::hex << (int)reg << std::endl;
    }
}

int main() {
    int file;
    const char *i2c_bus = "/dev/i2c-1"; 

    if ((file = open(i2c_bus, O_RDWR)) < 0) {
        std::cerr << "Failed to open the I2C bus. Check permissions and configuration." << std::endl;
        return 1;
    }

    if (ioctl(file, I2C_SLAVE, MPU6050_ADDRESS) < 0) {
        std::cerr << "Failed to acquire bus access and/or talk to slave." << std::endl;
        close(file);
        return 1;
    }

    // --- Initialization ---
    // 1. Wake up the device (PWR_MGMT_1 = 0x00)
    write_byte(file, MPU6050_PWR_MGMT_1, 0x00);
    
    // 2. Set the Full Scale Range to +/- 2g (ACCEL_CONFIG = 0x00)
    write_byte(file, MPU6050_ACCEL_CONFIG, 0x00);

    std::cout << "MPU6050 initialized successfully (Output in m/s^2)." << std::endl;

    while (true) {
        // --- Read Acceleration Data ---

        // Set the register address for reading Accel X High Byte
        unsigned char reg_start = MPU6050_ACCEL_XOUT_H;
        write(file, &reg_start, 1);
        
        // Reading all 6 bytes (X_H, X_L, Y_H, Y_L, Z_H, Z_L) at once
        unsigned char accel_buf[6];
        if (read(file, accel_buf, 6) != 6) {
            std::cerr << "Error reading all acceleration data." << std::endl;
            usleep(500000);
            continue;
        }

        // Combine bytes into raw 16-bit values
        short raw_accel_x = (accel_buf[0] << 8) | accel_buf[1];
        short raw_accel_y = (accel_buf[2] << 8) | accel_buf[3];
        short raw_accel_z = (accel_buf[4] << 8) | accel_buf[5];

        // --- Conversion and Calculation ---

        // 1. Convert raw values to g's
        double accel_x_g = (double)raw_accel_x / ACCEL_SENSITIVITY;
        double accel_y_g = (double)raw_accel_y / ACCEL_SENSITIVITY;
        double accel_z_g = (double)raw_accel_z / ACCEL_SENSITIVITY;
        
        // 2. CONVERT g's to m/s^2 (THIS IS THE KEY CHANGE)
        double accel_x_mss = accel_x_g * GRAVITY_MSS;
        double accel_y_mss = accel_y_g * GRAVITY_MSS;
        double accel_z_mss = accel_z_g * GRAVITY_MSS;

        // --- Print Results ---
        std::cout << "------------------------------" << std::endl;
        std::cout << "Accelerometer (m/s^2):" << std::endl;
        
        // Print with 3 decimal places for better precision
        printf("X: %.3f m/s^2\n", accel_x_mss);
        printf("Y: %.3f m/s^2\n", accel_y_mss);
        printf("Z: %.3f m/s^2\n", accel_z_mss);

        // Wait before the next reading
        usleep(500000); // 0.5 seconds
    }

    close(file);
    return 0;
}
