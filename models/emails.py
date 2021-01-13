from dataclasses import dataclass
from typing import List, Optional

from models.db import db
from models.posts import Post

posts_identifier = db.Table(
    "posts_identifier",
    db.Column("post_id", db.Integer, db.ForeignKey("post.id")),
    db.Column("email_id", db.String(120), db.ForeignKey("email.email")),
)


@dataclass
class Email(db.Model):
    email: str
    url: str
    search_query: str
    sent_posts: Optional[List[Post]]

    email = db.Column(db.String(120), primary_key=True)
    url = db.Column(db.String(500))
    search_query = db.Column(db.String(200))
    sent_posts = db.relationship("Post", secondary=posts_identifier)

    def __repr__(self):
        return "<Email %r>" % self.email

    def subscribe(self):
        db.session.add(self)
        db.session.commit()

    def unsubscribe(self):
        db.session.delete(self)
        db.session.commit()
