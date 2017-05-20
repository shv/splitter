jQuery(document).ready(function( $ ) {
	  "use strict";
	/* =========================
	   ScrollReveal
	   (on scroll fade animations)
	============================*/
	var revealConfig = { vFactor: 0.20 }
	window.sr = new scrollReveal(revealConfig);

	/* =========================
	   Detect Mobile Device
	============================*/
	var isMobile = {
	    Android: function() {
	        return navigator.userAgent.match(/Android/i);
	    },
	    BlackBerry: function() {
	        return navigator.userAgent.match(/BlackBerry/i);
	    },
	    iOS: function() {
	        return navigator.userAgent.match(/iPhone|iPad|iPod/i);
	    },
	    Opera: function() {
	        return navigator.userAgent.match(/Opera Mini/i);
	    },
	    Windows: function() {
	        return navigator.userAgent.match(/IEMobile/i);
	    },
	    any: function() {
	        return (isMobile.Android() || isMobile.BlackBerry() || isMobile.iOS() || isMobile.Opera() || isMobile.Windows());
	    }
	};

	/* ===========================
	   jQuery One Page Navigation
	==============================*/
	$('#main-nav').onePageNav({
	    filter: ':not(.external)'
	});

	$( ".expandable-gallery-item li" ).first().addClass( "selected" );
	$( ".section-tab .nav > li" ).first().addClass( "active" );
	$( ".section-tab .tab-content > .tab-pane" ).first().addClass( "active in" );
	$(window).stellar();
	$('.parallax-sections').stellar();
	/* ===========================
	   Custom Smooth Scroll For an Anchor
	==============================*/
	$(function() {
	  $('a.scroll-to[href*="#"]:not([href="#"])').click(function() {
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


	/* ===========================
	   Headhesive JS
	   (sticky header on scroll)
	==============================*/

	// Set headhesive options
    var options = {
        classes: {
            clone:   'header-clone',
            stick:   'header-stick',
            unstick: 'header-unstick'
        }
    };
	var headhesive = new Headhesive('.the-header', options);

	// Remove class of the clone header
	// so we can distinguish between the original and the clone header.
	$('.header-clone').removeClass('the-origin-header');


	/* ==========================
	   Progress Bar Animation
	=============================*/
	var skillbar = $('#skillbar').waypoint({
		handler: function() {
			$('.progress-bar').each(function(){
				$(this).animate({
					width:$(this).attr('data-percent')
				},500)
			})
		},
		offset: '150%'
	});

	/* =================================
	   Add Custom Class to Open Toggle Panel
	====================================*/
	$('.panel-heading a').click(function() {

		var clickElement = $(this);

		if (clickElement.parents('.panel-heading').is('.panel-active')) {
			$('.panel-heading').removeClass('panel-active');
		} else {
			$('.panel-heading').removeClass('panel-active');
			clickElement.parents('.panel-heading').addClass('panel-active');
		}
	});
	
		/* ===========================
	   Scroll to Top Button
	==============================*/
	$(window).scroll(function() {
        if($(this).scrollTop() > 100){
            $('#to-top').stop().animate({
                bottom: '30px'
                }, 750);
        }
        else{
            $('#to-top').stop().animate({
               bottom: '-100px'
            }, 750);
        }
    });

    $('#to-top').click(function() {
        $('html, body').stop().animate({
           scrollTop: 0
        }, 750, function() {
           $('#to-top').stop().animate({
               bottom: '-100px'
           }, 750);
        });
    });


	/* ==================================
	   Quicksand JS
	   (Filter team photo and portfolio)
	=====================================*/

	// Filter team photo
	var $teamClone = $("#team_grid").clone();

	$(".filter a").click(function(e){
		$(".filter li").removeClass("current");

		var $filterClass = $(this).parent().attr("class");

		if ($filterClass == "all") {
			var $filteredTeam = $teamClone.find("li");
		} else {
			var $filteredTeam = $teamClone.find("li[data-type~="+$filterClass+"]");
		}

		$("#team_grid").quicksand( $filteredTeam, {
			easing: "easeOutSine",
			adjustHeight: "dynamic",
			duration: 500,
			useScaling: true
		});

		$(this).parent().addClass("current");

		e.preventDefault();
	})

	// Filter Portfolio Gallery
	var $portfolioClone = $("#portfolio_grid").clone();

	$(".portfolio-filter a").click(function(e){
		$(".portfolio-filter li").removeClass("current");

		var $filterClass = $(this).parent().attr("class");

		if ($filterClass == "all") {
			var $filteredPortfolio = $portfolioClone.find("li");
		} else {
			var $filteredPortfolio = $portfolioClone.find("li[data-type~="+$filterClass+"]");
		}

		$("#portfolio_grid").quicksand( $filteredPortfolio, {
			easing: "easeOutSine",
			adjustHeight: "dynamic",
			duration: 500,
			useScaling: true
		});

		$(this).parent().addClass("current");

		e.preventDefault();
	})

	// Mobile Select Filter
	$("#mobile-team-filter").click(function(){
		$(this).toggleClass("select-active");
		$("ul.filter").toggleClass("filter-active");
	});

	$("#mobile-portfolio-filter").click(function(){
		$(this).toggleClass("select-active");
		$("ul.portfolio-filter").toggleClass("filter-active");
	});

	// Function to close the Notification
    $('a.notification-close').click(function(){
	    $(this).parent('div').fadeOut(200);
    });


	/* ==========================
	   Custom Popover
	   (for Language Selection)
	=============================*/
    $("[data-toggle=popover]").popover();



});



