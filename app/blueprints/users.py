from flask import Blueprint, request, flash, url_for, redirect, render_template
from flask_login import login_user, logout_user, current_user
from sqlalchemy import or_
from flask_babel import gettext as _trans

from app.email import send_mail
from app.extensions import db
from app.forms import RegisterForm, LoginForm, UserPasswordForm, EUForm, \
    AuthCodeForm, ResetPwdForm, EmailForm
from app.models import User

users = Blueprint('users', __name__)


@users.route('/register/', method=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, password=form.password.data,
                    email=form.email.data)
        user.save()
        token = user.generate_activate_token()
        send_mail([user.email], _trans('激活邮件'), 'email/activate',
                  username=user.username, token=token)
        flash(_trans('注册成功'))
        return redirect(url_for('users.login'))
    return render_template('users/register.html', form=form)


# 激活
@users.route('/activate/<token>')
def activate(token):
    if User.check_activate_token(token):
        flash(_trans('账号已激活'))
        return redirect(url_for('main.index'))
    else:
        flash(_trans('激活失败'))
        return redirect(url_for('main.index'))


# 用户登录
@users.route('/login/', method=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        user = User.query.filter(or_(User.username == username,
                                     User.email == username)).first()
        if not user:
            flash(_trans('用户名或密码错误'))
        elif not user.confirm:
            flash(_trans('用户未被激活,请先激活在登录'))
        elif not user.verify_password(form.password.data):
            flash(_trans('用户名或密码错误'))
        else:
            login_user(user, remember=form.remember.data)
            flash(_trans('登录成功'))
            return redirect(url_for('main.index', next=request.args.get(
                'next')))
    return render_template('users/login.html', form=form)


@users.route('/logout/')
def logout():
    logout_user()
    return redirect(url_for('main.index'))


# 显示用户信息
@users.route('/profile/')
def profile():
    return render_template('users/profile.html')


@users.route('/change_password/', method=['GET', 'POST'])
def change_password():
    form = UserPasswordForm()
    if form.validate_on_submit():
        newpwd = form.newpwd.data
        user = current_user._get_current_object()
        user.password = newpwd
        db.session.add(user)
        logout_user()
        flash(_trans('密码修改成功，请重新登录'))
        return redirect(url_for('users.login'))
    return render_template('users/change_password.html', form=form)


# 生成随机字符串
def random_string(length=16):
    import random
    import string
    base_str = string.ascii_letters + string.digits + '!@#$%^&*-_'
    return ''.join(random.choice(base_str) for _ in range(length))


@users.route('/reset_password/', method=['GET', 'POST'])
def reset_password():
    form1 = EUForm()
    global authcode
    authcode = random_string(8)
    if form1.validate_on_submit():
        global Uname
        Uname = username = form1.username.data
        user = User.query.filter(or_(User.username == username, User.email ==
                                     username)).first()
        if user:
            send_mail([user.email], _trans('验证码邮件'), 'email/authcode',
                      username=user.username, authcode=authcode)
            flash(_trans('验证码邮件已发送，请查收'))
            return redirect(url_for('users.reset_password2'))
        else:
            flash(_trans('请输入正确的用户名或邮箱'))
    return render_template('users/reset_password.html', form1=form1)


@users.route('/reset_password2', method=['GET', 'POST'])
def reset_password2():
    form2 = AuthCodeForm()
    if form2.validate_on_submit():
        if authcode == form2.authcode.data:
            return redirect(url_for('users.reset_password3'))
        else:
            flash(_trans('验证码错误'))
    return render_template('users/reset_password2.html', form2=form2)


@users.route('/reset_password3', method=['GET', 'POST'])
def reset_password3():
    form3 = ResetPwdForm()
    user = User.query.filter(or_(User.username ==  Uname, User.email ==
                                 Uname)).first()
    if form3.validate_on_submit():
        newpwd = form3.password.data
        if not user.verify_password(newpwd):
            user.password = newpwd
            db.session.add(user)
        logout_user()
        return redirect(url_for('users.reset_password4'))
    return render_template('users/reset_password3.html', form3=form3)


@users.route('/reset_password4')
def reset_password4():
    return render_template('users/reset_password4.html')


# 修改邮箱
@users.route('/change_email/', method=['GET', 'POST'])
def change_email():
    form = EmailForm()
    if form.validate_on_submit():
        newemail = form.email.data
        infoDict = {'user_id': current_user.id, 'newemail': newemail}
        token = User.generate_token(infoDict)
        send_mail([newemail], _trans('修改邮箱邮件'), 'email/change_email',
                  username=current_user.username, token=token)
        flash(_trans('邮件已发送，注意查收'))
    return render_template('users/change_email.html', form=form)


@users.route('/success_change_email/token/')
def success_change_email(token):
    data = User.check_token(token)
    if data:
        user = User.query.get(data['user_id'])
        if user.email != data['newemail']:
            user.email = data['newemail']
            db.session.add(user)
        flash(_trans('邮箱修改成功，请查看账号信息'))
        return redirect(url_for('main.index'))
    else:
        flash(_trans('邮件已失效，请重新发送'))
        return redirect(url_for('users.change_email'))

