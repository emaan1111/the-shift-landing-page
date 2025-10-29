# Analytics System Diagnosis

## Problem Identified ✅

Based on the Replit logs, you discovered:

### 1. **Database Tracking is Failing (500 Errors)**
```
POST /api/analytics/track HTTP/1.1" 500
```
- New analytics events are not being saved to the database
- This started happening between Oct 28 2PM-10PM

### 2. **Analytics Page Shows Old GitHub JSON Data**
```
GET /api/github/analytics/list HTTP/1.1" 200
GET /api/github/analytics/file?url=...visits-2025-10-29.json...
GET /api/github/analytics/file?url=...visits-2025-10-28.json...
```
- The page is falling back to reading old JSON files from GitHub
- This explains why you see "some data" but not recent data

### 3. **Missing Oct 28 Data (2PM-10PM)**
- During this time period, tracking was failing (500 errors)
- No JSON files were created for this period
- Data was never saved anywhere → **permanently lost**

## Root Cause Analysis

You have TWO tracking systems running simultaneously:

1. **OLD System**: JavaScript tracker writing to GitHub JSON files (`analytics/visits-*.json`)
2. **NEW System**: Database-based tracking via `/api/analytics/track`

The NEW system is failing with 500 errors, so analytics are being lost.

## To Fix on Replit

### Step 1: Check the Actual Error
Run this on Replit to see what's causing the 500 error:

```bash
cd /home/runner/the-shift-landing-page
python3 -c "
import database
import json
from datetime import datetime

# Try to insert a test analytics event
test_event = {
    'event_type': 'test',
    'timestamp': datetime.now().isoformat(),
    'visitor_id': 'test-visitor',
    'page': '/test',
    'referrer': ''
}

try:
    event_id = database.insert_analytics(test_event)
    print(f'✅ Success! Event ID: {event_id}')
except Exception as e:
    print(f'❌ Error: {e}')
    import traceback
    traceback.print_exc()
"
```

### Step 2: Check Which Tracker Your Site Uses
Check your main landing page (`index.html`) to see which tracking system it's using:

```bash
cd /home/runner/the-shift-landing-page
grep -n "tracker" index.html | head -20
```

Look for:
- `tracker-firebase.js` (old system, writes to GitHub)
- `tracker-db.js` (new system, uses database)
- `tracker.js` (which one is it?)

### Step 3: Fix the Tracker

**Option A: If using old tracker (tracker-firebase.js)**
Your site is still using the old GitHub-based tracking system. You need to switch to the database tracker.

**Option B: If using new tracker (tracker-db.js)**
The database is broken. Need to fix the `database.insert_analytics()` function.

## Quick Test Commands

Run these on your Replit shell:

```bash
# 1. Check which tracker is loaded in index.html
grep -A2 -B2 'tracker.*js' /home/runner/the-shift-landing-page/index.html

# 2. Test database insertion
cd /home/runner/the-shift-landing-page
python3 -c "import database; print(database.insert_analytics({'event_type': 'test', 'timestamp': '2025-10-29T12:00:00', 'visitor_id': 'test'}))"

# 3. Check Replit error logs
cat ~/.replit/replit.log | grep -A5 "500" | tail -50
```

## Expected Outcomes

After running these commands, you'll know:
1. ✅ Whether database insertion works
2. ✅ Which tracker your site is using
3. ✅ The exact error causing 500 responses
4. ✅ Whether to fix database code or switch trackers

## Next Steps

Once you run these commands, we can:
1. Fix the database insertion error (if it's broken)
2. OR switch from old tracker to new tracker
3. Verify new data is being saved
4. Accept that Oct 28 (2PM-10PM) data is permanently lost 😔
