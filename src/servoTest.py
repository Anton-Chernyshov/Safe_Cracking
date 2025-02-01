import RPi.GPIO as GPIO
from time import sleep

# GPIO Pin Setup
LOCKING_SERVO_PIN = 2
ROCKET_SERVO_PIN = 3

GPIO.setmode(GPIO.BCM)
GPIO.setup(LOCKING_SERVO_PIN, GPIO.OUT)
GPIO.setup(ROCKET_SERVO_PIN, GPIO.OUT)

# Set up PWM (50Hz is typical for servos)
lockingServoPWM = GPIO.PWM(LOCKING_SERVO_PIN, 50)  
rocketServoPWM = GPIO.PWM(ROCKET_SERVO_PIN, 50)

# Start PWM with neutral position (0% duty cycle)
lockingServoPWM.start(0)
rocketServoPWM.start(0)

# Track Servo States
lockingServoState = 0  # 0 = Locked, 1 = Unlocked
rocketServoState = 0

def setServoAngle(pwm, angle):
    """Convert angle to duty cycle and move servo"""
    duty = 2 + (angle / 18)  # Convert angle to duty cycle (0-180 maps to ~2-12%)
    pwm.ChangeDutyCycle(duty)
    sleep(0.3)  # Wait for servo to move
    pwm.ChangeDutyCycle(0)  # Stop sending PWM signal (prevents jitter)

def lockServo(pwm):
    """Moves servo to locked (0 degrees)"""
    print("Locking Servo")
    setServoAngle(pwm, 0)

def unlockServo(pwm):
    """Moves servo to unlocked (90 degrees)"""
    print("Unlocking Servo")
    setServoAngle(pwm, 90)

def toggleServo(pwm, state):
    """Toggles servo state between 0° (locked) and 90° (unlocked)"""
    if state == 0:
        unlockServo(pwm)
        return 1  # Update state to unlocked
    else:
        lockServo(pwm)
        return 0  # Update state to locked

# Example: Lock Servos on Start
lockServo(lockingServoPWM)
lockServo(rocketServoPWM)

while True:
    input("Press Enter to toggle servos...")

    # Toggle servos and update their states
    lockingServoState = toggleServo(lockingServoPWM, lockingServoState)
    rocketServoState = toggleServo(rocketServoPWM, rocketServoState)
