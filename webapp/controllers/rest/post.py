from datetime import datetime
from flask import abort
from flask_restful import Resource, fields, marshal_with

from .fields import HTMLField
from .parsers import post_get_parser, post_post_parser, post_put_parser, post_delete_parser
from webapp.models import db, User, Post, Tag

nested_tag_fields = {
    "id": fields.Integer(),
    "title": fields.String()
}

post_fields = {
    "id": fields.Integer(),
    "author": fields.String(attribute=lambda x: x.user.username),   # 只需要 author 对象的用户名属性即可。
    "title": fields.String(),
    "text": HTMLField(),
    "tags": fields.List(fields.Nested(nested_tag_fields)),
    "publish_date": fields.DateTime(dt_format="iso8601")
}

# 使用 HTTPie 测试：
# http 127.0.0.1:8080/api/post user=="Marco" page==1
class PostApi(Resource):
    @marshal_with(post_fields)
    def get(self, post_id=None):
        if post_id:
            # post = Post.query.get(post_id)
            # if not post:
            #     abort(404)
            post = Post.query.get_or_404(post_id)
            return post
        else:
            args = post_get_parser.parse_args()
            page = args["page"] or 1

            if args.get("user"):
                user = User.query.filter_by(username=args["user"]).first()
                posts = user.posts.order_by(Post.publish_date.desc()).paginate(page, 30)
            else:
                posts = Post.query.order_by(Post.publish_date.desc()).paginate(page, 30)
            return posts.items

    def post(self, post_id=None):
        if post_id:
            abort(400)  # bad request
        else:
            # strict 参数设为 True，表示如果请求中包含未在解析器中定义的参数时，抛出 400 (BadRequest) 异常。
            args = post_post_parser.parse_args(strict=True)

            user = User.verify_auth_token(args["token"])
            if not user:
                abort(401)  # Unauthorized

            new_post = Post(args["title"])
            new_post.user = user
            new_post.date = datetime.utcnow()
            new_post.text = args["text"]

            if args.get("tags"):
                for item in args["tags"]:
                    tag = Tag.query.filter_by(title=item).first()
                    if not tag:
                        tag = Tag(item)
                    new_post.tags.append(tag)

            db.session.add(new_post)
            db.session.commit()
            # 如果返回的是一个元组，第 2 个元素作为响应内容的 HTTP 状态码。
            # 还可以使用一个字典作为第 3 个元素，表示额外的响应头内容。
            return new_post.id, 201     # Created

    def put(self, post_id=None):
        # 修改必须要基于 post_id。
        if not post_id:
            abort(400)  # bad request

        post = Post.query.get_or_404(post_id)

        args = post_put_parser.parse_args(strict=True)
        user = User.verify_auth_token(args["token"])
        if not user:
            abort(401)  # Unauthorized
        elif user != post.user:
            abort(403)  # Forbidden

        post.title = args["title"] or post.title
        post.text = args["text"] or post.text

        if args["tags"]:
            for item in args["tags"]:
                tag = Tag.query.filter_by(title=item).first()

                if tag:
                    post.tags.append(tag)
                else:
                    new_tag = Tag(item)
                    post.tags.append(new_tag)

        db.session.add(post)
        db.session.commit()
        return post.id, 201     # Created

    def delete(self, post_id=None):
        if not post_id:
            abort(400)

        post = Post.query.get_or_404(post_id)

        args = post_delete_parser.parse_args(strict=True)
        user = User.verify_auth_token(args["token"])
        if not user:
            abort(401)
        elif user != post.user:
            abort(403)

        db.session.delete(post)
        db.session.commit()
        return "", 204      # No Content
