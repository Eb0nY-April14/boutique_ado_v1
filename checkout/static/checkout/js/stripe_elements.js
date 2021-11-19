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
var stripe_public_key = $('#id_stripe_public_key').text().slice(1, -1);
var client_secret = $('#id_client_secret').text().slice(1, -1);

/* Here, we'll set up stripe by creating a variable using our stripe public 
key. This is made possible by the stripe js included in the base template. */
var stripe = Stripe(stripe_public_key);
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
/* Finally, we mount the 'card' element to the div we created within the form 
that has an id of 'card-element' in checkout.html. */
card.mount('#card-element');
