# Petrol Partner — Non-Profit Carpooling for India 🇮🇳

India's first legally compliant, non-profit carpooling platform. Share rides, split fuel costs, and travel safe with triple-verified co-travellers.

## Features

- **Legal-Guard™ Price Engine** — Auto-caps ride cost at fuel + tolls. White-plate vehicles stay legal.
- **Pink Mode + SOS Shield** — Women-only rides. One-tap SOS sends GPS to 3 emergency contacts.
- **Triple Verification** — Aadhaar face-match + Corporate email + LinkedIn profile sync.
- **Smart Meeting Hubs** — AI-suggested pickup at Metro stations, toll plazas, bus stands.
- **UPI-First Splitting** — Instant GPay/PhonePe deep-links upon trip completion.

## Tech Stack

- **Backend:** Python Flask + Firebase Admin SDK
- **Frontend:** HTML5, Tailwind CSS v3 (CDN), Vanilla JS
- **Database:** Google Firestore
- **Auth:** Firebase Authentication (Google + Email)

## Setup

1. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Firebase Setup:**
   - Create a Firebase project with Firestore + Authentication enabled
   - Download service account key → `serviceAccountKey.json`
   - Enable Google Sign-In in Firebase Auth
   - Update `static/firebase_config.js` with your web app config

3. **Environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your secret key
   ```

4. **Run:**
   ```bash
   python app.py
   ```
   Open `http://localhost:5000`

## Routes

| Page | URL | Description |
|------|-----|-------------|
| Home | `/` | Landing page with search |
| Login | `/login` | Google + Email auth |
| Dashboard | `/dashboard` | Rides, bookings, settings |
| Post Ride | `/post-ride` | Multi-step ride creation |
| Search | `/search` | Find rides with filters |
| Live Trip | `/live-trip/<id>` | Trip view + SOS + UPI |
| Verify | `/verify` | Triple verification hub |

## Legal Disclaimer

Petrol Partner is a **Non-Profit Social Initiative**. Ride prices are capped at actual fuel + toll costs. This is NOT a commercial transport service.
