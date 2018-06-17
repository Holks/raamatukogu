import os
import logging
import logging.handlers

basedir = os.path.abspath(os.path.dirname(__file__))
logger = logging.getLogger('library')

FORMAT = '%(asctime)-12s [%(levelname)s] %(message)s'
formatter = logging.Formatter(FORMAT) 

Rthandler = logging.handlers.RotatingFileHandler('library.log', maxBytes=100*1024*1024,backupCount=10)
Rthandler.setLevel('INFO')
Rthandler.setFormatter(formatter)

streamer = logging.StreamHandler()
streamer.setFormatter(formatter)
streamer.setLevel('ERROR')

logging.getLogger('library').addHandler(streamer)
logging.getLogger('library').addHandler(Rthandler)


class Config:
    BOOKS_PER_PAGE = 25
    if os.environ.get('TEMPLATES_AUTO_RELOAD') is None:
        TEMPLATES_AUTO_RELOAD = True # == no need to restart server
    else:
        TEMPLATES_AUTO_RELOAD = os.environ['TEMPLATES_AUTO_RELOAD']
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')
    SECRET_KEY = os.environ.get('SECRET_KEY') or  b"""g7\n'lra=\xe1\xf1O\xf3\xea\xb8t\xb7\n\xc5\xd8\xcf\xed\x1e\x94\x02\xd7Jp\xcc\x1dZm\xc9(\xbe\xc5Y\xbf\xbas\xe9[b\xb3\xb2\xbalU\xa3kz&P\xb5i\xd7(\xa6)Z\xad3\x9e(\xe9"""
    if os.environ.get('DATABASE_URL') is None:
        #SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
        SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://kitsemampsel:e6FkVoF4d3PGiEG7@localhost/raamatukogu'
    else:
        SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']