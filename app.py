import os
from flask import Flask, request, render_template, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from pyzbar.pyzbar import decode
from PIL import Image
import requests

from extensions import db
from database import (
    init_db, add_comic, get_all_comics, delete_comic,
    create_user, verify_user, get_user_id, get_username_by_id,
    update_comic
)

from dotenv import load_dotenv
load_dotenv()

# -------------------- Flask App --------------------
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "supersecretkey")

# -------------------- Database Setup --------------------

# Get the DATABASE_URL environment variable
DATABASE_URL = os.getenv("DATABASE_URL", "")

# If DATABASE_URL is empty or points to an unreachable host (like the old remote), use local SQLite
if not DATABASE_URL or "weathered-frog" in DATABASE_URL:
    DATABASE_URL = "sqlite:///local.db"
    print("Using local SQLite database.")

# Fix old-style Heroku/Postgres URLs
elif DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
    print("Using remote PostgreSQL database.")

app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize SQLAlchemy
db.init_app(app)

with app.app_context():
    init_db()


# -------------------- Upload Config --------------------
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# -------------------- Flask-Login Setup --------------------
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"
login_manager.login_message = "Please log in to continue."

class UserSession(UserMixin):
    def __init__(self, id, username):
        self.id = id
        self.username = username

@login_manager.user_loader
def load_user(user_id):
    username = get_username_by_id(user_id)
    if username:
        return UserSession(user_id, username)
    return None

# -------------------- Helper Functions --------------------
def detect_isbn(image_path):
    img = Image.open(image_path)
    decoded_objects = decode(img)
    if decoded_objects:
        return decoded_objects[0].data.decode("utf-8")
    return None

def query_google_books(isbn):
    url = f"https://www.googleapis.com/books/v1/volumes?q=isbn:{isbn}"
    response = requests.get(url).json()
    if "items" in response:
        book = response["items"][0]["volumeInfo"]
        return {
            "Title": book.get("title", "Unknown"),
            "Authors": ", ".join(book.get("authors", ["Unknown"])),
            "Publisher": book.get("publisher", "Unknown"),
            "Published Date": book.get("publishedDate", "Unknown"),
            "Cover Image": book.get("imageLinks", {}).get("thumbnail", ""),
            "ISBN": isbn,
            "Info Link": book.get("infoLink", "")
        }
    return None

# -------------------- Routes --------------------
@app.route("/", methods=["GET", "POST"])
def index():
    message = None
    scanned_comic = None

    if request.method == "POST":
        # --- Upload image to scan ---
        if "image" in request.files:
            file = request.files["image"]
            if file.filename != "":
                file_path = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
                file.save(file_path)
                isbn = detect_isbn(file_path)
                if isbn:
                    scanned_comic = query_google_books(isbn)
                    if not scanned_comic:
                        message = f"Book with ISBN {isbn} not found"
                else:
                    message = "No barcode detected in the image"

        # --- Add comic to collection ---
        elif "add_isbn" in request.form:
            if not current_user.is_authenticated:
                flash("Please log in to add comics to your collection.", "error")
                return redirect(url_for("login", next=request.url))

            comic_to_add = {
                'isbn': request.form.get("add_isbn"),
                'title': request.form.get("add_title"),
                'authors': request.form.get("add_authors"),
                'publisher': request.form.get("add_publisher"),
                'published_date': request.form.get("add_published_date"),
                'cover_image': request.form.get("add_cover_image"),
                'info_link': request.form.get("add_info_link")
            }
            added = add_comic(comic_to_add, current_user.id)
            message = "Comic added to your collection!" if added else "Comic already exists in your collection."

    return render_template("index.html", scanned_comic=scanned_comic, message=message)

@app.route("/collection")
@login_required
def collection():
    sort = request.args.get("sort", "latest")
    if sort == "alphabetical":
        comics = get_all_comics(current_user.id, order_by="title")
    else:
        comics = get_all_comics(current_user.id, order_by="id DESC")
    return render_template("collection.html", collection=comics, current_sort=sort)

@app.route("/delete/<int:comic_id>", methods=["POST"])
@login_required
def delete_comic_route(comic_id):
    delete_comic(comic_id, current_user.id)
    flash("Comic deleted successfully.", "success")
    return redirect(url_for("collection"))

# -------------------- Authentication --------------------
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if create_user(username, password):
            flash("Account created successfully! Please log in.", "success")
            return redirect(url_for("login"))
        else:
            flash("Username already exists.", "error")
    return render_template("signup.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if verify_user(username, password):
            user_id = get_user_id(username)
            user = UserSession(user_id, username)
            login_user(user)
            flash(f"Welcome, {username}!")
            next_page = request.args.get("next")
            return redirect(next_page or url_for("index"))
        else:
            flash("Invalid username or password.", "error")
    return render_template("login.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "success")
    return redirect(url_for("index"))

@app.route("/edit_comic", methods=["POST"])
@login_required
def edit_comic():
    comic_id = request.form.get("comic_id")
    if not comic_id:
        flash("Invalid comic ID.", "error")
        return redirect(url_for("collection"))

    comic_data = {
        'title': request.form.get("title"),
        'authors': request.form.get("authors"),
        'publisher': request.form.get("publisher"),
        'cover_image': request.form.get("cover_image")
    }
    update_comic(comic_id, comic_data)
    flash("Comic updated successfully!", "success")
    return redirect(url_for("collection"))

# -------------------- Optional DB Check --------------------
@app.route("/dbcheck")
def dbcheck():
    return f"Connected to: {app.config['SQLALCHEMY_DATABASE_URI']}"

# -------------------- Run App --------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)
