#!/usr/bin/env python3
import argparse
import sys
from os import getenv, makedirs, linesep
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
makedirs(CONFIG_HOME, exist_ok=True)
DB_PATH = join(CONFIG_HOME, '{}.db'.format(APP_NAME))


def cli():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description="Remember Words")

    parser.add_argument(
        '-i', '--input',
        type=argparse.FileType('r'),
        default=None,
        help='add word from file, use - for stdin')
    parser.add_argument("-p", "--pop", action="store_true", help="pop up a memo")
    parser.add_argument("-v", "--verbose", action="store_true", help="be verbose")

    return parser.parse_args()


def echo(*args, **kwargs):
    print('[{}]'.format(APP_NAME), end='')
    print(*args, **kwargs)


args = cli()
if args.verbose:
    def verbose(*args, **kwargs):
        print(*args, file=sys.stderr, **kwargs)
else:
    def verbose(*args, **kwargs):
        pass


Base = declarative_base()


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
    interval = Column(Integer)
    scheduled_at = Column(DateTime)

    def __str__(self):
        return self.word


DB_URL = URL(drivername='sqlite', database=DB_PATH)
verbose(DB_URL)
engine = create_engine(DB_URL, echo=args.verbose)

Base.metadata.create_all(bind=engine)

Session = sessionmaker()
Session.configure(bind=engine)
session = Session()


def add_word(inputfile):
    text = inputfile.read()
    keyword, content = text.split(linesep, maxsplit=1)
    verbose('add word: {}'.format(keyword))
    verbose('with content: {}'.format(content))
    now = datetime.now()
    word = Word(keyword=keyword, content=content, created_at=now)
    session.add(word)
    session.commit()
    word_id = word.id
    for interval in [1, 3, 7, 30, 60]:
        when = now + timedelta(days=interval)
        memo = Memo(word_id=word_id, interval=interval, scheduled_at=when)
        session.add(memo)
    session.commit()
    echo('word added: {}'.format(keyword))
    return word


def pop_word():
    now = datetime.now()
    memos = session.query(Memo).filter(Memo.scheduled_at<=now)
    for memo in memos:
        verbose(memo.id, memo.scheduled_at)
        word_id = memo.word_id
        word = session.query(Word).filter(Word.id==word_id).first()
        echo('memo on day {}'.format(memo.interval))
        print(word.keyword)
        print(word.content)
        session.query(Memo).filter(Memo.id==memo.id).delete()
        session.commit()


if args.input:
    add_word(args.input)
elif args.pop:
    pop_word()

session.close()
