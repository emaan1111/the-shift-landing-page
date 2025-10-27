# Referral Tracking System

## Overview
The referral tracking system allows registered users to share a personalized referral link. When someone registers through their link, the system tracks who referred them.

## How It Works

### 1. User Registers
- User fills out the registration form on `index.html`
- Registration is saved to the database with a unique ID (e.g., ID: 123)
- The registration ID is stored in `localStorage` as `registrationId`

### 2. Referral Link Generation
- On the thank-you page, share buttons are automatically updated with the referral link
- **Referral Link Format**: `https://yoursite.com/?ref=123`
  - `ref` parameter contains the registration ID of the referrer

### 3. Referred User Visits
- When someone clicks a referral link (e.g., `/?ref=123`), they land on the index page
- The tracker (`tracker-db.js`) automatically captures the `ref` parameter
- All page visits and button clicks are tracked with `referred_by=123`

### 4. Referred User Registers
- When the referred user registers, their registration includes `referred_by=123`
- This creates a trackable relationship in the database

## Database Schema

### `registrations` Table
```sql
- id (INTEGER PRIMARY KEY) - Unique registration ID
- email, first_name, last_name, etc.
- referred_by (INTEGER) - ID of the user who referred them
```

### `analytics` Table  
```sql
- id (INTEGER PRIMARY KEY) - Event ID
- event, page, timestamp, etc.
- referred_by (INTEGER) - ID of the user whose link was used
```

## Implementation Details

### Files Modified

1. **database.py**
   - Added `referred_by` column to both tables
   - Updated `insert_analytics()` and `insert_registration()` to handle referral data

2. **add_referral_tracking.py**
   - Migration script to add referral columns (already run)

3. **tracker-db.js**
   - Captures `ref` parameter from URL
   - Includes `referredBy` in all tracking calls

4. **index.html**
   - Captures `ref` from URL when form is submitted
   - Passes `referredBy` to `trackRegistration()`
   - Stores registration ID in `localStorage` for share links

5. **thank-you.html**
   - `updateShareLinks()` function generates personalized referral links
   - Updates WhatsApp, Facebook, and Email share buttons
   - Uses registration ID from `localStorage`

## Share Button URLs

### WhatsApp
```
https://wa.me/?text=I%20just%20registered...%20https://yoursite.com/?ref=123
```

### Facebook
```
https://www.facebook.com/sharer/sharer.php?u=https://yoursite.com/?ref=123
```

### Email
```
mailto:?subject=...&body=...Register%20here:%20https://yoursite.com/?ref=123
```

## Tracking Referrals in Analytics Dashboard

### Query Registrations by Referrer
```sql
SELECT * FROM registrations WHERE referred_by = 123;
```

### Count Referrals per User
```sql
SELECT referred_by, COUNT(*) as referral_count 
FROM registrations 
WHERE referred_by IS NOT NULL 
GROUP BY referred_by 
ORDER BY referral_count DESC;
```

### Track Page Visits via Referral Links
```sql
SELECT * FROM analytics WHERE referred_by = 123;
```

## Example Flow

1. **Sarah registers** → Gets Registration ID: 123
2. **Sarah shares** WhatsApp link: `https://yoursite.com/?ref=123`
3. **Fatima clicks** Sarah's link
   - Visit tracked with `referred_by=123`
4. **Fatima registers** → Her registration includes `referred_by=123`
5. **Dashboard shows**: Sarah has 1 referral (Fatima)

## Benefits

✅ **Track Viral Growth** - See which users are most effective at sharing
✅ **Reward Referrers** - Identify top referrers for rewards/recognition  
✅ **Attribution** - Know where each registration came from
✅ **Marketing Insights** - Understand which channels drive referrals
✅ **Engagement Metrics** - See which users are most engaged (sharing)

## Future Enhancements

- Add referral leaderboard on analytics dashboard
- Send thank-you emails to users who get referrals
- Create referral rewards/incentives program
- Show users their own referral stats
- Track conversion rate per referrer
