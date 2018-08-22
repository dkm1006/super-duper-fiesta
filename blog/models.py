from py2neo import Graph, Node, Relationship, NodeMatcher
from passlib.hash import bcrypt
from datetime import datetime
import uuid
import os

# Setting environment variables
#url = os.environ.get('GRAPHENEDB_URL', 'http://localhost:7474')
username = os.environ.get('NEO4J_USERNAME')
password = os.environ.get('NEO4J_PASSWORD')
graph = Graph(username=username, password=password)
selector = NodeMatcher(graph)

#graph = Graph()

# Helper functions
def timestamp():
    epoch = datetime.utcfromtimestamp(0)
    now = datetime.now()
    delta = now - epoch
    return delta.total_seconds()

def date():
    return datetime.now().strftime('%Y-%m-%d')


# General functions
def get_todays_recent_posts(number=5):
    query = """
    MATCH (user:User)-[:published]->(post:Post)<-[:tagged]-(tag:Tag)
    WHERE post.date = {today}
    RETURN user.username AS username, post, COLLECT(tag.name) AS tags
    ORDER BY post.timestamp DESC LIMIT {number}
    """
    return graph.run(query, today=date(), number=number)


class User:
    """This is the object representing the User."""
    def __init__(self, username):
        self.username = username

    def find(self):
        user = selector.match("User", username=self.username).first()
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

    def add_post(self, title, text, tags):
        user = self.find()
        post = Node(
            "Post",
            id=str(uuid.uuid4()),
            title=title,
            text=text,
            timestamp=timestamp(),
            date=date()
        )
        publish_relationship = Relationship(user, "published", post)
        graph.create(publish_relationship)

        tags = [tag.strip() for tag in tags.lower().split(',')]
        for tagname in set(tags):
            tag = Node("Tag", name=tagname)
            graph.merge(tag, "Tag", "name")
            tag_relationship = Relationship(tag, "tagged", post)
            graph.create(tag_relationship)

    def get_recent_posts(self, number=5):
            query = """
            MATCH (user:User)-[:published]->(post:Post)<-[:tagged]-(tag:Tag)
            WHERE user.username = {username}
            RETURN post, COLLECT(tag.name) AS tags
            ORDER BY post.timestamp DESC LIMIT {number}
            """
            return graph.run(query, username=self.username, number=number)

    def like_post(self, post_id):
        user = self.find()
        post = selector.match("Post", id=post_id).first()
        like_relationship = Relationship(user, "liked", post)
        graph.merge(like_relationship)
        return True

    def get_similar_users(self, number=3):
        # Find similar users to logged-in user based on tags they blogged about
        query = """
        MATCH (you:User)-[:published]->(:Post)<-[:tagged]-(tag:Tag),
        (they:User)-[:published]->(:Post)<-[:tagged]-(tag)
        WHERE you.username = {username} AND you <> they
        WITH they, COLLECT(DISTINCT tag.name) as tags
        ORDER BY SIZE(tags) DESC LIMIT {number}
        RETURN they.username as similar_user, tags
        """
        return graph.run(query, username=self.username, number=number)

    def get_commonality_of_user(self, other):
        # Find number of likes and common topics both users blogged about
        query = """
        MATCH (they:User {username: {they} })
        MATCH (you:User {username: {you} })
        OPTIONAL MATCH (you)-[:published]->(:Post)<-[:tagged]-(tag:Tag),
                       (they)-[:published]->(:Post)<-[:tagged]-(tag)
        RETURN SIZE((they)-[:liked]->(:Post)<-[:published]-(you)) as likes,
               COLLECT(DISTINCT tag.name) as tags
        """
        return graph.run(query, they=other.username, you=self.username)
