class config:
    pass

class ProdConfig(config):
    pass

class DevConfig(config):
    DEBUG = True
    pass