// PETROL PARTNER — Firebase Configuration
// Public-facing keys for client SDK (safe to expose)
const firebaseConfig = {
    apiKey: "AIzaSyAhd3rBNzZyu-i0pTbJ3OntQTCwooThu4Q",
    authDomain: "petrolpartner-e3a04.firebaseapp.com",
    projectId: "petrolpartner-e3a04",
    storageBucket: "petrolpartner-e3a04.firebasestorage.app",
    messagingSenderId: "742650115372",
    appId: "1:742650115372:web:b838b1f1a275f79a966889",
    measurementId: "G-B6QNZX9B22"
  };

// Initialize Firebase
if (!firebase.apps.length) {
    firebase.initializeApp(firebaseConfig);
}
const auth = firebase.auth();
const googleProvider = new firebase.auth.GoogleAuthProvider();
googleProvider.setCustomParameters({ prompt: 'select_account' });

console.log('⛽ Petrol Partner Firebase SDK ready');
