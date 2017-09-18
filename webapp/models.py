from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

from webapp.extensions import bcrypt

db = SQLAlchemy()

tags = db.Table("post_tags",
                db.Column("post_id", db.Integer, db.ForeignKey("posts.id")),
                db.Column("tag_id", db.Integer, db.ForeignKey("tags.id"))
                )


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer(), primary_key=True)
    username = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(128))
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
        if password:
            self.set_password(password)

    def __repr__(self):
        return "<User '{}'>".format(self.username)

    def set_password(self, password):
        self.password = bcrypt.generate_password_hash(password)

    def check_password(self, password):
        bcrypt.check_password_hash(self.password, password)


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

class Tag(db.Model):
    __tablename__ = "tags"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))

    def __init__(self, title):
        self.title = title

    def __repr__(self):
        return "<Tag '{}'>".format(self.title)