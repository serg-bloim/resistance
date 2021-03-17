new Vue({
    el: "#app",
    data: {
        original: {
            player: {
                name: "undefined"
            },
        },
        temp: {},
        panel: 'gamelist',
        player: {
            name: "undefined"
        },
        active_game: {},
        gamelist: [{
                id: 'game1',
                players: []
            },
            {
                id: 'game2',
                players: [1, 2, 3]
            },
        ],
        console: console,
        p1: true,
        p2: false,
        todos: [{
                text: "Learn JavaScript",
                done: false
            },
            {
                text: "Learn Vue",
                done: false
            },
            {
                text: "Play around in JSFiddle",
                done: true
            },
            {
                text: "Build something awesome",
                done: true
            }
        ]
    },
    methods: {
        player_submit: function() {
            console.log("Name is: " + this.player.name)
            this.$http.put('/api/users/' + this.player.id, this.player).then(response => {
                this.update_user_internal(response.body)
            })
        },
        update_user_internal: function(upd) {
            this.player = upd
            this.original.player = Object.assign({}, this.player)
        },
        update_user: function() {
            this.$http.get('/api/whoami').then(response => {
                this.update_user_internal(response.body)
            })
        },
        refresh_gamelist: function() {
            this.$http.get('/api/games').then(resp => {
                this.gamelist = resp.body.games
            })
        },
        update_active_game: function() {
            this.$http.get('/api/games/active').then(resp => {
                this.active_game = resp.body
            }, resp => {
                this.active_game = {}
            })
        },
        has_active_game: function() {
            return 'id' in this.active_game
        },
        leave_active_game: function() {
            this.$http.delete('/api/games/active').then(resp => {
                this.update_active_game()
                this.update_user()
                this.refresh_gamelist()
                this.panel = 'gamelist'
            })
        },
        joinGame: function(game) {
            this.$http.put(`/api/games/${game.id}/join`).then(resp => {
                this.update_active_game()
                this.refresh_gamelist()
                this.update_user()
                this.panel = 'game'
            })
        },
        create_game: function() {
            this.$http.post(`/api/games`).then(resp => {
                this.update_active_game()
                this.refresh_gamelist()
                this.update_user()
                this.panel = 'game'
            })
        },
        start_active_game() {
            this.$http.post(`/api/games/${this.active_game.id}/start`).then(resp => {
                this.update_active_game()
            })
        },
        update_game_settings() {
            this.active_game.settings.maxPlayers = parseInt(this.active_game.settings.maxPlayers)
            data = {
                maxPlayers: parseInt(this.temp.active_game_settings.maxPlayers),
                rounds: this.temp.active_game_settings.rounds.trim().split(' ').map(v => {
                    return parseInt(v.trim())
                })
            }
            this.$http.put(`/api/games/${this.active_game.id}/settings`, data).then(
                resp => {
                    delete this.temp.active_game_settings
                    this.update_active_game()
                },
                resp => {
                    delete this.temp.active_game_settings
                    this.update_active_game()
                }
            )
        },
    },
    created: function() {
        console.log("created hook")
        this.update_user();
        this.refresh_gamelist();
        this.update_active_game();
    },
    computed: {
        game_settings_maxPlayers: {
            get() {
                return this.temp.active_game_settings ? this.temp.active_game_settings.maxPlayers : this.active_game.settings.maxPlayers
            },
            set(v) {
                if (!this.temp.active_game_settings) {
                    this.temp.active_game_settings = {
                        maxPlayers: this.active_game.settings.maxPlayers,
                        rounds: this.active_game.settings.rounds.join(' ')
                    }
                }
                this.temp.active_game_settings.maxPlayers = v
            }
        },
        game_settings_rounds: {
            get() {
                return this.temp.active_game_settings ? this.temp.active_game_settings.rounds : this.active_game.settings.rounds.join(' ')
            },
            set(v) {
                if (!this.temp.active_game_settings) {
                    this.temp.active_game_settings = {
                        maxPlayers: this.active_game.settings.maxPlayers,
                        rounds: this.active_game.settings.rounds.join(' ')
                    }
                }
                this.temp.active_game_settings.rounds = v
            }
        },
        active_game_can_start_game: function() {
            return this.show_game_settings && this.active_game.admin == this.player.id && this.active_game.settings.maxPlayers == this.active_game.players.length
        },
        show_game_settings(){
        return  this.active_game.stage == 'pending'
        },
    }
})