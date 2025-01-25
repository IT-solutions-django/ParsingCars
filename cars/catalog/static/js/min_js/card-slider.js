window.onload = function() {
    let e = document.querySelectorAll(".main-slides > .gallery-slide"),
        l = document.querySelector(".thumbnail-slides"),
        t = e.length,
        i = document.querySelectorAll(".main-slides > .slider-controller-button"),
        r = document.querySelector(".all-slides-count"),
        a = document.querySelector(".curr-slide-count"),
        s = document.querySelector(".previous-slide-button"),
        d = document.querySelector(".next-slide-button"),
        n = t - 6;
    function o() {
        for (let e = 0; e < document.querySelectorAll(".main-slides > .CORRECT").length; e++)
            if ("none" !== window.getComputedStyle(document.querySelectorAll(".main-slides > .CORRECT")[e]).display && void 0 !== document.querySelectorAll(".main-slides > .CORRECT")[e])
                return e;
        return !1
    }
    function c(e, l) {
        document.querySelectorAll(".main-slides > .CORRECT")[e].style.display = "none",
        setTimeout(function() {}, l)
    }
    function u(e, l) {
        document.querySelectorAll(".main-slides > .CORRECT")[e].style.display = "block",
        setTimeout(function() {}, l)
    }
    t >= 2 && (a.innerText = 1, r.innerText = t, t >= 6 ? function t() {
        for (let i = 0; i < 6; i++) {
            var r = document.createElement("img");
            if (r.src = e[i].src, r.classList = e[i].classList, r.classList.remove("gallery-slide"), r.classList += " gallery-slide-thumbnail", r.width = 96, r.height = 90, 5 === i) {
                var a = document.createElement("div");
                a.classList += " ACTIVE gallery-slide-wrapper",
                a.appendChild(r),
                n >= 1 && (a.innerHTML += `<p class="remains">+${n}</p>`),
                l.appendChild(a)
            } else
                l.appendChild(r)
        }
    }() : function i() {
        document.querySelector(".thumbnail-slides").innerHTML = " ";
        for (let r = 0; r < t; r++) {
            var a = document.createElement("img");
            a.src = e[r].src,
            a.classList = e[r].classList,
            a.classList.remove("gallery-slide"),
            a.classList.remove("ACTIVE"),
            a.classList += " gallery-slide-thumbnail",
            a.width = 96,
            a.height = 90,
            l.appendChild(a)
        }
    }(), i.forEach(function(e) {
        e.style.display = "block"
    })),
    document.querySelectorAll(".thumbnail-slides > .gallery-slide-thumbnail"),
    d.addEventListener("click", function() {
        var l;
        let t = o(),
            i = (l = t) >= 0 && void 0 !== e[l + 1] && l + 1,
            r = 1e3 * window.getComputedStyle(e[t]).transitionDuration.replace("s", "");
        !1 !== t && !1 !== i && c(t, r),
        !1 !== i && (a.innerText = i <= e.length ? i + 1 : e.length, u(i, r))
    }),
    s.addEventListener("click", function() {
        var l;
        let t = o(),
            i = (l = t) >= 0 && void 0 !== e[l - 1] && l - 1,
            r = 1e3 * window.getComputedStyle(e[t]).transitionDuration.replace("s", "");
        !1 !== t && !1 !== i && c(t, r),
        !1 !== i && (a.innerText = i <= e.length ? t : e.length, u(i, r))
    });
    document.querySelector(".thumbnail-slides").addEventListener("click", function(l) {
        if ("IMG" === l.target.tagName) {
            let t = Array.prototype.indexOf.call(l.currentTarget.children, l.target),
                i = o(),
                r = 1e3 * window.getComputedStyle(e[0]).transitionDuration.replace("s", "");
            !1 !== i && (c(i, r), console.log(i)),
            t >= 0 && (a.innerText = i <= e.length ? t + 1 : e.length, u(t, r))
        }
    });
    let m = document.querySelectorAll(".main-slides > .gallery-slide"),
        y = document.querySelectorAll(".main-slides > .CORRECT"),
        h = document.querySelector(".modal-gallery"),
        g = document.querySelector(".modal-gallery > .modal-gallery-main > .modal-gallery-slider"),
        S = document.querySelector(".modal-thumbnail");
    for (let b = 0; b < y.length; b++) {
        let f = document.createElement("img");
        f.src = y[b].src,
        f.classList = `modal-gallery-slide modal-slide-${b}`,
        g.appendChild(f)
    }
    if (y.length >= 2)
        for (let q = 0; q < y.length; q++) {
            let v = document.createElement("img");
            v.src = y[q].src,
            v.setAttribute("data-number", `${q}`),
            v.classList = `modal-thumbnail-slide thumbnail-slide-${q}`,
            S.appendChild(v)
        }
    function p(e, l) {
        document.querySelector(`.modal-slide-${e}`).style.display = "none",
        setTimeout(function() {}, l)
    }
    function L(e, l) {
        document.querySelector(`.modal-slide-${e}`).style.display = "block",
        setTimeout(function() {}, l)
    }
    function E() {
        for (let e = 0; e < document.querySelectorAll(".modal-gallery-slider > .modal-gallery-slide").length; e++)
            if ("none" !== window.getComputedStyle(document.querySelectorAll(".modal-gallery-slider > .modal-gallery-slide")[e]).display && void 0 !== document.querySelectorAll(".modal-gallery-slider > .modal-gallery-slide")[e])
                return e;
        return !1
    }
    document.querySelector(".modal-gallery-btn--close").addEventListener("click", () => {
        p(E()),
        h.style.display = "none",
        document.querySelectorAll(".modal-thumbnail-slide").forEach(e => {
            e.classList.remove("modal-thumbnail-slide--active")
        })
    }),
    m.forEach(e => {
        e.addEventListener("click", () => {
            let e = o();
            document.querySelectorAll(".modal-thumbnail-slide")[e].classList.add("modal-thumbnail-slide--active"),
            h.style.display = "block",
            L(e)
        })
    }),
    document.querySelectorAll(".modal-thumbnail-slide").forEach(e => {
        e.addEventListener("click", e => {
            let l = E();
            document.querySelectorAll(".modal-thumbnail-slide").forEach(e => {
                e.classList.remove("modal-thumbnail-slide--active")
            }),
            e.target.classList.add("modal-thumbnail-slide--active");
            let t = parseInt(e.target.dataset.number);
            p(l),
            L(t)
        })
    }),
    document.querySelector(".modal-gallery-btn--next").addEventListener("click", () => {
        var e;
        let l = E(),
            t = (e = l) >= 0 && void 0 !== document.querySelectorAll(".modal-gallery-slider > .modal-gallery-slide")[e + 1] && e + 1;
        document.querySelectorAll(".modal-thumbnail-slide").forEach(e => {
            e.classList.remove("modal-thumbnail-slide--active")
        }),
        document.querySelectorAll(".modal-thumbnail-slide")[t].classList.add("modal-thumbnail-slide--active"),
        L(t),
        p(l)
    }),
    document.querySelector(".modal-gallery-btn--prev").addEventListener("click", () => {
        var e;
        let l = E(),
            t = (e = l, console.log(typeof document.querySelectorAll(".modal-gallery-slider > .modal-gallery-slide")[e - 1]), e >= 0 && void 0 !== document.querySelectorAll(".modal-gallery-slider > .modal-gallery-slide")[e - 1] && e - 1);
        document.querySelectorAll(".modal-thumbnail-slide").forEach(e => {
            e.classList.remove("modal-thumbnail-slide--active")
        }),
        document.querySelectorAll(".modal-thumbnail-slide")[t].classList.add("modal-thumbnail-slide--active"),
        L(t),
        p(l)
    }),
    console.log("undefind" != typeof document.querySelector(".thumbnail-slides > .ACTIVE")),
    "undefind" != typeof document.querySelector(".thumbnail-slides > .ACTIVE") && document.querySelector(".thumbnail-slides > .ACTIVE").addEventListener("click", () => {
        !function i() {
            document.querySelector(".thumbnail-slides").innerHTML = " ";
            c(o()),
            u(5);
            for (let r = 0; r < t; r++) {
                var a = document.createElement("img");
                a.src = e[r].src,
                a.classList = e[r].classList,
                a.classList.remove("gallery-slide"),
                a.classList.remove("ACTIVE"),
                a.classList += " gallery-slide-thumbnail",
                a.width = 96,
                a.height = 90,
                l.appendChild(a)
            }
        }()
    })
};
