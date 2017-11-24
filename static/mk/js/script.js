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


    var form = $('#main-contact-form');
    form.submit(function(event){
        event.preventDefault();
        var form_status = $('<div class="form_status"></div>'),
            phone_number = form.find("input[name=phone]").val(),
            fio = form.find("input[name=fio]").val(),
            offer_id = form.find("input[name=offer_id]").val(),
            offer_info = form.find("[name=offer_info]").val(),
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
                fio: fio,
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
            //  yaCounterMain.reachGoal('submitOrderSuccess', {"order_price": form.attr("data-price"), "currency":"RUB", "offer_id": offer_id, "order_id": data.order_id});
            // } catch (err) {};
        });
        try {
            yaCounterMain.reachGoal('submitOrder', {"order_price": form.attr("data-price"), "currency":"RUB", "offer_id": offer_id});
        } catch (err) {};

    });
});
/*=================================
||          Owl Carousel
==================================*/
    $("#header-slider").owlCarousel({

        navigation : true, // Show next and prev buttons
        slideSpeed : 100,
        paginationSpeed : 400,
        singleItem: true,
        autoPlay: true,
        pagination: false,

        // "singleItem:true" is a shortcut for:
        // items : 1, 
        // itemsDesktop : false,
        // itemsDesktopSmall : false,
        // itemsTablet: false,
        // itemsMobile : false

    });

/*=================================
||          WOW
==================================*/
wow = new WOW(
    {
      boxClass:     'wow',      // default
      animateClass: 'animated', // default
      offset:       0,          // default
      mobile:       true,       // default
      live:         true        // default
    }
  )
wow.init();

/*=================================
||          Smooth Scrooling
==================================*/
    $(function() {
        $('a[href*=#]:not([href=#])').click(function() {
            if (location.pathname.replace(/^\//,'') == this.pathname.replace(/^\//,'') && location.hostname == this.hostname) {
                var target = $(this.hash);
                target = target.length ? target : $('[name=' + this.hash.slice(1) +']');
                if (target.length) {
                    $('html,body').animate({
                        scrollTop: (target.offset().top - 9)//top navigation height
                    }, 1000);
                    return false;
                }
            }
        });
    });

    
/*====================================================================
            Navbar shrink script
======================================================================*/
$(document).ready(function() {
    $(window).scroll(function() {
        if ($(document).scrollTop() > 50) {
            $('nav').addClass('shrink');
        } 
        else {
            $('nav').removeClass('shrink');
        }
    });
});


$(document).ready(function(){
    $(window).scroll(function() {
        if ($(document).scrollTop() > 50) {
            $("#logo").attr("src", $("#logo").attr("data-logo-stick"))
        }
        else {
             $("#logo").attr("src", $("#logo").attr("data-logo-main"))
        }
    });
});
/*=================================================================
            Load more button
===================================================================*/

$(document).ready(function () {
    $("#loadMenuContent").click(function(event) {
        
        $.get("php/ajax_menu.html", function(data){
            $('#moreMenuContent').append(data);
        });
        event.preventDefault();
        $(this).hide();
    }) ;
});

$(document).ready(function () {

    var $menuPricing = $('#menu-pricing');
    $menuPricing.mixItUp({
        selectors: {
            target: 'li'
        }
    });

});


/*=================================================
        Showing Icon in placeholder
=====================================================*/

$('.iconified').on('keyup', function() {
    var input = $(this);
    if(input.val().length === 0) {
        input.addClass('empty');
    } else {
        input.removeClass('empty');
    }
});

/*=========================================================
                Scroll  Speed
=======================================================*/

$(function() {  
    jQuery.scrollSpeed(100, 1000);
});