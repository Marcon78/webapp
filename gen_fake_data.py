from random import seed, randint, sample

import forgery_py

from webapp.controllers.main import db, \
    User, Post, Tag

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


# insert tags.
tags = ["Python", "SQLAlchemy", "Ruby", "AJAX", "Others"]

for t in tags:
    if not Tag.query.filter_by(title=t).first():
        new_tag = Tag(t)
        db.session.add(new_tag)
        db.session.commit()

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
