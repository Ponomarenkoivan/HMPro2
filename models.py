import datetime

from sqlalchemy import Column, Integer, String, REAL, ForeignKey, DateTime
from sqlalchemy.orm import mapped_column

from database import Base

class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    login = Column(String(50), unique=True)
    password = Column(String(50))
    ipn = Column(Integer, unique=True)
    full_name = Column(String(50))
    contacts = Column(String(100))
    pfoto = Column(String(100))
    email = Column(String(120), nullable=True)

    def __init__(self, login, password, ipn, full_name, contacts, pfoto):
        self.login = login
        self.password = password
        self.ipn = ipn
        self.full_name = full_name
        self.contacts = contacts
        self.pfoto = pfoto

    def __repr__(self):
        return f'<User {self.login}>,{self.ipn}'

class Item(Base):
    __tablename__ = 'item'
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    photo = Column(String(100))
    name = Column(String(50), unique=True)
    description = Column(String(100))
    price_hour = Column(REAL)
    price_day = Column(REAL)
    price_week = Column(REAL)
    price_month = Column(REAL)
    owner = Column(ForeignKey('user.id'))


    def __init__(self, photo, name, description, price_hour, price_day, price_month, owner):
        self.photo = photo
        self.name = name
        self.description = description
        self.price_hour = price_hour
        self.price_day = price_day
        self.price_month = price_month
        self.owner = owner


    def __repr__(self):
        return f'<Item{self.name}>, {self.id}, {self.owner}'


class Contract(Base):
    __tablename__ = 'contract'
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    text = Column(String(500))
    start_date = Column(String(50))
    end_date = Column(String(50))
    leaser = Column(Integer, unique=True)
    taker = Column(Integer, unique=True)
    item = Column(Integer, unique=True)
    status = Column(Integer, unique=True)
    signed_datetime = Column(DateTime, default=datetime.datetime.now)

    def __init__(self, text, start_date, end_date, leaser, taker, item, status):
        self.text = text
        self.start_date = start_date
        self.end_date = end_date
        self.leaser = leaser
        self.taker = taker
        self.item = item
        self.status = status

class Favorite(Base):
    __tablename__ = 'favorites'
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    user = Column(Integer, ForeignKey('user.id'))
    item = Column(Integer, ForeignKey('item.id'))
    timestamp = Column(DateTime, default=datetime.datetime.now, nullable=True)

    def __init__(self, user, item):
        self.user = user
        self.item = item

class Feedback(Base):
    __tablename__ = 'feedback'
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    author = Column(Integer, ForeignKey('user.id'))
    user = Column(Integer, ForeignKey('user.id'))
    text = Column(String(500))
    grade = Column(Integer)
    contract = Column(Integer, ForeignKey('contract.id'))
    timestamp = Column(DateTime, default=datetime.datetime.now)

    def __init__(self, author, user, text, grade, contract):
        self.author = author
        self.user = user
        self.text = text
        self.grade = grade
        self.contract = contract


class Search_history(Base):
    __tablename__ = 'search_history'
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    user = Column(Integer, ForeignKey('user.id'))
    search_text = Column(String(500))
    timestamp = Column(DateTime())

    def __init__(self, user, search_text, timestamp):
        self.user = user
        self.search_text = search_text
        self.timestamp = timestamp





