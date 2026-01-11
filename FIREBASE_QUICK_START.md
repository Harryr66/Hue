# Firebase Quick Start

## Your Firebase Project

**Project ID:** `studio-5050280174-67f07`  
**Client Config:** Already configured in `ui-nextjs/src/lib/firebase.ts`

## Step 1: Enable Firestore

1. Go to [Firebase Console](https://console.firebase.google.com/project/studio-5050280174-67f07/firestore)
2. Click "Create database"
3. Choose **Production mode** (or Test mode for development)
4. Select location closest to you
5. Click "Enable"

## Step 2: Get Service Account Key (For Backend)

**This is required for the Python API server:**

1. Go to [Service Accounts](https://console.firebase.google.com/project/studio-5050280174-67f07/settings/serviceaccounts/adminsdk)
2. Click "Generate new private key"
3. Save the JSON file (e.g., `firebase-service-account.json`)
4. **IMPORTANT:** Add to `.gitignore` (already done)

## Step 3: Set Environment Variable

```bash
export FIREBASE_SERVICE_ACCOUNT_PATH="/Users/harry/Desktop/HUE/firebase-service-account.json"
```

Or add to `.env` file:
```
FIREBASE_SERVICE_ACCOUNT_PATH=/Users/harry/Desktop/HUE/firebase-service-account.json
```

## Step 4: Set Firestore Security Rules

For **development/testing** (temporary):
```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    match /{document=**} {
      allow read, write: if true;
    }
  }
}
```

For **production** (secure):
```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    match /conversations/{conversationId} {
      allow read, write: if request.auth != null;
    }
    match /messages/{messageId} {
      allow read, write: if request.auth != null;
    }
  }
}
```

## Step 5: Install Dependencies

```bash
# Backend (Python)
pip install firebase-admin

# Frontend (Next.js) - optional, for direct client access
cd ui-nextjs
npm install firebase
```

## Step 6: Test

1. Start API server:
```bash
python3 api_server.py
```

2. Check console output - should say:
```
✅ Using Firebase Firestore
```

3. Send a message through the UI - check Firebase Console to see data appear!

## Troubleshooting

**Error: "Firebase not initialized"**
- Make sure service account path is correct
- Check that JSON file exists
- Verify environment variable is set

**Error: "Permission denied"**
- Check Firestore security rules
- Make sure Firestore is enabled in Firebase Console

**Data not appearing in Firestore**
- Check Firestore Console: https://console.firebase.google.com/project/studio-5050280174-67f07/firestore
- Verify collections: `conversations` and `messages` should appear

## Collections Structure

### `conversations` Collection
- Document ID: `conversation_id` (e.g., `conv-1234567890`)
- Fields:
  - `id`: string
  - `title`: string
  - `created_at`: timestamp
  - `updated_at`: timestamp

### `messages` Collection
- Document ID: `message_id` (e.g., `msg-1234567890`)
- Fields:
  - `id`: string
  - `conversation_id`: string
  - `role`: string (`user` or `assistant`)
  - `content`: string
  - `created_at`: timestamp

## Next Steps

- Client-side Firebase SDK is already configured in `ui-nextjs/src/lib/firebase.ts`
- You can optionally add real-time listeners in the Next.js app
- Backend uses Admin SDK and handles all database operations


