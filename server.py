from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import requests
import json
import os
from datetime import datetime
import database  # Import our database module

app = Flask(__name__, static_folder='.')
CORS(app)  # Enable CORS for all routes

# Initialize database on startup
database.init_db()

# Geolocation cache to prevent rate limiting
geolocation_cache = {}

# ClickFunnels Configuration
CLICKFUNNELS_CONFIG = {
    'apiKey': '7A8agApD4eXUESHF-ikrWlCF-k7IEjtTd7auzmiRbZ0',
    'workspaceId': 'jxRdRe',
    'teamId': 'JNqzOe',
    'tagIds': [367566],  # List-ShiftRegistered-Nov25
    'visitorTagIds': [367576]  # List-ShiftVisitiedNov24
}

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    if os.path.exists(path):
        return send_from_directory('.', path)
    return "File not found", 404

@app.route('/api/clickfunnels/contact', methods=['POST'])
def create_contact():
    try:
        # Get data from frontend
        data = request.json
        
        # Prepare payload for ClickFunnels
        default_tag_ids = data.get('tag_ids') or data.get('tagIds') or CLICKFUNNELS_CONFIG.get('tagIds', [367566])

        payload = {
            'contact': {
                'email_address': data.get('email'),
                'first_name': data.get('firstName', ''),
                'last_name': data.get('lastName', ''),
                'phone_number': data.get('phone', ''),
                'tag_ids': data.get('tag_ids') or data.get('tagIds') or default_tag_ids,
                'fields': {
                    'source': data.get('source', 'The Shift Landing Page'),
                    'utm_source': data.get('utm_source', ''),
                    'utm_medium': data.get('utm_medium', ''),
                    'utm_campaign': data.get('utm_campaign', ''),
                    'utm_content': data.get('utm_content', ''),
                    'country': data.get('country', ''),
                    'city': data.get('city', ''),
                    'referrer': data.get('referrer', ''),
                    'registration_date': data.get('registration_date', '')
                }
            }
        }
        
        # Send to ClickFunnels API (upsert handles create or update)
        url = f"https://api.myclickfunnels.com/api/v2/workspaces/{CLICKFUNNELS_CONFIG['workspaceId']}/contacts/upsert"
        
        headers = {
            'Authorization': f"Bearer {CLICKFUNNELS_CONFIG['apiKey']}",
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36'
        }
        
        response = requests.post(url, json=payload, headers=headers)
        
        if response.status_code == 200 or response.status_code == 201:
            return jsonify({
                'success': True,
                'data': response.json()
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': response.text,
                'status': response.status_code
            }), response.status_code
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'}), 200

