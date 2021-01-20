import pprint
from typing import Dict, List

import requests
from bs4 import BeautifulSoup
from dateutil.parser import parse
from flask import Request, jsonify
from sqlalchemy import desc

import settings
from mail_service import get_emails, send_mail
from models.db import db
from models.emails import Email, posts_identifier
from models.posts import Post


def get_posts() -> List[Post]:
    return Post.query.order_by(desc(Post.time)).all()


def drop_post_table() -> None:
    try:
        Post.__table__.drop(db.engine)
    except:
        pass
    db.create_all()


def print_posts() -> None:
    posts = get_posts()
    pprint.pprint(jsonify(posts))


def get_soup(url: str) -> BeautifulSoup:
    response = requests.get(url, headers=settings.HEADERS)
    if not response.ok:
        raise Exception(
            f"Failed to fetch soup! Status: {response.status_code}. Content: {response.content.decode('utf-8')}."
        )
    return BeautifulSoup(response.content, features="html.parser")


def add_hilight(post: Post, hilights: Dict[str, List[Post]], email: Email) -> None:
    sent_posts = email.sent_posts
    if post not in sent_posts:
        query_strings = email.search_query.split(",")
        if all(query_string.strip() in post.title for query_string in query_strings):
            if not email.email in hilights:
                hilights[email.email] = []
            if post not in hilights[email.email]:
                hilights[email.email].append(post)
                email.sent_posts.append(post)


def handle_bs_and_create_hilights(
    hilights: Dict[str, List[Post]],
    post_bs: BeautifulSoup,
    email: Email,
) -> None:
    post_title_element = post_bs.find("div", {"class": "structItem-title"})
    if len(post_title_element.find_all("a")) == 2:
        post_link = post_title_element.find_all("a")[1]
    else:
        post_link = post_title_element.find_all("a")[0]
    post_url = post_link["href"].split("/")
    post_url = "/".join(post_url[:-1])
    post_id = int(post_url.split(".")[-1].split("/")[0])
    post_title = post_link.text.lower()
    post_datetime = parse(post_bs.find("time", {"class": "u-dt"})["datetime"])

    existing_post = Post.query.get(post_id)
    if email.email in hilights:
        existing_post = existing_post or next(
            (x for x in hilights[email.email] if x.id == post_id), None
        )
    if not existing_post:
        post = Post(
            id=post_id,
            url=settings.BASE_URL + post_url,
            title=post_title,
            time=post_datetime,
        )
        db.session.add(post)
        add_hilight(post, hilights, email)
    else:
        add_hilight(existing_post, hilights, email)


def fetch_hilights_from_url(
    email: Email, hilights: Dict[str, List[Post]]
) -> List[Post]:

    soup = get_soup(email.url)
    posts = soup.findAll("div", {"class": "structItem"})
    for post_bs in posts:
        handle_bs_and_create_hilights(hilights, post_bs, email)
    return hilights


def fetch_posts(request: Request = None):
    hilights: Dict[str, List[Post]] = dict()

    for email in get_emails():
        try:
            fetch_hilights_from_url(email, hilights)
        except Exception as e:
            print(str(e))

    db.session.commit()

    send_mail(hilights, request)


def delete_old_posts() -> None:
    for url in db.session.query(Post.url).distinct():
        # Save at most 50 posts (the amount that fits on the page).
        posts = Post.query.filter(Post.url == url[0]).order_by(desc(Post.time)).all()
        for post in posts[50:]:
            db.session.delete(post)
        db.session.commit()
