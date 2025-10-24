# GitHub-Based Visitor Tracker Setup Guide

## What You're Getting

✅ Visitor data stored in your GitHub repository as JSON files  
✅ Beautiful analytics dashboard page at `/analytics.html`  
✅ Tracks page visits, button clicks, referrers, and more  
✅ No third-party services needed  
✅ Completely free forever  

## Step 1: Create a GitHub Personal Access Token

1. Go to **GitHub.com** → Click your profile picture (top right) → **Settings**
2. Scroll down and click **Developer settings** (bottom of left sidebar)
3. Click **Personal access tokens** → **Tokens (classic)**
4. Click **Generate new token** → **Generate new token (classic)**
5. Add a note: "The Shift Analytics Tracker"
6. Set expiration: **No expiration** (or choose your preference)
7. Select these permissions:
   - ✅ **repo** (full repo access - check the top box)
8. Scroll down and click **Generate token**
9. **IMPORTANT:** Copy the token immediately (starts with `ghp_...`)  
   ⚠️ You won't be able to see it again!

## Step 2: Add Token to Your Config File

⚠️ **IMPORTANT:** Never commit your token to GitHub! We've set up a secure config file.

1. Open the file **`js/analytics-config.js`**
2. Find this line:
   ```javascript
   token: 'YOUR_GITHUB_TOKEN',
   ```
3. Replace `YOUR_GITHUB_TOKEN` with your actual token:
   ```javascript
   token: 'ghp_your_actual_token_here',
   ```
4. **Save the file** - This file is in `.gitignore` so it won't be pushed to GitHub

✅ That's it! The token is now configured and secure.

## Step 3: Push to GitHub

Run these commands in your terminal:

```bash
git add .
git commit -m "Add GitHub analytics tracking"
git push
```

## Step 4: Test It!

1. **Visit your landing page** - Open `index.html` in your browser
2. **Click some buttons** - Try the "Register Now" button
3. **Check your GitHub repo** - Go to your repo and look in the `analytics/` folder
4. **You should see a new file** like `visits-2025-10-24.json`
5. **View your dashboard** - Open `analytics.html` in your browser

## Step 5: View Your Analytics

Simply open **`analytics.html`** in your browser to see:

📊 **Dashboard Features:**
- Total visits and unique visitors
- Button click tracking
- Traffic sources (where visitors came from)
- Page view statistics
- Recent activity log
- Beautiful charts and graphs

## What Gets Tracked

- ✅ Every page visit (index.html, thank-you.html, upsell.html)
- ✅ Button clicks ("Register Now", "Join", "Add to Calendar", etc.)
- ✅ Traffic sources (where visitors came from)
- ✅ Device info (screen size, language)
- ✅ Timestamps for all events

## How It Works

1. When someone visits your page, `tracker.js` runs
2. It creates/updates a JSON file in the `analytics/` folder on GitHub
3. Each day gets its own file (e.g., `visits-2025-10-24.json`)
4. The dashboard reads all the JSON files and displays beautiful stats

## Important Notes

⚠️ **Keep Your Token Safe:**
- Don't share your token publicly
- If you accidentally expose it, delete it and create a new one

📈 **Data Storage:**
- Each day's data is stored in a separate JSON file
- Files are named like: `visits-YYYY-MM-DD.json`
- Data is stored in your GitHub repo (free forever!)

🔒 **Privacy:**
- ✅ Does NOT use cookies
- ✅ Does NOT track personal information
- ✅ Only tracks anonymous usage data
- ✅ Data stored in YOUR private GitHub repo

## Troubleshooting

**If tracking doesn't work:**
1. Make sure you added your token to both files
2. Check that the `analytics/` folder exists in your GitHub repo
3. Make sure you pushed your changes to GitHub
4. Open browser console (F12) to see any errors

**If dashboard shows no data:**
1. Make sure you've visited your landing page first
2. Check that the `analytics/` folder has JSON files
3. Verify your token is correct in `analytics.html`
4. Wait a few seconds and refresh the dashboard

## Need Help?

If you run into issues, check:
- Browser console (F12) for error messages
- GitHub repo's `analytics/` folder for data files
- Make sure your token has the correct permissions
