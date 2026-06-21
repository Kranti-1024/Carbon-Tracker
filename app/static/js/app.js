/* =========================================================
   Carbon Ledger — app.js
   Core interaction engine: toasts, animations, counters,
   mobile menu, and category tab switching.
   ========================================================= */

document.addEventListener('DOMContentLoaded', () => {
  const prefersReduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* ---------------------------------------------------------
     1. Toast Notification System
     --------------------------------------------------------- */
  const toastContainer = document.getElementById('toastContainer');
  if (toastContainer) {
    const toasts = toastContainer.querySelectorAll('.toast');
    toasts.forEach((toast) => {
      const duration = parseInt(toast.dataset.autoDismiss) || 5000;
      const progressBar = toast.querySelector('.toast-progress');
      const closeBtn = toast.querySelector('.toast-close');

      // Set progress bar animation duration
      if (progressBar) {
        progressBar.style.animationDuration = duration + 'ms';
      }

      // Auto-dismiss
      const timer = setTimeout(() => dismissToast(toast), duration);

      // Close button
      if (closeBtn) {
        closeBtn.addEventListener('click', () => {
          clearTimeout(timer);
          dismissToast(toast);
        });
      }
    });
  }

  function dismissToast(toast) {
    toast.classList.add('dismiss');
    toast.addEventListener('animationend', () => toast.remove(), { once: true });
  }

  /* ---------------------------------------------------------
     2. Mobile Menu Toggle
     --------------------------------------------------------- */
  const menuToggle = document.getElementById('menuToggle');
  if (menuToggle) {
    menuToggle.addEventListener('click', () => {
      document.body.classList.toggle('nav-open');
    });

    // Close menu when clicking a nav link (mobile)
    const navLinks = document.querySelectorAll('#navLinks .nav-link, #navLinks .btn-nav');
    navLinks.forEach(link => {
      link.addEventListener('click', () => {
        document.body.classList.remove('nav-open');
      });
    });
  }

  /* ---------------------------------------------------------
     3. Scroll-triggered Animations (Intersection Observer)
     --------------------------------------------------------- */
  if (!prefersReduced) {
    const animElements = document.querySelectorAll('.anim-fade, .anim-slide');
    if (animElements.length > 0 && 'IntersectionObserver' in window) {
      const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
          if (entry.isIntersecting) {
            entry.target.classList.add('visible');
            observer.unobserve(entry.target);
          }
        });
      }, { threshold: 0.08, rootMargin: '0px 0px -40px 0px' });

      animElements.forEach(el => observer.observe(el));
    } else {
      // Fallback: make all visible immediately
      animElements.forEach(el => el.classList.add('visible'));
    }
  } else {
    // Reduced motion: show everything immediately
    document.querySelectorAll('.anim-fade, .anim-slide').forEach(el => {
      el.classList.add('visible');
    });
  }

  /* ---------------------------------------------------------
     4. Counter Animation
     --------------------------------------------------------- */
  if (!prefersReduced) {
    const counterElements = document.querySelectorAll('[data-value]');
    if (counterElements.length > 0 && 'IntersectionObserver' in window) {
      const counterObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
          if (entry.isIntersecting) {
            animateCounter(entry.target);
            counterObserver.unobserve(entry.target);
          }
        });
      }, { threshold: 0.5 });

      counterElements.forEach(el => counterObserver.observe(el));
    }
  } else {
    // Reduced motion: set final values immediately
    document.querySelectorAll('[data-value]').forEach(el => {
      el.textContent = el.dataset.value;
    });
  }

  function animateCounter(el) {
    const target = parseFloat(el.dataset.value);
    if (isNaN(target)) {
      el.textContent = el.dataset.value;
      return;
    }

    const suffix = el.dataset.suffix || '';
    const valueStr = el.dataset.value;
    const decimalPlaces = valueStr.includes('.') ? valueStr.split('.')[1].length : 0;
    const duration = 1200;
    const startTime = performance.now();

    function update(currentTime) {
      const elapsed = currentTime - startTime;
      const progress = Math.min(elapsed / duration, 1);

      // Ease out cubic
      const eased = 1 - Math.pow(1 - progress, 3);
      const current = target * eased;

      el.textContent = current.toFixed(decimalPlaces) + suffix;

      if (progress < 1) {
        requestAnimationFrame(update);
      } else {
        el.textContent = valueStr + suffix;
      }
    }

    requestAnimationFrame(update);
  }

  /* ---------------------------------------------------------
     5. Landing Page Gauge Animation
     --------------------------------------------------------- */
  const demoNumber = document.getElementById('demoNumber');
  const demoFill = document.getElementById('demoFill');

  if (demoNumber && demoFill) {
    const target = 7.6;
    const maxScale = 13;

    if (prefersReduced) {
      demoNumber.textContent = target.toFixed(1);
      demoFill.style.width = Math.min((target / maxScale) * 100, 100) + '%';
    } else {
      let current = 0;
      const steps = 50;
      const increment = target / steps;
      const interval = setInterval(() => {
        current += increment;
        if (current >= target) {
          current = target;
          clearInterval(interval);
        }
        demoNumber.textContent = current.toFixed(1);
        demoFill.style.width = Math.min((current / maxScale) * 100, 100) + '%';
      }, 25);
    }
  }

  /* ---------------------------------------------------------
     6. Category Tab Switching (log + edit pages)
     --------------------------------------------------------- */
  const categoryTabs = document.querySelector('.category-tabs');
  if (categoryTabs) {
    const tabs = categoryTabs.querySelectorAll('.cat-tab');
    const groups = document.querySelectorAll('.factor-group');

    tabs.forEach(tab => {
      tab.addEventListener('click', () => {
        const category = tab.dataset.category;

        tabs.forEach(t => t.classList.remove('active'));
        tab.classList.add('active');

        groups.forEach(g => {
          const isMatch = g.dataset.categoryGroup === category;
          g.classList.toggle('active', isMatch);
          const select = g.querySelector('select');
          if (select) {
            if (isMatch) {
              select.disabled = false;
              select.required = true;
            } else {
              select.disabled = true;
              select.required = false;
            }
          }
        });
      });
    });

    // Initialize: disable non-active selects on page load
    groups.forEach(g => {
      if (!g.classList.contains('active')) {
        const select = g.querySelector('select');
        if (select) {
          select.disabled = true;
          select.required = false;
        }
      }
    });
  }

  /* ---------------------------------------------------------
     7. Confirm Delete
     --------------------------------------------------------- */
  document.querySelectorAll('.delete-form').forEach(form => {
    form.addEventListener('submit', (e) => {
      if (!confirm('Remove this entry?')) {
        e.preventDefault();
      }
    });
  });
});
