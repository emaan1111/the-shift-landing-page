#!/bin/bash
# Download live database from Replit
# 
# INSTRUCTIONS:
# 1. Open your Replit Shell
# 2. Run this command to create a downloadable backup:
#    python3 backup_database.py
#
# 3. The backup files will be in database_backups/ folder
# 4. Download them from Replit file explorer
# 5. Then run this script locally to restore:
#    ./download_replit_database.sh

echo "================================================"
echo "  Download Database from Replit"
echo "================================================"
echo ""

# Check if backup files exist
if [ ! -d "database_backups" ]; then
    echo "❌ No database_backups folder found"
    echo ""
    echo "📝 To create backups on Replit:"
    echo "   1. Open Replit Shell"
    echo "   2. Run: python3 backup_database.py"
    echo "   3. Download the database_backups folder"
    echo "   4. Place it in this directory"
    echo ""
    exit 1
fi

echo "✅ Found database_backups folder"
echo ""

# Check for latest backup files
ANALYTICS_FILE=$(ls -t database_backups/analytics_latest.json 2>/dev/null | head -1)
REGISTRATIONS_FILE=$(ls -t database_backups/registrations_latest.json 2>/dev/null | head -1)

if [ -z "$ANALYTICS_FILE" ] || [ -z "$REGISTRATIONS_FILE" ]; then
    echo "❌ No backup files found in database_backups/"
    echo ""
    echo "📝 Expected files:"
    echo "   - database_backups/analytics_latest.json"
    echo "   - database_backups/registrations_latest.json"
    echo ""
    exit 1
fi

echo "📦 Found backup files:"
echo "   - $ANALYTICS_FILE"
echo "   - $REGISTRATIONS_FILE"
echo ""

# Backup current database
if [ -f "analytics.db" ]; then
    BACKUP_NAME="analytics.db.backup-$(date +%Y%m%d-%H%M%S)"
    echo "💾 Backing up current database to: $BACKUP_NAME"
    cp analytics.db "$BACKUP_NAME"
    echo ""
fi

# Restore from backup
echo "🔄 Restoring database from Replit backups..."
python3 backup_database.py restore "$ANALYTICS_FILE"
python3 backup_database.py restore "$REGISTRATIONS_FILE"

echo ""
echo "✅ Database restored!"
echo ""
echo "📊 Verify the data:"
python3 check_today_registrations.py

echo ""
echo "================================================"
