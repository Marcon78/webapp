from flask import Flask, url_for, redirect
from flask_login import current_user
from flask_principal import identity_loaded, UserNeed, RoleNeed

from webapp.config import DevConfig
from webapp.models import db, mongo
from webapp.extensions import (
    bootstrap, bcrypt, lm, principals, #rest_api,
    #debug_toolbar, #cache,
    assets_env, main_css, main_js, flask_gzip
    # youtube_ext
)
from webapp.controllers.blog import blog_blueprint
from webapp.controllers.main import main_blueprint
# from webapp.controllers.rest.post import PostApi
# from webapp.controllers.rest.auth import AuthApi
# from webapp.controllers.rest.comment import CommentApi

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
    mongo.init_app(app)
    bootstrap.init_app(app)
    bcrypt.init_app(app)
    lm.init_app(app)
    principals.init_app(app)

    # rest_api.add_resource(AuthApi,
    #                       "/api/auth")
    # rest_api.add_resource(PostApi,
    #                       "/api/post",
    #                       "/api/post/<int:post_id>")
    # rest_api.add_resource(CommentApi,
    #                       "/api/comments",
    #                       "/api/post/<int:post_id>/comments")
    # rest_api.init_app(app)

    # 如果使用了自定义的 flask_gzip 压缩 response 数据，那么需要关闭 Flask Debug Toolbar。
    # 因为它会将所有的响应都当作 UTF-8 文本进行处理。
    # debug_toolbar.init_app(app)
    # cache.init_app(app)

    assets_env.init_app(app)
    assets_env.register("main_js", main_js)
    assets_env.register("main_css", main_css)

    # youtube_ext.init_app(app)
    flask_gzip.init_app(app)

    @identity_loaded.connect_via(app)
    def on_identity_loaded(sender, identity):
        # set the user object of identity
        # 设置当前用户身份为 login 登录对象。
        identity.user = current_user

        # add the UserNeed to the identity
        # 添加 UserNeed 到 identity user 对象。
        if hasattr(current_user, "id"):
            identity.provides.add(UserNeed(current_user.id))

        # add each role to the identity
        # 每个 Role 添加到 identity user 对象，roles 是User的多对多关联。
        if hasattr(current_user, "roles"):
            for role in current_user.roles:
                identity.provides.add(RoleNeed(role.name))

    app.register_blueprint(blog_blueprint)
    app.register_blueprint(main_blueprint)

    return app


# @app.route("/")
# def index():
#     return redirect(url_for("blog.home"))
#
# app.register_blueprint(blog_blueprint)

# if __name__ == "__main__":
#     app = create_app("webapp.config.DevConfig")
#     app.run(port=8080)
