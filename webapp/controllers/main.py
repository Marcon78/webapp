from os import path
from flask import Blueprint, render_template, redirect, url_for, flash, current_app
from flask_login import login_user, logout_user
from flask_principal import identity_changed, Identity, IdentityContext, AnonymousIdentity

from webapp.extensions import admin_permission
from webapp.forms import LoginForm, RegisterForm
from webapp.models import db, User


main_blueprint = Blueprint("main", __name__,
                           template_folder=path.join(path.pardir, "templates", "main"))


# 上下文处理,可以在jinja2判断是否有执行权限
@main_blueprint.app_context_processor
def context():
    admin = IdentityContext(admin_permission)
    return dict(admin=admin)


@main_blueprint.route("/")
def index():
    return redirect(url_for("blog.home"))


@main_blueprint.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)

            # 当用户登录时，会触发 on_identity_loaded 方法，载入 Need 对象。
            identity_changed.send(
                # current_app 只是一个包装对象，要获取真正的对象，需要调用 _get_current_object() 方法。
                current_app._get_current_object(),
                identity=Identity(user.id)
            )

            flash("You have been logged in.", category="success")
            return redirect(url_for(".index"))
    return render_template("login.html", form=form)


# @main_blueprint.route("/logout", methods=["GET", "POST"])
@main_blueprint.route("/logout")
def logout():
    logout_user()

    identity_changed.send(
        current_app._get_current_object(),
        identity=AnonymousIdentity()
    )

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