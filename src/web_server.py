from flask import Flask, request, jsonify, render_template, redirect, url_for


app = Flask(__name__)

puzzle2Unlocked = False


@app.route("/")
def landingPage():
    return render_template("Intro.html")

@app.route("/info")
def info():               
    return render_template("Info.html")

@app.route("/unlockPuzzle2")#, methods=["POST"])
def unlockPuzzle2():
    global puzzle2Unlocked
    puzzle2Unlocked = True
    print("unlockedpuzzle2")
    return redirect(url_for("info"))

@app.route("/resetSafe")
def resetSafe():
    global puzzle2Unlocked
    puzzle2Unlocked = False
    return redirect(url_for("info"))

@app.route("/puzzle1")
def puzzle1():
    return render_template("Puzzle1.html")


@app.route("/puzzle2")
def puzzle2():
    if puzzle2Unlocked:
        return render_template("Puzzle2.html")
    else:
        return redirect(url_for("landingPage"))



#BUTTONS

@app.route("/button/<id>")
def button(id):
    print("Button pressed: ", id)
    return redirect(url_for(id))



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80, debug=1)








