from index import app
from post_service import fetch_posts

if __name__ == "__main__":
    print("Fetching posts..")
    with app.app_context():
        fetch_posts()
    print("Posts fetched!")
