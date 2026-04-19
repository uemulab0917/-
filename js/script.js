/* UEMULAB — Main Script */

(function () {
  'use strict';

  var header   = document.getElementById('header');
  var hamburger = document.getElementById('hamburger');
  var nav      = document.getElementById('nav');
  var pageTop  = document.getElementById('pageTop');
  var floatCta = document.getElementById('floatCta');

  /* ---- Header scroll ---- */
  function onScroll() {
    var y = window.scrollY;
    header.classList.toggle('scrolled', y > 20);
    pageTop.classList.toggle('visible', y > 500);
    if (floatCta) floatCta.style.display = y > 300 ? 'block' : 'none';
  }
  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();

  /* ---- Hamburger ---- */
  hamburger.addEventListener('click', function () {
    var isOpen = nav.classList.toggle('open');
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

  /* ---- Scroll animations ---- */
  var aosObserver = new IntersectionObserver(function (entries) {
    entries.forEach(function (entry) {
      if (entry.isIntersecting) {
        entry.target.classList.add('aos-animate');
        aosObserver.unobserve(entry.target);
      }
    });
  }, { threshold: 0.12, rootMargin: '0px 0px -50px 0px' });

  document.querySelectorAll('[data-aos]').forEach(function (el) {
    aosObserver.observe(el);
  });

  /* ---- Page top ---- */
  pageTop.addEventListener('click', function () {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  });

  /* ---- Smooth anchor scroll (offset for fixed header) ---- */
  document.querySelectorAll('a[href^="#"]').forEach(function (a) {
    a.addEventListener('click', function (e) {
      var target = document.querySelector(a.getAttribute('href'));
      if (!target) return;
      e.preventDefault();
      var offset = header.offsetHeight + 16;
      var top = target.getBoundingClientRect().top + window.scrollY - offset;
      window.scrollTo({ top: top, behavior: 'smooth' });
    });
  });

  /* ---- Active nav on scroll ---- */
  var sections  = document.querySelectorAll('section[id]');
  var navLinks  = document.querySelectorAll('.header__nav-link:not(.header__nav-link--cta)');

  var activeObs = new IntersectionObserver(function (entries) {
    entries.forEach(function (entry) {
      if (entry.isIntersecting) {
        navLinks.forEach(function (l) { l.classList.remove('active'); });
        var active = document.querySelector('.header__nav-link[href="#' + entry.target.id + '"]');
        if (active) active.classList.add('active');
      }
    });
  }, { rootMargin: '-40% 0px -50% 0px' });

  sections.forEach(function (s) { activeObs.observe(s); });

})();
