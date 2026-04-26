/**
 * Petrol Partner — Legal-Guard Cost Engine (Client-Side)
 * Real-time cost estimation for ride pricing.
 */
const CostEngine = {
    fuelPrices: { petrol: 104.21, diesel: 90.76, cng: 76.59 },
    defaultMileage: { petrol: 15, diesel: 18, cng: 22 },

    calculate(distanceKm, seats, fuelType = 'petrol', mileage = 0, tollCost = 0) {
        const fuelPrice = this.fuelPrices[fuelType] || this.fuelPrices.petrol;
        const vehicleMileage = mileage > 0 ? mileage : (this.defaultMileage[fuelType] || 15);
        const litresUsed = distanceKm / vehicleMileage;
        const fuelCost = litresUsed * fuelPrice;
        const totalCost = fuelCost + tollCost;
        const totalOccupants = seats + 1; // passengers + driver
        const maxPerSeat = totalCost / totalOccupants;
        return {
            distanceKm, fuelPrice, vehicleMileage, litresUsed: Math.round(litresUsed * 100) / 100,
            fuelCost: Math.round(fuelCost), tollCost: Math.round(tollCost),
            totalCost: Math.round(totalCost), maxPerSeat: Math.round(maxPerSeat),
            seats, totalOccupants, isNonProfit: true,
        };
    },

    validate(proposedPrice, maxLegalPrice) {
        return { isValid: proposedPrice <= maxLegalPrice, proposedPrice, maxLegalPrice };
    }
};
