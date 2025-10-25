from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import requests
import json
import os
from datetime import datetime

app = Flask(__name__, static_folder='.')
CORS(app)  # Enable CORS for all routes

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
        response = requests.get('https://ipapi.co/json/', timeout=5)
        if response.status_code == 200:
            return jsonify(response.json()), 200
        else:
            return jsonify({'error': 'Failed to fetch geolocation'}), response.status_code
    except Exception as e:
        return jsonify({'error': str(e)}), 500

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
    """Get all registrations from backup files and GitHub visits"""
    try:
        all_registrations = []
        
        # First, load from local backups
        backup_dir = 'backups'
        if os.path.exists(backup_dir):
            from glob import glob
            backup_files = sorted(glob(os.path.join(backup_dir, 'registrations-*.json')))
            
            for backup_file in backup_files:
                try:
                    with open(backup_file, 'r') as f:
                        registrations = json.load(f)
                        if isinstance(registrations, list):
                            all_registrations.extend(registrations)
                except:
                    pass
        
        # Then, try to load registrations from GitHub visits files
        try:
            config_path = os.path.join('.', 'js', 'analytics-config.js')
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    content = f.read()
                    import re
                    token_match = re.search(r"token:\s*['\"]([^'\"]+)['\"]", content)
                    owner_match = re.search(r"owner:\s*['\"]([^'\"]+)['\"]", content)
                    repo_match = re.search(r"repo:\s*['\"]([^'\"]+)['\"]", content)
                    
                    if token_match and owner_match and repo_match:
                        token = token_match.group(1)
                        owner = owner_match.group(1)
                        repo = repo_match.group(1)
                        
                        # Fetch list of files from GitHub
                        url = f"https://api.github.com/repos/{owner}/{repo}/contents/analytics"
                        headers = {
                            'Authorization': f'token {token}',
                            'Accept': 'application/vnd.github.v3+json'
                        }
                        
                        response = requests.get(url, headers=headers)
                        if response.status_code == 200:
                            files = response.json()
                            
                            # Look for visits files that may contain registrations
                            for file in files:
                                if 'visits' in file['name'].lower() and file['name'].endswith('.json'):
                                    try:
                                        file_url = file['url']
                                        file_response = requests.get(file_url, headers=headers)
                                        if file_response.status_code == 200:
                                            file_data = file_response.json()
                                            if 'content' in file_data:
                                                import base64
                                                decoded_content = base64.b64decode(file_data['content']).decode('utf-8')
                                                visits = json.loads(decoded_content)
                                                if isinstance(visits, list):
                                                    # Extract only registration events
                                                    for visit in visits:
                                                        if visit.get('event') == 'registration':
                                                            reg = {
                                                                'email': visit.get('email'),
                                                                'firstName': visit.get('firstName'),
                                                                'lastName': visit.get('lastName'),
                                                                'country': visit.get('country'),
                                                                'city': visit.get('city'),
                                                                'timestamp': visit.get('timestamp')
                                                            }
                                                            # Avoid duplicates
                                                            if not any(r.get('email') == reg.get('email') and r.get('timestamp') == reg.get('timestamp') for r in all_registrations):
                                                                all_registrations.append(reg)
                                    except:
                                        pass
        except:
            pass
        
        # Sort by timestamp (newest first)
        all_registrations.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        
        # Remove duplicates based on email and timestamp
        seen = set()
        unique_registrations = []
        for reg in all_registrations:
            key = (reg.get('email', ''), reg.get('timestamp', ''))
            if key not in seen and reg.get('email'):  # Only include if email exists
                seen.add(key)
                unique_registrations.append(reg)
        
        return jsonify(unique_registrations), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000, debug=True)
