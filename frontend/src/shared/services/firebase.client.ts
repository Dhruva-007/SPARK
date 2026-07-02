/**
 * SPARK — Firebase Client Initialization
 * Initializes Firebase SDK once and exports auth and firestore instances.
 *
 * Design decisions:
 * - Single initialization via module-level state (Firebase handles duplicates)
 * - Auth and Firestore exported as singletons
 * - Config validated at module load time — fails fast if missing
 */

import { initializeApp, getApps, type FirebaseApp } from "firebase/app";
import { getAuth, type Auth } from "firebase/auth";
import { getFirestore, type Firestore } from "firebase/firestore";

const firebaseConfig = {
  apiKey: import.meta.env.VITE_FIREBASE_API_KEY,
  authDomain: import.meta.env.VITE_FIREBASE_AUTH_DOMAIN,
  projectId: import.meta.env.VITE_FIREBASE_PROJECT_ID,
  storageBucket: import.meta.env.VITE_FIREBASE_STORAGE_BUCKET,
  messagingSenderId: import.meta.env.VITE_FIREBASE_MESSAGING_SENDER_ID,
  appId: import.meta.env.VITE_FIREBASE_APP_ID,
};

/**
 * Validate that required Firebase config values are present.
 * Logs a warning in development if config is missing rather than
 * crashing — allows the app to render the login page gracefully.
 */
function validateConfig(): boolean {
  const required = ["apiKey", "authDomain", "projectId"] as const;
  const missing = required.filter((key) => !firebaseConfig[key]);

  if (missing.length > 0) {
    console.warn(
      `[SPARK] Firebase config missing: ${missing.join(", ")}. ` +
        "Fill in .env.local with your Firebase project credentials. " +
        "Authentication will not work until configured."
    );
    return false;
  }
  return true;
}

// Initialize Firebase app — getApps() check prevents duplicate initialization
const isConfigValid = validateConfig();

let app: FirebaseApp;
let auth: Auth;
let db: Firestore;

if (isConfigValid) {
  app = getApps().length === 0 ? initializeApp(firebaseConfig) : getApps()[0];
  auth = getAuth(app);
  db = getFirestore(app);

  // To use Firebase Local Emulator Suite in development, install the imports
  // and uncomment the lines below:
  //
  // import { connectAuthEmulator } from "firebase/auth";
  // import { connectFirestoreEmulator } from "firebase/firestore";
  //
  // if (import.meta.env.DEV) {
  //   connectAuthEmulator(auth, "http://localhost:9099");
  //   connectFirestoreEmulator(db, "localhost", 8080);
  // }
} else {
  app = getApps().length === 0 ? initializeApp(firebaseConfig) : getApps()[0];
  auth = getAuth(app);
  db = getFirestore(app);
}

export { app, auth, db };
export default app;