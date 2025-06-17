from flask import Blueprint, request, redirect, url_for, session, render_template, flash
from flask_dance.contrib.google import google
from models.models import db, Favorite

favorites_bp = Blueprint("favorites", __name__, url_prefix="/favorites")


@favorites_bp.route("/")
def view_favorites():
    if not google.authorized:
        session["next_after_login"] = url_for("favorites.view_favorites")
        return redirect(url_for("login"))

    resp = google.get("/oauth2/v1/userinfo")
    if not resp.ok:
        flash("Failed to fetch user info", "error")
        return redirect(url_for("index"))

    user_email = resp.json()["email"]
    favorites = Favorite.query.filter_by(user_email=user_email).all()

    return render_template("favorites.html", favorites=favorites)


@favorites_bp.route("/add/<symbol>", methods=["POST"])
def add_favorite(symbol):
    if not google.authorized:
        session["next_after_login"] = url_for("favorites.view_favorites")
        return redirect(url_for("login"))

    resp = google.get("/oauth2/v1/userinfo")
    if not resp.ok:
        flash("Failed to fetch user info", "error")
        return redirect(url_for("index"))

    user_email = resp.json()["email"]

    # Avoid duplicates
    existing = Favorite.query.filter_by(user_email=user_email, symbol=symbol).first()
    if not existing:
        new_fav = Favorite(user_email=user_email, symbol=symbol)
        db.session.add(new_fav)
        db.session.commit()
        flash(f"{symbol} added to favorites.", "success")
    else:
        flash(f"{symbol} is already in your favorites.", "info")

    return redirect(request.referrer or url_for("index"))


@favorites_bp.route("/remove/<symbol>", methods=["POST"])
def remove_favorite(symbol):
    if not google.authorized:
        session["next_after_login"] = url_for("favorites.view_favorites")
        return redirect(url_for("login"))

    resp = google.get("/oauth2/v1/userinfo")
    if not resp.ok:
        flash("Failed to fetch user info", "error")
        return redirect(url_for("index"))

    user_email = resp.json()["email"]

    favorite = Favorite.query.filter_by(user_email=user_email, symbol=symbol).first()
    if favorite:
        db.session.delete(favorite)
        db.session.commit()
        flash(f"{symbol} removed from favorites.", "success")

    return redirect(request.referrer or url_for("favorites.view_favorites"))
