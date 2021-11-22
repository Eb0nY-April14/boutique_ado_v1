/*
    Core logic/payment flow for this comes from here:
    https://stripe.com/docs/payments/accept-a-payment
*/

/* This 2 lines of code below gets the stripe public key & 
client secret from the template using a little jQuery.
NOTE THAT: Those little script elements contain the values 
we need as their text so we can get them just by getting 
their ids & using the .text function. We'll also slice off 
the 1st and last character on each since they'll have 
quotation marks which we don't want. */
var stripePublicKey = $('#id_stripe_public_key').text().slice(1, -1);
var clientSecret = $('#id_client_secret').text().slice(1, -1);

/* Here, we'll set up stripe by creating a variable using our stripe public 
key. This is made possible by the stripe js included in the base template. */
var stripe = Stripe(stripePublicKey);
/* Then we can use the 'stripe' variable created above to create an instance 
of stripe elements. */ 
var elements = stripe.elements();

/* CSS from here: 
https://stripe.com/docs/stripe-js */
/* The card element can also accept a style argument so we'll get some basic 
styles from the stripe js Docs. */ 
var style = {
    base: {
        color: '#000',
        fontFamily: '"Helvetica Neue", Helvetica, sans-serif',
        fontSmoothing: 'antialiased',
        fontSize: '16px',
        '::placeholder': {
            // Change the default colour of the element to black.
            color: '#aab7c4'
        }
    },
    invalid: {
        // Change the invalid colour to match bootstrap's text danger class.
        color: '#dc3545',
        iconColor: '#dc3545'
    }
};
// We'll also use the stripe 'elements' created above to create a card element.
var card = elements.create('card', {style: style});
/* Finally, we mount the 'card' element to the div we created within  
the form that has an id of 'card-element' in checkout.html. */
card.mount('#card-element');

// Handle realtime validation errors on the card element
/* 1stly, we'll add an event listener on the card element to 
listen for any change event & every time it changes we'll check 
to see if there are any errors. */ 
card.addEventListener('change', function (event) {
    var errorDiv = document.getElementById('card-errors');
    /* If there are any errors, we'll display them in the card errors div 
    we created near the card element on the checkout page using back ticks. */ 
    if (event.error) {
        var html = `
            <span class="icon" role="alert">
                <i class="fas fa-times"></i>
            </span>
            <span>${event.error.message}</span>
        `;
        $(errorDiv).html(html);
      // The else part is activated if there are no errors.  
    } else {
        errorDiv.textContent = '';
    }
});

// Handle form submit
/* This gets the form element */ 
var form = document.getElementById('payment-form');
/* We then add an event listener to the payment forms 'submit' event. */ 
form.addEventListener('submit', function(ev) {
    /* The listener attached to the 'submit' event then prevents its 
    default action i.e post from taking place & instead, execute the 
    code after it. */ 
    ev.preventDefault();
    /* Here, we'll disable both the card element & submit button to 
    prevent multiple submissions before calling out to stripe.  */ 
    card.update({ 'disabled': true});
    $('#submit-button').attr('disabled', true);
    /* We'll trigger the overlay & fade out the form when the user clicks the submit
button and reverse that if there's any error. */ 
    $('#payment-form').fadeToggle(100);
    $('#loading-overlay').fadeToggle(100);
    /* Here, we call the confirm card payment method which  uses the 
    'stripe.confirm card payment' method to send the card information 
    securely to stripe. */ 
    stripe.confirmCardPayment(clientSecret, {
        // This provides the card to stripe 
        payment_method: {
            card: card,
        }
        /* It then executes this function below on the result. */ 
    }).then(function(result) {
        /* If there's an error, we handle it same way as done earlier 
        above i.e put the error right into the card error div. */ 
        if (result.error) {
            var errorDiv = document.getElementById('card-errors');
            var html = `
                <span class="icon" role="alert">
                <i class="fas fa-times"></i>
                </span>
                <span>${result.error.message}</span>`;
            $(errorDiv).html(html);
            /* If there's an error, we also want to re-enable the card  
            element & submit button to allow the user to fix it. */ 
            card.update({ 'disabled': false});
            $('#submit-button').attr('disabled', false);
            /* But if no error i.e the status of the payment intent comes back 
            as succeeded, we'll submit the form. */ 
        } else {
            if (result.paymentIntent.status === 'succeeded') {
                form.submit();
            }
        }
    });
});
