import sys
import os
import os.path
import uuid
import json
from glob import glob
from datetime import datetime
from board import Board

class OthelloHttpServer:
    def __init__(self):
        self.sessions = {}
        self.games = {}  # game_id -> game data
        self.waiting_players = []
        self.types = {}
        self.types['.pdf'] = 'application/pdf'
        self.types['.jpg'] = 'image/jpeg'
        self.types['.png'] = 'image/png'
        self.types['.txt'] = 'text/plain'
        self.types['.html'] = 'text/html'
        self.types['.css'] = 'text/css'
        self.types['.js'] = 'application/javascript'
        self.types['.json'] = 'application/json'

    def response(self, kode=404, message='Not Found', messagebody=bytes(), headers={}):
        tanggal = datetime.now().strftime('%c')
        resp = []
        resp.append("HTTP/1.0 {} {}\r\n".format(kode, message))
        resp.append("Date: {}\r\n".format(tanggal))
        resp.append("Connection: close\r\n")
        resp.append("Server: othelloserver/1.0\r\n")
        resp.append("Content-Length: {}\r\n".format(len(messagebody)))
        for kk in headers:
            resp.append("{}:{}\r\n".format(kk, headers[kk]))
        resp.append("\r\n")

        response_headers = ''
        for i in resp:
            response_headers = "{}{}".format(response_headers, i)
        
        # Mengubah message body ke bytes jika belum
        if type(messagebody) is not bytes:
            messagebody = messagebody.encode()

        response = response_headers.encode() + messagebody
        return response

    def proses(self, data):
        requests = data.split("\r\n")
        baris = requests[0]
        all_headers = [n for n in requests[1:] if n != '']

        # Parse POST body if exists
        post_body = ""
        if "\r\n\r\n" in data:
            parts = data.split("\r\n\r\n", 1)
            if len(parts) > 1:
                post_body = parts[1]

        j = baris.split(" ")
        try:
            method = j[0].upper().strip()
            if method == 'GET':
                object_address = j[1].strip()
                return self.http_get(object_address, all_headers)
            elif method == 'POST':
                object_address = j[1].strip()
                return self.http_post(object_address, all_headers, post_body)
            else:
                return self.response(400, 'Bad Request', '', {})
        except IndexError:
            return self.response(400, 'Bad Request', '', {})

    def http_get(self, object_address, headers):
        # API endpoints
        if object_address == '/':
            return self.get_main_page()
        elif object_address == '/api/status':
            return self.get_server_status()
        elif object_address.startswith('/api/register/'):
            # Extract player name from URL: /api/register/PlayerName
            player_name = object_address[14:]  # Remove '/api/register/'
            return self.register_player(player_name)
        elif object_address.startswith('/api/gamestate/'):
            # Extract session ID: /api/gamestate/session_id
            session_id = object_address[15:]
            return self.get_game_state(session_id)
        elif object_address == '/api/lobby':
            return self.get_lobby_info()
        else:
            # Serve static files
            return self.serve_static_file(object_address)

    def http_post(self, object_address, headers, post_body):
        if object_address == '/api/creategame':
            return self.create_game(post_body)
        elif object_address == '/api/joingame':
            return self.join_game(post_body)
        elif object_address == '/api/makemove':
            return self.make_move(post_body)
        elif object_address == '/api/leavegame':
            return self.leave_game(post_body)
        else:
            return self.response(404, 'Not Found', 'Endpoint not found', {})

    def get_main_page(self):
        """Return main game page"""
        html = """
<!DOCTYPE html>
<html>
<head>
    <title>Othello Multiplayer</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #2c3e50; color: white; }
        .container { max-width: 800px; margin: 0 auto; }
        h1 { text-align: center; color: #ecf0f1; }
        .section { background: #34495e; padding: 20px; margin: 20px 0; border-radius: 10px; }
        .button { background: #3498db; color: white; padding: 10px 20px; border: none; 
                 border-radius: 5px; cursor: pointer; margin: 5px; }
        .button:hover { background: #2980b9; }
        input { padding: 10px; margin: 10px 0; border: none; border-radius: 5px; width: 200px; }
        #gameBoard { display: grid; grid-template-columns: repeat(8, 50px); gap: 2px; 
                    background: #27ae60; padding: 10px; border-radius: 10px; margin: 20px auto; width: fit-content; }
        .cell { width: 50px; height: 50px; background: #2ecc71; border: 1px solid #27ae60; 
               display: flex; align-items: center; justify-content: center; cursor: pointer; }
        .cell:hover { background: #58d68d; }
        .piece { width: 40px; height: 40px; border-radius: 50%; }
        .black { background: #2c3e50; }
        .white { background: #ecf0f1; }
        .valid { background: #f39c12 !important; }
        .info { display: flex; justify-content: space-between; align-items: center; }
        .status { padding: 10px; background: #e74c3c; border-radius: 5px; margin: 10px 0; }
        .success { background: #27ae60; }
        .warning { background: #f39c12; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔴⚫ Othello Multiplayer ⚫🔴</h1>
        
        <div class="section" id="loginSection">
            <h3>Join Game</h3>
            <input type="text" id="playerName" placeholder="Enter your name" maxlength="20">
            <button class="button" onclick="registerPlayer()">Register</button>
        </div>
        
        <div class="section" id="lobbySection" style="display:none;">
            <h3>Game Lobby</h3>
            <div class="info">
                <div>Welcome, <span id="currentPlayer"></span>!</div>
                <button class="button" onclick="createGame()">Create New Game</button>
                <button class="button" onclick="refreshLobby()">Refresh</button>
            </div>
            <div id="availableGames"></div>
        </div>
        
        <div class="section" id="gameSection" style="display:none;">
            <div class="info">
                <div>
                    <strong>Game Status:</strong> <span id="gameStatus"></span><br>
                    <strong>Your Color:</strong> <span id="playerColor"></span><br>
                    <strong>Opponent:</strong> <span id="opponentName"></span>
                </div>
                <div>
                    <strong>Score:</strong><br>
                    Black: <span id="blackScore">2</span><br>
                    White: <span id="whiteScore">2</span>
                </div>
                <button class="button" onclick="leaveGame()" style="background: #e74c3c;">Leave Game</button>
            </div>
            <div id="gameBoard"></div>
        </div>
        
        <div id="message" class="status" style="display:none;"></div>
    </div>

    <script>
        let sessionId = null;
        let gameData = null;
        let currentGame = null;
        
        function showMessage(msg, type = 'error') {
            const messageDiv = document.getElementById('message');
            messageDiv.textContent = msg;
            messageDiv.className = 'status ' + type;
            messageDiv.style.display = 'block';
            setTimeout(() => messageDiv.style.display = 'none', 5000);
        }
        
        function registerPlayer() {
            const name = document.getElementById('playerName').value.trim();
            if (!name) {
                showMessage('Please enter your name');
                return;
            }
            
            fetch('/api/register/' + encodeURIComponent(name))
                .then(response => response.text())
                .then(data => {
                    try {
                        const result = JSON.parse(data);
                        if (result.success) {
                            sessionId = result.session_id;
                            document.getElementById('currentPlayer').textContent = name;
                            document.getElementById('loginSection').style.display = 'none';
                            document.getElementById('lobbySection').style.display = 'block';
                            showMessage('Welcome to Othello!', 'success');
                            refreshLobby();
                        } else {
                            showMessage(result.message || 'Registration failed');
                        }
                    } catch (e) {
                        showMessage('Server error');
                    }
                })
                .catch(err => showMessage('Connection error'));
        }
        
        function createGame() {
            if (!sessionId) return;
            
            fetch('/api/creategame', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({session_id: sessionId})
            })
                .then(response => response.text())
                .then(data => {
                    try {
                        const result = JSON.parse(data);
                        if (result.success) {
                            currentGame = result.game_id;
                            showMessage('Game created! Waiting for opponent...', 'success');
                            startGameUpdates();
                        } else {
                            showMessage(result.message || 'Failed to create game');
                        }
                    } catch (e) {
                        showMessage('Server error');
                    }
                })
                .catch(err => showMessage('Connection error'));
        }
        
        function joinGame(gameId) {
            if (!sessionId) return;
            
            fetch('/api/joingame', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({session_id: sessionId, game_id: gameId})
            })
                .then(response => response.text())
                .then(data => {
                    try {
                        const result = JSON.parse(data);
                        if (result.success) {
                            currentGame = gameId;
                            showMessage('Joined game successfully!', 'success');
                            startGameUpdates();
                        } else {
                            showMessage(result.message || 'Failed to join game');
                        }
                    } catch (e) {
                        showMessage('Server error');
                    }
                })
                .catch(err => showMessage('Connection error'));
        }
        
        function makeMove(row, col) {
            if (!sessionId || !currentGame) return;
            
            fetch('/api/makemove', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    session_id: sessionId,
                    game_id: currentGame,
                    row: row,
                    col: col
                })
            })
                .then(response => response.text())
                .then(data => {
                    try {
                        const result = JSON.parse(data);
                        if (result.success) {
                            showMessage('Move successful!', 'success');
                            updateGameState();
                        } else {
                            showMessage(result.message || 'Invalid move');
                        }
                    } catch (e) {
                        showMessage('Server error');
                    }
                })
                .catch(err => showMessage('Connection error'));
        }
        
        function leaveGame() {
            if (!sessionId || !currentGame) return;
            
            fetch('/api/leavegame', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({session_id: sessionId})
            })
                .then(() => {
                    currentGame = null;
                    gameData = null;
                    document.getElementById('gameSection').style.display = 'none';
                    document.getElementById('lobbySection').style.display = 'block';
                    refreshLobby();
                })
                .catch(err => showMessage('Connection error'));
        }
        
        function refreshLobby() {
            if (!sessionId) return;
            
            fetch('/api/lobby')
                .then(response => response.text())
                .then(data => {
                    try {
                        const result = JSON.parse(data);
                        if (result.success) {
                            updateLobbyDisplay(result.games);
                        }
                    } catch (e) {
                        showMessage('Server error');
                    }
                })
                .catch(err => showMessage('Connection error'));
        }
        
        function updateLobbyDisplay(games) {
            const container = document.getElementById('availableGames');
            if (games.length === 0) {
                container.innerHTML = '<p>No games available. Create one!</p>';
            } else {
                container.innerHTML = games.map(game => 
                    `<div style="background: #2c3e50; padding: 10px; margin: 5px 0; border-radius: 5px; display: flex; justify-content: space-between;">
                        <span>Game by ${game.creator} (${game.players}/2 players)</span>
                        <button class="button" onclick="joinGame('${game.id}')">Join</button>
                    </div>`
                ).join('');
            }
        }
        
        function startGameUpdates() {
            document.getElementById('lobbySection').style.display = 'none';
            document.getElementById('gameSection').style.display = 'block';
            updateGameState();
            
            // Update every 2 seconds
            setInterval(updateGameState, 2000);
        }
        
        function updateGameState() {
            if (!sessionId) return;
            
            fetch('/api/gamestate/' + sessionId)
                .then(response => response.text())
                .then(data => {
                    try {
                        const result = JSON.parse(data);
                        if (result.success) {
                            gameData = result.game_state;
                            updateGameDisplay();
                        }
                    } catch (e) {
                        console.error('Error parsing game state:', e);
                    }
                })
                .catch(err => console.error('Game state update failed:', err));
        }
        
        function updateGameDisplay() {
            if (!gameData) return;
            
            // Update game info
            document.getElementById('gameStatus').textContent = 
                gameData.game_over ? 'Game Over' : 
                (gameData.my_turn ? 'Your Turn' : 'Opponent Turn');
            
            document.getElementById('playerColor').textContent = 
                gameData.my_color === 1 ? 'Black' : 'White';
            
            document.getElementById('opponentName').textContent = 
                gameData.opponent_name || 'Waiting...';
            
            document.getElementById('blackScore').textContent = gameData.score[0];
            document.getElementById('whiteScore').textContent = gameData.score[1];
            
            // Update board
            updateBoard();
        }
        
        function updateBoard() {
            if (!gameData) return;
            
            const board = document.getElementById('gameBoard');
            board.innerHTML = '';
            
            for (let row = 0; row < 8; row++) {
                for (let col = 0; col < 8; col++) {
                    const cell = document.createElement('div');
                    cell.className = 'cell';
                    
                    const piece = gameData.board[row][col];
                    if (piece === 1) {
                        const pieceDiv = document.createElement('div');
                        pieceDiv.className = 'piece black';
                        cell.appendChild(pieceDiv);
                    } else if (piece === 2) {
                        const pieceDiv = document.createElement('div');
                        pieceDiv.className = 'piece white';
                        cell.appendChild(pieceDiv);
                    }
                    
                    // Check if valid move
                    const isValid = gameData.valid_moves.some(move => 
                        move[0] === row + 1 && move[1] === col + 1
                    );
                    
                    if (isValid && gameData.my_turn) {
                        cell.classList.add('valid');
                        cell.onclick = () => makeMove(row + 1, col + 1);
                    }
                    
                    board.appendChild(cell);
                }
            }
        }
        
        // Auto-refresh lobby every 5 seconds
        setInterval(() => {
            if (document.getElementById('lobbySection').style.display !== 'none') {
                refreshLobby();
            }
        }, 5000);
    </script>
</body>
</html>
        """
        return self.response(200, 'OK', html, {'Content-Type': 'text/html'})

    def get_server_status(self):
        """Return server status"""
        status = {
            'server': 'Othello Multiplayer Server',
            'version': '1.0',
            'active_sessions': len(self.sessions),
            'active_games': len(self.games),
            'waiting_players': len(self.waiting_players)
        }
        return self.response(200, 'OK', json.dumps(status), {'Content-Type': 'application/json'})

    def register_player(self, player_name):
        """Register a new player"""
        if not player_name or len(player_name.strip()) == 0:
            result = {'success': False, 'message': 'Player name required'}
            return self.response(400, 'Bad Request', json.dumps(result), {'Content-Type': 'application/json'})
        
        session_id = str(uuid.uuid4())
        self.sessions[session_id] = {
            'player_name': player_name.strip(),
            'game_id': None,
            'player_color': None,
            'created': datetime.now().timestamp()
        }
        
        result = {
            'success': True,
            'session_id': session_id,
            'player_name': player_name.strip()
        }
        
        return self.response(200, 'OK', json.dumps(result), {'Content-Type': 'application/json'})

    def create_game(self, post_body):
        """Create a new game"""
        try:
            data = json.loads(post_body)
            session_id = data.get('session_id')
            
            if not session_id or session_id not in self.sessions:
                result = {'success': False, 'message': 'Invalid session'}
                return self.response(400, 'Bad Request', json.dumps(result), {'Content-Type': 'application/json'})
            
            session = self.sessions[session_id]
            if session['game_id']:
                result = {'success': False, 'message': 'Already in a game'}
                return self.response(400, 'Bad Request', json.dumps(result), {'Content-Type': 'application/json'})
            
            # Create new game
            game_id = str(uuid.uuid4())
            board = Board()
            
            self.games[game_id] = {
                'board': board,
                'players': {session_id: {'name': session['player_name'], 'color': 1}},
                'created': datetime.now().timestamp(),
                'game_over': False,
                'winner': None
            }
            
            session['game_id'] = game_id
            session['player_color'] = 1
            
            result = {
                'success': True,
                'game_id': game_id,
                'player_color': 1
            }
            
            return self.response(200, 'OK', json.dumps(result), {'Content-Type': 'application/json'})
            
        except json.JSONDecodeError:
            result = {'success': False, 'message': 'Invalid JSON'}
            return self.response(400, 'Bad Request', json.dumps(result), {'Content-Type': 'application/json'})

    def join_game(self, post_body):
        """Join an existing game"""
        try:
            data = json.loads(post_body)
            session_id = data.get('session_id')
            game_id = data.get('game_id')
            
            if not session_id or session_id not in self.sessions:
                result = {'success': False, 'message': 'Invalid session'}
                return self.response(400, 'Bad Request', json.dumps(result), {'Content-Type': 'application/json'})
            
            if not game_id or game_id not in self.games:
                result = {'success': False, 'message': 'Game not found'}
                return self.response(400, 'Bad Request', json.dumps(result), {'Content-Type': 'application/json'})
            
            session = self.sessions[session_id]
            game = self.games[game_id]
            
            if len(game['players']) >= 2:
                result = {'success': False, 'message': 'Game is full'}
                return self.response(400, 'Bad Request', json.dumps(result), {'Content-Type': 'application/json'})
            
            # Add player to game
            game['players'][session_id] = {'name': session['player_name'], 'color': 2}
            session['game_id'] = game_id
            session['player_color'] = 2
            
            result = {
                'success': True,
                'game_id': game_id,
                'player_color': 2
            }
            
            return self.response(200, 'OK', json.dumps(result), {'Content-Type': 'application/json'})
            
        except json.JSONDecodeError:
            result = {'success': False, 'message': 'Invalid JSON'}
            return self.response(400, 'Bad Request', json.dumps(result), {'Content-Type': 'application/json'})

    def make_move(self, post_body):
        """Make a move in the game"""
        try:
            data = json.loads(post_body)
            session_id = data.get('session_id')
            game_id = data.get('game_id')
            row = data.get('row')
            col = data.get('col')
            
            if not all([session_id, game_id, row is not None, col is not None]):
                result = {'success': False, 'message': 'Missing parameters'}
                return self.response(400, 'Bad Request', json.dumps(result), {'Content-Type': 'application/json'})
            
            if session_id not in self.sessions:
                result = {'success': False, 'message': 'Invalid session'}
                return self.response(400, 'Bad Request', json.dumps(result), {'Content-Type': 'application/json'})
            
            if game_id not in self.games:
                result = {'success': False, 'message': 'Game not found'}
                return self.response(400, 'Bad Request', json.dumps(result), {'Content-Type': 'application/json'})
            
            session = self.sessions[session_id]
            game = self.games[game_id]
            board = game['board']
            
            # Check if it's player's turn
            if board.get_current_player() != session['player_color']:
                result = {'success': False, 'message': 'Not your turn'}
                return self.response(400, 'Bad Request', json.dumps(result), {'Content-Type': 'application/json'})
            
            # Make the move
            if board.make_move(row, col):
                # Check if game is over
                if board.is_game_over():
                    game['game_over'] = True
                    game['winner'] = board.get_winner()
                
                result = {'success': True, 'message': 'Move successful'}
                return self.response(200, 'OK', json.dumps(result), {'Content-Type': 'application/json'})
            else:
                result = {'success': False, 'message': 'Invalid move'}
                return self.response(400, 'Bad Request', json.dumps(result), {'Content-Type': 'application/json'})
                
        except json.JSONDecodeError:
            result = {'success': False, 'message': 'Invalid JSON'}
            return self.response(400, 'Bad Request', json.dumps(result), {'Content-Type': 'application/json'})

    def get_game_state(self, session_id):
        """Get current game state for a player"""
        if session_id not in self.sessions:
            result = {'success': False, 'message': 'Invalid session'}
            return self.response(400, 'Bad Request', json.dumps(result), {'Content-Type': 'application/json'})
        
        session = self.sessions[session_id]
        game_id = session['game_id']
        
        if not game_id or game_id not in self.games:
            result = {'success': False, 'message': 'Not in a game'}
            return self.response(400, 'Bad Request', json.dumps(result), {'Content-Type': 'application/json'})
        
        game = self.games[game_id]
        board = game['board']
        
        # Get opponent name
        opponent_name = None
        for pid, player in game['players'].items():
            if pid != session_id:
                opponent_name = player['name']
                break
        
        # Check if it's player's turn
        my_turn = (board.get_current_player() == session['player_color']) and len(game['players']) == 2
        
        game_state = {
            'board': board.get_grid(),
            'current_player': board.get_current_player(),
            'valid_moves': board.get_valid_moves() if not board.is_game_over() else [],
            'score': board.get_score(),
            'game_over': board.is_game_over(),
            'winner': board.get_winner() if board.is_game_over() else None,
            'my_turn': my_turn,
            'my_color': session['player_color'],
            'opponent_name': opponent_name,
            'players_count': len(game['players'])
        }
        
        result = {
            'success': True,
            'game_state': game_state
        }
        
        return self.response(200, 'OK', json.dumps(result), {'Content-Type': 'application/json'})

    def get_lobby_info(self):
        """Get available games in lobby"""
        available_games = []
        
        for game_id, game in self.games.items():
            if len(game['players']) == 1 and not game['game_over']:
                creator = list(game['players'].values())[0]['name']
                available_games.append({
                    'id': game_id,
                    'creator': creator,
                    'players': len(game['players'])
                })
        
        result = {
            'success': True,
            'games': available_games
        }
        
        return self.response(200, 'OK', json.dumps(result), {'Content-Type': 'application/json'})

    def leave_game(self, post_body):
        """Leave current game"""
        try:
            data = json.loads(post_body)
            session_id = data.get('session_id')
            
            if not session_id or session_id not in self.sessions:
                result = {'success': False, 'message': 'Invalid session'}
                return self.response(400, 'Bad Request', json.dumps(result), {'Content-Type': 'application/json'})
            
            session = self.sessions[session_id]
            game_id = session['game_id']
            
            if game_id and game_id in self.games:
                game = self.games[game_id]
                
                # Remove player from game
                if session_id in game['players']:
                    del game['players'][session_id]
                
                # If no players left, delete game
                if len(game['players']) == 0:
                    del self.games[game_id]
            
            # Clear session game info
            session['game_id'] = None
            session['player_color'] = None
            
            result = {'success': True, 'message': 'Left game successfully'}
            return self.response(200, 'OK', json.dumps(result), {'Content-Type': 'application/json'})
            
        except json.JSONDecodeError:
            result = {'success': False, 'message': 'Invalid JSON'}
            return self.response(400, 'Bad Request', json.dumps(result), {'Content-Type': 'application/json'})

    def serve_static_file(self, object_address):
        """Serve static files"""
        files = glob('./*')
        thedir = './'
        
        if object_address == '/':
            return self.get_main_page()
        
        # Remove leading slash
        object_address = object_address[1:]
        
        if thedir + object_address not in files:
            return self.response(404, 'Not Found', 'File not found', {})
        
        try:
            with open(thedir + object_address, 'rb') as fp:
                isi = fp.read()
            
            fext = os.path.splitext(thedir + object_address)[1]
            content_type = self.types.get(fext, 'application/octet-stream')
            
            headers = {'Content-Type': content_type}
            return self.response(200, 'OK', isi, headers)
            
        except Exception as e:
            return self.response(500, 'Internal Server Error', 'Error reading file', {})
            return self.response(500, 'Internal Server Error', 'Error reading file', {})