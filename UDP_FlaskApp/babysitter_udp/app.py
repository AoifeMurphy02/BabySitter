from flask import Flask, render_template, request, redirect, jsonify
from pubnub.pnconfiguration import PNConfiguration
from pubnub.pubnub import PubNub
from pubnub.exceptions import PubNubException
import os


app = flask = Flask(__name__)

# pubnub keys and ID
pnconfig = PNConfiguration()
pnconfig.subscribe_key = 'sub-c-f8bff00d-78e1-4bb1-86d5-e81d5043ed37'
pnconfig.publish_key = 'pub-c-a5e694de-d708-4674-9f6a-9df8bdae40a7'
pnconfig.secret_key = 'sec-c-MzVlZDVmMzUtZjU3OC00YjgzLTg2ZWEtN2NlZWIyNWEwNGQ3'  
pnconfig.uuid ='Baby-device'

pubnub =PubNub(pnconfig)

# granting access to post to channel

def grant_access():
    pubnub.grant()\
        .channels("New-channel")\
        .read(True)\
        .write(True)\
        .manage(True)\
        .sync()

grant_access()

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

# publish message to pubnub

@app.route('/publish', methods=['POST'])
def publish_message():
    message = request.json.get('message')
    if message:
        try:
            
            response = pubnub.publish().channel('New-channel').message({'text': message}).sync()

            # sucess
            response_data = {
                'status': 'success' if not response.status.is_error() else 'error',
                'status_code': response.status.status_code  
            }
            
            return jsonify(response_data)
        except PubNubException as e:
            return jsonify({'status': 'error', 'message': str(e)}), 500
    else:
        return jsonify({'status': 'error', 'message': 'No message provided'}), 400

    # return render_template("success.html")
if __name__ == "__main__":
    app.run(debug=True)