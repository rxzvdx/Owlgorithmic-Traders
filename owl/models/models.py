from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Favorite(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_email = db.Column(db.String(255), nullable=False)
    symbol = db.Column(db.String(10), nullable=False)
