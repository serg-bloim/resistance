def validate_game_settings_update(game_settings_update):
    for k in game_settings_update.keys():
        if k not in ['maxPlayers', 'rounds', 'impostors']:
            return False
    if type(game_settings_update['maxPlayers']) is not int:
        return False
    if type(game_settings_update['impostors']) is not int:
        return False
    for r in game_settings_update['rounds']:
        if type(r) is not int:
            return False
    return True



def validate_user_update(user_upd):
    return True
