var interest = (function($){

    function getParameterByName(name) {
        name = name.replace(/[\[]/, "\\[").replace(/[\]]/, "\\]");
        var regex = new RegExp("[\\?&]" + name + "=([^&#]*)"),
            results = regex.exec(location.search);
        return results === null ? "" : decodeURIComponent(results[1].replace(/\+/g, " "));
    }

    function stepSubmit(form, validate, success){
        form.submit(function(e){
            e.preventDefault();
            // Submit using ajax
            if (validate !== undefined){
                if (validate() === false){
                    return;
                }
            }
            if (location.search.indexOf('utm_') !== -1){
                var utm = 'utm_source=' + getParameterByName('utm_source')
                utm += '&utm_medium=' + getParameterByName('utm_medium')
                utm += '&utm_campaign=' + getParameterByName('utm_campaign')
                $(":input[name='utm']").val(utm);
            }
            $.ajax({
                type: "POST",
                url: form.attr("action"),
                data: form.serialize(),
            }).done(success);
        });
    }

    function checkInputType(){
        var input = $(":input[name='contact']");
        var emailRe = /^[\w\._]+@[\w\._]+$|^[\w\._]+@$|^[\w\._]+$/;
        var usPhoneRe = /^\+{0,1}[\d-]{1,16}$/;
        if (usPhoneRe.exec(input.val()) !== null) {
            console.log('is part of a mobile #');
            input.attr('type','tel');
        }
        else if (emailRe.exec(input.val()) !== null){
            console.log('is part of email');
            input.attr('type','email');
        }
        else {
            console.log('not an email address or phone number');
        }
    }

    /*function scrollTo(target){
        $('html,body').animate({
            scrollTop: target.offset().top - 98
        }, 1000);
    }*/

    stepSubmit($('#su-contact-form'), function(){
        var form = $('#su-contact-form');
        if ( $(":input[name='email']").val().length === 0 && $(":input[name='mobile']").val().length === 0 ) {
            $('#su-contact-form>.error').removeClass('hidden');
            return false;
        }
        return true;
    }, function(data){
        if (data.error !== undefined) {
            $('#su-contact-form>.error').removeClass('hidden');
        } else {
            // update hidden input with interest id in other forms
            $(":input[name='id']").val(data.id)
            $('#su-contact-form>.error').addClass('hidden');
            $('#su-contact-form').addClass("hidden");
            $('#su-contact-success').removeClass("hidden");
        }
    });
    stepSubmit($('#su-extra-form'), undefined, function(){
        $('#su-extra-form').hide();
        $('#su-extra-success, .close').removeClass('hidden');
        window.location.href = '#signup';
        $('.close').bind('click', function () {
            $('#su-contact-success h2').text('See you soon.');
            $('#su-contact-success p').hide();
            $('#su-contact-success a.btn').hide();
        });
    });

})(window.jQuery);
