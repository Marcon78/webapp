from flask import current_app, abort
from flask_restful import Resource
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

from .parsers import user_post_parser
from webapp.models import db, User


class AuthApi(Resource):
    def post(self):
        args = user_post_parser.parse_args()
        user = User.query.filter_by(username=args["username"]).one()

        if user.check_password(args["password"]):
            s = Serializer(current_app.config["SECRET_KEY"], expires_in=600)
            # 注意 dumps 出来的字节流必须解码为字符串。
            return {"token": s.dumps({"id": user.id}).decode("ASCII")}
        else:
            return abort(401)   # Unauthorized
