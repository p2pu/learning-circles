var interest = (function($){
    function stepSubmit(form, validate, success){
        form.submit(function(e){
            e.preventDefault();
            // Submit using ajax
            if (validate !== undefined){
                if (validate() === false){
                    return;
                }
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

    function scrollTo(target){
        $('html,body').animate({
            scrollTop: target.offset().top - 98
        }, 1000);
    }

    stepSubmit($('#su-contact-form'), function(){
        var form = $('#su-contact-form');
        if ( $(":input[name='email']").val().length === 0 && $(":input[name='mobile']").val().length === 0 ) {
            $('#su-contact-form>.error').removeClass('hidden');
            return false;
        }
        return true;
    }, function(data){
        // update hidden input with interest id in other forms
        if (data.error !== undefined) {
            $('#su-contact');
        } else {
            $(":input[name='id']").val(data.id)
            $('#su-contact').addClass("hidden");
            $('#su-course').removeClass("hidden");
            scrollTo($('#su-course'));
        }
    });
    stepSubmit($('#su-course-form'), undefined, function(){
        $('#su-course').addClass("hidden");
        $('#su-location').removeClass("hidden");
        scrollTo($('#su-location'));
    });
    stepSubmit($('#su-location-form'), undefined, function(){
        $('#su-location').addClass("hidden");
        $('#su-time').removeClass("hidden");
        scrollTo($('#su-time'));
    });
    stepSubmit($('#su-time-form'), undefined, function(){
        $('#su-time').addClass("hidden");
        $('#su-thanks').removeClass("hidden");
        scrollTo($('#su-thanks'));
    });


    //$(":input[name='contact']").on('blur', checkInputType);
    
})(window.jQuery);
