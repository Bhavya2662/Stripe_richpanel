// Create a Stripe client
var stripe = Stripe('pk_test_51NdGfwSH8lu44vb8qMFt3KhLPEK3DkU4oRstwfgST8p3MWNUUJ0O41ccYdFcDbVKqIyiM64LWIzBBA3lJG776ExE00x2i6foIQ'); // Replace with your Stripe public key

// Create an instance of Elements
var elements = stripe.elements();

// Create an instance of the card Element
var card = elements.create('card');

// Add an instance of the card Element into the `card-element` div
card.mount('#card-element');

// Handle form submission
var form = document.getElementById('payment-form'); // Change this to your actual form ID
form.addEventListener('submit', function (event) {
    event.preventDefault();

    stripe.createToken(card).then(function (result) {
        if (result.error) {
            // Inform the user if there was an error
            var errorElement = document.getElementById('card-errors'); // Change this to your actual error element ID
            errorElement.textContent = result.error.message;
        } else {
            // Send the token to your server
            stripeTokenHandler(result.token);
        }
    });
});

// Submit the form with the token ID
function stripeTokenHandler(token) {
    var form = document.getElementById('payment-form'); // Change this to your actual form ID
    var hiddenInput = document.createElement('input');
    hiddenInput.setAttribute('type', 'hidden');
    hiddenInput.setAttribute('name', 'stripeToken');
    hiddenInput.setAttribute('value', token.id);
    form.appendChild(hiddenInput);

    // Submit the form
    form.submit();
}
