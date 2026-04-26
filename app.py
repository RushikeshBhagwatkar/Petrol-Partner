"""
Petrol Partner — Main Flask Application
Production-grade carpooling backend for the 2026 Indian market.
Uses Firebase Admin SDK + Firestore for auth and data.
"""
import os
import uuid
from datetime import datetime
from functools import wraps

from flask import (
    Flask, render_template, request, jsonify,
    session, redirect, url_for, abort
)
from flask_wtf.csrf import CSRFProtect
import firebase_admin
from firebase_admin import credentials, auth, firestore
from dotenv import load_dotenv

from config import Config, SUPPORTED_CITIES, MEETING_HUBS, ROUTE_DISTANCES
from price_engine import (
    calculate_legal_price_per_seat,
    get_route_info,
    validate_price,
    get_fuel_price,
    get_default_mileage,
)

load_dotenv()

# ── Flask App ──────────────────────────────────────────────
app = Flask(__name__)
app.config.from_object(Config)
csrf = CSRFProtect(app)

# ── Firebase Init ──────────────────────────────────────────
firebase_cred_path = Config.FIREBASE_SERVICE_ACCOUNT_JSON
if os.path.exists(firebase_cred_path):
    cred = credentials.Certificate(firebase_cred_path)
    firebase_admin.initialize_app(cred)
    db = firestore.client()
    print("[OK] Firebase & Firestore connected.")
else:
    print("[WARN] Firebase service account key not found. Firestore will not work.")
    db = None

# ── Jinja Context ──────────────────────────────────────────
@app.context_processor
def inject_globals():
    """Inject global variables into all templates."""
    return {
        'cities': SUPPORTED_CITIES,
        'hubs': MEETING_HUBS,
        'current_year': datetime.now().year,
        'app_name': 'Petrol Partner',
    }

