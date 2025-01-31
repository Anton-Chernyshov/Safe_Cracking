from flask import Flask, render_template, redirect, url_for, session
from datetime import datetime, timezone, timedelta
import serial
from gpiozero import AngularServo, Button
from time import sleep
from random import randint

"""
###############################################
TO DO:
 - figure out why puzzle 2 is not working
 - add victory screen once code has been entered
 - do the key
 - SERVOS!!!!




"""

############## SERVO HANDLING & PUZZLE 2

lockingServo = [AngularServo(2, min_angle=0, max_angle=90, initial_angle=0), 0]  
rocketServo = [AngularServo(3, min_angle=0, max_angle=90, initial_angle=0)]

puzzle2Pin = Button(14)
rocketLaunchPin = Button(15)

rocketLaunchPin.when_released = lambda : unlockServo(rocketServo)
rocketLaunchPin.when_pressed = lambda : lockServo(rocketServo)

def lockServo(servo: list):
    """Lock the servo (move to 0 degrees)."""
    if servo[1] != 0:
        servo[0].angle = 0
        sleep(0.3)
        servo[0].angle = None  # Disable PWM after moving
        servo[1] = 0

def unlockServo(servo: list):
    """Unlock the servo (move to 90 degrees)."""
    if servo[1] != 1:
        servo[0].angle = 90
        sleep(0.3)
        servo[0].angle = None  # Disable PWM after moving
        servo[1] = 1

def toggleServo(servo: list):
    """Toggle the servo state."""
    if servo[1] == 0:
        unlockServo(servo)
    else:
        lockServo(servo)




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
        unlockServo(lockingServo)  # Unlock the rocket
        launchCodeEntered = True  # Mark as entered
    else:
        print("Incorrect Code. Try Again.")

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
    for _ in range(5):  
        data = getData().strip()  # Strip unwanted characters
        if data == "1":
            session["puzzle1Complete"] = True
            break

    if session.get("puzzle1Complete", False):
        session["puzzle2Unlocked"] = True
        return redirect(url_for("puzzle2"))
    return redirect(url_for("puzzle1"))

@app.route("/puzzle2/checkCompletion")
def checkCompletion2():
    
    if puzzle2Pin.is_active:
        session["puzzle2Complete"] = True
    
    if session.get("puzzle2Complete", False):
        return redirect(url_for("launchCode"))  # Go to launch code page FIRST
    
    return redirect(url_for("puzzle2"))


@app.route("/launchCode")
def launchCode():

    return render_template("code.html", LAUNCH_CODE=rocketLaunchCode)

@app.route("/victory")
def checkWin():
    if session.get("puzzle1Complete") and session.get("puzzle2Complete") and session.get("launchCodeEntered", False):
        if not session.get("safeUnlocked", False):  # Only unlock once
            unlockServo(lockingServo)
            session["safeUnlocked"] = True  # Mark as unlocked
        return render_template("victory.html")
    
    return redirect(url_for("launchCode"))  # Ensure they see the launch code first

@app.route("/submitCode/<code>")
def submitCode(code):
    """Check if entered code is correct and mark launch as ready."""
    if code == rocketLaunchCode:
        session["launchCodeEntered"] = True  # Mark as entered
        unlockServo(rocketServo)  # Unlock rocket if code is correct
        return redirect(url_for("victory"))  # Now allow victory
    else:
        return redirect(url_for("launchCode"))  # Stay on code page if wrong




@app.route('/reset-timer')
def reset_timer():
    session["start_time"] = datetime.now(timezone.utc).isoformat()

    # Reset puzzle states
    session["puzzle1Complete"] = False
    session["puzzle2Complete"] = False
    session["puzzle2Unlocked"] = False
    session["safeUnlocked"] = False

    # Reset physical locks
    lockServo(rocketServo)
    lockServo(lockingServo)

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


@app.route("/secret/toggleServo/<servo>")
def toggleWebServo(servo):
    if servo == "lockingServo":
        servo = lockingServo
    elif servo == "rocketServo":
        servo = rocketServo
    else:
        print("uhoh")
        return redirect(url_for("info"))
    print(f"toglging {servo}")
    toggleServo(servo)
    return redirect(url_for("info"))

############ run the app
if __name__ == '__main__':
    app.run(debug=True)
