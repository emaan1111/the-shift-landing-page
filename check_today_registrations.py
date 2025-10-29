#!/usr/bin/env python3
"""
Quick script to check today's registrations
Run this on your Replit server to see live data
"""

from database import get_db
from datetime import datetime, timedelta

def check_registrations():
    """Check registrations for today and recent days"""
    
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Get today's date
        today = datetime.now().strftime('%Y-%m-%d')
        yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        
        print('=' * 80)
        print('🔍 REGISTRATION REPORT')
        print('=' * 80)
        
        # Today's registrations
        cursor.execute('''
            SELECT COUNT(*) as count 
            FROM registrations 
            WHERE DATE(timestamp) = ?
        ''', (today,))
        today_count = cursor.fetchone()['count']
        
        print(f'\n📅 Today ({today}): {today_count} registration(s)')
        
        if today_count > 0:
            cursor.execute('''
                SELECT id, email, first_name, last_name, country, city, timestamp
                FROM registrations 
                WHERE DATE(timestamp) = ?
                ORDER BY timestamp DESC
            ''', (today,))
            
            registrations = cursor.fetchall()
            print('-' * 80)
            for reg in registrations:
                name = f"{reg['first_name'] or ''} {reg['last_name'] or ''}".strip() or 'N/A'
                country = reg['country'] or 'N/A'
                city = reg['city'] or 'N/A'
                time = reg['timestamp'].split('T')[1][:8] if 'T' in reg['timestamp'] else 'N/A'
                print(f"  {time} | {name} | {reg['email']}")
                print(f"           Location: {city}, {country}")
                print()
        
        # Yesterday's registrations
        cursor.execute('''
            SELECT COUNT(*) as count 
            FROM registrations 
            WHERE DATE(timestamp) = ?
        ''', (yesterday,))
        yesterday_count = cursor.fetchone()['count']
        
        print(f'📅 Yesterday ({yesterday}): {yesterday_count} registration(s)')
        
        # Last 7 days
        seven_days_ago = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        cursor.execute('''
            SELECT DATE(timestamp) as date, COUNT(*) as count 
            FROM registrations 
            WHERE DATE(timestamp) >= ?
            GROUP BY DATE(timestamp)
            ORDER BY date DESC
        ''', (seven_days_ago,))
        
        weekly = cursor.fetchall()
        
        print(f'\n📊 Last 7 Days:')
        print('-' * 80)
        total_week = 0
        for day in weekly:
            print(f"  {day['date']}: {day['count']} registration(s)")
            total_week += day['count']
        
        print(f'\n  Total: {total_week} registrations')
        
        # All-time stats
        cursor.execute('SELECT COUNT(*) as count FROM registrations')
        total_count = cursor.fetchone()['count']
        
        cursor.execute('SELECT COUNT(DISTINCT visitor_id) as count FROM registrations WHERE visitor_id IS NOT NULL')
        unique_visitors = cursor.fetchone()['count']
        
        print(f'\n📈 All-Time Stats:')
        print('-' * 80)
        print(f'  Total Registrations: {total_count}')
        print(f'  Unique Visitors: {unique_visitors}')
        
        # Top countries
        cursor.execute('''
            SELECT country, COUNT(*) as count 
            FROM registrations 
            WHERE country IS NOT NULL AND country != ''
            GROUP BY country 
            ORDER BY count DESC
            LIMIT 5
        ''')
        countries = cursor.fetchall()
        
        if countries:
            print(f'\n🌍 Top Countries:')
            print('-' * 80)
            for country in countries:
                print(f"  {country['country']}: {country['count']} registration(s)")
        
        # Recent analytics events
        cursor.execute('''
            SELECT event, COUNT(*) as count 
            FROM analytics 
            WHERE DATE(timestamp) = ?
            GROUP BY event
            ORDER BY count DESC
        ''', (today,))
        
        events = cursor.fetchall()
        
        if events:
            print(f'\n📊 Today\'s Analytics Events:')
            print('-' * 80)
            for event in events:
                print(f"  {event['event']}: {event['count']}")
        
        print('\n' + '=' * 80)

if __name__ == '__main__':
    check_registrations()