@app.route('/api/github/analytics/list', methods=['GET'])
def list_analytics():
    """Proxy endpoint to list analytics files from GitHub"""
    try:
        # Read GitHub config from analytics-config.js file
        config_path = os.path.join('.', 'js', 'analytics-config.js')
        with open(config_path, 'r') as f:
            content = f.read()
            # Extract token from JavaScript file
            import re
            token_match = re.search(r"token:\s*['\"]([^'\"]+)['\"]", content)
            owner_match = re.search(r"owner:\s*['\"]([^'\"]+)['\"]", content)
            repo_match = re.search(r"repo:\s*['\"]([^'\"]+)['\"]", content)
            
            if not token_match or not owner_match or not repo_match:
                return jsonify({'error': 'GitHub configuration not found'}), 500
            
            token = token_match.group(1)
            owner = owner_match.group(1)
            repo = repo_match.group(1)
        
        url = f"https://api.github.com/repos/{owner}/{repo}/contents/analytics"
        headers = {
            'Authorization': f'token {token}',
            'Accept': 'application/vnd.github.v3+json'
        }
        
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            return jsonify(response.json()), 200
        else:
            return jsonify({'error': response.text, 'status': response.status_code}), response.status_code
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/github/analytics/file', methods=['GET'])
def get_analytics_file():
    """Proxy endpoint to get a specific analytics file from GitHub"""
    try:
        file_url = request.args.get('url')
        if not file_url:
            return jsonify({'error': 'Missing file URL parameter'}), 400
        
        # Read GitHub config
        config_path = os.path.join('.', 'js', 'analytics-config.js')
        with open(config_path, 'r') as f:
            content = f.read()
            import re
            token_match = re.search(r"token:\s*['\"]([^'\"]+)['\"]", content)
            
            if not token_match:
                return jsonify({'error': 'GitHub token not found'}), 500
            
            token = token_match.group(1)
        
        headers = {
            'Authorization': f'token {token}',
            'Accept': 'application/vnd.github.v3.raw'
        }
        
        response = requests.get(file_url, headers=headers)
        
        if response.status_code == 200:
            return response.text, 200, {'Content-Type': 'application/json'}
        else:
            return jsonify({'error': response.text, 'status': response.status_code}), response.status_code
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/github/analytics/delete', methods=['POST'])
def delete_analytics_file():
    """Proxy endpoint to delete analytics files from GitHub"""
    try:
        data = request.json
        file_path = data.get('path')
        sha = data.get('sha')
        
        if not file_path or not sha:
            return jsonify({'error': 'Missing path or sha parameter'}), 400
        
        # Read GitHub config
        config_path = os.path.join('.', 'js', 'analytics-config.js')
        with open(config_path, 'r') as f:
            content = f.read()
            import re
            token_match = re.search(r"token:\s*['\"]([^'\"]+)['\"]", content)
            owner_match = re.search(r"owner:\s*['\"]([^'\"]+)['\"]", content)
            repo_match = re.search(r"repo:\s*['\"]([^'\"]+)['\"]", content)
            branch_match = re.search(r"branch:\s*['\"]([^'\"]+)['\"]", content)
            
            if not token_match or not owner_match or not repo_match:
                return jsonify({'error': 'GitHub configuration not found'}), 500
            
            token = token_match.group(1)
            owner = owner_match.group(1)
            repo = repo_match.group(1)
            branch = branch_match.group(1) if branch_match else 'main'
        
        url = f"https://api.github.com/repos/{owner}/{repo}/contents/{file_path}"
        headers = {
            'Authorization': f'token {token}',
            'Accept': 'application/vnd.github.v3+json',
            'Content-Type': 'application/json'
        }
        
        payload = {
            'message': f'Delete analytics data: {file_path}',
            'sha': sha,
            'branch': branch
        }
        
        response = requests.delete(url, json=payload, headers=headers)
        
        if response.status_code in [200, 204]:
            return jsonify({'success': True}), 200
        else:
            return jsonify({'error': response.text, 'status': response.status_code}), response.status_code
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/geolocation', methods=['GET'])
def get_geolocation():
    """Proxy endpoint for geolocation API to avoid CORS issues"""
    try:
        # Get client IP address
        client_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
        if client_ip:
            client_ip = client_ip.split(',')[0].strip()
        
        # Check cache first
        if client_ip in geolocation_cache:
            return jsonify(geolocation_cache[client_ip]), 200
        
        # Make API call if not in cache
        response = requests.get('https://ipapi.co/json/', timeout=5)
        if response.status_code == 200:
            data = response.json()
            # Cache the result
            geolocation_cache[client_ip] = data
            return jsonify(data), 200
        else:
            # Return a default response on rate limit or error
            default_data = {'city': 'Unknown', 'country': 'Unknown', 'error': 'Rate limited'}
            return jsonify(default_data), 200
    except Exception as e:
        # Return a default response on exception
        default_data = {'city': 'Unknown', 'country': 'Unknown', 'error': str(e)}
        return jsonify(default_data), 200

@app.route('/api/backup/registration', methods=['POST'])
def backup_registration():
    """Backup registration data to local JSON file"""
    try:
        data = request.json
        
        # Add timestamp if not present
        if 'timestamp' not in data:
            data['timestamp'] = datetime.now().isoformat()
        
        # Create backups directory if it doesn't exist
        backup_dir = 'backups'
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)
        
        # Use date-based filename
        today = datetime.now().strftime('%Y-%m-%d')
        backup_file = os.path.join(backup_dir, f'registrations-{today}.json')
        
        # Read existing data or create new list
        existing_data = []
        if os.path.exists(backup_file):
            try:
                with open(backup_file, 'r') as f:
                    existing_data = json.load(f)
            except:
                existing_data = []
        
        # Add new registration
        existing_data.append(data)
        
        # Save back to file
        with open(backup_file, 'w') as f:
            json.dump(existing_data, f, indent=2)
        
        return jsonify({'success': True, 'message': 'Registration backed up'}), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/registrations', methods=['GET'])
