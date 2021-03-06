import os

from flask_babel import Babel
from flask_script import Manager
from flask_migrate import MigrateCommand

from app import create_app

config_name = os.environ.get('FLASK_CONFIG') or 'default'

app = create_app(config_name)

manager = Manager(app)
babel = Babel(app)

manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
    manager.run()
