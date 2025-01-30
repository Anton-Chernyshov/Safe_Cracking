from flask import Flask, render_template, redirect, url_for, session
from datetime import datetime, timezone, timedelta
import serial
from gpiozero import Servo
from gpiozero import Button

rocketLaunchCode = "1234"
lockingServo = (Servo(4), 0) # 0 is locked, 1 is unlocked
rocketServo = (Servo(5), 0) # 0 is locked, 1 is unlocked
puzzle2Pin = Button(6)
rocketLaunchPin = Button(7)

rocketLaunchPin.when_unpressed = lambda : unlockServo(rocketServo)
rocketLaunchPin.when_pressed = lambda : lockServo(rocketServo)

def lockServo(servo : tuple[Servo, int]):
    servo[0].min()
    servo[1] = 0
    return None

def unlockServo(servo : tuple[Servo, int]):
    servo[0].max()
    servo[1] = 1
    return None

def toggleServo(servo : tuple[Servo, int]):
    if servo[1] == 0:
        unlockServo(servo)
    else:
        lockServo(servo)
    return None





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
serialPath = serial.Serial("/dev/ttyACM0",9600)

def getData() -> int:
    try:
        global serialPath
        data = serialPath.readline().decode("utf-8")
        return data
    except Exception as e:
        print(e)

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
    if puzzle2Unlocked:
        elapsed_time = getTime()
        return render_template('Puzzle2.html', elapsed_time=elapsed_time)
    else:
        return redirect(url_for('info'))
    

####### TEST FUNCTIONS REMOVE
@app.route("/testPuzzle1")
def testPuzzle1():
    global puzzle1Complete
    puzzle1Complete = True
    return redirect(url_for("puzzle1"))

@app.route("/testPuzzle2")
def testPuzzle2():
    global puzzle2Complete
    puzzle2Complete = True
    return redirect(url_for("puzzle2"))

@app.route('/unlockPuzzle2')
def unlock_puzzle2():
    global puzzle2Unlocked
    puzzle2Unlocked = True
    return redirect(url_for('puzzle2'))
########################################

@app.route("/puzzle1/checkCompletion")
def checkCompletion():
    
    global puzzle1Complete
    if getData() == "1":
        puzzle1Complete = True

    if puzzle1Complete: 
        global puzzle2Unlocked
        puzzle2Unlocked = True

        print("unlockedpuzzle2")
        return redirect(url_for("puzzle2"))
    else:
        return redirect(url_for("puzzle1"))

@app.route("/puzzle2/checkCompletion")
def checkCompletion2():
    
    global puzzle2Complete
    if puzzle2Pin.is_pressed:
        puzzle2Complete = True
    if puzzle2Complete: 
        return redirect(url_for("victory"))
    else:
        return redirect(url_for("puzzle2"))

@app.route("/launchCode")
def launchCode():

    return render_template("code.html", LAUNCH_CODE=rocketLaunchCode)

@app.route("/victory")
def checkWin():
    if puzzle1Complete and puzzle2Complete:
        unlockServo(lockingServo)
        return render_template("victory.html")
    else:
        return redirect(url_for("info"))


@app.route('/reset-timer')
def reset_timer():

    session['start_time'] = datetime.now(timezone.utc).isoformat()

    # CODE HERE TO RESET THE SAFE  (counterintuitive, i know)

    lockServo(rocketServo)
    lockServo(lockingServo)

    return redirect(url_for('info'))


@app.route("/resetSafe")
def resetSafe():

    return render_template("resetSafe.html")

if __name__ == '__main__':
    app.run(debug=True)
