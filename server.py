from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import requests
import json
import os
from datetime import datetime

# Try PostgreSQL first, fallback to SQLite
try:
    # Check if DATABASE_URL is set
    if not os.getenv('DATABASE_URL'):
        raise ValueError("DATABASE_URL not set, using SQLite")
    import database_unified as database  # Import PostgreSQL database module
    print("✅ Using PostgreSQL database")
except (ValueError, Exception) as e:
    print(f"⚠️  PostgreSQL not available ({e})")
    print("✅ Using SQLite database (analytics.db)")
    import database_sqlite as database  # Fallback to SQLite

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
        with database.get_db() as conn:
            cursor = conn.cursor()
            
            # Get counts before deletion
            cursor.execute('SELECT COUNT(*) as count FROM analytics')
            analytics_count = cursor.fetchone()['count']
            
            cursor.execute('SELECT COUNT(*) as count FROM registrations')
            registrations_count = cursor.fetchone()['count']
            
            # Delete all data
            cursor.execute('DELETE FROM analytics')
            cursor.execute('DELETE FROM registrations')
            # No need to commit - context manager handles it
        
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

@app.route('/api/waitinglist', methods=['POST'])
def add_to_waitinglist():
    """Add someone to the waiting list"""
    try:
        data = request.json
        
        # Add server timestamp if not present
        if 'timestamp' not in data:
            data['timestamp'] = datetime.now().isoformat()
        
        # Insert into database
        waitlist_id = database.insert_waitinglist(data)
        
        if waitlist_id:
            # Also send to ClickFunnels with waiting list tag
            try:
                cf_data = {
                    'email': data.get('email'),
                    'firstName': data.get('firstName', ''),
                    'lastName': data.get('lastName', ''),
                    'phone': data.get('phone', ''),
                    'tagIds': [367577],  # Waiting list tag (you'll need to create this in ClickFunnels)
                    'source': 'The Shift Waiting List',
                    'hear_about': data.get('hearAbout', '')
                }
                
                # Send to ClickFunnels (non-blocking, don't fail if it doesn't work)
                requests.post(
                    f"http://localhost:{request.environ.get('SERVER_PORT', 5000)}/api/clickfunnels/contact",
                    json=cf_data,
                    timeout=5
                )
            except:
                pass  # Don't fail if ClickFunnels integration fails
            
            return jsonify({
                'success': True,
                'id': waitlist_id,
                'message': 'Successfully added to waiting list'
            }), 200
        else:
            return jsonify({
                'success': True,
                'message': 'Already on waiting list'
            }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/waitinglist', methods=['GET'])
def get_waitinglist():
    """Get all waiting list entries"""
    try:
        entries = database.get_all_waitinglist()
        return jsonify(entries), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/settings', methods=['GET'])
def get_settings():
    """Get all settings"""
    try:
        settings = database.get_all_settings()
        return jsonify(settings), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/settings/<key>', methods=['GET'])
def get_setting(key):
    """Get a specific setting"""
    try:
        value = database.get_setting(key)
        if value is not None:
            return jsonify({'key': key, 'value': value}), 200
        else:
            return jsonify({'error': 'Setting not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/settings/<key>', methods=['PUT', 'POST'])
def update_setting(key):
    """Update a setting"""
    try:
        data = request.json
        value = data.get('value')
        
        if value is None:
            return jsonify({'error': 'Value is required'}), 400
        
        database.set_setting(key, str(value))
        
        return jsonify({
            'success': True,
            'key': key,
            'value': value,
            'message': f'Setting {key} updated successfully'
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
