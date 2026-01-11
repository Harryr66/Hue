# Firebase Setup Guide

## Quick Setup

**Your Firebase Project ID:** `studio-5050280174-67f07`

### Option 1: Firebase Service Account JSON File (Required for Backend)

**You need this for the Python API server (Admin SDK)**

1. **Get your Firebase service account key**:
   - Go to [Firebase Console](https://console.firebase.google.com/project/studio-5050280174-67f07/settings/serviceaccounts/adminsdk)
   - Project Settings → Service Accounts
   - Click "Generate new private key"
   - Save the JSON file (e.g., `firebase-service-account.json`)

2. **Set environment variable**:
   ```bash
   export FIREBASE_SERVICE_ACCOUNT_PATH="/path/to/firebase-service-account.json"
   ```
   
   Or add to `.env`:
   ```
   FIREBASE_SERVICE_ACCOUNT_PATH=/path/to/firebase-service-account.json
   ```

### Option 2: Environment Variable (Alternative)

1. **Get your Firebase service account JSON** (same as above)

2. **Set as environment variable** (for serverless/cloud deployment):
   ```bash
   export FIREBASE_SERVICE_ACCOUNT='{"type":"service_account","project_id":"...","private_key_id":"...","private_key":"...","client_email":"...","client_id":"...","auth_uri":"...","token_uri":"...","auth_provider_x509_cert_url":"...","client_x509_cert_url":"..."}'
   ```

### Option 3: Google Application Credentials (GCP)

If running on Google Cloud Platform:
```bash
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/service-account-key.json"
```

## Firebase Console Setup

1. **Create a Firebase project** (if you haven't):
   - Go to [Firebase Console](https://console.firebase.google.com/)
   - Create new project or select existing

2. **Enable Firestore**:
   - Go to Firestore Database
   - Click "Create database"
   - Start in **production mode** (or test mode for development)
   - Choose location (closest to your users)

3. **Set up Firestore Security Rules** (for production):
   ```javascript
   rules_version = '2';
   service cloud.firestore {
     match /databases/{database}/documents {
       // Only allow reads/writes if authenticated (adjust as needed)
       match /conversations/{conversationId} {
         allow read, write: if request.auth != null;
       }
       match /messages/{messageId} {
         allow read, write: if request.auth != null;
       }
     }
   }
   ```

   **For development/testing**, you can use:
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
   ⚠️ **WARNING**: Test mode allows anyone to read/write. Only use for development!

4. **Get Service Account Key**:
   - Project Settings → Service Accounts
   - Click "Generate new private key"
   - Download JSON file

## Installation

1. **Install Firebase Admin SDK**:
   ```bash
   pip install firebase-admin
   ```

   Or install all requirements:
   ```bash
   pip install -r requirements.txt
   ```

2. **Add service account file to `.gitignore`** (IMPORTANT):
   ```
   firebase-service-account.json
   *.json
   !package.json
   !tsconfig.json
   ```

## Testing

1. **Start the API server**:
   ```bash
   python3 api_server.py
   ```

2. **Check Firebase Console**:
   - Go to Firestore Database
   - You should see `conversations` and `messages` collections appear when you send messages

## Firestore Collections

- **`conversations`** collection:
  - Document ID: `conversation_id`
  - Fields: `id`, `title`, `created_at`, `updated_at`

- **`messages`** collection:
  - Document ID: `message_id`
  - Fields: `id`, `conversation_id`, `role`, `content`, `created_at`

## Benefits of Firebase

✅ **Scalable**: Handles millions of documents  
✅ **Real-time**: Can add real-time listeners (optional)  
✅ **Cloud-hosted**: No database server to manage  
✅ **Free tier**: Generous free tier for development  
✅ **Auto-scaling**: Handles traffic spikes automatically  
✅ **Backups**: Built-in backup and restore  
✅ **Multi-region**: Global distribution

## Firebase Emulator (Local Development)

For local testing without using cloud:

```bash
# Install Firebase CLI
npm install -g firebase-tools

# Initialize emulator
firebase init emulators

# Start emulator
firebase emulators:start --only firestore
```

Then set environment variable:
```bash
export FIRESTORE_EMULATOR_HOST="localhost:8080"
```

## Troubleshooting

**Error: "Firebase not initialized"**
- Make sure service account path is correct
- Check that JSON file is valid
- Verify environment variable is set

**Error: "Permission denied"**
- Check Firestore security rules
- Verify service account has proper permissions
- For production, ensure rules are secure

**Error: "Project not found"**
- Verify `project_id` in service account JSON matches Firebase project
- Check that project exists in Firebase Console

## Production Checklist

- [ ] Service account key is secure (not in git)
- [ ] Firestore security rules are set (not test mode)
- [ ] Firestore is in production mode
- [ ] Appropriate indexes are created (if needed)
- [ ] Backup strategy is in place
- [ ] Monitoring/alerts are configured

