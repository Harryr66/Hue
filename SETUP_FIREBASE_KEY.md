# Firebase Service Account Key Setup

## Quick Steps:

1. **Save the JSON file** in your project root:
   ```
   /Users/harry/Desktop/HUE/firebase-service-account.json
   ```

2. **Add to `.env` file**:
   ```
   FIREBASE_SERVICE_ACCOUNT_PATH=/Users/harry/Desktop/HUE/firebase-service-account.json
   ```

3. **Install dependencies**:
   ```bash
   pip install firebase-admin
   ```

4. **Test it**:
   ```bash
   python3 api_server.py
   ```
   
   You should see: `✅ Using Firebase Firestore`

## File Location:

The JSON key file should be saved as:
```
firebase-service-account.json
```

In your project root directory: `/Users/harry/Desktop/HUE/`

## Security Note:

✅ The `.gitignore` is already configured to exclude this file  
✅ It won't be committed to git  
✅ Keep it secure and don't share it publicly


