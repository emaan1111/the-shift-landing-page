# Zoom Opt-in Testing Guide

## Issue: Zoom Opt-ins Not Being Recorded

### What I Fixed:
1. ✅ Fixed the `/api/zoom-optin` GET endpoint to return proper `{success: true, optins: []}` format
2. ✅ Verified database table exists and is correctly structured
3. ✅ Verified server endpoint logic is correct
4. ✅ Server is running on http://127.0.0.1:5001

### How to Test Zoom Opt-ins:

#### Step 1: Make Sure Server is Running
```bash
# Check if server is running
lsof -i :5001

# If not running, start it:
cd /Users/aribafarheen/the-shift-landing-page
export DATABASE_URL='postgresql://aribafarheen@localhost:5432/analytics'
export PORT=5001
python3 server.py
```

#### Step 2: Test the Zoom Opt-in Flow

1. **Open Event Dashboard**: http://127.0.0.1:5001/event-dashboard.html

2. **Click "Join Zoom Session" button**
   - A modal should popup

3. **Fill in the form**:
   - Name: Your Test Name
   - Email: test@example.com

4. **Click "Join Zoom Now"**

5. **Check browser console** (F12 or Cmd+Option+I):
   - Look for any JavaScript errors in the Console tab
   - Check the Network tab for the POST request to `/api/zoom-optin`
   - Should show Status 200 with response: `{"success": true, "id": 1}`

#### Step 3: Verify Data Was Saved

**Method 1: View in Browser**
- Go to: http://127.0.0.1:5001/view-zoom-optins.html
- You should see your test entry

**Method 2: Check Database Directly**
```bash
psql -U aribafarheen -d analytics -c "SELECT * FROM zoom_optins;"
```

**Method 3: Test API Directly**
```bash
# Test GET endpoint
curl http://127.0.0.1:5001/api/zoom-optin | python3 -m json.tool
```

### Common Issues & Solutions:

#### Issue 1: Modal doesn't open
**Cause**: JavaScript error
**Solution**: 
- Open browser console (F12)
- Look for error messages
- Make sure you're accessing via http://127.0.0.1:5001 not file://

#### Issue 2: Form submits but nothing happens
**Cause**: Server not running or network error
**Solution**:
- Check server is running: `lsof -i :5001`
- Check browser Network tab for failed requests
- Look at server terminal for error messages

#### Issue 3: "Error saving your information"
**Cause**: Server returned error
**Solution**:
- Check server terminal output for error messages
- Verify DATABASE_URL is set correctly
- Check database table exists: `\d zoom_optins` in psql

#### Issue 4: Data saves but doesn't show in viewer
**Cause**: GET endpoint issue
**Solution**:
- Test GET endpoint directly: `curl http://127.0.0.1:5001/api/zoom-optin`
- Should return: `{"success": true, "optins": [...]}`
- Hard refresh the viewer page (Cmd+Shift+R)

### Manual Database Test:

Insert a test record manually to verify table works:
```sql
psql -U aribafarheen -d analytics

INSERT INTO zoom_optins (name, email, optin_timestamp)
VALUES ('Manual Test', 'manual@test.com', NOW());

SELECT * FROM zoom_optins;
```

Then check if it appears at: http://127.0.0.1:5001/view-zoom-optins.html

### Debug Checklist:

- [ ] Server is running on port 5001
- [ ] DATABASE_URL environment variable is set
- [ ] PostgreSQL service is running (`brew services list | grep postgresql`)
- [ ] Database 'analytics' exists
- [ ] Table 'zoom_optins' exists with correct schema
- [ ] Browser console shows no JavaScript errors
- [ ] Network tab shows successful POST to `/api/zoom-optin`
- [ ] Server terminal shows no error messages
- [ ] Hard refresh browser after changes

### Watch Server Logs:

When you submit the form, watch the server terminal. You should see:
```
127.0.0.1 - - [DATE] "POST /api/zoom-optin HTTP/1.1" 200 -
```

If you see status 500 or 400, there's a server error. Check the terminal output above that line for the Python error traceback.

### Current Status:

✅ Server code is correct
✅ Database table exists
✅ Endpoint returns proper JSON format
✅ JavaScript form handler looks correct

**Next Step**: Test the actual form submission and watch:
1. Browser console for errors
2. Network tab for the API call
3. Server terminal for incoming request

The most likely issue is one of:
- Server not running when you test
- JavaScript error preventing form submission
- CORS issue (shouldn't be since we have CORS enabled)
- Browser cache showing old code

Try a hard refresh (Cmd+Shift+R) and test again!
