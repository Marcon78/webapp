# 禁止由于 flask_cache 的 jinja2ext.py 中使用了 flask.ext.cache 而不是 flask_cache，
# 而造成的 ExtDeprecationWarning。
import warnings
from flask.exthook import ExtDeprecationWarning

warnings.simplefilter("ignore", ExtDeprecationWarning)

from flask_bootstrap import Bootstrap
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_principal import Principal, Permission, RoleNeed
# from flask_restful import Api
# from flask_debugtoolbar import DebugToolbarExtension
# http://pythonhosted.org/Flask-Cache/
# from flask_cache import Cache
from flask_assets import Environment, Bundle

# from flask_youtube import Youtube

from flask import request
from gzip import GzipFile
from io import BytesIO

bootstrap = Bootstrap()
bcrypt = Bcrypt()
lm = LoginManager()
principals = Principal()
# rest_api = Api()
# debug_toolbar = DebugToolbarExtension()
# cache = Cache()
assets_env = Environment()

admin_permission = Permission(RoleNeed("ADMINISTRATOR"))
poster_permission = Permission(RoleNeed("AUTHOR"))
default_permission = Permission(RoleNeed("DEFAULT"))

# # 如果需要为匿名用户实现一些特定的功能，可创建一个继承自 AnonymousUserMixin 的自定义类，并指派给默认的匿名用户。
# lm.anonymous_user = your_custom_anonymous_user
lm.login_view = "main.login"
lm.login_message = "Please login to access this page"
lm.login_message_category = "info"
lm.session_protection = "strong"

main_css = Bundle(
    "css/bootstrap.css",
    filters="cssmin",
    output="css/common.css"
)

main_js = Bundle(
    "js/jquery.js",
    "js/bootstrap.js",
    "js/ckeditor.js",
    filters="jsmin",
    output="js/common.js"
)


# 接受一个（unicode 类型的）用户 ID，并且返回一个用户对象（或者 None）。
@lm.user_loader
def load_user(user_id):
    from webapp.models import User
    return User.query.get(int(user_id))

# youtube_ext = Youtube()

class GZip(object):
    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        # 为应用的 after_request 事件注册一个函数。用于压缩返回的结果。
        app.after_request(self.after_request)

    def after_request(self, response):
        encoding = request.headers.get("Accept-Encoding", "")
        if "gzip" not in encoding or \
                not response.status_code in (200, 201):
            return response

        response.direct_passthrough = False

        # 开始压缩 response 中的数据。
        gzip_buffer = BytesIO()
        with GzipFile(mode="wb", compresslevel=5, fileobj=gzip_buffer) as gzip_file:
            gzip_file.write(response.get_data())

        response.set_data(bytes(gzip_buffer.getvalue()))

        response.headers["Content-Encoding"] = "gzip"
        response.headers["Content-Length"] = response.content_length

        return response

flask_gzip = GZip()
