import time, math
import board, busio
from adafruit_mpu6050 import MPU6050

# ------------------ I2C + MPU6050 Setup ------------------
i2c = busio.I2C(board.SCL, board.SDA)  # i2c-1 on Pi
mpu = MPU6050(i2c)
mpu.accelerometer_range = 2  # ±2g

# ------------------ Scoring Variables ------------------
rider_score = 100
last_motion_time = time.time()
last_reward_time = time.time()
idle_threshold = 0.2      # m/s² below which considered idle
harsh_accel_thr = 2.0     # m/s²
harsh_brake_thr = -3.0    # m/s²
smooth_speed_limit = 50   # km/h (dummy)
sampling_rate = 0.1       # seconds

print("Rider score system started (Ctrl+C to stop)\n")

try:
    while True:
        ax, ay, az = mpu.acceleration  # in m/s²
        total_acc = math.sqrt(ax*ax + ay*ay + az*az)

        # remove gravity (approx)
        lin_ax = ax
        # if you mount properly, ax is longitudinal accel

        # --------- HARSH ACCELERATION / BRAKING ----------
        if lin_ax > harsh_accel_thr:
            rider_score -= 5
            print(f"Harsh Acceleration! ax={lin_ax:.2f}  → Score={rider_score}")

        elif lin_ax < harsh_brake_thr:
            rider_score -= 5
            print(f"Harsh Braking! ax={lin_ax:.2f}  → Score={rider_score}")

        # --------- PROLONGED IDLING ----------
        # consider idle if |lin_ax| < idle_threshold
        if abs(lin_ax) < idle_threshold:
            # no significant motion
            if time.time() - last_motion_time > 30:  # 30 s idle
                rider_score -= 2
                print(f"Prolonged Idling 30s → Score={rider_score}")
                last_motion_time = time.time()  # reset timer
        else:
            last_motion_time = time.time()  # moving, reset idle timer

        # --------- SMOOTH RIDING REWARD ----------
        # (simulate speed here; replace with GPS speed later)
        simulated_speed = 40  # km/h constant dummy
        if simulated_speed < smooth_speed_limit:
            if time.time() - last_reward_time > 60:  # every minute
                rider_score += 5
                if rider_score > 100:
                    rider_score = 100
                print(f"Smooth Riding Reward → Score={rider_score}")
                last_reward_time = time.time()

        # prevent score from going below 0
        rider_score = max(rider_score, 0)

        time.sleep(sampling_rate)

except KeyboardInterrupt:
    print(f"\nFinal Rider Score: {rider_score}")

