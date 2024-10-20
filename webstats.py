import os
from flask import Flask, render_template, send_from_directory
from flask_socketio import SocketIO, emit
import json
from data import get_top_cpu_processes

app = Flask(__name__)
socketio = SocketIO(app)

# Default route to serve HTML content
@app.route('/')
def index():
    return render_template('index.html')

# Route to serve favicon.ico
@app.route('/favicon.ico')
def favicon():
    return send_from_directory('static', 'favicon.ico', mimetype='image/vnd.microsoft.icon')

# Route to serve JavaScript files from the 'static' directory
@app.route('/js/<path:filename>')
def serve_js(filename):
    js_directory = os.path.join(app.root_path, 'static')  # Path to static folder
    try:
        # Ensure the requested file exists
        return send_from_directory(js_directory, filename, mimetype='application/javascript')
    except FileNotFoundError:
        # Return 404 if the file is not found
        abort(404)

# WebSocket handler for JSON responses
@socketio.on('stats_request')
def handle_stats_request(data):
    processes = get_top_cpu_processes()
    emit('stats_response', processes)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5150)
