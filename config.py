import os

class Config:
    SECRET_KEY = os.urandom(24)
    DATABASE = 'bank.db'
    DEBUG = True