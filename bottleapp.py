# A very simple Bottle Hello World app for you to get started with...
from bottle import default_app, route, static_file, put, get, delete, HTTPResponse, post

from users import *
from validations import *

cache = 0
games = {'game1': {'id': 'game1',
                   'admin': 1,
                   'players': [{'id': 1, 'name': 'Orange'}, {'id': 3, 'name': 'Red'},
                               {'id': 4, 'name': 'Green'}, {'id': 5, 'name': 'Purple'}, {'id': 6, 'name': 'Yellow'}],
                   'voting': {
                       'id': 1,
                       'proposal': ['Orange', 'Green'],
                       'votes': {
                           '1': 'yes',
                           '2': 'no',
                           '3': 'undefined'
                       }
                   }
                   }}


@route('/')
def hello_world():
    print('serving index.html')
    file = 'index.html'
    root = './static'
    resp = static_file(file, root)
    if not is_user_logged_in():
        register_new_user(resp=resp)
    return resp


@route('/static/<filepath:path>')
def server_static(filepath):
    return static_file(filepath, root='./static')


@get('/api/games')
def api_get_games():
    resp_keys = ["id", "players"]
    games_resp = [{key: g[key] for key in resp_keys} for g in games.values()]
    return {'games': games_resp}


@post('/api/games')
def api_create_game():
    me = get_current_user()
    if me['game'] in games:
        return HTTPResponse("User already in a game " + me['game'], 400)
    next_game_name = next('game'+str(x) for x in range(1, 1000) if 'game'+str(x) not in games)
    game = {'id': next_game_name, 'admin': me['id'], 'players': [me]}
    games[next_game_name] = game
    me['game'] = next_game_name
    return game

@put('/api/games/<gid>')
def api_update_game(gid):
    me = get_current_user()
    if gid in games and games[gid]['admin'] != me['id']:
        HTTPResponse("Only game admin can change settings", 403)
    if gid not in games:
        # init a game
        games[gid] = {'id': gid, 'admin': me['id'], 'players': []}
        api_join_game(gid)
    validate_game_update(request.body)
    return {'games': list(games.keys())}


@get('/api/games/active')
def api_get_active_game():
    me = get_current_user()
    if me['game'] not in games:
        return HTTPResponse( "Something went wrong", 400)
    return games[me['game']]

@delete('/api/games/active')
def api_leave_active_game():
    me = get_current_user()
    if me['game'] not in games:
        return HTTPResponse("Something went wrong", 400)
    gid=me['game']
    active_game = games[gid]
    active_game['players'] = [p for p in active_game['players'] if p['id'] != me['id']]
    me['game']=''
    if len(active_game['players']) == 0:
        del games[gid]


@get('/api/games/<gid>')
def api_get_game_by_id(gid):
    return games[gid]

@route('/api/games/<gid>/join', method='PUT')
def api_join_game(gid):
    game = games[gid]
    me = get_current_user()
    if me['game'] in games:
        return HTTPResponse("User " + me['name'] + " already in the game " + game['id'], 400)
    game['players'].append(me)
    me['game'] = gid
    return 'added'

@route('/api/whoami')
def whoami():
    return get_current_user()


@put('/api/users/<uid>')
def update_user(uid):
    me = get_current_user()
    if uid != me['id']:
        HTTPResponse("You cannot change another user", 403)
    upd = request.json
    validate_user_update(upd)
    users[uid] = {**me, **upd}
    return users[uid]


@route('/api/register')
def regi():
    return register_new_user()


application = default_app()
