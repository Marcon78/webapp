import os


basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    # 是否需要追踪对象的修改并且发送信号。这需要额外的内存，如果不必要的可以禁用它。
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = "j5@CRnKRfSG9XCcp"


class ProdConfig(Config):
    pass


class DevConfig(Config):
    DEBUG = True
    # 是否记录所有发到标准输出(stderr)的语句。
    SQLALCHEMY_ECHO = False
    # SQLALCHEMY_DATABASE_URI = os.environ.get("DEV_DATABASE_URL") or \
    #     "sqlite:///" + os.path.join(basedir, "data-dev.sqlite")
    SQLALCHEMY_DATABASE_URI = os.environ.get("DEV_DATABASE_URL") or \
        "sqlite:///" + os.path.join(os.path.pardir, "data-dev.sqlite")
    MONGODB_SETTINGS = {
        "db": "local",
        "host": "192.168.7.150",
        "port": 27017
    }
