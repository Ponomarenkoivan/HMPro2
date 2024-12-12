import os

from celery import Celery
from sqlalchemy import select

import models
from database import db_session, init_db

from models import Item, Contract


app = Celery('tasks', broker=f'pyamqp://guest@{os.environ.get("RABBITMQ_HOST", "localhost")}//')

@app.task
def add(x, y):
    print(x + y)

@app.task
def send_email(contract_id):

    import smtplib

    from email.message import EmailMessage

    init_db()
    contracts = db_session.scalars(select(models.Contract).filter_by(id=contract_id)).scalar()
    item = db_session.scalar(select(models.Item).filter_by(id=contracts.item)).scalar()

    import smtplib
    # creates SMTP session
    s = smtplib.SMTP('smtp.gmail.com', 587)
    # start TLS for security
    s.starttls()
    # Authentication
    s.login("sender_email_id", "sender_email_id_password")
    # message to be sent
    message = "Message_you_need_to_send"
    # sending the mail
    s.sendmail("appmail@exmple.com", "user1@exmple.com", message)
    s.sendmail("appmail2@exmple.com", "user2@exmple.com", message)
    # terminating the session
    s.quit()