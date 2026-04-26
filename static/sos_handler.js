/**
 * Petrol Partner — SOS Handler
 * Emergency alert system with geolocation.
 */
const SOSHandler = {
    async getLocation() {
        return new Promise((resolve, reject) => {
            if (!navigator.geolocation) reject(new Error('Geolocation not supported'));
            navigator.geolocation.getCurrentPosition(
                pos => resolve({ lat: pos.coords.latitude, lng: pos.coords.longitude }),
                err => reject(err), { timeout: 5000, enableHighAccuracy: true }
            );
        });
    },
    async trigger(rideId) {
        let location = { lat: 0, lng: 0 };
        try { location = await this.getLocation(); } catch (e) { console.warn('GPS unavailable'); }
        const res = await fetch('/api/sos/trigger', {
            method: 'POST', headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ ride_id: rideId, latitude: location.lat, longitude: location.lng }),
        });
        return await res.json();
    }
};
