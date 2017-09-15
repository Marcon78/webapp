import os
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager, Server
from flask_script.commands import ShowUrls

from webapp import create_app
from webapp.models import db, User, Post, Comment, Tag

env = os.environ.get("WEBAPP_ENV", "dev")
app = create_app("webapp.config.%sConfig" % env.capitalize())

migrate = Migrate(app, db)

manager = Manager(app)
manager.add_command("server", Server(port=8080))
manager.add_command("show-urls", ShowUrls())
manager.add_command("db", MigrateCommand)


# make_shell_context 函数会创建一个 Python 命令行，并且在应用上下文中执行。
# 返回的字典告诉 Flask Script 在打开命令行时进行一些默认的导入工作。
@manager.shell
def make_shell_context():
    return dict(app=app, db=db,
                User=User, Post=Post, Comment=Comment, Tag=Tag)

if __name__ == "__main__":
    manager.run()
