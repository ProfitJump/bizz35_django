/******/
(() => { // webpackBootstrap
    /******/
    "use strict";
    var __webpack_exports__ = {};
    /*!***********************************************************!*\
      !*** ../demo9/src/js/custom/utilities/modals/new-card.js ***!
      \***********************************************************/


// Class definition
    var KTModalNewCard = function () {
        var submitButton;
        var cancelButton;
        var validator;
        var form;
        var modal;
        var modalEl;

        // Init form inputs
        var initForm = function () {
            // Expiry month. For more info, plase visit the official plugin site: https://select2.org/
            $(form.querySelector('[name="card_expiry_month"]')).on('change', function () {
                // Revalidate the field when an option is chosen
                validator.revalidateField('card_expiry_month');
            });

            // Expiry year. For more info, plase visit the official plugin site: https://select2.org/
            $(form.querySelector('[name="card_expiry_year"]')).on('change', function () {
                // Revalidate the field when an option is chosen
                validator.revalidateField('card_expiry_year');
            });
        }

        // Handle form validation and submittion
        var handleForm = function () {
            // Stepper custom navigation

            // Init form validation rules. For more info check the FormValidation plugin's official documentation:https://formvalidation.io/
            validator = FormValidation.formValidation(
                form,
                {
                    fields: {
                        'card_name': {
                            validators: {
                                notEmpty: {
                                    message: 'Name on card is required'
                                }
                            }
                        },
                        'card_number': {
                            validators: {
                                notEmpty: {
                                    message: 'Card member is required'
                                },
                                creditCard: {
                                    message: 'Card number is not valid'
                                }
                            }
                        },
                        'card_expiry_month': {
                            validators: {
                                notEmpty: {
                                    message: 'Month is required'
                                }
                            }
                        },
                        'card_expiry_year': {
                            validators: {
                                notEmpty: {
                                    message: 'Year is required'
                                }
                            }
                        },
                        'card_cvv': {
                            validators: {
                                notEmpty: {
                                    message: 'CVV is required'
                                },
                                digits: {
                                    message: 'CVV must contain only digits'
                                },
                                stringLength: {
                                    min: 3,
                                    max: 4,
                                    message: 'CVV must contain 3 to 4 digits only'
                                }
                            }
                        }
                    },

                    plugins: {
                        trigger: new FormValidation.plugins.Trigger(),
                        bootstrap: new FormValidation.plugins.Bootstrap5({
                            rowSelector: '.fv-row',
                            eleInvalidClass: '',
                            eleValidClass: ''
                        })
                    }
                }
            );

            // Action buttons
            submitButton.addEventListener('click', function (e) {
                // Prevent default button action
                e.preventDefault();

                // Validate form before submit
                if (validator) {
                    validator.validate().then(function (status) {
                        console.log('validated!');

                        if (status == 'Valid') {
                            // Show loading indication
                            submitButton.setAttribute('data-kt-indicator', 'on');

                            // Disable button to avoid multiple click
                            submitButton.disabled = true;

                            // Simulate form submission. For more info check the plugin's official documentation: https://sweetalert2.github.io/
                            setTimeout(function () {
                                // Remove loading indication
                                submitButton.removeAttribute('data-kt-indicator');

                                // Enable button
                                submitButton.disabled = false;
                                // Show popup confirmation
                                var formData = $(this).serialize();  // get form data
                                // Get the CSRF token from the cookie
                                function getCookie(name) {
                                    let cookieValue = null;
                                    if (document.cookie && document.cookie !== '') {
                                        const cookies = document.cookie.split(';');
                                        for (let i = 0; i < cookies.length; i++) {
                                            const cookie = cookies[i].trim();
                                            // Does this cookie string begin with the name we want?
                                            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                                                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                                                break;
                                            }
                                        }
                                    }
                                    return cookieValue;
                                }

                                const csrftoken = getCookie('csrftoken');

                                $.ajax({
                                    type: 'POST',
                                    headers: {
                                        'X-CSRFToken': csrftoken
                                    },
                                    url: '/ewallet/',
                                    data: formData,
                                    success: function (response) {
                                        console.log(message);  // log the response message
                                        Swal.fire({
                                            title: "Success!",
                                            text: response.message,
                                            icon: "success",
                                            confirmButtonText: "OK"
                                        })
                                    },
                                    error: function (response) {
                                        console.log(message);  // log the error message
                                        Swal.fire({
                                            title: "Error!",
                                            text: response.message,
                                            icon: "error",
                                            confirmButtonText: "OK"
                                        });
                                    }
                                });

                            }, 2000);
                        } else {
                            // Show popup warning. For more info check the plugin's official documentation: https://sweetalert2.github.io/
                            Swal.fire({
                                text: "1Sorry, looks like there are some errors detected, please try again.",
                                icon: "error",
                                buttonsStyling: false,
                                confirmButtonText: "Ok, got it!",
                                customClass: {
                                    confirmButton: "btn btn-primary"
                                }
                            });
                        }
                    });
                }
            });

            cancelButton.addEventListener('click', function (e) {
                e.preventDefault();
                validator.resetForm();
                validator.resetField(document.getElementById('card_expiry_month'));
                validator.resetField($('#card_expiry_year')[0]);
                form.reset(); // Reset form
                const monthSelect = document.getElementById("card_expiry_month");
                monthSelect.selectedIndex = 0;
                const yearSelect = document.getElementById("card_expiry_year");
                yearSelect.selectedIndex = 0;
                yearSelect.dispatchEvent(new Event('change')); // trigger change event to update select2 year
                monthSelect.dispatchEvent(new Event('change'));
            });


        }

        return {
            // Public functions
            init: function () {
                // Elements
                modalEl = document.querySelector('#kt_modal_new_card');

                if (!modalEl) {
                    return;
                }

                modal = new bootstrap.Modal(modalEl);

                form = document.querySelector('#kt_modal_new_card_form');
                submitButton = document.getElementById('kt_modal_new_card_submit');
                cancelButton = document.getElementById('kt_modal_new_card_cancel');

                initForm();
                handleForm();
            }
        };
    }();

// On document ready
    KTUtil.onDOMContentLoaded(function () {
        KTModalNewCard.init();
    });
    /******/
})()
;
//# sourceMappingURL=new-card.js.map