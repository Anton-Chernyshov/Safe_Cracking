from flask import Flask, render_template, redirect, url_for, session
from datetime import datetime, timezone, timedelta
import serial
#from gpiozero import AngularServo, Button
import RPi.GPIO as GPIO
from time import sleep
from random import randint

"""
###############################################
TO DO:
 - add victory screen once code has been entered
 - do the key, key will be added to the ground of the servo ( when tunred the servo wil snap to the correct angle and win.)


"""

######## ASSIGNMENTS OF PINS ###########
LOCKING_SERVO_PIN = 2
ROCKET_SERVO_PIN = 3
PUZZLE_2_DETECTION_PIN = 14
ROCKET_LAUNCH_KEY_PIN = 15


GPIO.setmode(GPIO.BCM)
GPIO.setup(LOCKING_SERVO_PIN, GPIO.OUT)
GPIO.setup(ROCKET_SERVO_PIN, GPIO.OUT)
GPIO.setup(PUZZLE_2_DETECTION_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(ROCKET_LAUNCH_KEY_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
lockingServoPWM = GPIO.PWM(LOCKING_SERVO_PIN, 50)  
rocketServoPWM = GPIO.PWM(ROCKET_SERVO_PIN, 50)
lockingServoPWM.start(0)
rocketServoPWM.start(0)
lockingServoState = 0  # 0 is locked, 1 is unlocked
rocketServoState = 0

############## SERVO HANDLING & PUZZLE 2

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
    """Toggles servo state between 0 (locked) and 90 (unlocked)"""
    if state == 0:
        unlockServo(pwm)
        return 1  # Update state to unlocked
    else:
        lockServo(pwm)
        return 0  # Update state to locked




############## CODE HANDLING
from pad4pi import rpi_gpio
rocketLaunchCode = "7355608" # lulz
launchCodeEntered = False
entered_code = ""

KEYPAD = [
    ["1", "2", "3", "A"],
    ["4", "5", "6", "B"],
    ["7", "8", "9", "C"],
    ["*", "0", "#", "D"]
]
ROW_PINS = [5, 6, 13, 19]
COL_PINS = [12, 16, 20, 21]
factory = rpi_gpio.KeypadFactory()
keypad = factory.create_keypad(keypad=KEYPAD, row_pins=ROW_PINS, col_pins=COL_PINS)

def key_pressed(key):
    """Handles key presses from the 4x4 matrix keypad."""
    global entered_code

    if key == "#":  # Check code when "#" is pressed
        check_launch_code(entered_code)
        entered_code = ""  # Reset after checking
    elif key == "*":  # Clear entry when "*" is pressed
        entered_code = ""
        print("Code entry cleared.")
    else:
        entered_code += key  # Append key to entered code
        

def check_launch_code(code):
    """Validates the entered launch code."""
    global launchCodeEntered
    if code == rocketLaunchCode:
        print("Correct Code! Unlocking Rocket")
        #################
        # WIN CONDITION HERE ( you stupid itiot)
        unlockServo(lockingServoPWM)  # Unlock the rocket
        unlockServo(rocketServoPWM)

        launchCodeEntered = True  # Mark as entered
    else:
        print(f"Incorrect Code. Try Again. you entered {code}")

# Attach keypress function to keypad
keypad.registerKeyPressHandler(key_pressed)





################# FLASK APP

app = Flask(__name__)

app.secret_key = 'your_secret_key'  # Required for session management
COUNTDOWN_DURATION = timedelta(minutes=10)  # 10 minutes
# Initialize the timer in the session

def initialize_timer():
    if 'start_time' not in session:
        # Store the current time as a string
        session['start_time'] = datetime.now(timezone.utc).isoformat()

def getTime():
    """Calculate the remaining time for the countdown."""
    start_time_str = session.get('start_time')
    if isinstance(start_time_str, str):
        try:
            start_time = datetime.fromisoformat(start_time_str)
            elapsed = datetime.now(timezone.utc) - start_time
            remaining = COUNTDOWN_DURATION - elapsed
            if remaining.total_seconds() <= 0:
                return "00:00:00"  # Timer has expired
            return str(remaining).split('.')[0]  # Format as HH:MM:SS
        except ValueError:
            return "00:00:00"  # Handle invalid session data
    else:
        return "00:00:00"  # Default fallback



puzzle1Complete = False
puzzle2Unlocked = False
puzzle2Complete = False
serialPath = serial.Serial("/dev/ttyACM0",9600, timeout=1)

def getData() -> str:
    try:
        global serialPath
        data = serialPath.readline().decode("utf-8")
        return data
    except Exception as e:
        print(f"Serial Error: {e}")
        return "0"

@app.route('/')
def info():
    print(getData())
    elapsed_time = getTime()
    return render_template('Info.html', elapsed_time=elapsed_time)

@app.route('/puzzle1')
def puzzle1():
    elapsed_time = getTime()
    return render_template('Puzzle1.html', elapsed_time=elapsed_time)

@app.route('/puzzle2')
def puzzle2():
    if session.get("puzzle2Unlocked", False):  # Use session instead of global variable
        elapsed_time = getTime()
        return render_template('Puzzle2.html', elapsed_time=elapsed_time)
    return redirect(url_for('info'))
    
@app.route("/puzzle1/checkCompletion")
def checkCompletion():
    print("Checking Puzzle 1 Completion...")  # Debugging statement
    
    for _ in range(5):  
        data = getData().strip()  # Strip whitespace and newline
        print(f"Received Data from Arduino: '{data}'")  # Debugging statement

        if data == "1":
            print("Puzzle 1 Complete!")  # Debugging statement
            session["puzzle1Complete"] = True
            break
        sleep(0.1)  # Allow slight delay for stability

    # Debugging print statements
    print(f"Session puzzle1Complete: {session.get('puzzle1Complete', False)}")

    if session.get("puzzle1Complete", False):
        print("Unlocking Puzzle 2!")  # Debugging statement
        session["puzzle2Unlocked"] = True
        return redirect(url_for("puzzle2"))

    print("Redirecting back to Puzzle 1")  # Debugging statement
    return redirect(url_for("puzzle1"))

@app.route("/puzzle2/checkCompletion")
def checkCompletion2():
    
    if GPIO.input(PUZZLE_2_DETECTION_PIN) == GPIO.HIGH:
        session["puzzle2Complete"] = True
    
    if session.get("puzzle2Complete", False):
        return redirect(url_for("launchCode"))  # Go to launch code page FIRST
    
    return redirect(url_for("puzzle2"))


@app.route("/launchCode")
def launchCode():

    return render_template("code.html", LAUNCH_CODE=rocketLaunchCode)

@app.route("/victory")
def victory():
    return render_template("victory.html")






@app.route('/reset-timer')
def reset_timer():
    session["start_time"] = datetime.now(timezone.utc).isoformat()

    # Reset puzzle states
    session["puzzle1Complete"] = False
    session["puzzle2Complete"] = False
    session["puzzle2Unlocked"] = False
    session["safeUnlocked"] = False

    # Reset physical locks
    lockServo(rocketServoPWM)
    lockServo(lockingServoPWM)

    # generate new launch code
    global rocketLaunchCode
    rocketLaunchCode = str(randint(1000000, 9999999))
    print(f"New Launch Code: {rocketLaunchCode}")
    return redirect(url_for('info'))


@app.route("/resetSafe")
def resetSafe():

    return render_template("resetSafe.html")


####### TEST FUNCTIONS REMOVE
@app.route("/testPuzzle1")
def testPuzzle1():
    session["puzzle1Complete"] = True
    return redirect(url_for("puzzle1"))

@app.route("/testPuzzle2")
def testPuzzle2():
    session["puzzle2Complete"] = True
    return redirect(url_for("puzzle2"))

@app.route('/unlockPuzzle2')
def unlock_puzzle2():
    session["puzzle2Unlocked"] = True
    return redirect(url_for('puzzle2'))


@app.route("/secret/unlockServo/<servo>")
def unlockWebServo(servo):
    if servo == "lockingServo":
        servo = lockingServoPWM
    elif servo == "rocketServo":
        servo = rocketServoPWM
    else:
        print("uhoh")
        return redirect(url_for("info"))
    print(f"unlocking {servo}")
    unlockServo(servo)
    return redirect(url_for("info"))

@app.route("/secret/lockServo/<servo>")
def lockWebServo(servo):
    if servo == "lockingServo":
        servo = lockingServoPWM
    elif servo == "rocketServo":
        servo = rocketServoPWM
    else:
        print("uhoh")
        return redirect(url_for("info"))
    print(f"locking {servo}")
    lockServo(servo)
    return redirect(url_for("info"))

@app.route("/secret/toggleServo/<servo>")
def toggleWebServo(servo):
    global lockingServoState, rocketServoState

    if servo == "lockingServo":
        servo = lockingServoPWM
        state = lockingServoState
        lockingServoState = toggleServo(servo, state)
    elif servo == "rocketServo":
        servo = rocketServoPWM
        state = rocketServoState
        rocketServoState = toggleServo(servo, state)
    else:
        print("uhoh")
        return redirect(url_for("info"))
    print(f"toggling {servo}")
    return redirect(url_for("info"))

############ run the app
if __name__ == '__main__':
    app.run(debug=True)
