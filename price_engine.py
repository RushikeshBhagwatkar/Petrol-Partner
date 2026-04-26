"""
Petrol Partner — Legal-Guard Price Engine
Calculates the "True Running Cost" and caps passenger contributions
so they NEVER exceed 100% of actual cost (non-profit compliance).

This ensures rides on private (white-plate) vehicles remain legally
cost-sharing and not commercial transport.
"""
from config import Config, ROUTE_DISTANCES


def get_fuel_price(fuel_type: str) -> float:
    """Get current fuel price per litre based on fuel type."""
    prices = {
        'petrol': Config.FUEL_PRICE_PETROL,
        'diesel': Config.FUEL_PRICE_DIESEL,
        'cng': Config.FUEL_PRICE_CNG,
    }
    return prices.get(fuel_type.lower(), Config.FUEL_PRICE_PETROL)


def get_default_mileage(fuel_type: str) -> float:
    """Get default vehicle mileage (km/L) based on fuel type."""
    mileage = {
        'petrol': Config.DEFAULT_MILEAGE_PETROL,
        'diesel': Config.DEFAULT_MILEAGE_DIESEL,
        'cng': Config.DEFAULT_MILEAGE_CNG,
    }
    return mileage.get(fuel_type.lower(), Config.DEFAULT_MILEAGE_PETROL)


def get_route_info(from_city: str, to_city: str) -> dict:
    """
    Get route distance and toll information for a city pair.
    Returns dict with 'distance' (km) and 'tolls' (₹).
    """
    key = (from_city.strip().title(), to_city.strip().title())
    route = ROUTE_DISTANCES.get(key)
    if route:
        return route
    # Fallback for non-hardcoded routes (simple estimate: 100km, 0 tolls)
    # In production, this would integrate with Google Maps Distance Matrix API
    return {'distance': 100, 'tolls': 0, 'is_estimate': True}


def calculate_true_running_cost(
    distance_km: float,
    fuel_type: str = 'petrol',
    vehicle_mileage: float = None,
    toll_cost: float = 0,
    fuel_price_override: float = None
) -> dict:
    """
    Calculate the True Running Cost of a trip.

    Args:
        distance_km: Total distance in kilometres
        fuel_type: 'petrol', 'diesel', or 'cng'
        vehicle_mileage: km per litre (uses default if None)
        toll_cost: Total toll charges in ₹
        fuel_price_override: Override fuel price (₹/litre)

    Returns:
        dict with fuel_cost, toll_cost, total_cost, litres_used
    """
    fuel_price = fuel_price_override or get_fuel_price(fuel_type)
    mileage = vehicle_mileage or get_default_mileage(fuel_type)

    if mileage <= 0:
        mileage = get_default_mileage(fuel_type)

    litres_used = distance_km / mileage
    fuel_cost = litres_used * fuel_price
    total_cost = fuel_cost + toll_cost

    return {
        'fuel_price_per_litre': round(fuel_price, 2),
        'vehicle_mileage': round(mileage, 1),
        'distance_km': round(distance_km, 1),
        'litres_used': round(litres_used, 2),
        'fuel_cost': round(fuel_cost, 2),
        'toll_cost': round(toll_cost, 2),
        'total_cost': round(total_cost, 2),
    }


def calculate_legal_price_per_seat(
    distance_km: float,
    seats: int,
    fuel_type: str = 'petrol',
    vehicle_mileage: float = None,
    toll_cost: float = 0,
    fuel_price_override: float = None
) -> dict:
    """
    Calculate the maximum legal (non-profit) price per seat.

    The total contributions from all passengers MUST NOT exceed
    100% of the True Running Cost. This is the Legal-Guard cap.

    The driver effectively pays their own share (1 seat worth).
    So: max_per_seat = total_cost / (seats + 1 driver)
    But since the driver collects from passengers only:
    max_per_seat = total_cost / total_occupants (including driver)

    Args:
        distance_km: Total distance in km
        seats: Number of passenger seats offered
        fuel_type: Fuel type
        vehicle_mileage: Vehicle mileage (km/L)
        toll_cost: Toll charges (₹)
        fuel_price_override: Override fuel price (₹/L)

    Returns:
        dict with full cost breakdown and legal max price per seat
    """
    if seats < 1:
        seats = 1

    cost = calculate_true_running_cost(
        distance_km=distance_km,
        fuel_type=fuel_type,
        vehicle_mileage=vehicle_mileage,
        toll_cost=toll_cost,
        fuel_price_override=fuel_price_override
    )

    total_occupants = seats + 1  # passengers + driver
    max_per_seat = cost['total_cost'] / total_occupants

    # Apply the legal cap factor (should be 1.0 for non-profit)
    capped_price = max_per_seat * Config.MAX_COST_RECOVERY_FACTOR

    # Driver's saving = what passengers collectively contribute
    max_passenger_contribution = capped_price * seats
    driver_share = cost['total_cost'] - max_passenger_contribution

    return {
        **cost,
        'seats_offered': seats,
        'total_occupants': total_occupants,
        'max_price_per_seat': round(capped_price, 0),
        'driver_share': round(max(driver_share, 0), 2),
        'total_passenger_contribution': round(max_passenger_contribution, 2),
        'is_non_profit': max_passenger_contribution <= cost['total_cost'],
        'cost_recovery_percent': round(
            (max_passenger_contribution / cost['total_cost'] * 100)
            if cost['total_cost'] > 0 else 0, 1
        ),
    }


def validate_price(proposed_price: float, max_legal_price: float) -> dict:
    """
    Validate a driver's proposed price against the legal cap.

    Returns:
        dict with is_valid, proposed_price, max_legal_price, and message
    """
    is_valid = proposed_price <= max_legal_price
    return {
        'is_valid': is_valid,
        'proposed_price': round(proposed_price, 2),
        'max_legal_price': round(max_legal_price, 2),
        'message': (
            '✅ Price is within the legal non-profit limit.'
            if is_valid else
            f'⚠️ Price exceeds legal limit of ₹{max_legal_price:.0f}. '
            f'Reduce by ₹{proposed_price - max_legal_price:.0f} to comply.'
        ),
    }
