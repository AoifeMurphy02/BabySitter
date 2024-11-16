from flask import Flask, render_template, request, redirect

app = flask = Flask(__name__)

VIDEO_URL = "http://192.168.183.28:8000/video1.mp4"

SPORTS = ["Basketball", "Badminton","Volleyball"]
REGISTRANTS = {}

@app.route("/", methods=["GET","POST"])
def index():
    return render_template("index.html", sports=SPORTS)


@app.route("/registrants")
def registrants():
    return render_template("registrants.html", registrants=REGISTRANTS)

@app.route("/register", methods=["GET","POST"])
def register():
    name = request.form.get("name")
    sport = request.form.get("sport")
    if not name:
            return render_template("error.html", message="You must provide a name.")
    if not sport:
        message = "You need to select a sport"
        return render_template("error.html", message=message)
    if sport not in SPORTS:
        message = "Invalid sport."
        return render_template("error.html", message=message)
    REGISTRANTS[name] = sport
    return redirect("/registrants")

@app.route("/video")
def video():
    return render_template("video.html", video_url=VIDEO_URL)

    # return render_template("success.html")
if __name__ == "__main__":
    app.run(debug=True)