from datetime import datetime
from flask import abort
from flask_restful import Resource

from webapp.extensions import admin_permission
from webapp.models import db, User, Post, Comment
from .parsers import comment_put_parser


class CommentApi(Resource):
    # @admin_permission.require(http_exception=403)
    def put(self, post_id=None):
        args = comment_put_parser.parse_args()
        user = User.verify_auth_token(args["token"])

        # import pdb
        # pdb.set_trace()

        if (not user) and (not admin_permission.can()):
            abort(401)  # Unauthorized

        if post_id:
            post = Post.query.get_or_404(post_id)
            if (user != post.user) and (not admin_permission.can()):
                abort(403)  # Forbidden
            comment_list = post.comments
        else:
            if not admin_permission.can():
                abort(403)  # Forbidden
            comment_list = Comment.query.all()

        for c in comment_list:
            c.text = args["text"] or c.text
            c.date = datetime.utcnow()
            db.session.add(c)
        db.session.commit()

        return c.id, 201, {"count": comment_list.count()}   # Created