# ── Auth Decorator ─────────────────────────────────────────
def login_required(f):
    """Redirect to login or return 401 for API if user is not authenticated."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            if request.path.startswith('/api/'):
                return jsonify({'status': 'error', 'message': 'Please login first'}), 401
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


# ═══════════════════════════════════════════════════════════
#  PAGE ROUTES
# ═══════════════════════════════════════════════════════════

@app.route('/')
def index():
    """Landing page with search bar and popular routes."""
    return render_template('index.html', title='Petrol Partner — Non-Profit Carpooling India')


@app.route('/login')
def login():
    """Authentication page."""
    if 'user' in session:
        return redirect(url_for('dashboard'))
    return render_template('login.html', title='Login — Petrol Partner')


@app.route('/dashboard')
@login_required
def dashboard():
    """User dashboard with bookings, rides, and verification status."""
    user_uid = session['user']['uid']
    bookings = []
    my_rides = []
    user_profile = {}

    if db:
        # Get user profile
        user_doc = db.collection('users').document(user_uid).get()
        if user_doc.exists:
            user_profile = user_doc.to_dict()

        # Get bookings as passenger
        booking_docs = db.collection('bookings').where(
            filter=firestore.FieldFilter('passenger_id', '==', user_uid)
        ).limit(20).stream()
        for doc in booking_docs:
            b = doc.to_dict()
            b['id'] = doc.id
            ride_doc = db.collection('rides').document(b.get('ride_id', '')).get()
            if ride_doc.exists:
                b['ride'] = ride_doc.to_dict()
            bookings.append(b)

        # Get rides offered as driver
        ride_docs = db.collection('rides').where(
            filter=firestore.FieldFilter('driver_id', '==', user_uid)
        ).limit(20).stream()
        for doc in ride_docs:
            r = doc.to_dict()
            r['id'] = doc.id
            my_rides.append(r)

        # Get booking requests for driver to approve
        requests_docs = db.collection('bookings').where(
            filter=firestore.FieldFilter('driver_id', '==', user_uid)
        ).where(
            filter=firestore.FieldFilter('status', '==', 'pending')
        ).limit(20).stream()
        booking_requests = []
        for doc in requests_docs:
            req = doc.to_dict()
            req['id'] = doc.id
            booking_requests.append(req)

    return render_template(
        'dashboard.html',
        title='Dashboard — Petrol Partner',
        bookings=bookings,
        my_rides=my_rides,
        booking_requests=booking_requests,
        profile=user_profile,
    )

@app.route('/api/admin/verify-user/<user_uid>', methods=['POST'])
@csrf.exempt
def admin_verify_user(user_uid):
    """Simulate Admin/Govt API verification of a user's identity."""
    if not db: return jsonify({'status': 'error'}), 500
    try:
        db.collection('users').document(user_uid).update({
            'aadhaar_status': 'verified',
            'verification_level': firestore.Increment(1),
            'is_verified': True
        })
        return jsonify({'status': 'success', 'message': 'User verified by Admin.'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/ride/verify-passenger/<booking_id>')
@login_required
def secure_passenger_viewer(booking_id):
    """Secure viewer for the driver to verify passenger ID at pickup."""
    if not db: abort(500)
    
    booking_doc = db.collection('bookings').document(booking_id).get()
    if not booking_doc.exists: abort(404)
    booking = booking_doc.to_dict()
    
    # Check if current user is the driver
    if booking.get('driver_id') != session['user']['uid']:
        abort(403)
        
    ride_doc = db.collection('rides').document(booking.get('ride_id')).get()
    ride = ride_doc.to_dict()
    
    # Check if ride status is 'arrived' (industry safety standard)
    # For demo, we'll allow it if status is 'scheduled' or 'arrived'
    if ride.get('status', 'scheduled') not in ['arrived', 'started']:
        return "Verification only available once you've arrived at pickup point.", 403

    # Generate a 'signed URL' for the passenger's ID (simulation)
    # In production, use firebase_admin.storage.bucket().blob().generate_signed_url()
    passenger_doc = db.collection('users').document(booking.get('passenger_id')).get()
    passenger_profile = passenger_doc.to_dict()
    
    # Mock document URL - in production this is a signed URL to a private bucket
    id_doc_url = "https://images.unsplash.com/photo-1557053910-d9eaba703fc9?q=80&w=500" 
    
    return render_template(
        'secure_viewer.html',
        booking=booking,
        passenger=passenger_profile,
        id_doc_url=id_doc_url,
        driver_ip=request.remote_addr
    )

@app.route('/api/ride/<ride_id>/status', methods=['POST'])
@csrf.exempt
@login_required
def update_ride_status(ride_id):
    """Update ride status (Arrived, Started, Completed)."""
    if not db: return jsonify({'status': 'error'}), 500
    data = request.json or {}
    new_status = data.get('status')
    
    ride_ref = db.collection('rides').document(ride_id)
    ride = ride_ref.get().to_dict()
    
    if ride.get('driver_id') != session['user']['uid']:
        return jsonify({'status': 'error', 'message': 'Unauthorized'}), 403
        
    ride_ref.update({'status': new_status})
    return jsonify({'status': 'success', 'new_status': new_status})


@app.route('/post-ride')
@login_required
def post_ride():
    """Multi-step ride posting form."""
    return render_template('post_ride.html', title='Post a Ride — Petrol Partner')


@app.route('/search')
def search_rides_page():
    """Search results page."""
    from_city = request.args.get('from', '')
    to_city = request.args.get('to', '')
    date = request.args.get('date', '')
    pink_mode = request.args.get('pink_mode', '') == 'on'

    rides = []
    if db and from_city and to_city:
        query = db.collection('rides').where(
            filter=firestore.FieldFilter('from_city', '==', from_city)
        ).where(
            filter=firestore.FieldFilter('to_city', '==', to_city)
        ).where(
            filter=firestore.FieldFilter('status', '==', 'active')
        )

        if date:
            query = query.where(filter=firestore.FieldFilter('date', '==', date))

        if pink_mode:
            query = query.where(filter=firestore.FieldFilter('is_pink_mode', '==', True))

        docs = query.stream()
        for doc in docs:
            ride = doc.to_dict()
            ride['id'] = doc.id
            # Only show rides with available seats
            if ride.get('seats_left', 0) > 0:
                rides.append(ride)

    return render_template(
        'search_results.html',
        title=f'{from_city} to {to_city} — Petrol Partner' if from_city else 'Search Rides',
        rides=rides,
        from_city=from_city,
        to_city=to_city,
        date=date,
        pink_mode=pink_mode,
    )


@app.route('/live-trip/<ride_id>')
@login_required
def live_trip(ride_id):
    """Live trip view with SOS and payment."""
    ride = {}
    booking = {}
    passenger_bookings = []
    is_driver = False
    if db:
        ride_doc = db.collection('rides').document(ride_id).get()
        if ride_doc.exists:
            ride = ride_doc.to_dict()
            ride['id'] = ride_doc.id
            is_driver = (ride.get('driver_id') == session['user']['uid'])
            
            # Fetch driver profile for UPI ID
            driver_doc = db.collection('users').document(ride.get('driver_id', '')).get()
            if driver_doc.exists:
                ride['driver_profile'] = driver_doc.to_dict()

            if is_driver:
                # Driver sees all confirmed/arrived bookings
                docs = db.collection('bookings').where(
                    filter=firestore.FieldFilter('ride_id', '==', ride_id)
                ).where(
                    filter=firestore.FieldFilter('status', '==', 'confirmed')
                ).stream()
                for doc in docs:
                    b = doc.to_dict()
                    b['id'] = doc.id
                    passenger_bookings.append(b)
            else:
                # Passenger sees their own booking
                user_uid = session['user']['uid']
                docs = db.collection('bookings').where(
                    filter=firestore.FieldFilter('ride_id', '==', ride_id)
                ).where(
                    filter=firestore.FieldFilter('passenger_id', '==', user_uid)
                ).limit(1).stream()
                for doc in docs:
                    booking = doc.to_dict()
                    booking['id'] = doc.id

    return render_template(
        'live_trip.html',
        title='Live Trip — Petrol Partner',
        ride=ride,
        booking=booking,
        passenger_bookings=passenger_bookings,
        is_driver=is_driver
    )


@app.route('/verify')
@login_required
def verify():
    """Triple-Verification Hub page."""
    user_profile = {}
    if db:
        user_doc = db.collection('users').document(session['user']['uid']).get()
        if user_doc.exists:
            user_profile = user_doc.to_dict()

    return render_template(
        'verify.html',
        title='Verify Your Identity — Petrol Partner',
        profile=user_profile,
    )


@app.route('/logout')
def logout():
    """Clear session and redirect to home."""
    session.clear()
    return redirect(url_for('index'))


# ═══════════════════════════════════════════════════════════
#  API ROUTES
# ═══════════════════════════════════════════════════════════

@app.route('/api/auth/verify-token', methods=['POST'])
@csrf.exempt
def verify_token():
    """Verify Firebase ID token and create session."""
    id_token = request.json.get('idToken')
    if not id_token:
        return jsonify({'status': 'error', 'message': 'Missing token'}), 400

    try:
        decoded_token = auth.verify_id_token(id_token)
        uid = decoded_token['uid']

        user_info = {
            'uid': uid,
            'name': decoded_token.get('name', 'Anonymous'),
            'email': decoded_token.get('email', ''),
            'photo_url': decoded_token.get('picture', ''),
        }
        session['user'] = user_info
        session.permanent = True

        # Upsert user profile in Firestore
        if db:
            user_ref = db.collection('users').document(uid)
            if not user_ref.get().exists:
                user_ref.set({
                    'uid': uid,
                    'full_name': user_info['name'],
                    'email': user_info['email'],
                    'photo_url': user_info['photo_url'],
                    'gender': '',
                    'phone': '',
                    'aadhaar_status': 'pending',
                    'linkedin_url': '',
                    'corp_email': '',
                    'corp_email_verified': False,
                    'rating': 5.0,
                    'total_rides': 0,
                    'vehicle_details': {},
                    'upi_id': '',
                    'emergency_contacts': [],
                    'is_verified': False,
                    'verification_level': 0,
                    'created_at': firestore.SERVER_TIMESTAMP,
                })

        return jsonify({'status': 'success', 'user': user_info})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 401


# ── Ride Management ────────────────────────────────────────

@app.route('/api/post-ride', methods=['POST'])
@csrf.exempt
@login_required
def api_post_ride():
    """Create a new ride with Legal-Guard pricing."""
    if not db:
        return jsonify({'status': 'error', 'message': 'Database not connected'}), 500

    data = request.json
    try:
        from_city = data['from_city']
        to_city = data['to_city']
        seats = int(data.get('total_seats', 3))
        fuel_type = data.get('fuel_type', 'petrol')
        vehicle_mileage = float(data.get('vehicle_mileage', 0)) or None
        meeting_hub = data.get('meeting_hub', '')
        dropoff_hub = data.get('dropoff_hub', '')
        is_pink_mode = data.get('is_pink_mode', False)

        # Get route info
        route = get_route_info(from_city, to_city)
        distance_km = route['distance']
        toll_cost = route['tolls']

        if distance_km <= 0:
            return jsonify({
                'status': 'error',
                'message': f'Route {from_city} → {to_city} not supported yet.'
            }), 400

        # Calculate legal price
        pricing = calculate_legal_price_per_seat(
            distance_km=distance_km,
            seats=seats,
            fuel_type=fuel_type,
            vehicle_mileage=vehicle_mileage,
            toll_cost=toll_cost,
        )

        # Validate proposed price (if driver overrides)
        proposed_price = float(data.get('price_per_seat', pricing['max_price_per_seat']))
        validation = validate_price(proposed_price, pricing['max_price_per_seat'])

        if not validation['is_valid']:
            # Auto-cap to legal maximum
            proposed_price = pricing['max_price_per_seat']

        ride_data = {
            'driver_id': session['user']['uid'],
            'driver_name': session['user']['name'],
            'driver_photo': session['user'].get('photo_url', ''),
            'from_city': from_city,
            'to_city': to_city,
            'date': data['date'],
            'time': data['time'],
            'meeting_hub': meeting_hub,
            'dropoff_hub': dropoff_hub,
            'distance_km': distance_km,
            'fuel_type': fuel_type,
            'vehicle_mileage': pricing['vehicle_mileage'],
            'fuel_cost': pricing['fuel_cost'],
            'toll_cost': pricing['toll_cost'],
            'total_running_cost': pricing['total_cost'],
            'price_per_seat': proposed_price,
            'max_legal_price': pricing['max_price_per_seat'],
            'total_seats': seats,
            'seats_left': seats,
            'is_pink_mode': is_pink_mode,
            'is_non_profit': True,
            'cost_recovery_percent': pricing['cost_recovery_percent'],
            'passengers': [],
            'status': 'active',
            'vehicle_details': data.get('vehicle_details', {}),
            'created_at': firestore.SERVER_TIMESTAMP,
        }

        new_ride_ref = db.collection('rides').add(ride_data)
        return jsonify({
            'status': 'success',
            'ride_id': new_ride_ref[1].id,
            'pricing': pricing,
        })
    except KeyError as e:
        return jsonify({'status': 'error', 'message': f'Missing field: {e}'}), 400
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/calculate-cost', methods=['POST'])
@csrf.exempt
def api_calculate_cost():
    """Real-time Legal-Guard cost estimation (no auth required)."""
    data = request.json or {}
    from_city = data.get('from_city', '')
    to_city = data.get('to_city', '')
    seats = int(data.get('seats', 3))
    fuel_type = data.get('fuel_type', 'petrol')
    vehicle_mileage = float(data.get('vehicle_mileage', 0)) or None

    route = get_route_info(from_city, to_city)
    if route['distance'] <= 0:
        return jsonify({'status': 'error', 'message': 'Route not found'}), 404

    pricing = calculate_legal_price_per_seat(
        distance_km=route['distance'],
        seats=seats,
        fuel_type=fuel_type,
        vehicle_mileage=vehicle_mileage,
        toll_cost=route['tolls'],
    )

    return jsonify({'status': 'success', 'pricing': pricing})


@app.route('/api/book/<ride_id>', methods=['POST'])
@csrf.exempt
@login_required
def book_ride(ride_id):
    """Book a seat on a ride (atomic transaction)."""
    if not db:
        return jsonify({'status': 'error', 'message': 'Database not connected'}), 500

    passenger_id = session['user']['uid']
    # 1. Check passenger verification level
    user_doc = db.collection('users').document(passenger_id).get()
    user_data = user_doc.to_dict() if user_doc.exists else {}
    if user_data.get('verification_level', 0) < 1:
        return jsonify({
            'status': 'error', 
            'message': 'Verification required. Please upload your documents in the Verification Hub first.'
        }), 403

    @firestore.transactional
    def update_seats(transaction, ride_ref):
        snapshot = ride_ref.get(transaction=transaction)
        if not snapshot.exists:
            return {'success': False, 'message': 'Ride not found'}

        ride_data = snapshot.to_dict()
        if ride_data.get('driver_id') == passenger_id:
            return {'success': False, 'message': 'You cannot book your own ride.'}

        if ride_data.get('seats_left', 0) <= 0:
            return {'success': False, 'message': 'No seats available'}

        # Create booking request (PENDING)
        booking_ref = db.collection('bookings').document()
        transaction.set(booking_ref, {
            'ride_id': ride_id,
            'passenger_id': passenger_id,
            'passenger_name': session['user']['name'],
            'passenger_photo': session['user'].get('photo_url', ''),
            'driver_id': ride_data.get('driver_id'),
            'status': 'pending', # Wait for driver approval
            'amount_due': ride_data.get('price_per_seat', 0),
            'created_at': firestore.SERVER_TIMESTAMP,
            'upi_payment_status': 'pending'
        })
        # We don't decrement seats yet, wait for driver confirmation
        return {'success': True, 'booking_id': booking_ref.id}

    try:
        ride_ref = db.collection('rides').document(ride_id)
        transaction = db.transaction()
        result = update_seats(transaction, ride_ref)
        if result['success']:
            return jsonify({'status': 'success', 'booking_id': result.get('booking_id')})
        else:
            return jsonify({'status': 'error', 'message': result['message']})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


# ── Verification ───────────────────────────────────────────

@app.route('/api/verify/aadhaar', methods=['POST'])
@csrf.exempt
@login_required
def verify_aadhaar():
    """Simulate Aadhaar/Govt ID face-match verification."""
    if db:
        db.collection('users').document(session['user']['uid']).update({
            'aadhaar_status': 'verified',
            'verification_level': firestore.Increment(1),
        })
    return jsonify({
        'status': 'success',
        'message': 'Aadhaar identity verified successfully.',
        'badge': 'aadhaar_verified',
    })


@app.route('/api/verify/corp-email', methods=['POST'])
@csrf.exempt
@login_required
def verify_corp_email():
    """Verify corporate/university email."""
    data = request.json or {}
    corp_email = data.get('corp_email', '')

    if not corp_email or '@' not in corp_email:
        return jsonify({'status': 'error', 'message': 'Invalid email'}), 400

    # In production: send OTP to corp email and verify
    if db:
        db.collection('users').document(session['user']['uid']).update({
            'corp_email': corp_email,
            'corp_email_verified': True,
            'verification_level': firestore.Increment(1),
        })
    return jsonify({
        'status': 'success',
        'message': f'Corporate email {corp_email} verified.',
        'badge': 'corp_verified',
    })


@app.route('/api/verify/linkedin', methods=['POST'])
@csrf.exempt
@login_required
def verify_linkedin():
    """Sync LinkedIn profile URL."""
    data = request.json or {}
    linkedin_url = data.get('linkedin_url', '')

    if not linkedin_url or 'linkedin.com' not in linkedin_url:
        return jsonify({'status': 'error', 'message': 'Invalid LinkedIn URL'}), 400

    if db:
        db.collection('users').document(session['user']['uid']).update({
            'linkedin_url': linkedin_url,
            'verification_level': firestore.Increment(1),
        })
    return jsonify({
        'status': 'success',
        'message': 'LinkedIn profile linked successfully.',
        'badge': 'linkedin_verified',
    })


@app.route('/api/profile/update', methods=['POST'])
@csrf.exempt
@login_required
def update_profile():
    """Update user profile fields."""
    data = request.json or {}
    allowed_fields = ['gender', 'phone', 'vehicle_details', 'emergency_contacts', 'upi_id']
    updates = {k: v for k, v in data.items() if k in allowed_fields}

    if not updates:
        return jsonify({'status': 'error', 'message': 'No valid fields to update'}), 400

    if db:
        db.collection('users').document(session['user']['uid']).update(updates)

    return jsonify({'status': 'success', 'message': 'Profile updated.'})


# ── SOS System ─────────────────────────────────────────────

@app.route('/api/sos/trigger', methods=['POST'])
@csrf.exempt
@login_required
def trigger_sos():
    """Trigger an SOS alert — logs location and notifies contacts."""
    data = request.json or {}
    ride_id = data.get('ride_id', '')
    lat = data.get('latitude', 0)
    lng = data.get('longitude', 0)

    if not ride_id:
        return jsonify({'status': 'error', 'message': 'Missing ride_id'}), 400

    alert_id = str(uuid.uuid4())

    if db:
        # Create SOS alert record
        db.collection('sos_alerts').document(alert_id).set({
            'ride_id': ride_id,
            'user_id': session['user']['uid'],
            'user_name': session['user']['name'],
            'timestamp': firestore.SERVER_TIMESTAMP,
            'location_lat': lat,
            'location_lng': lng,
            'alert_type': 'emergency',
            'contacts_notified': [],
            'resolved': False,
        })

        # Get user's emergency contacts
        user_doc = db.collection('users').document(session['user']['uid']).get()
        contacts = []
        if user_doc.exists:
            contacts = user_doc.to_dict().get('emergency_contacts', [])

        # In production: Send SMS/push to emergency contacts
        # For now, mark them as notified in the alert
        if contacts:
            db.collection('sos_alerts').document(alert_id).update({
                'contacts_notified': contacts,
            })

    return jsonify({
        'status': 'success',
        'alert_id': alert_id,
        'message': 'SOS alert sent. Emergency contacts have been notified.',
        'contacts_notified': len(contacts) if 'contacts' in dir() else 0,
    })


@app.route('/api/sos/resolve', methods=['POST'])
@csrf.exempt
@login_required
def resolve_sos():
    """Mark an SOS alert as resolved."""
    data = request.json or {}
    alert_id = data.get('alert_id', '')

    if db and alert_id:
        db.collection('sos_alerts').document(alert_id).update({
            'resolved': True,
            'resolved_at': firestore.SERVER_TIMESTAMP,
        })

    return jsonify({'status': 'success', 'message': 'SOS alert resolved.'})


# ── Meeting Hubs ───────────────────────────────────────────

@app.route('/api/hubs/suggest', methods=['GET'])
def suggest_hubs():
    """Get meeting hub suggestions for a city."""
    city = request.args.get('city', '')
    hubs = MEETING_HUBS.get(city.strip().title(), [])
    return jsonify({'status': 'success', 'city': city, 'hubs': hubs})


# ── UPI Payment ───────────────────────────────────────────

@app.route('/api/book/<booking_id>/action', methods=['POST'])
@csrf.exempt
@login_required
def booking_action(booking_id):
    """Approve or Reject a booking request (Driver only)."""
    if not db: return jsonify({'status': 'error', 'message': 'DB error'}), 500
    
    data = request.json or {}
    action = data.get('action') # 'approve' or 'reject'
    driver_id = session['user']['uid']

    @firestore.transactional
    def process_action(transaction, booking_ref):
        b_snap = booking_ref.get(transaction=transaction)
        if not b_snap.exists: return {'success': False, 'message': 'Booking not found'}
        
        b_data = b_snap.to_dict()
        if b_data.get('driver_id') != driver_id:
            return {'success': False, 'message': 'Unauthorized'}
        
        if b_data.get('status') != 'pending':
            return {'success': False, 'message': 'Booking already processed'}
        
        ride_ref = db.collection('rides').document(b_data.get('ride_id'))
        r_snap = ride_ref.get(transaction=transaction)
        if not r_snap.exists: return {'success': False, 'message': 'Ride not found'}
        
        r_data = r_snap.to_dict()

        if action == 'approve':
            if r_data.get('seats_left', 0) <= 0:
                return {'success': False, 'message': 'No seats left'}
            
            transaction.update(booking_ref, {'status': 'confirmed'})
            transaction.update(ride_ref, {
                'seats_left': r_data['seats_left'] - 1
            })
            return {'success': True, 'message': 'Booking approved'}
        else:
            transaction.update(booking_ref, {'status': 'rejected'})
            return {'success': True, 'message': 'Booking rejected'}

    try:
        booking_ref = db.collection('bookings').document(booking_id)
        res = process_action(db.transaction(), booking_ref)
        return jsonify(res)
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/upi/confirm', methods=['POST'])
@csrf.exempt
@login_required
def confirm_upi_payment():
    """Record a UPI payment for a booking."""
    data = request.json or {}
    booking_id = data.get('booking_id', '')
    upi_txn_id = data.get('upi_transaction_id', '')

    if not booking_id:
        return jsonify({'status': 'error', 'message': 'Missing booking_id'}), 400

    if db:
        db.collection('bookings').document(booking_id).update({
            'upi_transaction_id': upi_txn_id,
            'upi_payment_status': 'completed',
            'paid_at': firestore.SERVER_TIMESTAMP,
        })

    return jsonify({'status': 'success', 'message': 'Payment recorded.'})


# ── Search API (JSON) ──────────────────────────────────────

@app.route('/api/search-rides', methods=['GET'])
def api_search_rides():
    """JSON API for ride search (used by JS)."""
    from_city = request.args.get('from', '')
    to_city = request.args.get('to', '')
    date = request.args.get('date', '')
    pink_mode = request.args.get('pink_mode', '') == 'true'

    rides = []
    if db and from_city and to_city:
        query = db.collection('rides').where(
            filter=firestore.FieldFilter('from_city', '==', from_city)
        ).where(
            filter=firestore.FieldFilter('to_city', '==', to_city)
        ).where(
            filter=firestore.FieldFilter('status', '==', 'active')
        )

        if date:
            query = query.where(filter=firestore.FieldFilter('date', '==', date))
        if pink_mode:
            query = query.where(filter=firestore.FieldFilter('is_pink_mode', '==', True))

        docs = query.stream()
        for doc in docs:
            ride = doc.to_dict()
            ride['id'] = doc.id
            # Remove server timestamp (not JSON serializable)
            ride.pop('created_at', None)
            if ride.get('seats_left', 0) > 0:
                rides.append(ride)

    return jsonify({'status': 'success', 'rides': rides, 'count': len(rides)})


# ═══════════════════════════════════════════════════════════
#  ERROR HANDLERS
# ═══════════════════════════════════════════════════════════

@app.errorhandler(404)
def not_found(e):
    return render_template('base.html', error_code=404, error_message='Page not found'), 404


@app.errorhandler(500)
def server_error(e):
    return render_template('base.html', error_code=500, error_message='Internal server error'), 500


# ═══════════════════════════════════════════════════════════
#  RUN
# ═══════════════════════════════════════════════════════════

if __name__ == '__main__':
    app.run(debug=True, port=5000, host='0.0.0.0')
