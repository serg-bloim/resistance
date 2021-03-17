import random
import string

from bottle import request, response

GUEST_USER = '0'
users={
    GUEST_USER:{'id':'0', 'name':'<noname>', 'game': ''},
    '1':{'id':'1', 'name': 'Orange', 'game': ''},
    '2':{'id':'1', 'name': 'Blue', 'game': ''},
    '3':{'id':'1', 'name': 'Simple', 'game': ''},
    '4':{'id':'1', 'name': 'TryHard', 'game': ''},
    }

def get_user_id():
    uid = request.cookies.userid or GUEST_USER
    if uid not in users:
        uid = GUEST_USER
    return uid

def get_current_user():
    return users[get_user_id()]

def is_user_logged_in():
    return get_user_id() != GUEST_USER

def register_new_user(name='New Player', resp=response):
    uid = str(max((int(uid) for uid in users.keys()))+1)
    avatar_sid = ''.join(random.choice(string.ascii_lowercase) for x in range(6))
    user = {'id': uid, 'name': name, 'game': '', 'avatar': 'https://robohash.org/'+avatar_sid}
    print('registering new user: ' + str(user))
    print('users before ' + str(users))
    users[uid] = user
    resp.set_cookie('userid', uid)
    return user

