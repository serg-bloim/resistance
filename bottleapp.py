# A very simple Bottle Hello World app for you to get started with...
import random

from bottle import default_app, route, static_file, put, get, delete, HTTPResponse, post

from users import *
from validations import *

cache = 0
games = {'game1': {'id': 'game1',
                   'admin': 1,
                   'settings': {
                       'maxPlayers': 6,
                       'impostors': 2,
                       'rounds': [2, 3, 4, 3, 2],
                   },
                   'stage': 'pending',
                   'players': [{'id': 1, 'name': 'Orange'}, {'id': 2, 'name': 'Red'},
                               {'id': 3, 'name': 'Green'}, {'id': 4, 'name': 'Purple'}],
                   # 'players': [1, 2, 3, 4],
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
    next_game_name = next('game' + str(x) for x in range(1, 1000) if 'game' + str(x) not in games)
    game = {'id': next_game_name,
            'admin': me['id'],
            'stage': 'pending',
            'turn': 0,
            'vote': {},
            'vote_log': [],
            'settings': {
                'maxPlayers': 6,
                'impostors': 2,
                'rounds': [2, 3, 4, 3, 2],
            },
            'players': [me],
            'roles': {},
            }
    games[next_game_name] = game
    me['game'] = next_game_name
    return populate_users(game)


@put('/api/games/<gid>/settings')
def api_update_game(gid):
    me = get_current_user()
    if gid in games and games[gid]['admin'] != me['id']:
        HTTPResponse("Only game admin can change settings", 403)
    settings = request.json
    if not validate_game_settings_update(settings):
        return HTTPResponse("Incorrect data", 400)
    games[gid]['settings'] = settings
    return games[gid]['settings']


@get('/api/games/active')
def api_get_active_game():
    me = get_current_user()
    if me['game'] not in games:
        return HTTPResponse("Something went wrong", 400)
    return populate_users(games[me['game']])


@delete('/api/games/active')
def api_leave_active_game():
    me = get_current_user()
    if me['game'] not in games:
        return HTTPResponse("Something went wrong", 400)
    gid = me['game']
    active_game = games[gid]
    active_game['players'] = [p for p in active_game['players'] if p['id'] != me['id']]
    me['game'] = ''
    if len(active_game['players']) == 0:
        del games[gid]


@get('/api/games/<gid>')
def api_get_game_by_id(gid):
    return populate_users(games[gid])


@route('/api/games/<gid>/join', method='PUT')
def api_join_game(gid):
    game = games[gid]
    me = get_current_user()
    if me['game'] in games:
        return HTTPResponse("User " + me['name'] + " already in the game " + game['id'], 400)
    game['players'].append(me)
    me['game'] = gid
    return 'added'


@put('/api/games/<gid>/vote')
def api_vote(gid):
    game = games[gid]
    me = get_current_user()
    if not me['game'] == gid:
        return HTTPResponse("User " + me['name'] + " is not in the game " + game['id'], 400)
    game['vote'][me['id']] = request.json['vote']
    return 'accepted'


@delete('/api/games/<gid>/vote')
def api_delete_vote(gid):
    game = games[gid]
    me = get_current_user()
    if not me['game'] == gid:
        return HTTPResponse("User " + me['name'] + " is not in the game " + game['id'], 400)
    if me['id'] in game['vote']:
        del game['vote'][me['id']]
    return 'deleted'


@post('/api/games/<gid>/vote/reveal')
def api_reveal_vote(gid):
    game = games[gid]
    me = get_current_user()
    if not me['game'] == gid:
        return HTTPResponse("User " + me['name'] + " is not in the game " + game['id'], 400)
    if len(game['vote']) == 0:
        return HTTPResponse("There is no voting in game " + game['id'], 400)
    game['vote_log'].append(game['vote'])
    game['vote'] = {}
    return 'deleted'


def is_admin(game, me):
    return game['admin'] == me['id']


@post('/api/games/<gid>/start')
def api_start_game(gid):
    game = games[gid]
    me = get_current_user()
    if not is_admin(game, me):
        return HTTPResponse("Only admin can start the game", 403)
    if not game['stage'] == 'pending':
        return HTTPResponse(
            "Cannot start game " + gid + ". Cannot start a game in stage '" + game['stage'] + "'. Only 'pending'", 400)
    if not len(game['players']) == game['settings']['maxPlayers']:
        return HTTPResponse("Cannot start game " + gid + ". Players should match maxPlayers setting", 400)
    game['stage'] = 'started'
    players = game['players']
    impostors = [p['id'] for p in random.sample(players, game['settings']['impostors'])]

    def computeRoles(pid):
        return ['impostor' if pid in impostors else 'civ']

    game['roles'] = {p['id']: computeRoles(p['id']) for p in game['players']}
    return 'started'


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
    users[uid]['name'] = upd['name']
    return users[uid]


@route('/api/register')
def regi():
    return register_new_user()


def populate_users(game):
    return game
    # return {**game, 'players': [users[pid] for pid in game['players']]}


application = default_app()
