/* Firstly, we'll get the value of the country field when the page
loads and store it in a variable. */ 
let countrySelected = $('#id_default_country').val();
/*  Since the value will be an empty string if the 1st option is selected,
to determine if that's what is selected, we'll use this as a boolean i.e
if country selected is false, then we want the colour of this element to be 
that placeholder's grey colour. */ 
if(!countrySelected) {
    $('#id_default_country').css('color', '#aab7c4');
};
/* Next, we need to capture the change event so that every time the box 
changes, we'll get the value of it & then determine the proper colour. */ 
$('#id_default_country').change(function() {
    countrySelected = $(this).val();
    if(!countrySelected) {
        $(this).css('color', '#aab7c4');
    /* The else part takes care of if the box does not change */   
    } else {
        $(this).css('color', '#000');
    }
});