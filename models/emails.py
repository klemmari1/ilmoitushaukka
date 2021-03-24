from dataclasses import dataclass
from typing import List, Optional

from models.db import db
from models.posts import Post

posts_identifier = db.Table(
    "posts_identifier",
    db.Column("post_id", db.Integer, db.ForeignKey("post.id", ondelete='CASCADE'), nullable=True),
    db.Column("email_id", db.Integer, db.ForeignKey("email.id", ondelete='CASCADE'), nullable=True),
)


@dataclass
class Email(db.Model):
    id: Optional[int]
    email: str
    url: str
    search_query: str
    sent_posts: Optional[List[Post]]

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(120))
    url = db.Column(db.String(500))
    search_query = db.Column(db.String(200))
    sent_posts = db.relationship(
        "Post", secondary=posts_identifier, passive_deletes=True
    )

    def __repr__(self):
        return "<Email %r>" % self.email

    def subscribe(self):
        db.session.add(self)
        db.session.commit()

    def unsubscribe(self):
        db.session.delete(self)
        db.session.commit()
