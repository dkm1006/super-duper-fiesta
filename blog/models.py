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
        if not self.find():
            user = Node("User", username = self.username, password = bcrypt.encrypt(password))
            graph.create(user)
            return True
        else:
            return False
            
