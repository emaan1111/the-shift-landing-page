#!/usr/bin/env python3
"""
View Registration Backups
Simple script to view registration backup files
"""

import json
import os
from datetime import datetime
from glob import glob

def view_registrations():
    backup_dir = 'backups'
    
    if not os.path.exists(backup_dir):
        print("❌ No backups directory found. No registrations backed up yet.")
        return
    
    # Find all registration backup files
    backup_files = sorted(glob(os.path.join(backup_dir, 'registrations-*.json')))
    
    if not backup_files:
        print("❌ No registration backup files found.")
        return
    
    print("=" * 80)
    print("📋 REGISTRATION BACKUPS")
    print("=" * 80)
    
    total_registrations = 0
    
    for backup_file in backup_files:
        try:
            with open(backup_file, 'r') as f:
                registrations = json.load(f)
            
            if not registrations:
                continue
            
            filename = os.path.basename(backup_file)
            date = filename.replace('registrations-', '').replace('.json', '')
            
            print(f"\n📅 {date} - {len(registrations)} registrations")
            print("-" * 80)
            
            for idx, reg in enumerate(registrations, 1):
                total_registrations += 1
                name = f"{reg.get('firstName', '')} {reg.get('lastName', '')}".strip()
                email = reg.get('email', 'N/A')
                country = reg.get('country', 'N/A')
                city = reg.get('city', '')
                timestamp = reg.get('timestamp', 'N/A')
                
                location = f"{city}, {country}" if city else country
                
                print(f"{idx:3}. {name:25} | {email:30} | {location:25} | {timestamp}")
        
        except Exception as e:
            print(f"❌ Error reading {backup_file}: {e}")
    
    print("\n" + "=" * 80)
    print(f"✅ Total Registrations: {total_registrations}")
    print("=" * 80)

if __name__ == '__main__':
    view_registrations()
