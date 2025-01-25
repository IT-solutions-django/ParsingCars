var swiper = new Swiper(".recomindation__swiper", {
    slidesPerView: 4,
    spaceBetween: 16,
    allowTouchMove: !1,
    navigation: {
        nextEl: ".swiper-button-next",
        prevEl: ".swiper-button-prev"
    },
    breakpoints: {
        1200: {
            slidesPerView: 3,
            allowTouchMove: !0,
            mousewheel: {
                sensitivity: 1
            },
            spaceBetween: 12
        },
        992: {
            slidesPerView: 2.1,
            allowTouchMove: !0,
            mousewheel: {
                sensitivity: 1
            },
            spaceBetween: 12
        },
        768: {
            slidesPerView: 1.1,
            allowTouchMove: !0,
            mousewheel: {
                sensitivity: 1
            },
            spaceBetween: 12
        }
    }
});
