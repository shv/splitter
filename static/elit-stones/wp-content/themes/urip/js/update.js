jQuery(document).ready(function( $ ) {
	// Smooth Scroll for Original Navbar
	$(function() {
	  $('.the-origin-header .navbar-nav li a[href*="#"]:not([href="#"])').click(function() {
		if (location.pathname.replace(/^\//,'') == this.pathname.replace(/^\//,'') && location.hostname == this.hostname) {
		  var target = $(this.hash);
		  target = target.length ? target : $('[name=' + this.hash.slice(1) +']');
		  if (target.length) {
			$('html,body').animate({
			  scrollTop: target.offset().top - 50
			}, 1000);
			return false;
		  }
		}
	  });
	});

	// One Page Nav for Navbar
	$('.header-clone .navbar-nav').onePageNav({
		filter: ':not(.external)'
	});

	// Hide Mobile Nav Collapse On Click
	$('.navbar-nav a').on('click', function(){
		$(".navbar-toggle").click() //bootstrap 3.x by Richard
	});

	$( ".vc_tta-container" ).addClass( "container bootstrap container-vc-tabs" );
	
	var active = 'contact-trigger';
	$('a').removeClass('external').filter('a[rel^="'+active+'"]').addClass('contact-trigger');	
				
	/* ===============
	   Dropdown Menu
	==================*/
	$('ul.main-nav > li:has(ul)').addClass("dropdown");

    function dequeue(){
	$(this).dequeue();
	};

	$('ul.main-nav > li > a.external').click(function() {

		var checkElement = $(this).next();

		$('ul.main-nav li').removeClass('active');
		$(this).closest('li').addClass('active');

		if((checkElement.is('ul')) && (checkElement.is(':visible'))) {
			$(this).closest('li').removeClass('active');
			checkElement.slideUp(200, dequeue);
		}

		if((checkElement.is('ul')) && (!checkElement.is(':visible'))) {
			$('ul.main-nav ul:visible').slideUp('normal');
			checkElement.slideDown(200, dequeue);
		}

		if (checkElement.is('ul')) {
			return false;
		} else {
			return true;
		}
	});
				
	/* ===============
	   Dropdown Menu For new version
	==================*/
	$('ul.main-nav > li:has(ul)').addClass("dropdown");

    function dequeue(){
	$(this).dequeue();
	};

	$('ul.main-nav > li.menu-item-has-children > a').click(function() {

		var checkElement = $(this).next();

		$('ul.main-nav li').removeClass('active');
		$(this).closest('li').addClass('active');

		if((checkElement.is('ul')) && (checkElement.is(':visible'))) {
			$(this).closest('li').removeClass('active');
			checkElement.slideUp(200, dequeue);
		}

		if((checkElement.is('ul')) && (!checkElement.is(':visible'))) {
			$('ul.main-nav ul:visible').slideUp('normal');
			checkElement.slideDown(200, dequeue);
		}

		if (checkElement.is('ul')) {
			return false;
		} else {
			return true;
		}
	});
			
});