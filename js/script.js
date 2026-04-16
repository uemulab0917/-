/* UEMULAB GYM — Main Script */

(function () {
  'use strict';

  /* ---- Header scroll effect ---- */
  const header = document.getElementById('header');
  function onScroll() {
    header.classList.toggle('scrolled', window.scrollY > 20);
    pageTop.classList.toggle('visible', window.scrollY > 400);
  }
  window.addEventListener('scroll', onScroll, { passive: true });

  /* ---- Hamburger menu ---- */
  const hamburger = document.getElementById('hamburger');
  const nav = document.getElementById('nav');

  hamburger.addEventListener('click', function () {
    const isOpen = nav.classList.toggle('open');
    hamburger.classList.toggle('active', isOpen);
    document.body.style.overflow = isOpen ? 'hidden' : '';
  });

  nav.querySelectorAll('.header__nav-link').forEach(function (link) {
    link.addEventListener('click', function () {
      nav.classList.remove('open');
      hamburger.classList.remove('active');
      document.body.style.overflow = '';
    });
  });

  /* ---- Scroll animations (AOS-like) ---- */
  const aosEls = document.querySelectorAll('[data-aos]');
  const aosObserver = new IntersectionObserver(function (entries) {
    entries.forEach(function (entry) {
      if (entry.isIntersecting) {
        entry.target.classList.add('aos-animate');
        aosObserver.unobserve(entry.target);
      }
    });
  }, { threshold: 0.15, rootMargin: '0px 0px -60px 0px' });

  aosEls.forEach(function (el) {
    aosObserver.observe(el);
  });

  /* ---- Counter animation ---- */
  function animateCounter(el, target, duration) {
    var start = 0;
    var step = target / (duration / 16);
    var timer = setInterval(function () {
      start += step;
      if (start >= target) {
        start = target;
        clearInterval(timer);
      }
      el.textContent = Math.floor(start).toLocaleString();
    }, 16);
  }

  var counterObserver = new IntersectionObserver(function (entries) {
    entries.forEach(function (entry) {
      if (entry.isIntersecting) {
        var el = entry.target;
        var target = parseInt(el.textContent, 10);
        animateCounter(el, target, 1600);
        counterObserver.unobserve(el);
      }
    });
  }, { threshold: 0.5 });

  document.querySelectorAll('.counter').forEach(function (el) {
    counterObserver.observe(el);
  });

  /* ---- FAQ accordion ---- */
  document.querySelectorAll('.faq__q').forEach(function (btn) {
    btn.addEventListener('click', function () {
      var expanded = btn.getAttribute('aria-expanded') === 'true';
      /* close all */
      document.querySelectorAll('.faq__q').forEach(function (b) {
        b.setAttribute('aria-expanded', 'false');
        b.nextElementSibling.classList.remove('open');
      });
      /* open clicked if was closed */
      if (!expanded) {
        btn.setAttribute('aria-expanded', 'true');
        btn.nextElementSibling.classList.add('open');
      }
    });
  });

  /* ---- Page top button ---- */
  var pageTop = document.getElementById('pageTop');
  pageTop.addEventListener('click', function () {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  });

  /* ---- Contact form (front-end only) ---- */
  var form = document.getElementById('contactForm');
  if (form) {
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var valid = form.checkValidity();
      if (!valid) {
        form.reportValidity();
        return;
      }
      var btn = form.querySelector('[type="submit"]');
      btn.textContent = '送信中...';
      btn.disabled = true;
      setTimeout(function () {
        form.innerHTML =
          '<div style="text-align:center;padding:60px 20px;">' +
          '<p style="font-family:var(--font-serif);font-size:1.6rem;color:var(--gold);margin-bottom:16px;">✓ 送信完了</p>' +
          '<p style="color:var(--mid);font-size:.9rem;line-height:1.9;">お問い合わせありがとうございます。<br/>2営業日以内にご連絡いたします。</p>' +
          '</div>';
      }, 1200);
    });
  }

  /* ---- Smooth anchor scroll (offset for fixed header) ---- */
  document.querySelectorAll('a[href^="#"]').forEach(function (a) {
    a.addEventListener('click', function (e) {
      var target = document.querySelector(a.getAttribute('href'));
      if (!target) return;
      e.preventDefault();
      var offset = header.offsetHeight + 20;
      var top = target.getBoundingClientRect().top + window.scrollY - offset;
      window.scrollTo({ top: top, behavior: 'smooth' });
    });
  });

  /* ---- Active nav highlight on scroll ---- */
  var sections = document.querySelectorAll('section[id]');
  var navLinks = document.querySelectorAll('.header__nav-link:not(.header__nav-link--cta)');

  var activeObserver = new IntersectionObserver(function (entries) {
    entries.forEach(function (entry) {
      if (entry.isIntersecting) {
        navLinks.forEach(function (l) { l.classList.remove('active'); });
        var active = document.querySelector('.header__nav-link[href="#' + entry.target.id + '"]');
        if (active) active.classList.add('active');
      }
    });
  }, { rootMargin: '-40% 0px -50% 0px' });

  sections.forEach(function (s) { activeObserver.observe(s); });

})();
