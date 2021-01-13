from index import app
from post_service import delete_old_posts

if __name__ == "__main__":
    print("Deleting old posts..")
    with app.app_context():
        delete_old_posts()
    print("Posts deleted!")
