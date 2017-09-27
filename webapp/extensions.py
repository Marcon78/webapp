from flask_bootstrap import Bootstrap
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_principal import Principal, Permission, RoleNeed
from flask_restful import Api
from flask_debugtoolbar import DebugToolbarExtension
# http://pythonhosted.org/Flask-Cache/
from flask_cache import Cache
from flask_assets import Environment, Bundle

# from flask_youtube import Youtube

bootstrap = Bootstrap()
bcrypt = Bcrypt()
lm = LoginManager()
principals = Principal()
rest_api = Api()
debug_toolbar = DebugToolbarExtension()
cache = Cache()
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