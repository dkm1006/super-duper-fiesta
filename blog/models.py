from py2neo import Graph, Node, Relationship
from passlib.hash import bcrypt
from datetime import datetime
import uuid

graph = Graph()

class User:
    """This is the object representing the User."""
    def __init__(self, username):
        self.username = username

    def find(self):
        user = graph.find_one("User", "username", name = self.username)
        return user

    def register(self, password):
        # Create a User node if the username does not exist
        if not self.find():
            user = Node("User", username = self.username, password = bcrypt.encrypt(password))
            graph.create(user)
            return True
        else: # Notify the caller that the username already exists
            return False

    def verify_password(self, password):
        user = self.find()

        # Check if user was found
        if user:
            return bcrypt.verify(password, user['password'])
        else:
            return False
