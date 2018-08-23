/*global location, jQuery, window, console */

var P2PU = window.P2PU || {};

(function ($, P2PU) {

    'use strict';


    var init = function () {
        $('body').css("padding-bottom", $('footer').height());

        $(function () {
            // Smoth scrolling
            $('a[href*=#]:not([href=#],[href=#interest-extra],[data-toggle="collapse"])').click(function () {
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
        });
        $('input[type=url]').keyup(function () {
            if (($(this).val().length >=5) && ($(this).val().substr(0, 5) != 'http:') && ($(this).val().substr(0, 5) != 'https') ) {
                $(this).val('http://' + $(this).val());
            }
        });
    };

    P2PU.Splash = {};
    P2PU.Splash.init = init;

}(jQuery, P2PU));
