from flask import Flask, url_for, redirect
from flask_bootstrap import Bootstrap

from webapp.config import DevConfig
from webapp.models import db
from webapp.controllers.blog import blog_blueprint
from webapp.controllers.main import main_blueprint


bootstrap = Bootstrap()


def create_app(object_name):
    """
    An flask application factory, as explained here:
    http://flask.pocoo.org/docs/patterns/appfactories/

    Arguments:
        object_name: the python path of the config object,
                     e.g. project.config.ProdConfig
    """
    app = Flask(__name__)
    app.config.from_object(object_name)

    db.init_app(app)
    bootstrap.init_app(app)

    app.register_blueprint(blog_blueprint)
    app.register_blueprint(main_blueprint)

    return app


# @app.route("/")
# def index():
#     return redirect(url_for("blog.home"))
#
# app.register_blueprint(blog_blueprint)

if __name__ == "__main__":
    app = create_app("webapp.config.DevConfig")
    app.run(port=8080)
