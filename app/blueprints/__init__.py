from .main import main
from .users import users

DEFAULT_BLUEPRINT = (
    (main, ''),
    (users, '/users')
)


# 循环读取蓝本并注册到app
def config_blueprint(app):
    for blueprint, prefix in DEFAULT_BLUEPRINT:
        app.register_blueprint(blueprint, url_prefix=prefix)
