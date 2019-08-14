import os


class Config(object):
    DEBUG = False
    TESTING = False


class ProductionConfig(Config):
    @property
    def SECRET_KEY(self):
        key = os.environ.get('SECRET_KEY')
        if key is None:
            raise ValueError('No SECRET_KEY set for Flask')
        return key


class DevelopmentConfig(Config):
    DEBUG = True
    SECRET_KEY = 'dev'


class TestingConfig(Config):
    TESTING = True
    SECRET_KEY = 'test'
