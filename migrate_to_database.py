"""
Migration script to move data from GitHub/JSON backups to SQLite database
Run this once to migrate your existing data
"""

import json
import os
import glob
import requests
import base64
import re
from database import init_db, insert_analytics, insert_registration

def migrate_from_backups():
    """Migrate data from local backup JSON files"""
    print('📦 Migrating from local backup files...')
    
    backup_dir = 'backups'
    if not os.path.exists(backup_dir):
        print('⚠️  No backups directory found')
        return 0
    
    backup_files = sorted(glob.glob(os.path.join(backup_dir, 'registrations-*.json')))
    
    count = 0
    for backup_file in backup_files:
        print(f'  Processing {backup_file}...')
        try:
            with open(backup_file, 'r') as f:
                registrations = json.load(f)
                if isinstance(registrations, list):
                    for reg in registrations:
                        # Convert field names to match database expectations
                        data = {
                            'email': reg.get('email') or reg.get('emailAddress'),
                            'firstName': reg.get('firstName') or reg.get('first_name'),
                            'lastName': reg.get('lastName') or reg.get('last_name'),
                            'phone': reg.get('phone'),
                            'country': reg.get('country'),
                            'city': reg.get('city'),
                            'region': reg.get('region'),
                            'timezone': reg.get('timezone'),
                            'ipAddress': reg.get('ipAddress') or reg.get('ip_address'),
                            'visitorId': reg.get('visitorId') or reg.get('visitor_id'),
                            'sessionId': reg.get('sessionId') or reg.get('session_id'),
                            'hookVariant': reg.get('hookVariant') or reg.get('hook_variant') or reg.get('variant'),
                            'referrer': reg.get('referrer'),
                            'utmSource': reg.get('utmSource') or reg.get('utm_source'),
                            'utmMedium': reg.get('utmMedium') or reg.get('utm_medium'),
                            'utmCampaign': reg.get('utmCampaign') or reg.get('utm_campaign'),
                            'utmContent': reg.get('utmContent') or reg.get('utm_content'),
                            'timestamp': reg.get('timestamp')
                        }
                        
                        if data['email']:  # Only insert if email exists
                            result = insert_registration(data)
                            if result:
                                count += 1
        except Exception as e:
            print(f'  ❌ Error processing {backup_file}: {e}')
    
    print(f'✅ Migrated {count} registrations from backups')
    return count

