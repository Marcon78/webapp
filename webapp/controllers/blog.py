import locale
from datetime import datetime
from os import path
from sqlalchemy import func
from flask import Blueprint, render_template, redirect, url_for, abort, request
from flask_login import login_required, current_user
from flask_principal import Permission, UserNeed

from webapp.models import db, User, Post, Comment, Tag, tags, \
    Userm, BlogPost, QuotePost, VideoPost, ImagePost
from webapp.forms import CommentForm, PostForm
from webapp.extensions import poster_permission, admin_permission, cache


blog_blueprint = Blueprint("blog", __name__,
                           template_folder=path.join(path.pardir, "templates", "blog"),
                           url_prefix="/blog")


# key_prefix 要求是一个字符串，因此这里可以不用使用 encode()。
def make_cache_key(*args, **kwargs):
    """Dynamic creation the request url."""
    path = request.path
    args = str(hash(frozenset(request.args.items())))
    # return str((path + args).encode("utf-8"))
    return path + args


# key_prefix 对于非视图函数是必需的，这样 Flask Cache 才会正确地保存函数的返回值。
# 对于每一个被缓存的函数，这个值应该是唯一的。
# 这里的 timeout 值很大，因为与视图相比，函数的输出结果可能发生的变动更少。
@cache.cached(timeout=7200, key_prefix="sidebar_data")
def sidebar_data():
    recent = Post.query.order_by(Post.publish_date.desc()).limit(5).all()
    # 取 5 个最常用标签。
    # 使用 SQLAlchemy 的 func 库可以返回一个计数器。
    top_tags = db.session.query(
        Tag, func.count(tags.c.post_id).label("total")
    ).join(tags).group_by(Tag).order_by("total DESC").limit(5).all()
    return recent, top_tags


@blog_blueprint.route("/")
@blog_blueprint.route("/<int:page>")
@cache.cached(timeout=600)  # 缓存 60 秒。
def home(page=1):
    posts = Post.query.order_by(Post.publish_date.desc()).paginate(page, 10)
    recent, top_tags = sidebar_data()
    return render_template("home.html",
                           posts=posts,
                           recent=recent, top_tags=top_tags)


@blog_blueprint.route("/post/<int:post_id>", methods=["GET", "POST"])
@cache.cached(timeout=600, key_prefix=make_cache_key)
def post(post_id):
    form = CommentForm()
    if form.validate_on_submit():
        new_comment = Comment()
        new_comment.name = form.name.data
        new_comment.text = form.text.data
        new_comment.post_id = post_id
        db.session.add(new_comment)
        db.session.commit()
        return redirect(url_for(".post", post_id=post_id))
    post = Post.query.get_or_404(post_id)
    tags = post.tags
    comments = post.comments.order_by(Comment.date.desc()).all()
    recent, top_tags = sidebar_data()
    return render_template("post.html",
                           post=post, tags=tags, comments=comments,
                           recent=recent, top_tags=top_tags,
                           form=form)


@blog_blueprint.route("/new", methods=["GET", "POST"])
@login_required
@poster_permission.require(http_exception=403)  # Forbidden	禁止访问。
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        new_post = Post(form.title.data)
        new_post.text = form.text.data
        db.session.add(new_post)
        db.session.commit()
        # if form.type.data == "blog":
        #     new_post = BlogPost()
        #     new_post.text = form.text.data
        # elif form.type.data == "image":
        #     new_post = ImagePost()
        #     new_post.image_url = form.image.data
        # elif form.type.data == "video":
        #     new_post = VideoPost()
        #     new_post.video_object = form.video.data
        # elif form.type.data == "quote":
        #     new_post = QuotePost()
        #     new_post.text = form.text.data
        #     new_post.author = form.author.data
        #
        # new_post.title = form.title.data
        new_post.user = Userm.objects(username=current_user.username).one()
        # new_post.save(
        #     # # 与 SQLAlchemy 不同，MongoEngine 不会在 ReferenceField 中自动保存关联对象。
        #     # # 如果要在保存当前文档变更的同时对引用文档的变更也进行保存，则需要将 cascade 设为 True。
        #     # cascade=True,
        #     # # 插入文档时，会根据类中的参数定义进行类型检查，如果不希望检查，可以将 validate 设为 False。
        #     # validate=False,
        #     # # 写入级别。
        #     # write_concern={"w": 0},             # 不会等待写入，发生错误也不会通知客户端。
        #     # write_concern={"w": 1},             # 不会等待写入。缺省行为。
        #     # write_concern={"w": 1, "j": True},  # 会等待写入
        # )

        return redirect(url_for(".post", post_id=new_post.id))
    return render_template("new.html", form=form)

# 注意，如果要在 Jinja2 模板中使用 admin，需要 admin_permission 授权。
# 权限貌似不能够叠加使用。只能在创建的时候，通过 union 创建合并的权限。
@blog_blueprint.route("/edit/<int:id>", methods=["GET", "POST"])
@login_required
@poster_permission.require(http_exception=403)
# @admin_permission.require(http_exception=403)
def edit_post(id):
    post = Post.query.get_or_404(id)
    # 用户权限
    permission = Permission(UserNeed(post.user.id))
    # We want admins to be able to edit any post
    if permission.can() or admin_permission.can():
        form = PostForm()
        if form.validate_on_submit():
            post.title = form.title.data
            post.text = form.text.data
            post.publish_date = datetime.utcnow()
            db.session.add(post)
            db.session.commit()
            return redirect(url_for(".post", post_id=post.id))
        form.title.data = post.title
        form.text.data = post.text
        return render_template("edit.html", post=post, form=form)
    abort(403)


@blog_blueprint.route("/tag/<string:tag_name>")
def tag(tag_name):
    tag = Tag.query.filter_by(title=tag_name).first_or_404()
    posts = tag.posts.order_by(Post.publish_date.desc()).all()
    recent, top_tags = sidebar_data()
    return render_template("tag.html",
                           tag=tag, posts=posts,
                           recent=recent, top_tags=top_tags)


@blog_blueprint.route("/user/<string:username>")
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    posts = user.posts.order_by(Post.publish_date.desc()).all()
    recent, top_tags = sidebar_data()
    return render_template("user.html",
                           user=user, posts=posts,
                           recent=recent, top_tags=top_tags)
