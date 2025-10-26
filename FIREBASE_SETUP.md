# Firebase Setup Guide

This guide walks you through setting up Firebase for your landing page analytics.

## Step 1: Create a Firebase Project

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Click **"Add project"**
3. Enter project name: `the-shift-landing-page` (or your preferred name)
4. Follow the setup wizard (you can disable Google Analytics for now)
5. Create the project

## Step 2: Set Up Firestore Database

1. In Firebase Console, go to **"Build" → "Firestore Database"**
2. Click **"Create database"**
3. Select region: **`us-central1`** (or closest to your users)
4. Start in **Test mode** (we'll secure it later)
5. Click **"Create"**

## Step 3: Get Your Firebase Config

1. In Firebase Console, click the **Settings icon** (⚙️) → **Project settings**
2. Scroll to **"Your apps"** section
3. Click **"Add app"** → Select **Web** (</>)
4. Register app with name: `the-shift-landing-page`
5. Copy the Firebase config object

Your config will look like:
```javascript
const firebaseConfig = {
  apiKey: "YOUR_API_KEY",
  authDomain: "your-project.firebaseapp.com",
  projectId: "your-project-id",
  storageBucket: "your-project.appspot.com",
  messagingSenderId: "123456789",
  appId: "1:123456789:web:abcdef123456"
};
```

## Step 4: Create Firebase Config File

Create `js/firebase-config.js` with your config (see template below)

## Step 5: Set Up Firestore Security Rules

Replace your Firestore Security Rules with:

```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // Allow reads from the frontend app
    match /analytics/{document=**} {
      allow read: if true;
      allow write: if request.auth != null;
    }
    match /registrations/{document=**} {
      allow read: if true;
      allow write: if true;
    }
  }
}
```

This allows:
- Public read access (for your analytics)
- Anyone can write registration data (no auth needed)
- Authenticated writes for admin functions

## Step 6: Update Your Code

1. Replace `tracker.js` with the new Firebase version
2. Update `index.html` to load Firebase SDK
3. Test tracking by visiting the page

## Step 7: View Data in Firebase Console

1. Go to Firestore → Collections
2. You should see `analytics` and `registrations` collections populating
3. Click on documents to see individual event data

## Step 8: Python Analysis (Optional)

To analyze data from Python:
```bash
pip install firebase-admin
python analyze-hook-ab-test.py
```

This will connect directly to Firebase and generate reports.

## Troubleshooting

**Q: Data not saving?**
- Check browser console for errors
- Verify Firebase config is correct
- Check Firestore security rules

**Q: Can't read data from Python?**
- Download service account key from Firebase Console
- Place in project root as `firebase-key.json`
- Update Python script with correct path

**Q: Want to make database private later?**
- Add authentication rules to restrict access
- Only allow writes from your domain

