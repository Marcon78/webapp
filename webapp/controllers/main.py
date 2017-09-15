from os import path
from flask import Blueprint, redirect, url_for

main_blueprint = Blueprint("main", __name__,
                           template_folder=path.join(path.pardir, "templates", "main"))

@main_blueprint.route("/")
def index():
    return redirect(url_for("blog.home"))
