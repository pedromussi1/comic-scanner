from extensions import db
from werkzeug.security import generate_password_hash, check_password_hash

# -------------------- Models --------------------

class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)

    comics = db.relationship("Comic", backref="owner", cascade="all, delete-orphan")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Comic(db.Model):
    __tablename__ = "comics"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    isbn = db.Column(db.String(50))
    title = db.Column(db.String(300))
    authors = db.Column(db.String(300))
    publisher = db.Column(db.String(300))
    published_date = db.Column(db.String(100))
    cover_image = db.Column(db.String(500))
    info_link = db.Column(db.String(500))

    __table_args__ = (
        db.UniqueConstraint("user_id", "isbn", name="user_isbn_unique"),
    )

# -------------------- Database Functions --------------------

def init_db():
    """Create all tables"""
    db.create_all()

# -------------------- User Functions --------------------

def create_user(username, password):
    if User.query.filter_by(username=username).first():
        return False
    user = User(username=username)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    return True

def verify_user(username, password):
    user = User.query.filter_by(username=username).first()
    return user.check_password(password) if user else False

def get_user_id(username):
    user = User.query.filter_by(username=username).first()
    return user.id if user else None

def get_username_by_id(user_id):
    user = User.query.get(user_id)
    return user.username if user else None

# -------------------- Comic Functions --------------------

def add_comic(comic_data, user_id):
    if Comic.query.filter_by(user_id=user_id, isbn=comic_data.get("isbn")).first():
        return False
    comic = Comic(
        user_id=user_id,
        isbn=comic_data.get("isbn"),
        title=comic_data.get("title"),
        authors=comic_data.get("authors"),
        publisher=comic_data.get("publisher"),
        published_date=comic_data.get("published_date"),
        cover_image=comic_data.get("cover_image"),
        info_link=comic_data.get("info_link"),
    )
    db.session.add(comic)
    db.session.commit()
    return True

def get_all_comics(user_id, order_by="id DESC"):
    if order_by.lower() == "title":
        comics = Comic.query.filter_by(user_id=user_id).order_by(Comic.title).all()
    else:
        comics = Comic.query.filter_by(user_id=user_id).order_by(db.desc(Comic.id)).all()

    # Convert each comic object to a tuple in the expected order
    comics_tuples = [
        (
            c.id,
            c.user_id,
            c.isbn,
            c.title,
            c.authors,
            c.publisher,
            c.published_date,
            c.cover_image,
            c.info_link
        )
        for c in comics
    ]
    return comics_tuples


def delete_comic(comic_id, user_id):
    comic = Comic.query.filter_by(id=comic_id, user_id=user_id).first()
    if comic:
        db.session.delete(comic)
        db.session.commit()

def update_comic(comic_id, updated_data):
    comic = Comic.query.get(comic_id)
    if comic:
        comic.title = updated_data.get("title")
        comic.authors = updated_data.get("authors")
        comic.publisher = updated_data.get("publisher")
        comic.cover_image = updated_data.get("cover_image")
        db.session.commit()
