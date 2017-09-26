import os


basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    # 是否需要追踪对象的修改并且发送信号。这需要额外的内存，如果不必要的可以禁用它。
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = "j5@CRnKRfSG9XCcp"


class ProdConfig(Config):
    CACHE_TYPE = "simple"


class DevConfig(Config):
    DEBUG = True
    # 禁止 Flask Debug Toolbar 拦截 HTTP 302 重定向请求。
    DEBUG_TB_INTERCEPT_REDIRECTS = False
    # 禁止 Flask Assets 在开发环境中编译库文件。
    ASSETS_DEBUG = True
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

    # CACHE_TYPE = "null"
    # CACHE_TYPE = "simple"
    CACHE_TYPE = "redis"
    CACHE_REDIS_HOST = "192.168.7.150"
    CACHE_REDIS_PORT = "6379"
    CACHE_REDIS_PASSWORD = ""
    CACHE_REDIS_DB = "0"