def migrate_from_github():
    """Migrate data from GitHub analytics files"""
    print('📦 Migrating from GitHub analytics files...')
    
    # Read GitHub config
    config_path = os.path.join('.', 'js', 'analytics-config.js')
    if not os.path.exists(config_path):
        print('⚠️  No analytics-config.js found')
        return 0
    
    try:
        with open(config_path, 'r') as f:
            content = f.read()
            token_match = re.search(r"token:\s*['\"]([^'\"]+)['\"]", content)
            owner_match = re.search(r"owner:\s*['\"]([^'\"]+)['\"]", content)
            repo_match = re.search(r"repo:\s*['\"]([^'\"]+)['\"]", content)
            
            if not token_match or not owner_match or not repo_match:
                print('⚠️  GitHub configuration not complete')
                return 0
            
            token = token_match.group(1)
            owner = owner_match.group(1)
            repo = repo_match.group(1)
            
            if token == 'YOUR_GITHUB_TOKEN':
                print('⚠️  GitHub token not configured')
                return 0
    except Exception as e:
        print(f'❌ Error reading GitHub config: {e}')
        return 0
    
    # Fetch analytics files from GitHub
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/analytics"
    headers = {
        'Authorization': f'token {token}',
        'Accept': 'application/vnd.github.v3+json'
    }
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            print(f'⚠️  Could not fetch GitHub analytics: {response.status_code}')
            return 0
        
        files = response.json()
        
        analytics_count = 0
        registration_count = 0
        
        for file in files:
            if file['name'].endswith('.json'):
                print(f'  Processing {file["name"]}...')
                try:
                    file_response = requests.get(file['url'], headers=headers)
                    if file_response.status_code == 200:
                        file_data = file_response.json()
                        if 'content' in file_data:
                            decoded_content = base64.b64decode(file_data['content']).decode('utf-8')
                            events = json.loads(decoded_content)
                            
                            if isinstance(events, list):
                                for event in events:
                                    event_type = event.get('event')
                                    
                                    if event_type == 'registration':
                                        # Insert as registration
                                        data = {
                                            'email': event.get('email') or event.get('emailAddress'),
                                            'firstName': event.get('firstName') or event.get('first_name'),
                                            'lastName': event.get('lastName') or event.get('last_name'),
                                            'phone': event.get('phone'),
                                            'country': event.get('country'),
                                            'city': event.get('city'),
                                            'region': event.get('region'),
                                            'timezone': event.get('timezone'),
                                            'ipAddress': event.get('ipAddress') or event.get('ip_address'),
                                            'visitorId': event.get('visitorId') or event.get('visitor_id'),
                                            'sessionId': event.get('sessionId') or event.get('session_id'),
                                            'hookVariant': event.get('hookVariant') or event.get('hook_variant'),
                                            'referrer': event.get('referrer'),
                                            'utmSource': event.get('utmSource') or event.get('utm_source'),
                                            'utmMedium': event.get('utmMedium') or event.get('utm_medium'),
                                            'utmCampaign': event.get('utmCampaign') or event.get('utm_campaign'),
                                            'utmContent': event.get('utmContent') or event.get('utm_content'),
                                            'timestamp': event.get('timestamp')
                                        }
                                        
                                        if data['email']:
                                            result = insert_registration(data)
                                            if result:
                                                registration_count += 1
                                    else:
                                        # Insert as analytics event
                                        data = {
                                            'event': event_type,
                                            'page': event.get('page'),
                                            'timestamp': event.get('timestamp'),
                                            'visitorId': event.get('visitorId') or event.get('visitor_id'),
                                            'sessionId': event.get('sessionId') or event.get('session_id'),
                                            'email': event.get('email'),
                                            'name': event.get('name'),
                                            'country': event.get('country'),
                                            'city': event.get('city'),
                                            'region': event.get('region'),
                                            'ipAddress': event.get('ipAddress') or event.get('ip_address'),
                                            'timezone': event.get('timezone'),
                                            'referrer': event.get('referrer'),
                                            'userAgent': event.get('userAgent') or event.get('user_agent'),
                                            'screenWidth': event.get('screenWidth') or event.get('screen_width'),
                                            'screenHeight': event.get('screenHeight') or event.get('screen_height'),
                                            'language': event.get('language'),
                                            'hookVariant': event.get('hookVariant') or event.get('hook_variant'),
                                            'buttonName': event.get('buttonName') or event.get('button_name'),
                                            'duration': event.get('duration'),
                                            'utmSource': event.get('utmSource') or event.get('utm_source'),
                                            'utmMedium': event.get('utmMedium') or event.get('utm_medium'),
                                            'utmCampaign': event.get('utmCampaign') or event.get('utm_campaign'),
                                            'utmContent': event.get('utmContent') or event.get('utm_content')
                                        }
                                        
                                        insert_analytics(data)
                                        analytics_count += 1
                                        
                except Exception as e:
                    print(f'  ❌ Error processing {file["name"]}: {e}')
        
        print(f'✅ Migrated {analytics_count} analytics events and {registration_count} registrations from GitHub')
        return analytics_count + registration_count
        
    except Exception as e:
        print(f'❌ Error fetching from GitHub: {e}')
        return 0

def main():
    print('🚀 Starting migration to database...\n')
    
    # Initialize database
    print('📊 Initializing database...')
    init_db()
    print()
    
    # Migrate from backups
    backup_count = migrate_from_backups()
    print()
    
    # Migrate from GitHub
    github_count = migrate_from_github()
    print()
    
    total = backup_count + github_count
    print(f'✅ Migration complete! Total records migrated: {total}')
    print()
    print('Next steps:')
    print('1. Update your HTML files to use tracker-db.js instead of tracker.js')
    print('2. Restart your Flask server')
    print('3. Test the new tracking system')
    print()
    print('Your old data is safe in backups/ and GitHub - you can keep them as backup!')

if __name__ == '__main__':
    main()
