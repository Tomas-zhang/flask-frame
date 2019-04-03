from threading import Thread
from .extensions import mail
from flask import current_app, render_template
from flask_mail import Message


def async_send_mail(app, msg):
    with app.app_context():
        mail.send(msg)


def send_mail(to, subject, template, **kwargs):
    app = current_app._get_current_object()
    msg = Message(subject=subject, recipients=to, sender=app.config[
        'MAIL_USERNAME'])
    msg.html = render_template(template + '.html', **kwargs)
    msg.body = render_template(template + '.txt', **kwargs)

    thr = Thread(target=async_send_mail, args=[app, msg])
    thr.start()
