from dataclasses import dataclass
from datetime import datetime

from models.db import db


@dataclass
class Post(db.Model):
    id: int
    url: str
    title: str
    time: datetime

    id = db.Column(db.Integer, primary_key=True, autoincrement=False)
    url = db.Column(db.String(1000))
    title = db.Column(db.String(200))
    time = db.Column(db.DateTime)

    def __repr__(self):
        return "<Post %r>" % self.id