def get_all_registrations():
    """Get all registrations from database (replacing GitHub + backup files)"""
    try:
        registrations = database.get_all_registrations()
        return jsonify(registrations), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# NEW DATABASE ENDPOINTS

@app.route('/api/analytics/track', methods=['POST'])
def track_analytics():
    """Track analytics event to database"""
    try:
        data = request.json
        
        # Add server timestamp if not present
        if 'timestamp' not in data:
            data['timestamp'] = datetime.now().isoformat()
        
        event_id = database.insert_analytics(data)
        
        return jsonify({
            'success': True,
            'id': event_id,
            'message': 'Event tracked successfully'
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/analytics/registration', methods=['POST'])
def track_registration():
    """Track registration to database"""
    try:
        data = request.json
        
        # Add server timestamp if not present
        if 'timestamp' not in data:
            data['timestamp'] = datetime.now().isoformat()
        
        reg_id = database.insert_registration(data)
        
        if reg_id:
            return jsonify({
                'success': True,
                'id': reg_id,
                'message': 'Registration tracked successfully'
            }), 200
        else:
            return jsonify({
                'success': True,
                'message': 'Duplicate registration skipped'
            }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/analytics/stats', methods=['GET'])
def get_analytics_stats():
    """Get analytics statistics"""
    try:
        stats = database.get_analytics_stats()
        return jsonify(stats), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/analytics/events', methods=['GET'])
def get_analytics_events():
    """Get analytics events with optional filtering"""
    try:
        event_type = request.args.get('event')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        limit = request.args.get('limit', type=int)
        
        events = database.get_all_analytics(
            event_type=event_type,
            start_date=start_date,
            end_date=end_date,
            limit=limit
        )
        
        return jsonify(events), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/analytics/event/<int:event_id>', methods=['GET', 'DELETE'])
def manage_analytics_event(event_id):
    """Get or delete a specific analytics event"""
    try:
        if request.method == 'GET':
            event = database.get_analytics_event_by_id(event_id)
            if event:
                return jsonify(event), 200
            else:
                return jsonify({'error': 'Event not found'}), 404
        
        elif request.method == 'DELETE':
            success = database.delete_analytics_event(event_id)
            if success:
                return jsonify({
                    'success': True,
                    'message': f'Analytics event {event_id} deleted successfully'
                }), 200
            else:
                return jsonify({'error': 'Event not found'}), 404
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/registration/<int:registration_id>', methods=['GET', 'DELETE'])
def manage_registration(registration_id):
    """Get or delete a specific registration"""
    try:
        if request.method == 'GET':
            registration = database.get_registration_by_id(registration_id)
            if registration:
                return jsonify(registration), 200
            else:
                return jsonify({'error': 'Registration not found'}), 404
        
        elif request.method == 'DELETE':
            success = database.delete_registration(registration_id)
            if success:
                return jsonify({
                    'success': True,
                    'message': f'Registration {registration_id} deleted successfully'
                }), 200
            else:
                return jsonify({'error': 'Registration not found'}), 404
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/database/reset', methods=['POST'])
def reset_database():
    """Delete all analytics events and registrations from database"""
    try:
        conn = database.get_db().__enter__()
        cursor = conn.cursor()
        
        # Get counts before deletion
        cursor.execute('SELECT COUNT(*) FROM analytics')
        analytics_count = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM registrations')
        registrations_count = cursor.fetchone()[0]
        
        # Delete all data
        cursor.execute('DELETE FROM analytics')
        cursor.execute('DELETE FROM registrations')
        conn.commit()
        
        database.get_db().__exit__(None, None, None)
        
        return jsonify({
            'success': True,
            'message': f'Database reset successful',
            'deleted': {
                'analytics': analytics_count,
                'registrations': registrations_count
            }
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
