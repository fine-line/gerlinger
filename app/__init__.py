import os
import logging
from logging.handlers import SMTPHandler, RotatingFileHandler

from flask import Flask
from config import Config


def create_app(config_class=Config):
    # Создание экземпляра приложения
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Регистрация blueprint-ов
    from app.core import bp as core_bp
    app.register_blueprint(core_bp)

    from app.errors import bp as errors_bp
    app.register_blueprint(errors_bp, url_prefix="/error")

    from app.calc.temperature_difference import bp as temperature_difference_bp
    app.register_blueprint(temperature_difference_bp, 
                           url_prefix="/calc/temperature-difference")
    
    if not (app.debug or app.testing):
        # Отправка ошибок на почту
        if app.config["MAIL_SERVER"]:
            mail_handler = SMTPHandler(
                mailhost=(app.config["MAIL_SERVER"], app.config["MAIL_PORT"]),
                fromaddr=app.config["MAIL_USERNAME"],
                toaddrs=app.config["ADMINS"], 
                subject="Gerlinger Failure",
                credentials=(app.config["MAIL_USERNAME"], app.config["MAIL_PASSWORD"]))
            mail_handler.setLevel(logging.ERROR)
            app.logger.addHandler(mail_handler)
            
        # Сохранение логов в файл
        if not os.path.exists("logs"):
            os.mkdir("logs")
        file_handler = RotatingFileHandler("logs/gerlinger.log", 
                                           maxBytes=10240, 
                                           backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            "%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]"))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        # Запись в лог старта сервера
        app.logger.setLevel(logging.INFO)
        app.logger.info("App startup")
    return app
