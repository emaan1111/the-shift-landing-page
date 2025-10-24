# The Shift Landing Page

## Overview
A beautiful and responsive landing page for "The Shift" - a 3-day Islamic parenting challenge for Muslim mothers. The project helps mothers transform their children's relationship with Islam.

## Project Type
Full-stack web application with Flask backend and vanilla JavaScript frontend

## Architecture
- **Frontend**: Pure HTML5, CSS3, and vanilla JavaScript
- **Backend**: Flask (Python) server with ClickFunnels API integration
- **API Integration**: ClickFunnels contact management
- **No build process**: Ready to serve as-is

## Files
- `server.py` - Flask backend server with API endpoints
- `index.html` - Main landing page with registration form
- `thank-you.html` - Thank you/confirmation page
- `requirements.txt` - Python dependencies
- `README.md` - Project documentation

## Technologies
- **Backend**: Flask, Flask-CORS, Requests
- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **External APIs**: ClickFunnels API v2
- **Fonts**: Google Fonts (Playfair Display & Poppins)

## Running Locally
The site is served using Flask on port 5000. The Flask server handles both static file serving and API endpoints.

## Recent Changes
- **2025-10-24**: Added Flask backend with ClickFunnels integration
  - Created server.py with Flask backend
  - Installed Flask, flask-cors, and requests packages
  - Added ClickFunnels API integration for contact management
  - Updated workflow to run Flask server
  - Added Python-specific .gitignore entries
- **2025-10-23**: Imported from GitHub and configured for Replit environment
  - Added .gitignore for Replit-specific files
  - Created replit.md for project documentation
  - Configured workflow to serve on port 5000
  - Set up deployment configuration

## Deployment
Configured for Replit Autoscale deployment using Gunicorn (production-ready WSGI server).

### Production Setup
- **Server**: Gunicorn with 4 workers
- **Port**: 5000
- **Entry point**: server:app
- **Auto-installs**: Gunicorn via build command

The deployment is production-ready and will handle the ClickFunnels API integration securely.
