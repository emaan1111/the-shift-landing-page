# Replit Backend Setup for ClickFunnels Integration

## What We Created

A simple Python Flask backend that acts as a proxy between your frontend and ClickFunnels API. This solves the CORS issue.

## Files Created:

1. **`server.py`** - Flask backend that handles API calls to ClickFunnels
2. **`requirements.txt`** - Python dependencies (Flask, Flask-CORS, Requests)
3. **`.replit`** - Replit configuration to run the Python server

## How It Works:

```
Your Form → Backend (server.py) → ClickFunnels API → Success!
```

The backend runs on Replit and handles the ClickFunnels API calls server-side, avoiding CORS issues.

## Setup Instructions:

### Step 1: Install Dependencies

In Replit Shell, run:
```bash
pip install -r requirements.txt
```

### Step 2: Start the Server

In Replit, click the **"Run"** button or run:
```bash
python server.py
```

The server will start on port 5000.

### Step 3: Configure Replit to Serve Both

Replit needs to serve:
- **Backend**: Python Flask server (port 5000)
- **Frontend**: HTML files (port 8000 or your current setup)

**Option A: Use Flask to serve everything**

Update `server.py` to also serve static files:

```python
from flask import Flask, request, jsonify, send_from_directory

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/<path:path>')
def static_files(path):
    return send_from_directory('.', path)
```

Then just run: `python server.py`

**Option B: Use a reverse proxy**

Keep your current HTTP server and proxy `/api/*` requests to Flask.

## Testing:

1. Make sure Flask server is running
2. Visit your Replit URL (e.g., `https://your-repl.repl.co`)
3. Fill out the registration form
4. Check browser console for success message
5. Verify contact appears in ClickFunnels

## Endpoints:

- `POST /api/clickfunnels/contact` - Create contact in ClickFunnels
- `GET /health` - Check if backend is running

## Example Request:

```javascript
fetch('/api/clickfunnels/contact', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({
        email: 'test@example.com',
        firstName: 'Test',
        lastName: 'User',
        country: 'United States',
        city: 'New York',
        source: 'Registration Form',
        registration_date: new Date().toISOString()
    })
})
```

## Security Note:

The `server.py` file is gitignored since it contains your API key. Keep it secure!

## Troubleshooting:

### "Module not found" error
Run: `pip install -r requirements.txt`

### "Port already in use"
Stop the Python server and try again, or use a different port.

### Form still not working
1. Check browser console for errors
2. Check Flask server logs for errors
3. Verify the backend URL is correct (should be `/api/clickfunnels/contact`)

---

## Quick Start on Replit:

1. Click **"Run"** in Replit (it will install dependencies and start server)
2. Your form should now work!
3. Test by filling out the registration form
