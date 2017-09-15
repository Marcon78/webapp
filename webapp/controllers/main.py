from os import path
from flask import Blueprint, render_template, redirect, url_for, flash

from webapp.forms import LoginForm, RegisterForm
from webapp.models import db, User


main_blueprint = Blueprint("main", __name__,
                           template_folder=path.join(path.pardir, "templates", "main"))


@main_blueprint.route("/")
def index():
    return redirect(url_for("blog.home"))


@main_blueprint.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        flash("You have been logged in.", category="success")
        return redirect(url_for(".index"))
    return render_template("login.html",
                           form=form)


# @main_blueprint.route("/logout", methods=["GET", "POST"])
@main_blueprint.route("/logout")
def logout():
    flash("You have been logged out.", category="success")
    return redirect(url_for(".index"))


@main_blueprint.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        new_user = User()
        new_user.username = form.username.data
        new_user.set_password(form.password.data)
        db.session.add(new_user)
        db.session.commit()

        flash("A new user has been created, please login.",
              category="success")

        return redirect(url_for(".login"))

    return render_template("register.html",
                           form=form)