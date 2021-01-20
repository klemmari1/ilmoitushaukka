import os

from flask import redirect, render_template, request, session, url_for
from flask_api import FlaskAPI

import settings
from mail_service import subscribe_email, unsubscribe_email
from models.db import db
from post_service import delete_old_posts, drop_post_table, fetch_posts, get_posts

app = FlaskAPI(__name__)
app.secret_key = settings.SECRET_KEY


# DB Setup
conn_str = os.getenv("DATABASE_URL", "sqlite:///app.db")
app.config["SQLALCHEMY_DATABASE_URI"] = conn_str
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.app_context().push()

db.init_app(app)
db.create_all()


@app.route("/", methods=["GET"])
def home():
    unsubscribe = request.args.get("unsubscribe")
    if unsubscribe:
        is_unsubscribed = unsubscribe_email(unsubscribe)
        if is_unsubscribed:
            session["success"] = "Email unsubscribed from sale alerts!"
        else:
            session["warning"] = "Email is not subscribed to sale alerts!"
    return render_template(
        "index.html",
        success=session.pop("success", None),
        warning=session.pop("warning", None),
    )


@app.route("/", methods=["POST"])
def handle_email_form():
    sub_type = request.form["sub-type"]
    email_input = request.form["email-input"][:120]
    url = request.form["search-url"][:500]
    search_query = request.form["search-query"][:200].lower()

    if sub_type == "subscribe" and (
        not url or not search_query or settings.BASE_URL not in url
    ):
        session["warning"] = "Invalid URL or search query!"
        return redirect(url_for("home"))

    if sub_type == "subscribe":
        is_subscribed = subscribe_email(email_input, url, search_query)
        if is_subscribed:
            session["success"] = "Email subscribed to sale alerts!"
        else:
            session["warning"] = "Email already subscribed to sale alerts!"
    elif sub_type == "unsubscribe":
        is_unsubscribed = unsubscribe_email(email_input)
        if is_unsubscribed:
            session["success"] = "Email unsubscribed from sale alerts!"
        else:
            session["warning"] = "Email is not subscribed to sale alerts!"
    return redirect(url_for("home"))


@app.route("/posts/", methods=["GET"])
def posts_list():
    return get_posts()


@app.route("/posts/fetch/", methods=["GET"])
def posts_fetch():
    fetch_posts()
    return {"status": "ok"}


@app.route("/posts/delete_old/", methods=["GET"])
def posts_delete_old():
    delete_old_posts()
    return {"status": "ok"}


@app.route("/posts/delete_all/", methods=["GET"])
def drop_posts():
    drop_post_table()
    return {"status": "ok"}


if __name__ == "__main__":
    app.run(debug=True, port=5000)
