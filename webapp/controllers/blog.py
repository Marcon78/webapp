from os import path
from flask import Blueprint, render_template, redirect, url_for
from sqlalchemy import func
from webapp.models import db, User, Post, Comment, Tag, tags
from webapp.forms import CommentForm
# from ..models import db, Post, Tag, tags


blog_blueprint = Blueprint("blog", __name__,
                           template_folder=path.join(path.pardir, "templates", "blog"),
                           url_prefix="/blog")


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
def home(page=1):
    posts = Post.query.order_by(Post.publish_date.desc()).paginate(page, 10)
    recent, top_tags = sidebar_data()
    return render_template("home.html",
                           posts=posts,
                           recent=recent, top_tags=top_tags)


@blog_blueprint.route("/post/<int:post_id>", methods=["GET", "POST"])
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
