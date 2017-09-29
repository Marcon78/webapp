#!/usr/bin/env python
import os
COV = None
if os.environ.get("FLASK_COVERAGE"):
    import coverage
    COV = coverage.coverage(branch=True, include="webapp/*")
    COV.start()


from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager, Server
from flask_script.commands import ShowUrls, Clean

from webapp import create_app
from webapp.models import db, User, Role, Post, Comment, Tag, \
    Userm, Commentm, Postm
from gen_fake_data import gen_fake_roles, gen_fake_users, gen_fake_tags, gen_fake_posts, gen_fake_comments

basedir = os.path.abspath(os.path.dirname(__file__))

env = os.environ.get("WEBAPP_ENV", "dev")
app = create_app("webapp.config.%sConfig" % env.capitalize())

migrate = Migrate(app, db)

manager = Manager(app)
manager.add_command("server", Server(port=8080))
manager.add_command("show-urls", ShowUrls())
# 清除工作目录中 Python 编译出来的 .pyc 和 .pyo 文件。
manager.add_command("clean", Clean())
manager.add_command("db", MigrateCommand)

@manager.command
def test(coverage=False):
    if coverage and not os.environ.get("FLASK_COVERAGE"):
        import sys
        os.environ["FLASK_COVERAGE"] = "1"
        os.execvp(sys.executable, [sys.executable] + sys.argv)

    import unittest
    tests = unittest.TestLoader().discover("test")
    # unittest.main() # 用这个是最简单的，下面的用法可以同时测试多个类
    # 这个等价于上述但可设置 verbosity=2，省去了运行时加 -v
    unittest.TextTestRunner(verbosity=2).run(tests)
    if COV:
        COV.stop()
        COV.save()
        print("Coverage Summary:")
        COV.report()
        covdir = os.path.join(basedir, "/tmp/coverage")
        COV.html_report(directory=covdir)
        print("HTML version: file://%s/index.html" % covdir)
        COV.erase()


# make_shell_context 函数会创建一个 Python 命令行，并且在应用上下文中执行。
# 返回的字典告诉 Flask Script 在打开命令行时进行一些默认的导入工作。
@manager.shell
def make_shell_context():
    return dict(app=app, db=db,
                User=User, Role=Role, Post=Post, Comment=Comment, Tag=Tag,
                Userm=Userm, Commentm=Commentm, Postm=Postm)

@manager.command
def gen_fake():
    # 创建数据表，如果数据表存在，则忽视。
    db.create_all()
    gen_fake_roles(db)
    gen_fake_users(db)
    gen_fake_tags(db)
    gen_fake_posts(db)
    gen_fake_comments(db)

if __name__ == "__main__":
    manager.run()
