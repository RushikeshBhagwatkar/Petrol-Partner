"""
Petrol Partner — Centralized Configuration
All environment variables and constants for the application.
"""
import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Application configuration loaded from environment variables."""

    # Flask
    SECRET_KEY = os.getenv('FLASK_SECRET_KEY', 'petrol-partner-secret-key-change-in-prod')
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    SESSION_COOKIE_SECURE = os.getenv('FLASK_ENV') == 'production'

    # Firebase
    FIREBASE_SERVICE_ACCOUNT_JSON = os.getenv('FIREBASE_SERVICE_ACCOUNT_JSON', 'serviceAccountKey.json')

    # Fuel Prices (₹ per litre — updated periodically)
    FUEL_PRICE_PETROL = float(os.getenv('FUEL_PRICE_PETROL', '104.21'))
    FUEL_PRICE_DIESEL = float(os.getenv('FUEL_PRICE_DIESEL', '90.76'))
    FUEL_PRICE_CNG = float(os.getenv('FUEL_PRICE_CNG', '76.59'))

    # Legal-Guard: Maximum price cap factor (1.0 = 100% of running cost)
    MAX_COST_RECOVERY_FACTOR = 1.0

    # Default vehicle mileage (km/L) if not specified
    DEFAULT_MILEAGE_PETROL = 15.0
    DEFAULT_MILEAGE_DIESEL = 18.0
    DEFAULT_MILEAGE_CNG = 22.0


# --- Route Distance Data (km) for major Indian city pairs ---
# Used when Google Maps API is not available
ROUTE_DISTANCES = {
    ('Mumbai', 'Pune'): {'distance': 149, 'tolls': 290},
    ('Pune', 'Mumbai'): {'distance': 149, 'tolls': 290},
    ('Mumbai', 'Nashik'): {'distance': 167, 'tolls': 195},
    ('Nashik', 'Mumbai'): {'distance': 167, 'tolls': 195},
    ('Mumbai', 'Nagpur'): {'distance': 840, 'tolls': 1050},
    ('Nagpur', 'Mumbai'): {'distance': 840, 'tolls': 1050},
    ('Pune', 'Nagpur'): {'distance': 720, 'tolls': 870},
    ('Nagpur', 'Pune'): {'distance': 720, 'tolls': 870},
    ('Pune', 'Nashik'): {'distance': 212, 'tolls': 240},
    ('Nashik', 'Pune'): {'distance': 212, 'tolls': 240},
    ('Mumbai', 'Aurangabad'): {'distance': 337, 'tolls': 420},
    ('Aurangabad', 'Mumbai'): {'distance': 337, 'tolls': 420},
    ('Pune', 'Aurangabad'): {'distance': 237, 'tolls': 310},
    ('Aurangabad', 'Pune'): {'distance': 237, 'tolls': 310},
    ('Mumbai', 'Bengaluru'): {'distance': 981, 'tolls': 1280},
    ('Bengaluru', 'Mumbai'): {'distance': 981, 'tolls': 1280},
    ('Pune', 'Bengaluru'): {'distance': 840, 'tolls': 1100},
    ('Bengaluru', 'Pune'): {'distance': 840, 'tolls': 1100},
    ('Mumbai', 'Hyderabad'): {'distance': 711, 'tolls': 920},
    ('Hyderabad', 'Mumbai'): {'distance': 711, 'tolls': 920},
    ('Bengaluru', 'Hyderabad'): {'distance': 570, 'tolls': 650},
    ('Hyderabad', 'Bengaluru'): {'distance': 570, 'tolls': 650},
    ('Mumbai', 'Goa'): {'distance': 590, 'tolls': 620},
    ('Goa', 'Mumbai'): {'distance': 590, 'tolls': 620},
    ('Pune', 'Goa'): {'distance': 448, 'tolls': 480},
    ('Goa', 'Pune'): {'distance': 448, 'tolls': 480},
    ('Delhi', 'Jaipur'): {'distance': 281, 'tolls': 620},
    ('Jaipur', 'Delhi'): {'distance': 281, 'tolls': 620},
    ('Delhi', 'Chandigarh'): {'distance': 243, 'tolls': 540},
    ('Chandigarh', 'Delhi'): {'distance': 243, 'tolls': 540},
    ('Delhi', 'Agra'): {'distance': 233, 'tolls': 590},
    ('Agra', 'Delhi'): {'distance': 233, 'tolls': 590},
    ('Chennai', 'Bengaluru'): {'distance': 346, 'tolls': 470},
    ('Bengaluru', 'Chennai'): {'distance': 346, 'tolls': 470},
    ('Kolkata', 'Bhubaneswar'): {'distance': 440, 'tolls': 520},
    ('Bhubaneswar', 'Kolkata'): {'distance': 440, 'tolls': 520},
}

# --- Supported Cities ---
SUPPORTED_CITIES = [
    'Mumbai', 'Pune', 'Nagpur', 'Nashik', 'Aurangabad',
    'Bengaluru', 'Hyderabad', 'Chennai', 'Goa',
    'Delhi', 'Jaipur', 'Chandigarh', 'Agra',
    'Kolkata', 'Bhubaneswar',
]

# --- Meeting Hub Presets ---
MEETING_HUBS = {
    'Mumbai': [
        {'name': 'Thane Station', 'type': 'railway', 'lat': 19.1860, 'lng': 72.9756},
        {'name': 'Vashi Toll Naka', 'type': 'toll', 'lat': 19.0728, 'lng': 72.9988},
        {'name': 'Dadar TT Circle', 'type': 'landmark', 'lat': 19.0178, 'lng': 72.8478},
        {'name': 'Borivali Station (W)', 'type': 'railway', 'lat': 19.2307, 'lng': 72.8567},
        {'name': 'Panvel Bus Stand', 'type': 'bus_stand', 'lat': 18.9894, 'lng': 73.1175},
    ],
    'Pune': [
        {'name': 'Hinjewadi Phase 1 Gate', 'type': 'landmark', 'lat': 18.5912, 'lng': 73.7380},
        {'name': 'Wakad Bridge', 'type': 'landmark', 'lat': 18.5989, 'lng': 73.7621},
        {'name': 'Swargate Bus Stand', 'type': 'bus_stand', 'lat': 18.5018, 'lng': 73.8636},
        {'name': 'Chandni Chowk Flyover', 'type': 'landmark', 'lat': 18.5281, 'lng': 73.8140},
        {'name': 'Pune Station', 'type': 'railway', 'lat': 18.5285, 'lng': 73.8743},
    ],
    'Nagpur': [
        {'name': 'Nagpur Railway Station', 'type': 'railway', 'lat': 21.1500, 'lng': 79.0900},
        {'name': 'Automotive Square', 'type': 'landmark', 'lat': 21.1250, 'lng': 79.0480},
    ],
    'Nashik': [
        {'name': 'Nashik CBS', 'type': 'bus_stand', 'lat': 19.9975, 'lng': 73.7898},
        {'name': 'Dwarka Circle', 'type': 'landmark', 'lat': 20.0063, 'lng': 73.7621},
    ],
    'Bengaluru': [
        {'name': 'Silk Board Junction', 'type': 'landmark', 'lat': 12.9170, 'lng': 77.6230},
        {'name': 'Majestic Bus Stand', 'type': 'bus_stand', 'lat': 12.9770, 'lng': 77.5730},
        {'name': 'Electronic City Toll', 'type': 'toll', 'lat': 12.8456, 'lng': 77.6603},
    ],
    'Hyderabad': [
        {'name': 'Mehdipatnam Bus Stop', 'type': 'bus_stand', 'lat': 17.3950, 'lng': 78.4430},
        {'name': 'LB Nagar X Roads', 'type': 'landmark', 'lat': 17.3490, 'lng': 78.5520},
    ],
    'Delhi': [
        {'name': 'Kashmere Gate ISBT', 'type': 'bus_stand', 'lat': 28.6679, 'lng': 77.2285},
        {'name': 'Dhaula Kuan', 'type': 'landmark', 'lat': 28.5921, 'lng': 77.1667},
        {'name': 'Rajiv Chowk Metro', 'type': 'metro', 'lat': 28.6328, 'lng': 77.2197},
    ],
}
