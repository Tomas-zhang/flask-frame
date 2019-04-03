from flask import Flask, render_template
from config import config
from .extensions import config_extensions
from .blueprints import config_blueprint


def config_errorhandler(app):
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('error/404.html', e=e)


# 工厂模式，生成一个app实例对象
def create_app(config_mode='default'):
    app = Flask(__name__)
    app.config.from_object(config.get(config_mode))
    app.config.from_pyfile('babel.cfg')
    config[config_mode].init_app(app)
    config_extensions(app)
    config_blueprint(app)
    config_errorhandler(app)
    return app
