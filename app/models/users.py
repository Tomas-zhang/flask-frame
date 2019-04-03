from datetime import datetime

from flask import current_app, flash
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from itsdangerous import BadSignature, SignatureExpired
from app.extensions import db, login_manager
from flask_babel import lazy_gettext as _
from flask_login import UserMixin


class Base(object):
    def save(self):
        try:
            db.session.add(self)
            db.session.commit()
        except:
            db.session.rollback()


class User(Base, UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32), nullable=False, unique=True)
    password_hash = db.Column(db.String(128), nullable=False)
    email = db.column(db.String(64), nullable=False, unique=True)
    confirm = db.column(db.Boolean, default=False)
    create_time = db.Column(db.DateTime, doc=_('创建时间'), default=datetime.now)

    def __init__(self, username, password, email):
        self.username = username
        self.password_hash = generate_password_hash(password)
        self.email = email

    def __repr__(self):
        return self.username

    # 密码字段保护
    @property
    def password(self):
        raise AttributeError(_('密码是不可读属性'))

    # 设置密码， 加密存储
    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    # 生成激活token
    def generate_activate_token(self):
        # 创建用于生成token的类，需要传递秘钥和有效期expires_in默认=3600,expires_in=60
        s = Serializer(current_app.config['SECRET_KEY'])
        return s.dumps({'id': self.id})

    # 生成任意的token
    @staticmethod
    def generate_token(dict_data):
        s = Serializer(current_app.config['SECRET_KEY'])
        return s.dumps(dict_data)

    # 检查任意token是否有效,返回真实词典数据
    @staticmethod
    def check_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            dict_data = s.loads(token)
        except SignatureExpired:
            flash(_('邮件已过期'))
            return False
        except BadSignature:
            flash(_('无效的验证邮箱'))
            return False
        return dict_data

    # 账户激活，因为激活时还不知道是哪个用户
    @staticmethod
    def check_activate_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except SignatureExpired:
            flash(_('激活邮件已过期'))
            return False
        except BadSignature:
            flash(_('无效的激活'))
            return False
        user = User.query.get(data.get('id'))
        if not user:
            flash(_('激活的账号不存在'))
            return False
        # 激活
        if not user.confirm:
            user.confirm = True
            db.session.add(user)
        return True

    # 密码校验
    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    @login_manager.user_loader
    def load_user(uid):
        return User.query.get(int(uid))
