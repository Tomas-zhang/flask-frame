from flask_login import current_user
from flask_wtf import FlaskForm
from sqlalchemy.testing.pickleable import User
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo, \
    ValidationError
from flask_babel import gettext as _


class RegisterForm(FlaskForm):
    username = StringField(_('用户名'), validators=[
        DataRequired(message=_('请填写用户名')),
        Length(4, 20, message=_('长度在4到20个字符之间'))
    ])
    email = StringField('邮箱', validators=[
        DataRequired(message=_('请填写邮箱')),
        Email(message=_('请填写正确的邮箱格式'))
    ])
    password = PasswordField('密码', validators=[
        DataRequired(message=_('请填写密码')),
        Length(8, 20, message=_('密码长度在8到20个字符之间')),
        EqualTo('confirm', message=_('密码不一致'))
    ])
    confirm = PasswordField(_('密码确认'))
    submit = SubmitField(_('注册'))

    # 检验username是否存在
    def validate_username(self, field):
        user = User.query.filter_by(username=field.data).first()
        if user:
            raise ValidationError(_('用户名已存在'))

    def validate_email(self, field):
        user = User.query.filter_by(email=field.data).first()
        if user:
            raise ValidationError(_('邮箱已存在'))


class LoginForm(FlaskForm):
    username = StringField(_('用户名或邮箱'), validators=[
        DataRequired(message=_('用户名不能为空'))
    ])
    password = PasswordField(_('密码'), validators=[
        DataRequired(message=_('密码不能为空'))
    ])
    remember = BooleanField(_('记住我'), default=True)
    submit = SubmitField(_('登录'))


class UserPasswordForm(FlaskForm):
    oldpwd = PasswordField(_('原密码'), validators=[
        DataRequired(message=_('原密码不能为空'))
    ])
    newpwd = PasswordField(_('新密码'), validators=[
        DataRequired(message=_('请填写新密码')),
        Length(8, 20, message=_('密码长度8到20个字符')),
        EqualTo('confirm', message=_('密码不一致'))
    ])
    confirm = PasswordField(_('密码确认'))
    submit = SubmitField(_('提交'))

    def validate_oldpwd(self, field):
        user = current_user._get_current_object()
        if not user.verify_password(field.data):
            raise ValidationError(_('原密码错误'))

    def validate_newpwd(self, field):
        user = current_user._get_current_object()
        if user.verify_password(field.data):
            raise ValidationError(_('新旧密码不能一样'))


# 填写新邮箱来修改邮箱
class EmailForm(FlaskForm):
    email = StringField(_('新邮箱'), validators=[
        DataRequired(message=_('请填写新邮箱')),
        Email(message=_('请填写正确的邮箱格式'))
    ])
    submit = SubmitField(_('提交'))


# 用来提交用户名或邮箱来重置密码
class EUForm(FlaskForm):
    username = StringField(_('用户名或有效的邮箱'), validators=[
        DataRequired(message=_('用户名不能为空'))
    ])
    submit = SubmitField(_('下一步'), render_kw={'style': "float: right"})


# 用来提交验证码
class AuthCodeForm(FlaskForm):
    authcode = StringField(_('验证码'), validators=[
        DataRequired(message=_('验证码不能为空'))
    ])
    submit = SubmitField(_('提交'), render_kw={'style': "float: right"})


# 重置密码
class ResetPwdForm(FlaskForm):
    password = PasswordField(_('新密码'), validators=[
        DataRequired(message=_('请填写密码')),
        Length(8, 20, message=_('密码长度8到20个字符')),
        EqualTo('confirm', message=_('密码不一致'))
    ])
    confirm = PasswordField(_('密码确认'))
    submit = SubmitField(_('确定'), render_kw={'style': "float: right"})
