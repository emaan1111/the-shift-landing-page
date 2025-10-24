# ClickFunnels 2.0 Integration Setup

## Overview
This integration automatically sends contact information to ClickFunnels 2.0 when visitors land on your pages with email parameters in the URL. Simply landing on the page with `?email=` applies the visitor tag, and clicking any CTA instantly registers the contact (adding the registration tag) and sends them to the upsell flow.
It uses the ClickFunnels **upsert** endpoint so existing contacts get updated with the latest tags rather than failing with a duplicate-email error.

## Configuration Complete ✅
- **API Key**: Configured
- **Workspace ID**: jxRdRe
- **Team ID**: JNqzOe
- **Default Registration Tag**: `List-ShiftRegistered-Nov25`
- **Visitor Tag**: `List-ShiftVisitiedNov24`

## How It Works

### Automatic Contact Creation
When someone visits your page with an email in the URL, the contact is automatically created in ClickFunnels with:

**Required:**
- Email address

**Optional:**
- First name
- Last name
- Phone number
- UTM parameters (source, medium, campaign, content)
- Geolocation (country, city)
- Referrer URL
- Source page URL

### URL Parameter Examples

```
# Basic email only
https://yoursite.com/?email=sarah@example.com

# With name
https://yoursite.com/?email=sarah@example.com&name=Sarah

# With separate first/last name
https://yoursite.com/?email=john@example.com&first_name=John&last_name=Doe

# With phone
https://yoursite.com/?email=sarah@example.com&name=Sarah&phone=+1234567890

# With UTM parameters
https://yoursite.com/?email=sarah@example.com&name=Sarah&utm_source=facebook&utm_medium=cpc&utm_campaign=shift-challenge
```

## Files Created

1. **js/clickfunnels-config.js** - Contains your API credentials (gitignored for security)
2. **js/clickfunnels-integration.js** - Integration logic
3. **CLICKFUNNELS_SETUP.md** - This file

## Data Sent to ClickFunnels

```javascript
{
  contact: {
    email: "sarah@example.com",
    first_name: "Sarah",
    last_name: "Johnson",
    phone_number: "+1234567890",
    fields: {
      source: "https://yoursite.com/?email=...",
      utm_source: "facebook",
      utm_medium: "cpc",
      utm_campaign: "shift-challenge",
      country: "United States",
      city: "New York",
      referrer: "https://google.com"
    }
  }
}
```

## Testing

### Local Testing
1. Start your local server: `python3 -m http.server 8000`
2. Visit: `http://localhost:8000/?email=test@example.com&name=TestUser`
3. Check browser console for success message: "✅ Contact sent to ClickFunnels"
4. Verify contact appears in ClickFunnels 2.0 → Contacts

### CTA Auto-Registration
- Open the landing page with an email parameter, e.g. `http://localhost:8000/?email=cta-test@example.com`
- Click any button with the CTA styling (purple "Yes, I want to join..." buttons)
- You should be redirected straight to the upsell page (`upsell.html`) and see the contact in ClickFunnels with both tags (`List-ShiftVisitiedNov24` + `List-ShiftRegistered-Nov25`). If the email already existed, it will be updated in-place via the upsert call.
- The visit tag is also applied automatically when the page loads.

### Check Browser Console
- **Success**: `✅ Successfully registered contact in ClickFunnels`
- **No Email**: `No email found in URL parameters. Skipping ClickFunnels sync.`
- **Error**: Check the error message for API issues

## Manual Triggering

You can also manually trigger the ClickFunnels sync from JavaScript:

```javascript
// Call this function anywhere in your code
window.registerInClickFunnels();
```

## Troubleshooting

### Contact Not Appearing in ClickFunnels
1. Check browser console for error messages
2. Verify API key is still valid in ClickFunnels settings
3. Ensure email parameter is present in URL
4. Check ClickFunnels API rate limits

### API Errors
- **401 Unauthorized**: API key is invalid or expired
- **403 Forbidden**: Check workspace permissions
- **422 Unprocessable**: Check email format is valid
- **429 Too Many Requests**: Rate limit exceeded, wait and retry

### CORS Issues
- Must use a local server (not file:// protocol)
- Use `python3 -m http.server 8000` for testing

## Security Notes

⚠️ **Important**: The `js/clickfunnels-config.js` file is gitignored to protect your API key.

**Before deploying to production:**
1. Never commit the config file to GitHub
2. Use environment variables or server-side API calls for production
3. Consider implementing server-side proxy for API calls

## Updating Tag IDs

If you change the tag names or create new tags in ClickFunnels, update the IDs in:

1. `js/clickfunnels-config.js`
   ```javascript
   const CLICKFUNNELS_CONFIG = {
       apiKey: 'YOUR_KEY',
       workspaceId: 'YOUR_WORKSPACE',
       teamId: 'YOUR_TEAM',
       tagIds: [/* registration tag ids */],
       visitorTagIds: [/* visitor tag ids */]
   };
   ```
2. `server.py` (search for `tagIds` and `visitorTagIds`)

Keep the arrays synchronised so the browser and backend apply the same tags.

## Custom Fields in ClickFunnels

The integration sends these fields to ClickFunnels custom fields:
- `source` - Full URL where visitor registered
- `utm_source` - UTM source parameter
- `utm_medium` - UTM medium parameter  
- `utm_campaign` - UTM campaign parameter
- `country` - Visitor's country
- `city` - Visitor's city
- `referrer` - Previous page URL

Make sure these custom fields exist in your ClickFunnels workspace, or they will be ignored.

## Adding More Fields

To add more fields to sync, edit `js/clickfunnels-integration.js`:

```javascript
// In the payload section, add your field:
fields: {
    source: contactData.source || window.location.href,
    your_custom_field: contactData.yourValue || '',
    // ... other fields
}
```

## Pages Integrated

The ClickFunnels integration is active on:
- ✅ index.html (Main landing page)
- ✅ thank-you.html (Thank you page)
- ✅ upsell.html (Upsell page)

## Support

For ClickFunnels API documentation, visit:
https://developer.myclickfunnels.com/reference/introduction
