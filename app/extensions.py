from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_mail import Mail
from flask_moment import Moment
from flask_login import LoginManager
from flask_debugtoolbar import DebugToolbarExtension
from flask_cache import Cache

bootstrap = Bootstrap()
db = SQLAlchemy()
migrate = Migrate(db=db)
mail = Mail()
moment = Moment()
login_manager = LoginManager()
toolbar = DebugToolbarExtension()
cache = Cache()


def config_extensions(app):
    bootstrap.init_app(app)
    db.init_app(app)
    migrate.init_app(app)
    mail.init_app(app)
    moment.init_app(app)
    login_manager.init_app(app)
    toolbar.init_app(app)
    cache.init_app(app)

    login_manager.login_view = 'users.login'
    login_manager.login_message = '需要先登录'

    # 设置session保护级别
    # 'strong'：最严格的保护，一旦用户登录信息改变，立即退出登录
    login_manager.session_protection = 'strong'
