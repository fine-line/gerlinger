import os
from dotenv import load_dotenv

basedir = os.path.dirname(__file__)
load_dotenv(os.path.join(basedir, ".env"))


class Config():
    SECRET_KEY = os.environ.get("SECRET_KEY")
    # Конфигурации почты для отправки ошибок сервера
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = os.environ.get('MAIL_PORT')
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    ADMINS = os.environ.get('ADMINS')