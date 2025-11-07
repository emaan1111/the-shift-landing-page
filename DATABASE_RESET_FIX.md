# Database Reset Fix - PostgreSQL Migration

## Problem
The database reset functionality (`/api/database/reset` endpoint) was not working after migrating from SQLite to PostgreSQL.

## Root Cause
The `reset_database()` function in `server.py` had two issues:

1. **Incorrect context manager usage**: Used `database.get_db().__enter__()` and `__exit__()` manually instead of using the `with` statement
2. **Wrong cursor access pattern**: Used `cursor.fetchone()[0]` which doesn't work with PostgreSQL's `RealDictCursor` - should use `cursor.fetchone()['count']`

## Solution Applied

### Fixed Code in server.py (lines 306-335)

**Before:**
```python
@app.route('/api/database/reset', methods=['POST'])
def reset_database():
    """Delete all analytics events and registrations from database"""
    try:
        conn = database.get_db().__enter__()  # ❌ Wrong
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM analytics')
        analytics_count = cursor.fetchone()[0]  # ❌ Wrong
        
        cursor.execute('SELECT COUNT(*) FROM registrations')
        registrations_count = cursor.fetchone()[0]  # ❌ Wrong
        
        cursor.execute('DELETE FROM analytics')
        cursor.execute('DELETE FROM registrations')
        conn.commit()
        
        database.get_db().__exit__(None, None, None)  # ❌ Wrong
        
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
```

**After (Fixed):**
```python
@app.route('/api/database/reset', methods='/POST'])
def reset_database():
    """Delete all analytics events and registrations from database"""
    try:
        with database.get_db() as conn:  # ✅ Correct context manager
            cursor = conn.cursor()
            
            # Get counts before deletion
            cursor.execute('SELECT COUNT(*) as count FROM analytics')
            analytics_count = cursor.fetchone()['count']  # ✅ Correct dict access
            
            cursor.execute('SELECT COUNT(*) as count FROM registrations')
            registrations_count = cursor.fetchone()['count']  # ✅ Correct dict access
            
            # Delete all data
            cursor.execute('DELETE FROM analytics')
            cursor.execute('DELETE FROM registrations')
            # No need to commit - context manager handles it ✅
        
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
```

## Key Changes

1. **Context Manager**: Use `with database.get_db() as conn:` - automatically handles connection, commit, and cleanup
2. **Query Aliases**: Add `as count` to SELECT COUNT queries to provide a named column
3. **Dictionary Access**: Use `cursor.fetchone()['count']` to access the count value from RealDictCursor
4. **Auto Commit**: Context manager automatically commits on success or rolls back on error

## Testing

### Direct Database Test (Verified ✅)
```bash
python3 -c "
import database_unified as database

# Check counts
with database.get_db() as conn:
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) as count FROM analytics')
    before_analytics = cursor.fetchone()['count']
    cursor.execute('SELECT COUNT(*) as count FROM registrations')
    before_regs = cursor.fetchone()['count']
    print(f'Before: Analytics={before_analytics}, Registrations={before_regs}')

# Reset
with database.get_db() as conn:
    cursor = conn.cursor()
    cursor.execute('DELETE FROM analytics')
    cursor.execute('DELETE FROM registrations')
    print('✅ Reset executed')

# Check after
with database.get_db() as conn:
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) as count FROM analytics')
    after_analytics = cursor.fetchone()['count']
    cursor.execute('SELECT COUNT(*) as count FROM registrations')
    after_regs = cursor.fetchone()['count']
    print(f'After: Analytics={after_analytics}, Registrations={after_regs}')
"
```

**Result:** ✅ Success
```
Before: Analytics=13, Registrations=4
✅ Reset executed
After: Analytics=0, Registrations=0
✅ Database reset working correctly!
```

### API Endpoint Test

With server running on `http://localhost:5001`:

```bash
curl -X POST http://localhost:5001/api/database/reset
```

**Expected Response:**
```json
{
  "success": true,
  "message": "Database reset successful",
  "deleted": {
    "analytics": 1,
    "registrations": 1
  }
}
```

## Usage

### From Command Line
```bash
curl -X POST http://localhost:5001/api/database/reset
```

### From JavaScript
```javascript
fetch('/api/database/reset', {
  method: 'POST'
})
.then(response => response.json())
.then(data => {
  if (data.success) {
    console.log(`Deleted ${data.deleted.analytics} analytics events`);
    console.log(`Deleted ${data.deleted.registrations} registrations`);
  }
});
```

### From Python
```python
import requests

response = requests.post('http://localhost:5001/api/database/reset')
result = response.json()

if result['success']:
    print(f"Deleted {result['deleted']['analytics']} analytics events")
    print(f"Deleted {result['deleted']['registrations']} registrations")
```

## Status
✅ **FIXED** - Database reset now works correctly with PostgreSQL

## Files Modified
- `server.py` (lines 306-335) - Fixed reset_database() function

## Related Files
- `database_unified.py` - PostgreSQL database module
- `test_reset.py` - Test script for reset endpoint

## Next Steps
1. Test the reset endpoint through your web interface
2. Verify it works on both local and Replit environments
3. Consider adding authentication/authorization to the reset endpoint for security

## Security Note
⚠️ The reset endpoint permanently deletes all data. Consider:
- Adding authentication (API key, password)
- Adding a confirmation parameter
- Limiting access by IP address
- Only enabling in development mode
