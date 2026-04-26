/**
 * Petrol Partner — UPI Deep-Link Handler
 * Generates UPI payment links for GPay, PhonePe, Paytm.
 */
const UPIHandler = {
    generateLink(payeeVPA, payeeName, amount, txnNote, txnId) {
        const params = new URLSearchParams({
            pa: payeeVPA, pn: payeeName, am: amount.toFixed(2),
            cu: 'INR', tn: txnNote || 'PetrolPartner Ride',
        });
        if (txnId) params.set('tr', txnId);
        return 'upi://pay?' + params.toString();
    },
    openPayment(payeeVPA, payeeName, amount, txnNote) {
        const link = this.generateLink(payeeVPA, payeeName, amount, txnNote);
        window.location.href = link;
    }
};
