# Delete API Documentation

## 🗑️ Delete Functionality

You can now delete individual registrations and analytics events using their IDs.

## API Endpoints

### Delete a Registration

**Endpoint:** `DELETE /api/registration/<id>`

**Example:**
```bash
curl -X DELETE http://127.0.0.1:3000/api/registration/5
```

**Response (Success):**
```json
{
  "success": true,
  "message": "Registration 5 deleted successfully"
}
```

**Response (Not Found):**
```json
{
  "error": "Registration not found"
}
```

---

### Delete an Analytics Event

**Endpoint:** `DELETE /api/analytics/event/<id>`

**Example:**
```bash
curl -X DELETE http://127.0.0.1:3000/api/analytics/event/100
```

**Response (Success):**
```json
{
  "success": true,
  "message": "Analytics event 100 deleted successfully"
}
```

---

### Get a Specific Registration

**Endpoint:** `GET /api/registration/<id>`

**Example:**
```bash
curl http://127.0.0.1:3000/api/registration/5
```

**Response:**
```json
{
  "id": 5,
  "email": "example@email.com",
  "first_name": "John",
  "last_name": "Doe",
  "country": "United States",
  "timestamp": "2025-10-27T10:30:00"
}
```

---

### Get a Specific Analytics Event

**Endpoint:** `GET /api/analytics/event/<id>`

**Example:**
```bash
curl http://127.0.0.1:3000/api/analytics/event/100
```

**Response:**
```json
{
  "id": 100,
  "event": "page_visit",
  "page": "/",
  "visitor_id": "visitor_123456",
  "country": "Canada",
  "timestamp": "2025-10-27T10:15:00"
}
```

---

## Using in Python

```python
import requests

BASE_URL = "http://127.0.0.1:3000"

# Get a registration
response = requests.get(f"{BASE_URL}/api/registration/5")
if response.status_code == 200:
    registration = response.json()
    print(f"Found: {registration['email']}")

# Delete a registration
response = requests.delete(f"{BASE_URL}/api/registration/5")
if response.status_code == 200:
    print("✅ Deleted successfully!")
elif response.status_code == 404:
    print("❌ Not found")

# Get an analytics event
response = requests.get(f"{BASE_URL}/api/analytics/event/100")
if response.status_code == 200:
    event = response.json()
    print(f"Event: {event['event']} on {event['page']}")

# Delete an analytics event
response = requests.delete(f"{BASE_URL}/api/analytics/event/100")
if response.status_code == 200:
    print("✅ Deleted successfully!")
```

---

## Using in JavaScript/Frontend

```javascript
// Get a registration
fetch('http://127.0.0.1:3000/api/registration/5')
  .then(response => response.json())
  .then(data => console.log('Registration:', data));

// Delete a registration
fetch('http://127.0.0.1:3000/api/registration/5', {
  method: 'DELETE'
})
  .then(response => response.json())
  .then(data => {
    if (data.success) {
      console.log('✅ Deleted:', data.message);
    }
  });

// Get an analytics event
fetch('http://127.0.0.1:3000/api/analytics/event/100')
  .then(response => response.json())
  .then(data => console.log('Event:', data));

// Delete an analytics event
fetch('http://127.0.0.1:3000/api/analytics/event/100', {
  method: 'DELETE'
})
  .then(response => response.json())
  .then(data => {
    if (data.success) {
      console.log('✅ Deleted:', data.message);
    }
  });
```

---

## Finding IDs

### To find registration IDs:

1. **View all registrations:**
   ```bash
   curl http://127.0.0.1:3000/api/registrations
   ```

2. **Using Python:**
   ```python
   from database import get_all_registrations
   regs = get_all_registrations(limit=10)
   for reg in regs:
       print(f"ID: {reg['id']}, Email: {reg['email']}")
   ```

3. **View on registrations page:**
   - Open: http://127.0.0.1:3000/registrations.html
   - The ID is shown in the table

### To find analytics event IDs:

1. **View all events:**
   ```bash
   curl http://127.0.0.1:3000/api/analytics/events?limit=10
   ```

2. **Using Python:**
   ```python
   from database import get_all_analytics
   events = get_all_analytics(limit=10)
   for event in events:
       print(f"ID: {event['id']}, Event: {event['event']}, Page: {event['page']}")
   ```

---

## Complete API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/registrations` | Get all registrations |
| GET | `/api/registration/<id>` | Get specific registration |
| DELETE | `/api/registration/<id>` | Delete specific registration |
| GET | `/api/analytics/events` | Get all analytics events |
| GET | `/api/analytics/event/<id>` | Get specific event |
| DELETE | `/api/analytics/event/<id>` | Delete specific event |
| GET | `/api/analytics/stats` | Get statistics |
| POST | `/api/analytics/track` | Track new event |
| POST | `/api/analytics/registration` | Track new registration |

---

## Important Notes

⚠️ **Deletion is permanent!** There's no undo.

✅ **Best practice:** Always backup your database before bulk deletions:
```bash
cp analytics.db analytics.db.backup
```

✅ **Test first:** Use GET to verify you have the right ID before DELETE
