AOS.init({
    once: true,
});

document.addEventListener('DOMContentLoaded', () => {
	phoneInputs = document.querySelectorAll('.fb_phone');
	phoneInputs.forEach(function (input) {
		var phoneMask = IMask(input, {
			mask: '+{7} (000) 000-00-00'
		});
	});

	$('.fb_phone').on('input', function () {
		validatePhoneNumber($(this).val(), $(this));
	});

	function validatePhoneNumber(phoneNumber, phone_input) {
		var regex = /^\+7 \(\d{3}\) \d{3}-\d{2}-\d{2}$/;
		var isValid = regex.test(phoneNumber);

		if (isValid) {
			phone_input.removeClass("is-invalid");
		}
		else {
			phone_input.addClass("is-invalid")
		}
	}

	// ������ ������ �����
	var didScroll;
	var lastScrollTop = 0;
	var delta = 5;
	var navbarHeight = $('header').outerHeight();

	$(window).scroll(function(event){
		didScroll = true;
	});

	setInterval(function() {
		if (didScroll) {
			hasScrolled();
			didScroll = false;
		}
	}, 150);

	function hasScrolled() {
		var st = $(this).scrollTop();

		if(Math.abs(lastScrollTop - st) <= delta)
			return;

		if (st > lastScrollTop && st > navbarHeight){
			$('header').removeClass('nav-down').addClass('nav-up');
			document.getElementById('navbarNav').classList.remove('show');
		}
		else {
			if(st + $(window).height() < $(document).height()) {
				$('header').removeClass('nav-up').addClass('nav-down');
			}
		}
		lastScrollTop = st;
	};
})