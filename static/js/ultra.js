// Initialize particles (tsparticles)
document.addEventListener('DOMContentLoaded', function(){
  if(window.tsParticles){
    tsParticles.load('particles-js', {
      fpsLimit: 60,
      particles: {
        number: { value: 60 },
        color: { value: ['#ff6b88', '#8e6bff', '#ffe18d'] },
        shape: { type: 'circle' },
        opacity: { value: 0.7, random: { enable: true, minimumValue: 0.2 } },
        size: { value: { min: 1, max: 5 } },
        move: { enable: true, speed: 0.6, direction: 'none', outModes: { default: 'bounce' } },
        links: { enable: false }
      },
      interactivity: {
        events: {
          onhover: { enable: true, mode: 'repulse' },
          onclick: { enable: true, mode: 'push' }
        },
        modes: { repulse: { distance: 120 }, push: { quantity: 4 } }
      },
      detectRetina: true,
      background: { color: '' }
    });
  }

  // GSAP reveal for elements with .reveal
  gsap.registerPlugin(ScrollTrigger);
  const reveals = document.querySelectorAll('.reveal');
  reveals.forEach((el, i) => {
    gsap.to(el, {
      opacity: 1,
      y: 0,
      duration: 0.9,
      delay: i * 0.08,
      ease: 'power3.out',
      scrollTrigger: {
        trigger: el,
        start: 'top 85%'
      }
    });
  });

  // subtle floating animation for logo mark
  gsap.to('.logo-mark', { y: -6, repeat: -1, yoyo: true, duration: 3, ease: 'sine.inOut' });

  // parallax-like move for card on mouse move (desktop)
  const card = document.querySelector('.card-glass');
  if(card && window.matchMedia('(pointer:fine)').matches){
    document.addEventListener('mousemove', (e) => {
      const r = card.getBoundingClientRect();
      const cx = r.left + r.width/2;
      const cy = r.top + r.height/2;
      const dx = (e.clientX - cx) / r.width;
      const dy = (e.clientY - cy) / r.height;
      gsap.to(card, { rotationY: dx * 6, rotationX: dy * -6, duration: 0.6, transformPerspective:800, ease:'power3.out' });
    });
    document.addEventListener('mouseleave', ()=> gsap.to(card, { rotationY:0, rotationX:0, duration:0.6 }));
  }
});
