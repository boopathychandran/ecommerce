document.addEventListener('DOMContentLoaded', function() {
  // Progress step helper: activate step by index (0-based)
  window.checkout = window.checkout || {};
  window.checkout.setStep = function(idx){
    var steps = Array.prototype.slice.call(document.querySelectorAll('.checkout-step'));
    steps.forEach(function(el, i){
      var isActive = (i === idx);
      el.classList.toggle('active', isActive);
      // animate using GSAP if available
      if(window.gsap){
        if(isActive){
          gsap.to(el, {scale:1.03, duration:0.28, ease: 'power2.out'});
          gsap.fromTo(el, {y:6, opacity:0.92}, {y:0, opacity:1, duration:0.32, ease:'power2.out'});
        } else {
          gsap.to(el, {scale:1, duration:0.18, ease:'power2.out'});
          gsap.to(el, {opacity:0.92, duration:0.18, ease:'power2.out'});
        }
      }
    });
  }

  // Address form validation + submit UX
  var addressForm = document.querySelector('form[data-checkout="address"]');
  if(addressForm){
    addressForm.addEventListener('submit', function(e){
      // simple required checks
      var required = addressForm.querySelectorAll('input[required], textarea[required]');
      var valid = true;
      required.forEach(function(inp){
        if(!inp.value.trim()){
          inp.classList.add('invalid');
          valid = false;
        } else {
          inp.classList.remove('invalid');
        }
      });
      if(!valid){
        e.preventDefault();
        // focus first invalid
        var first = addressForm.querySelector('.invalid');
        if(first) first.focus();
        // tiny shake effect
        addressForm.classList.add('shake');
        setTimeout(function(){ addressForm.classList.remove('shake'); }, 400);
        return false;
      }
      // disable submit and show loading
      var btn = addressForm.querySelector('button[type=submit]');
      if(btn){
        btn.classList.add('btn-loading');
      }
    });
  }

  // Payment button UX: show spinner and disable while checkout opens
  var rzpBtn = document.getElementById('rzp-button');
  if(rzpBtn){
    rzpBtn.addEventListener('click', function(){
      rzpBtn.classList.add('btn-loading');
      if(window.gsap){
        gsap.fromTo(rzpBtn.querySelector('.spinner')||rzpBtn, {rotation:0}, {rotation:360, duration:0.8, repeat: -1, ease:'linear'});
      }
      setTimeout(function(){ 
        rzpBtn.classList.remove('btn-loading'); 
        if(window.gsap && rzpBtn.querySelector('.spinner')) gsap.killTweensOf(rzpBtn.querySelector('.spinner'));
      }, 6000); // safety
    });
  }

});
