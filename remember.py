#!/usr/bin/env python3
import argparse
import sys
from os import getenv
from os import makedirs
from os.path import join
from datetime import datetime, timedelta

from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.engine.url import URL
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

APP_NAME = 'remember'
HOME = getenv('HOME')
CONFIG_HOME = '{}/.config/{}'.format(HOME, APP_NAME)
DB_PATH = join(CONFIG_HOME, '{}.db'.format(APP_NAME))
DB_URL = URL(drivername='sqlite', database=DB_PATH)

makedirs(CONFIG_HOME, exist_ok=True)

parser = argparse.ArgumentParser(
    formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    description="Remember Words")

parser.add_argument("-a", "--add", action="store_true", help="Add new word")
parser.add_argument("--keyword", help="word keyword")
parser.add_argument("--content", help="word content")
parser.add_argument("-p", "--pop", action="store_true", help="Pop a word")
parser.add_argument("-v", "--verbose", action="store_true", help="Be verbose")

args = parser.parse_args()

VERBOSE = args.verbose

if VERBOSE:
    def verbose(*args, **kwargs):
        print(*args, file=sys.stderr, **kwargs)
else:
    def verbose(*args, **kwargs):
        pass


Base = declarative_base()
engine = create_engine(DB_URL, echo=VERBOSE)
verbose(DB_URL)

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
        verbose(memo.id, memo.scheduled_at)
        word_id = memo.word_id
        word = session.query(Word).filter(Word.id==word_id).first()
        verbose(word.keyword, word.content)
        session.query(Memo).filter(Memo.id==memo.id).delete()
        session.commit()

session.close()
