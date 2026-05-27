import os
import sys
import time
import platform
from datetime import datetime
from flask import Flask, render_template, jsonify, request

START_TIME = time.time()
STRESS_END_TIME = 0.0

def create_app():
    # Use explicit template and static folders
    app = Flask(__name__,
                template_folder=os.path.join(os.path.dirname(__file__), 'templates'),
                static_folder=os.path.join(os.path.dirname(__file__), 'static'))

    # Configuration setup
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'antigravity-secret-key-1919')

    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/api/status')
    def status():
        uptime = round(time.time() - START_TIME, 2)
        return jsonify({
            'status': 'healthy',
            'uptime_seconds': uptime,
            'python_version': sys.version,
            'platform': platform.platform(),
            'server_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'environment': 'development',
            'port': 1919
        })

    @app.route('/api/echo', methods=['GET', 'POST'])
    def echo():
        if request.method == 'POST':
            data = request.get_json(silent=True) or {}
            message = data.get('message', '')
            name = data.get('name', 'Guest')
        else:
            message = request.args.get('message', '')
            name = request.args.get('name', 'Guest')

        return jsonify({
            'success': True,
            'message': f"Hello {name}! Flask received your message: '{message}'",
            'echo': {
                'message': message,
                'name': name
            },
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })

    @app.route('/api/health')
    def health():
        return jsonify({
            'status': 'OK',
            'timestamp': datetime.now().isoformat(),
            'code': 200
        })

    @app.route('/api/files')
    def list_files():
        root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        file_list = []
        
        # Scan src and test folders
        targets = ['src', 'test']
        for target in targets:
            target_path = os.path.join(root_dir, target)
            if os.path.exists(target_path):
                for root, _, files in os.walk(target_path):
                    for file in files:
                        if file.endswith(('.py', '.html', '.css', '.js')):
                            full_path = os.path.join(root, file)
                            rel_path = os.path.relpath(full_path, root_dir)
                            file_list.append(rel_path.replace('\\', '/'))
                            
        # Scan root files
        for file in ['run.py', 'requirements.txt']:
            if os.path.exists(os.path.join(root_dir, file)):
                file_list.append(file)
                
        return jsonify({
            'success': True,
            'files': sorted(file_list)
        })

    @app.route('/api/files/content')
    def get_file_content():
        filepath = request.args.get('filepath', '')
        if not filepath:
            return jsonify({'success': False, 'error': 'Missing filepath parameter'}), 400
            
        root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        target_path = os.path.abspath(os.path.join(root_dir, filepath))
        
        # Security path boundary validation
        if not target_path.startswith(root_dir) or not os.path.isfile(target_path):
            return jsonify({'success': False, 'error': 'Forbidden - Access outside project scope is denied'}), 403
            
        try:
            with open(target_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return jsonify({
                'success': True,
                'filepath': filepath,
                'content': content
            })
        except Exception as e:
            return jsonify({'success': False, 'error': f"Failed to read file: {str(e)}"}), 500

    @app.route('/api/metrics')
    def get_metrics():
        global STRESS_END_TIME
        now = time.time()
        
        if now < STRESS_END_TIME:
            # Active stress simulation decay calculations
            remaining = STRESS_END_TIME - now
            fraction = remaining / 15.0 # Max stress 15s
            cpu = round(45.0 + 50.0 * fraction + (now % 3), 1)
            memory = round(55.0 + 32.0 * fraction + (now % 2), 1)
            sockets = int(45 + 90 * fraction)
            stress_active = True
        else:
            # Normal idle environment
            cpu = round(12.0 + (now % 4) * 1.5, 1)
            memory = round(38.0 + (now % 2) * 0.5, 1)
            sockets = int(8 + (now % 3))
            stress_active = False
            
        return jsonify({
            'success': True,
            'cpu_percentage': min(cpu, 100.0),
            'memory_percentage': min(memory, 100.0),
            'active_sockets': sockets,
            'stress_active': stress_active,
            'stress_time_remaining': max(round(STRESS_END_TIME - now, 1), 0.0)
        })

    @app.route('/api/metrics/stress', methods=['POST'])
    def trigger_stress():
        global STRESS_END_TIME
        STRESS_END_TIME = time.time() + 15.0
        return jsonify({
            'success': True,
            'message': 'Cloud Stress Test activated! Simulating peak visitor loads (90%+) for 15 seconds.',
            'ends_at': STRESS_END_TIME
        })

    @app.errorhandler(404)
    def page_not_found(e):
        if request.path.startswith('/api/'):
            return jsonify({
                'success': False,
                'error': 'Not Found',
                'message': 'The requested API endpoint does not exist.'
            }), 404
        return render_template('index.html'), 404

    return app
