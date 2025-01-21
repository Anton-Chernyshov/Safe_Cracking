from flask import Flask, request, jsonify, render_template, redirect, url_for


app = Flask(__name__)

puzzle1Complete = False
puzzle2Complete = False
puzzle2Unlocked = False



@app.route("/")
def info():               
    return render_template("Info.html")



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
        return redirect(url_for("info"))


@app.route("/puzzle1/checkCompletion")
def checkCompletion():
    
    global puzzle1Complete
    puzzle1Complete = True
    if puzzle1Complete:
        global puzzle2Unlocked
        puzzle2Unlocked = True
        print("unlockedpuzzle2")
        return redirect(url_for("puzzle2"))
    else:
        return redirect(url_for("info"))


@app.route("/victory")
def checkWin():
    if puzzle1Complete and puzzle2Complete:
        return render_template("victory.html")
    else:
        return redirect(url_for("info"))
#BUTTONS

@app.route("/button/<id>")
def button(id):
    print("Button pressed: ", id)
    return redirect(url_for(id))



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80, debug=1)








