'''
db
database file, containing all the logic to interface with the sql database
'''

from sqlalchemy import create_engine, or_
from sqlalchemy.orm import Session
from models import *

from pathlib import Path

# creates the database directory
Path("database") \
    .mkdir(exist_ok=True)

# "database/main.db" specifies the database file
# change it if you wish
# turn echo = True to display the sql output
engine = create_engine("sqlite:///database/main.db", echo=False)

# initializes the database
Base.metadata.create_all(engine)

# inserts a user to the database
def insert_user(username: str, password: str):
    with Session(engine) as session:
        user = User(username=username, password=password)
        session.add(user)
        session.commit()

# gets a user from the database
def get_user(username: str):
    with Session(engine) as session:
        return session.get(User, username)

# Function to add a friendship
def add_friendship(user1: str, user2: str):
    with Session(engine) as session:
        friendship = Friendship(user1=user1, user2=user2)
        session.add(friendship)
        session.commit()

# Function to create a friend request

def create_friend_request(sender: str, receiver: str, status: str):
    with Session(engine) as session:
        try:
            request = FriendRequest(sender=sender, receiver=receiver, status=status)
            session.add(request)
            session.commit()
        except Exception as e:
            print(f"An error occurred: {e}")
            session.rollback()
            raise

# Function to get friend requests for a user
def get_friend_requests(username: str):
    with Session(engine) as session:
        requests_received = session.query(FriendRequest).filter(FriendRequest.receiver == username).all()
        requests_sent = session.query(FriendRequest).filter(FriendRequest.sender == username).all()
        
        received_details = [{'sender': request.sender, 'receiver': request.receiver, 'status': request.status} for request in requests_received]
        sent_details = [{'sender': request.sender, 'receiver': request.receiver, 'status': request.status} for request in requests_sent]
        
        return {'receiver': received_details, 'sent': sent_details}


def get_friend_list(username: str):
    with Session(engine) as session:
        friendships = session.query(Friendship).filter((Friendship.user1 == username) | (Friendship.user2 == username)).all()
        friend_list = [friendship.user2 if friendship.user1 == username else friendship.user1 for friendship in friendships]
        return friend_list

def check_friend_request(sender: str, receiver: str):
    with Session(engine) as session:
        return session.query(FriendRequest).filter_by(sender=sender, receiver=receiver).first() is not None
    
def accept_friend_request(sender: str, receiver: str):
    with Session(engine) as session:
        try:
            request = session.query(FriendRequest).filter_by(sender=sender, receiver=receiver).first()
            if not request:
                return False, "No friend request found"
            
            request.status = 'accepted'
            friendship = Friendship(user1=sender, user2=receiver)
            session.add(friendship)
            
            session.commit()
            return True, "Friend request accepted"
        except Exception as e:
            session.rollback()
            return False, str(e)

def reject_friend_request(sender: str, receiver: str):
    with Session(engine) as session:
        try:
            request = session.query(FriendRequest).filter_by(sender=sender, receiver=receiver).first()
            if not request:
                return False, "No friend request found"
            
            request.status = 'rejected'
            session.commit()
            return True, "Friend request rejected"
        except Exception as e:
            session.rollback()
            return False, str(e)

def withdraw_friend_request(sender: str, receiver: str):
    with Session(engine) as session:
        try:
            request = session.query(FriendRequest).filter_by(sender=sender, receiver=receiver).first()
            if not request:
                return False, "No friend request found"
            request.status = 'sent'
            request = FriendRequest(user1=sender, user2=receiver, status= request.status)
            session.delete(request)
            session.commit()
            return True, "Friend request withdrawed"
        except Exception as e:
            session.rollback()
            return False, str(e)