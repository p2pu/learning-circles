/*global location, jQuery, window, console */


var P2PU = window.P2PU || {};

(function ($, P2PU) {

    'use strict';


    var init = function () {
        $(function () {
            // Smoth scrolling
            $('.navbar-nav a[href*=#]:not([href=#])').click(function () {
                if (location.pathname.replace(/^\//, '') === this.pathname.replace(/^\//, '') && location.hostname === this.hostname) {
                    var target = $(this.hash);
                    target = target.length ? target : $('[name=' + this.hash.slice(1) + ']');
                    if (target.length) {
                        $('html,body').animate({
                            scrollTop: target.offset().top - 98
                        }, 1000);
                        return false;
                    }
                }
            });

            function equalHeight(group) {    
                var tallest = 0;    
                group.each(function() {       
                    var thisHeight = $(this).height();       
                    if(thisHeight > tallest) {          
                        tallest = thisHeight;       
                    }    
                });    
                group.each(function() { $(this).height(tallest); });
            } 

            $(document).ready(function() {   
                equalHeight($(".thumbnail").parent()); 
            });
        });
    };

    P2PU.Splash = {};
    P2PU.Splash.init = init;

}(jQuery, P2PU));
