// Firebase client-side SDK configuration
import { initializeApp, getApps, FirebaseApp } from 'firebase/app';
import { getFirestore, Firestore } from 'firebase/firestore';

const firebaseConfig = {
  apiKey: "AIzaSyDwwEKtL7A4G4bpS3XDO0iVgE7zXNfF14M",
  authDomain: "studio-5050280174-67f07.firebaseapp.com",
  projectId: "studio-5050280174-67f07",
  storageBucket: "studio-5050280174-67f07.firebasestorage.app",
  messagingSenderId: "314283798266",
  appId: "1:314283798266:web:799a75e7ea7d79bc876343"
};

// Initialize Firebase (client-side only)
let app: FirebaseApp | undefined;
let db: Firestore | undefined;

if (typeof window !== 'undefined') {
  // Only initialize on client side
  const apps = getApps();
  if (apps.length === 0) {
    app = initializeApp(firebaseConfig);
  } else {
    app = apps[0];
  }
  db = getFirestore(app);
}

export { app, db };
export default { app, db };


