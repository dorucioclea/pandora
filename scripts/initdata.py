#!/usr/bin/env python

import utils
import api
from faker import Faker

utils.enable_logging()
fake = Faker()

def user_exists(user):
    try:
        api.login(user['login'], user['password'])
    except:
        return False
    return True

def ensure_user(user):
    if not user_exists(user):
        api.post('/api/data/user', user)

users = [
    {
        'login': 'admin',
        'name': 'admin',
        'email': 'stodyshev@gmail.com',
        'password': 'admin123',
        'role': 'admin',
    },
    {
        'login': 'sergeyt',
        'name': 'sergeyt',
        'email': 'stodyshev@gmail.com',
        'password': 'sergeyt123',
    },
]

channels = [
]

def init():
    for user in users:
        ensure_user(user)
    for channel in channels:
        api.post('/api/data/channel', channel)

def generate():
    for i in range(100):
        name = fake.name()
        user = {
            'login': name,
            'name': name,
            'email': name + '123@gmail.com',
            'password': name + '123',
        }
        ensure_user(user)

init()
# generate()
