import os
import json
from flask import Flask, render_template, send_from_directory
from flask_socketio import SocketIO, emit
from data import get_processes

process_list = None
app = Flask(__name__)
socketio = SocketIO(app)

with open('conf.json', 'r', encoding='utf-8') as file:
    app.config['PROCESS_LIST'] = json.load(file)

# Default route to serve HTML content
@app.route('/')
def index():
    if 'PROCESS_LIST' in app.config:
        return render_template('index.html', monitoredProcesses=app.config['PROCESS_LIST'])
    return jsonify(error="An unexpected error occurred."), 500

# Route to serve favicon.ico
@app.route('/favicon.ico')
def favicon():
    return send_from_directory('static', 'favicon.ico', mimetype='image/vnd.microsoft.icon')

# Route to serve JavaScript files from the 'static' directory
@app.route('/<folder>/<path:filename>')
def serve_js(folder, filename):
    directory = os.path.join(app.root_path, 'static')  # Path to static folder
    try:
        if folder == 'css':
            return send_from_directory(directory, filename, mimetype='text/css')
        elif folder == 'js':
            return send_from_directory(directory, filename, mimetype='application/javascript')
        else:
            raise FileNotFoundError
    except FileNotFoundError:
        abort(404)

# WebSocket handler for JSON responses
@socketio.on('stats_request')
def handle_stats_request(config):
    if isinstance(config, dict) \
      and 'watch_list' in config \
      and len(config['watch_list']) > 0:
        processes = get_processes(config['watch_list'])
        emit('stats_response', processes)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5150)
