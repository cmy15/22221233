'''
app.py contains all of the server application
this is where you'll find all of the get/post request handlers
the socket event handlers are inside of socket_routes.py
'''

from flask import Flask, render_template, request, abort, url_for, jsonify
from flask_socketio import SocketIO
import db
import secrets


# import logging

# this turns off Flask Logging, uncomment this to turn off Logging
# log = logging.getLogger('werkzeug')
# log.setLevel(logging.ERROR)

app = Flask(__name__)

# secret key used to sign the session cookie

socketio = SocketIO(app)

# don't remove this!!
import socket_routes

# index page
@app.route("/")
def index():
    return render_template("index.jinja")

# login page
@app.route("/login")
def login():    
    return render_template("login.jinja")

# handles a post request when the user clicks the log in button
@app.route("/login/user", methods=["POST"])
def login_user():
    if not request.is_json:
        abort(404)

    username = request.json.get("username")
    password = request.json.get("password")

    user = db.get_user(username)
    if user is None:
        return "Error: User does not exist!"

    if user.password != password:
        return "Error: Password does not match!"

    return url_for('home', username=request.json.get("username"))

# handles a get request to the signup page
@app.route("/signup")
def signup():
    return render_template("signup.jinja")

# Handles POST request for user signup
@app.route("/signup/user", methods=["POST"])
def signup_user():
    if not request.is_json:
        abort(404)
    username = request.json.get("username")
    password = request.json.get("password")

    if db.get_user(username) is None:
        db.insert_user(username, password)
        return url_for('home', username=username)
    return "Error: User already exists!"

# handler when a "404" error happens
@app.errorhandler(404)
def page_not_found(_):
    return render_template('404.jinja'), 404

# home page, where the messaging app is
@app.route("/home")
def home():
    if request.args.get("username") is None:
        abort(404)
    username = request.args.get("username")
    friends = db.get_friend_list(username)
    friend_request = db.get_friend_requests(username)  # 确保这个函数存在且正确实现
    return render_template("home.jinja", username=username, friends=friends, friend_request=friend_request)

@app.route("/add_friend", methods=["POST"])
def add_friend():
    if not request.is_json:
        abort(404)

    current_user = request.json.get("username")
    friend_username = request.json.get("friend_username")

    if db.get_user(friend_username) is None:
        return {"error": "User does not exist!"}, 404
    
    db.create_friend_request(current_user, friend_username, 'sent')
    return {"message": "Friend request sent successfully!"}, 200
 
@app.route('/accept_friend_request/<sender_username>', methods=['POST'])
def accept_friend_request(sender_username):

    print("Received sender_username:", sender_username)
    if not request.is_json:
        print("Error: Request is not JSON")
        return jsonify({"error": "Request must be JSON"}), 400

    current_user = request.json.get("username")
    
    print(current_user, sender_username)
    if not current_user:
        print("Error: Username not provided")
        return jsonify({"error": "Username required"}), 400

    if not db.check_friend_request(sender_username, current_user):
        print("Error: Friend request not found between", sender_username, "and", current_user)
        return jsonify({"error": "Friend request not found"}), 404

    result, message = db.accept_friend_request(sender_username, current_user)
    if result:
        return jsonify({"message": "Friend request accepted"}), 200
    else:
        return jsonify({"error": message}), 500

@app.route('/reject_friend_request/<sender_username>', methods=['POST'])
def reject_friend_request(sender_username):

    print("Received sender_username:", sender_username)
    if not request.is_json:
        print("Error: Request is not JSON")
        return jsonify({"error": "Request must be JSON"}), 400

    current_user = request.json.get("username")
    
    print(current_user, sender_username)
    if not current_user:
        print("Error: Username not provided")
        return jsonify({"error": "Username required"}), 400

    if not db.check_friend_request(sender_username, current_user):
        print("Error: Friend request not found between", sender_username, "and", current_user)
        return jsonify({"error": "Friend request not found"}), 404

    result, message = db.reject_friend_request(sender_username, current_user)
    if result:
        return jsonify({"message": "Friend request rejected"}), 200
    else:
        return jsonify({"error": message}), 500

@app.route('/withdraw_friend_request/<sender_username>', methods=['POST'])
def withdraw_friend_request(sender_username):

    print("Withdraw sender_username:", sender_username)
    if not request.is_json:
        print("Error: Request is not JSON")
        return jsonify({"error": "Request must be JSON"}), 400

    current_user = request.json.get("username")
    
    print(current_user, sender_username)
    if not current_user:
        print("Error: Username not provided")
        return jsonify({"error": "Username required"}), 400

    if not db.check_friend_request(sender_username, current_user):
        print("Error: Friend request not found between", sender_username, "and", current_user)
        return jsonify({"error": "Friend request not found"}), 404

    result, message = db.withdraw_friend_request(sender_username, current_user)
    if result:
        return jsonify({"message": "Friend request withdrawed"}), 200
    else:
        return jsonify({"error": message}), 500


if __name__ == '__main__':
    socketio.run(app)