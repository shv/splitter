jQuery(function($) {'use strict';
	$('a[data-referer-button]').click(function(){
		var referer_button = $(this).attr('data-referer-button'),
			args = "?impression_id="+impression_id;
			if (referer_button) {
				args = args+"&referer_button="+referer_button;
			};

		// alert(referer_button);
		$(this).attr('href', $(this).attr('href')+args);
		return true;
	});

	//Responsive Nav
	$('li.dropdown').find('.fa-angle-down').each(function(){
		$(this).on('click', function(){
			if( $(window).width() < 768 ) {
				$(this).parent().next().slideToggle();
			}
			return false;
		});
	});

	//Fit Vids
	if( $('#video-container').length ) {
		$('#video-container').fitVids();
	}

	//Initiat WOW JS
	new WOW().init();

	// portfolio filter
	$(window).load(function(){

		$('.main-slider').addClass('animate-in');
		$('.preloader').remove();
		//End Preloader

		if( $('.masonery_area').length ) {
			$('.masonery_area').masonry();//Masonry
		}

		var $portfolio_selectors = $('.portfolio-filter >li>a');
		
		if($portfolio_selectors.length) {
			
			var $portfolio = $('.portfolio-items');
			$portfolio.isotope({
				itemSelector : '.portfolio-item',
				layoutMode : 'fitRows'
			});
			
			$portfolio_selectors.on('click', function(){
				$portfolio_selectors.removeClass('active');
				$(this).addClass('active');
				var selector = $(this).attr('data-filter');
				$portfolio.isotope({ filter: selector });
				return false;
			});
		}

	});


	$('.timer').each(count);
	function count(options) {
		var $this = $(this);
		options = $.extend({}, options || {}, $this.data('countToOptions') || {});
		$this.countTo(options);
	}
		
	// Search
	$('.fa-search').on('click', function() {
		$('.field-toggle').fadeToggle(200);
	});

	// Contact form
	var form = $('#main-contact-form');
	form.submit(function(event){
		event.preventDefault();
		var form_status = $('<div class="form_status"></div>'),
			phone_number = form.find("input[name=phone]").val(),
			offer_id = form.find("input[name=offer_id]").val(),
			offer_info = form.find("input[name=offer_info]").val(),
			regex = /^\+\d\(\d\d\d\)\d\d\d\-\d\d\-\d\d$/;
		if (!regex.exec(phone_number)) {
			form.prepend( $('<div class="alert alert-danger fade in">'+
                             '<h4>Введите, пожалуйста, корректный номер телефона в формате +7(999)000-00-00</h4></div>').fadeIn() );
			try {
				yaCounterMain.reachGoal('submitIncorrectPhone', {"order_price": form.attr("data-price"), "currency":"RUB", "offer_id": offer_id, "phone_number": phone_number});
			} catch (err) {};
			return;
		};
		$.ajax({
			url: $(this).attr('action'),
			method: "POST",
	        headers: {
	            "X-CSRFToken": form.find("input[name=csrfmiddlewaretoken]").val()
	        },
			data: {
				CSRF: form.find("input[name=csrfmiddlewaretoken]").val(),
				phone: phone_number,
				offer_id: offer_id,
				offer_info: offer_info,
				page_id: form.find("input[name=page_id]").val(),
				impression_id: form.find("input[name=impression_id]").val(),
			},
			beforeSend: function(){
				form.find('.alert-danger').hide();
				form.prepend( form_status.html('<p><i class="fa fa-spinner fa-spin"></i> Заказ отправляется...</p>').fadeIn() );
			}
		}).done(function(data){
			form.replaceWith('<div class="alert alert-success fade in">'+
                             '<h4><center>Спасибо за заказ.</center></h4>'+
							 '<p>Номер вашего заказа: <strong>' + data.order_id +
							 '</strong>.<br />В самое ближайшее время с вами свяжется наш менеджер и уточнит детали заказа и адрес доставки.<br />'+
							 ' А пока желаем вам хорошего дня.</p>'+
							 '</div>');
			// try {
			// 	yaCounterMain.reachGoal('submitOrderSuccess', {"order_price": form.attr("data-price"), "currency":"RUB", "offer_id": offer_id, "order_id": data.order_id});
			// } catch (err) {};
		});
		try {
			yaCounterMain.reachGoal('submitOrder', {"order_price": form.attr("data-price"), "currency":"RUB", "offer_id": offer_id});
		} catch (err) {};

	});

	// Progress Bar
	$.each($('div.progress-bar'),function(){
		$(this).css('width', $(this).attr('data-transition')+'%');
	});

	if( $('#gmap').length ) {
		var map;

		map = new GMaps({
			el: '#gmap',
			lat: 43.04446,
			lng: -76.130791,
			scrollwheel:false,
			zoom: 16,
			zoomControl : false,
			panControl : false,
			streetViewControl : false,
			mapTypeControl: false,
			overviewMapControl: false,
			clickable: false
		});

		map.addMarker({
			lat: 43.04446,
			lng: -76.130791,
			animation: google.maps.Animation.DROP,
			verticalAlign: 'bottom',
			horizontalAlign: 'center',
			backgroundColor: '#3e8bff',
		});
	}

});