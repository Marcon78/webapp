from datetime import datetime
from sqlalchemy import func
from flask import Flask, render_template, url_for, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from flask_bootstrap import Bootstrap
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length
from config import DevConfig


app = Flask(__name__)
app.config.from_object(DevConfig)

db = SQLAlchemy(app)

bootstrap = Bootstrap(app)

tags = db.Table("post_tags",
                db.Column("post_id", db.Integer, db.ForeignKey("posts.id")),
                db.Column("tag_id", db.Integer, db.ForeignKey("tags.id"))
                )


class Tag(db.Model):
    __tablename__ = "tags"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))

    def __init__(self, title):
        self.title = title

    def __repr__(self):
        return "<Tag '{}'>".format(self.title)


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer(), primary_key=True)
    username = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(32))
    # relationship 的第一个参数表明这个关系的另一端是哪个模型；
    # backref 参数向外键（从属）模型中添加一个以此字符串命名的属性，从而定义反向关系；
    # lazy 参数指定如何加载相关记录。可选值有：
    #     select（首次访问时按需加载）
    #     immediate（源对象加载后就加载）
    #     joined（加载记录，但使用联结）
    #     subquery（立即加载，但使用子查询）
    #     noload（永不加载）
    #     dynamic（不加载记录，但提供加载记录的查询）
    posts = db.relationship("Post", backref="user", lazy="dynamic")

    def __init__(self, username, password=None):
        self.username = username
        self.password = password

    def __repr__(self):
        return "<User '{}'>".format(self.username)


class Post(db.Model):
    __tablename__ = "posts"

    id = db.Column(db.Integer(), primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    text = db.Column(db.Text(), nullable=False)
    publish_date = db.Column(db.DateTime(), default=datetime.utcnow())
    # ForeignKey 的 column 参数是一个形式为 "tablename.columnkey" 或者 "schema.tablename.columnkey" 的字符串。
    # 之所以使用“表名.字段”，而不是使用“类名.变量”引用，是因为在 SQLAlchemy 初始化期间，类对象可能还没有被创建出来。
    user_id = db.Column(db.Integer(), db.ForeignKey("users.id"))
    comments = db.relationship("Comment", backref="post", lazy="dynamic")
    # secondary 参数会告知 SQLAlchemy 该关联被保存在该参数指定的表中。
    tags = db.relationship("Tag",
                           secondary=tags,
                           backref=db.backref("posts", lazy="dynamic"),
                           lazy="dynamic")

    def __init__(self, title):
        self.title = title

    def __repr__(self):
        return "<Post '{}'>".format(self.title)


class Comment(db.Model):
    __tablename__ = "comments"

    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(255))
    text = db.Column(db.Text())
    date = db.Column(db.DateTime(), default=datetime.utcnow())
    post_id = db.Column(db.Integer, db.ForeignKey("posts.id"))

    def __repr__(self):
        return "<Comment '{}'>".format(self.text[:15])


class CommentForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired(), Length(max=255)],
                       render_kw={
                           "placeholder": "Your name",
                           "style": "background: url(/static/login-locked-icon.png) no-repeat 15px center;text-indent: 28px"
                       })
    text = TextAreaField("Comment", validators=[DataRequired()])
    submit = SubmitField("Add Comment", render_kw={"style": "color:#FFFFFF; background-color:#337ab7"})


def sidebar_data():
    recent = Post.query.order_by(Post.publish_date.desc()).limit(5).all()
    # 取 5 个最常用标签。
    # 使用 SQLAlchemy 的 func 库可以返回一个计数器。
    top_tags = db.session.query(Tag,
                                func.count(tags.c.post_id).label("total")
                                ).join(tags).group_by(Tag).order_by("total DESC").limit(5).all()
    return recent, top_tags


@app.route("/")
@app.route("/<int:page>")
def home(page=1):
    posts = Post.query.order_by(Post.publish_date.desc()).paginate(page, 10)
    recent, top_tags = sidebar_data()
    return render_template("home.html",
                           posts=posts,
                           recent=recent, top_tags=top_tags)


@app.route("/post/<int:post_id>", methods=["GET", "POST"])
def post(post_id):
    form = CommentForm()
    if form.validate_on_submit():
        new_comment = Comment()
        new_comment.name = form.name.data
        new_comment.text = form.text.data
        new_comment.post_id = post_id
        db.session.add(new_comment)
        db.session.commit()
        return redirect(url_for("post", post_id=post_id))
    post = Post.query.get_or_404(post_id)
    tags = post.tags
    comments = post.comments.order_by(Comment.date.desc()).all()
    recent, top_tags = sidebar_data()
    return render_template("post.html",
                           post=post, tags=tags, comments=comments,
                           recent=recent, top_tags=top_tags,
                           form=form)


@app.route("/tag/<string:tag_name>")
def tag(tag_name):
    tag = Tag.query.filter_by(title=tag_name).first_or_404()
    posts = tag.posts.order_by(Post.publish_date.desc()).all()
    recent, top_tags = sidebar_data()
    return render_template("tag.html",
                           tag=tag, posts=posts,
                           recent=recent, top_tags=top_tags)


@app.route("/user/<string:username>")
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    posts = user.posts.order_by(Post.publish_date.desc()).all()
    recent, top_tags = sidebar_data()
    return render_template("user.html",
                           user=user, posts=posts,
                           recent=recent, top_tags=top_tags)


if __name__ == "__main__":
    app.run(port=8080)