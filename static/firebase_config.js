// PETROL PARTNER — Firebase Configuration
// Public-facing keys for client SDK (safe to expose)
const firebaseConfig = {
  apiKey: "AIzaSyAW_sTKr-EXuzFswZDB-N4UyHia6jV7jh0",
  authDomain: "maharide-7a362.firebaseapp.com",
  projectId: "maharide-7a362",
  storageBucket: "maharide-7a362.firebasestorage.app",
  messagingSenderId: "466345031115",
  appId: "1:466345031115:web:f69382b296a4505057324e",
  measurementId: "G-9SLSX4G3H1"
};

// Initialize Firebase
if (!firebase.apps.length) {
    firebase.initializeApp(firebaseConfig);
}
const auth = firebase.auth();
const googleProvider = new firebase.auth.GoogleAuthProvider();
googleProvider.setCustomParameters({ prompt: 'select_account' });

console.log('⛽ Petrol Partner Firebase SDK ready');
