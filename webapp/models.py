from datetime import datetime
from flask import current_app
from flask_mongoengine import MongoEngine
from flask_sqlalchemy import SQLAlchemy
from flask_login import AnonymousUserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer, SignatureExpired, BadSignature

from webapp.extensions import bcrypt#, cache


db = SQLAlchemy()
mongo = MongoEngine()

tags = db.Table("post_tags",
                db.Column("post_id", db.Integer, db.ForeignKey("posts.id")),
                db.Column("tag_id", db.Integer, db.ForeignKey("tags.id"))
                )

roles = db.Table("role_users",
                 db.Column("role_id", db.Integer, db.ForeignKey("roles.id")),
                 db.Column("user_id", db.Integer, db.ForeignKey("users.id"))
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
    # cascade 参数配置在父对象上执行的操作对相关对象的影响。
    posts = db.relationship("Post", backref="user",
                            lazy="dynamic",
                            cascade="all, delete-orphan")
    roles = db.relationship("Role",
                            secondary=roles,
                            backref=db.backref("users", lazy="dynamic"),
                            lazy="dynamic")

    def __init__(self, username, password=None):
        self.username = username
        if password:
            self.set_password(password)
        # one() 方法，完整的提取所有的记录行，
        # 并且如果没有明确的一条记录行（没有找到这条记录）或者结果中存在多条记录行，
        # 将会引发错误异常 NoResultFound 或者 MultipleResultsFound。
        default_role = Role.query.filter_by(name="DEFAULT").one()
        self.roles.append(default_role)

    def __repr__(self):
        return "<User '{}'>".format(self.username)

    def set_password(self, password):
        self.password = bcrypt.generate_password_hash(password)

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password, password)

    def is_authenticated(self):
        return not isinstance(self, AnonymousUserMixin)

    def is_active(self):
        return True

    def is_anonymous(self):
        return isinstance(self, AnonymousUserMixin)

    def get_id(self):
        return str(self.id)

    @staticmethod
    # @cache.memoize(timeout=60)  # memoize 不但会存储函数的运行结果，也会存储调用时的参数。
    def verify_auth_token(token):
        s = Serializer(current_app.config["SECRET_KEY"])
        try:
            data = s.loads(token)
        except SignatureExpired:
            return None
        except BadSignature:
            return None

        return User.query.get(data["id"])


class Role(db.Model):
    __tablename__ = "roles"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    description = db.Column(db.String(255))

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return "<Role '{}'>".format(self.name)


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
    # delete-orphan cascade is not supported on a many-to-many or many-to-one relationship when single_parent is not set.
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


#
# Mongo Example Code
#

available_roles = ("ADMINISTRATOR", "AUTHOR", "DEFAULT")

# 从 mongo.Document 继承，意味着只有在类中定义的键才会被保存到数据集合中。
# 如果是从 mongo.DynamicDocument 继承，则任何额外的字段都会被认为是 DynamicField，并且被保存到文档中。
class Userm(mongo.Document):
    username = mongo.StringField(primary_key=None,
                                 db_field=None,
                                 required=True,
                                 default=None,
                                 unique=False,
                                 unique_with=None,
                                 choices=None)
    password = mongo.StringField(required=True)
    roles = mongo.ListField(mongo.StringField(choices=available_roles))

    def __repr__(self):
        return "<User '{}'>".format(self.username)


# mongo.EmbeddedDocument 是一个内嵌的文档，可以将其传给 EmbeddedDocumentField 类型的字段。
class Commentm(mongo.EmbeddedDocument):
    name = mongo.StringField(required=True)
    text = mongo.StringField(required=True)
    date = mongo.DateTimeField(default=datetime.utcnow())

    def __repr__(self):
        return "<Comment '{}'>".format(self.text[:15])


class Postm(mongo.Document):
    title = mongo.StringField(required=True)
    publish_date = mongo.DateTimeField(default=datetime.utcnow())
    # ReferenceField 只是简单地保存了一个文档的唯一 ID，当被查询时，MongoEngine 会根据此 ID 返回被引用的文档。
    user = mongo.ReferenceField(Userm)
    comments = mongo.ListField(mongo.EmbeddedDocumentField(Commentm))
    tags = mongo.ListField(mongo.StringField())

    def __repr__(self):
        return "<Post '{}'>".format(self.title)

    # 文档的很多属性都可以通过类属性 meta 手动设置。
    meta = {
        # # 如果已经在现成的数据集上工作，希望把新写的类绑定到此集合上，设置 collection 键。
        # "collectino": "user_posts",
        # # 文档最大数量（个）。
        # "max_documents": 10000,
        # # 单个文档最大长度（字节 bytes）。
        # "max_size": 2000000,
        # # 集合默认的排序方式："+"表示升序，"-"表示降序。可以被查询时的 order_by 覆盖。
        # "ordering": ["-published_date"],
        # # 索引定义。字段前缀"+"表示升序，"-"表示降序。
        # # http://docs.mongoengine.org/guide/defining-documents.html?highlight=meta#indexes
        # "indexes": [
        #     "title",
        #     "$title",  # text index
        #     "#title",  # hashed index
        #     ("title", "-publish_date")
        # ],
        # 允许继承，默认是 False。
        # 由于继承后的子类不是直接派生于 Document，因此将不会独立存储于自己的集合中，而是和父（超）类保存在同一个集合中。
        "allow_inheritance": True
    }


class BlogPost(Postm):
    text = mongo.StringField(required=True)

    @property
    def type(self):
        return "blog"


class VideoPost(Postm):
    video_object = mongo.StringField(required=True)

    @property
    def type(self):
        return "video"


class ImagePost(Postm):
    image_url = mongo.StringField(required=True)

    @property
    def type(self):
        return "image"


class QuotePost(Postm):
    quote = mongo.StringField(required=True)
    author = mongo.StringField(required=True)

    @property
    def type(self):
        return "quote"
