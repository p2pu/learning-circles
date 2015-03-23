/*global jQuery, window, console */


var P2PU = window.P2PU || {};

(function ($, P2PU) {

	'use strict';


	var init = function () {
		$(function () {
			// Index calculation height
			//$('.splash').css('height', $( window ).height());

			// p2pu tab
			$(".p2pu-tab").p2puSlider({
				navbarContainer: '.navbar',
				icon: '.p2pu-tab-icon',
				iconUp: 'fa fa-chevron-down',
				iconDown: 'fa fa-chevron-up'
			});

			// Smoth scrolling
			$('a[href*=#]:not([href=#])').click(function () {
				if (location.pathname.replace(/^\//, '') === this.pathname.replace(/^\//, '') && location.hostname === this.hostname) {
					var target = $(this.hash);
					target = target.length ? target : $('[name=' + this.hash.slice(1) + ']');
					if (target.length) {
						$('html,body').animate({
							scrollTop: target.offset().top - 0
						}, 1000);
						return false;
					}
				}
			});
		});
	};

	P2PU.Splash = {};
	P2PU.Splash.init = init;

}(jQuery, P2PU));