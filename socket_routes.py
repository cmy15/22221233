'''
socket_routes
file containing all the routes related to socket.io
'''


from flask_socketio import join_room, emit, leave_room
from flask import request

try:
    from __main__ import socketio
except ImportError:
    from app import socketio

from models import Room, User, Friendship, FriendRequest

import db

room = Room()

# when the client connects to a socket
# this event is emitted when the io() function is called in JS
@socketio.on('connect')
def connect():
    username = request.cookies.get("username")
    room_id = request.cookies.get("room_id")
    if room_id is None or username is None:
        return
    # socket automatically leaves a room on client disconnect
    # so on client connect, the room needs to be rejoined
    join_room(int(room_id))
    emit("incoming", (f"{username} has connected", "green"), to=int(room_id))

# event when client disconnects
# quite unreliable use sparingly
@socketio.on('disconnect')
def disconnect():
    username = request.cookies.get("username")
    room_id = request.cookies.get("room_id")
    if room_id is None or username is None:
        return
    emit("incoming", (f"{username} has disconnected", "red"), to=int(room_id))



# send message event handler
@socketio.on("send")
def send(username, message, room_id):
    # Here we should add message encryption logic before emitting
    emit("incoming", (f"{username}: {message}"), to=room_id)


    
# join room event handler
# sent when the user joins a room
# Join room event
@socketio.on("join")
def join(sender_name, receiver_name):
    receiver = db.get_user(receiver_name)
    if receiver is None:
        return "Unknown receiver!"
    sender = db.get_user(sender_name)
    if sender is None:
        return "Unknown sender!"
    room_id = room.get_room_id(receiver_name)
    if room_id is not None:
        room.join_room(sender_name, room_id)
        join_room(room_id)
        emit("incoming", (f"{sender_name} has joined the room.", "green"), to=room_id, include_self=False)
        emit("incoming", (f"{sender_name} has joined the room. Now talking to {receiver_name}.", "green"))
        return room_id
    room_id = room.create_room(sender_name, receiver_name)
    join_room(room_id)
    emit("incoming", (f"{sender_name} has joined the room. Now talking to {receiver_name}.", "green"), to=room_id)
    return room_id

# leave room event handler
@socketio.on("leave")
def leave(username, room_id):
    emit("incoming", (f"{username} has left the room.", "red"), to=room_id)
    leave_room(room_id)
    room.leave_room(username)

# Handling friend requests and friend list
@socketio.on("add_friend")
def add_friend(sender, receiver):
    if not db.get_user(receiver):
        return "User does not exist."
    db.create_friend_request(sender, receiver, 'sent')
    emit("friend_request_sent", {"sender": sender, "receiver": receiver})

@socketio.on("accept_friend")
def accept_friend(sender, receiver):
    db.create_friend_request(sender, receiver, 'accepted')
    db.add_friendship(sender, receiver)
    emit("friend_added", {"friend": receiver}, to=sender)

@socketio.on("reject_friend")
def reject_friend(sender, receiver):
    db.create_friend_request(sender, receiver, 'rejected')

@socketio.on("withdraw_friend")
def reject_friend(sender, receiver):
    db.create_friend_request(sender, receiver, 'rejected')
    db.withdraw_friend_request(sender, receiver)


@socketio.on("list_friends")
def list_friends(username):
    friends = db.get_friend_list(username)
    emit("friend_list", {"username": username, "friends": friends})
