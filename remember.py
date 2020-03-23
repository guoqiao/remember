#!/usr/bin/env python3
import argparse
from os import getenv
from os import makedirs
from os.path import join
from datetime import datetime, timedelta

import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.engine.url import URL

APP_NAME = 'remember'
HOME = getenv('HOME')
CONFIG_HOME = '{}/.config/{}'.format(HOME, APP_NAME)
makedirs(CONFIG_HOME, exist_ok=True)

DB_PATH = join(CONFIG_HOME, '{}.db'.format(APP_NAME))
DB_URL = URL(drivername='sqlite', database=DB_PATH)
print(DB_URL)


ENVVAR_PRIFIX = APP_NAME.upper()
def _getenv(name, default=None):
    return getenv('{}_{}'.format(ENVVAR_PRIFIX, name), default=default)


print(sqlalchemy.__version__)

from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
engine = create_engine(DB_URL, echo=True)

from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship, sessionmaker


class Word(Base):

    __tablename__ = 'word'

    id = Column(Integer, primary_key=True)
    keyword = Column(String)
    content = Column(String)
    created_at = Column(DateTime)

    def __str__(self):
        return self.keyword


class Memo(Base):

    __tablename__ = 'memo'

    id = Column(Integer, primary_key=True)
    word_id = Column(Integer, ForeignKey('word.id'))
    scheduled_at = Column(DateTime)

    def __str__(self):
        return self.word

#  engine.connect()
Base.metadata.create_all(bind=engine)


parser = argparse.ArgumentParser(
    formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    description="Remember Words",
)

parser.add_argument(
    "-a", "--add", action="store_true",
    help="Add new word")

parser.add_argument(
    "--keyword",
    help="word keyword")

parser.add_argument(
    "--content",
    help="word content")

parser.add_argument(
    "-p", "--pop", action="store_true",
    help="Pop a word from memo list")

args = parser.parse_args()

Session = sessionmaker()
Session.configure(bind=engine)
session = Session()


now = datetime.now()

if args.add:
    row = Word(keyword=args.keyword, content=args.content, created_at=now)
    session.add(row)
    session.commit()

    word_id = row.id
    for interval in [1, 3, 7, 30]:
        when = now + timedelta(days=interval)
        row = Memo(word_id=word_id, scheduled_at=when)
        session.add(row)
    session.commit()

if args.pop:
    memo = session.query(Memo).order_by(Memo.scheduled_at).first()
    if memo:
        print(memo.id, memo.scheduled_at)
        word_id = memo.word_id
        word = session.query(Word).filter(Word.id==word_id).first()
        print(word.keyword, word.content)
        session.query(Memo).filter(Memo.id==memo.id).delete()
        session.commit()

session.close()
