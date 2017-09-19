import forgery_py
from random import seed, randint, sample

from webapp.models import User, Role, Post, Tag, Comment


def gen_fake_users(db):
    # insert users.
    users = [
        {"name": "Marco", "password": "dog"},
        {"name": "Ricky", "password": "cat"},
        {"name": "Emily", "password": "penguin"},
        {"name": "John", "password": "mouse"},
        {"name": "David", "password": "hedgehog"},
        {"name": "Susan", "password": "lizard"},
        {"name": "Hermione", "password": "rabbit"}
    ]

    for u in users:
        if not User.query.filter_by(username=u["name"]).first():
            new_user = User(u["name"], u["password"])
            db.session.add(new_user)
    db.session.commit()


def gen_fake_roles(db):
    roles = ["ADMINISTRATOR", "AUTHOR", "DEFAULT"]
    for r in roles:
        if not Role.query.filter_by(name=r).first():
            new_role = Role(r)
            db.session.add(new_role)
    db.session.commit()


def gen_fake_tags(db):
    # insert tags.
    tags = ["Python", "SQLAlchemy", "Ruby", "AJAX", "Others"]

    for t in tags:
        if not Tag.query.filter_by(title=t).first():
            new_tag = Tag(t)
            db.session.add(new_tag)
    db.session.commit()


def gen_fake_posts(db):
    tag_list = [t for t in Tag.query.all()]

    # insert posts.
    seed()
    user_count = User.query.count()
    for i in range(100):
        title = "Post" + str(i)
        if not Post.query.filter_by(title=title).first():
            new_post = Post(title)
            new_post.text = forgery_py.lorem_ipsum.sentence()
            new_post.user = User.query.offset(randint(0, user_count-1)).first()
            new_post.tags = sample(tag_list, randint(1, len(tag_list)))  # 取样 1 至 len(tag_list) 个。
            db.session.add(new_post)
    db.session.commit()


def gen_fake_comments(db):
    # insert comments.
    post_count = Post.query.count()
    for i in range(500):
        post = Post.query.offset(randint(0, post_count-1)).first()
        if post.comments.count() < 3:
            new_comment = Comment()
            new_comment.post_id = post.id
            new_comment.name = forgery_py.name.full_name()
            new_comment.text = forgery_py.lorem_ipsum.sentence()
            db.session.add(new_comment)
    db.session.commit()
