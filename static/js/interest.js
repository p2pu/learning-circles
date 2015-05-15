var interest = (function($){
    function stepSubmit(form, success){
        form.submit(function(e){
            e.preventDefault();
            // Submit using ajax
            /*if (!form[0].checkValidity()){
                alert('boo');
            }*/
            $.ajax({
                type: "POST",
                url: form.attr("action"), 
                data: form.serialize(),
            }).done(function(data){ success(data); });
        });
    }
    stepSubmit($('#su-contact-form'), function(data){
        // update hidden input with interest id in other forms
        $(":input[name='id']").val(data.id)
        $('#su-contact').addClass("hidden");
        $('#su-course').removeClass("hidden");
    });
    stepSubmit($('#su-course-form'), function(){
        $('#su-course').addClass("hidden");
        $('#su-location').removeClass("hidden");
    });
    stepSubmit($('#su-location-form'), function(){
        $('#su-location').addClass("hidden");
        $('#su-time').removeClass("hidden");
    });
    stepSubmit($('#su-time-form'), function(){
        $('#su-time').addClass("hidden");
        $('#su-thanks').removeClass("hidden");
    });
    
})(window.jQuery);
