(function(){
  // Lightweight lazy loader: looks for images with data-lazy="true" and swaps data-src/data-srcset into src/srcset
  const lazyImages = [].slice.call(document.querySelectorAll('img[data-lazy="true"]'));
  if('IntersectionObserver' in window && lazyImages.length>0){
    const io = new IntersectionObserver((entries, obs)=>{
      entries.forEach(entry=>{
        if(entry.isIntersecting){
          const img = entry.target;
          if(img.dataset.src){ img.src = img.dataset.src; }
          if(img.datasetSrcset || img.dataset.srcset){ img.srcset = img.dataset.srcset || img.datasetSrcset; }
          if(img.dataset.sizes){ img.sizes = img.dataset.sizes; }
          img.classList.remove('lazyload');
          img.removeAttribute('data-lazy');
          obs.unobserve(img);
        }
      });
    }, {rootMargin: '200px 0px', threshold: 0.01});

    lazyImages.forEach(img => io.observe(img));
    return;
  }

  // Fallback: load all images immediately
  lazyImages.forEach(img=>{
    if(img.dataset.src){ img.src = img.dataset.src; }
    if(img.dataset.srcset){ img.srcset = img.dataset.srcset; }
    if(img.dataset.sizes){ img.sizes = img.dataset.sizes; }
    img.classList.remove('lazyload');
    img.removeAttribute('data-lazy');
  });
})();
