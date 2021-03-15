new Vue({
    el: "#app",
    data: {
        original: {
            player: {
                name: "undefined"
            },
        },
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
        toggle: function(todo) {
            todo.done = !todo.done
        },
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
            }, resp=>{
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
        }
    },
    created: function() {
        console.log("created hook")
        this.update_user();
        this.refresh_gamelist();
        this.update_active_game();
    }
})