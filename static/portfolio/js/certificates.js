(function(){
  // IntersectionObserver reveal
  const observer = new IntersectionObserver((entries)=>{
    entries.forEach(e=>{
      if(e.isIntersecting){
        e.target.classList.add('revealed');
        observer.unobserve(e.target);
      }
    })
  },{threshold:0.08});

  document.querySelectorAll('.cert-card').forEach(el=>observer.observe(el));

  // Lightbox functionality
  const lightbox = document.getElementById('lightbox');
  const lbImage = document.getElementById('lb-image');
  const lbCaption = document.getElementById('lb-caption');
  const lbClose = document.getElementById('lb-close');
  const lbPrev = document.getElementById('lb-prev');
  const lbNext = document.getElementById('lb-next');
  const cards = Array.from(document.querySelectorAll('.cert-card'));
  // If the certificates markup isn't on this page, bail out silently
  if(!lightbox || !lbImage || !lbClose) return;
  let currentIndex = 0;

  function openLightbox(index){
    const cert = window.CERTIFICATES[index];
    if(!cert) return;
    currentIndex = index;
    lbImage.src = cert.image_url;
    lbImage.alt = cert.title;
    lbCaption.textContent = cert.title + (cert.issuer? (' — ' + cert.issuer):'');
    lightbox.setAttribute('aria-hidden','false');
    document.body.style.overflow = 'hidden';
  }
  function closeLightbox(){
    lightbox.setAttribute('aria-hidden','true');
    lbImage.src = '';
    document.body.style.overflow = '';
  }
  function prev(){openLightbox((currentIndex-1+cards.length)%cards.length)}
  function next(){openLightbox((currentIndex+1)%cards.length)}

  cards.forEach((card, idx)=>{
    card.addEventListener('click',()=>openLightbox(idx));
    card.addEventListener('keydown',(ev)=>{ if(ev.key==='Enter' || ev.key===' ') openLightbox(idx) });
    // parallax on mouse move
    const img = card.querySelector('.cert-thumb');
    card.addEventListener('mousemove',(e)=>{
      const r = card.getBoundingClientRect();
      const x = (e.clientX - r.left)/r.width - 0.5;
      const y = (e.clientY - r.top)/r.height - 0.5;
      img.style.transform = `translate(${x*8}px,${y*6}px) scale(1.03)`;
    });
    card.addEventListener('mouseleave',()=>{ img.style.transform='scale(1)'; });
  });

  lbClose.addEventListener('click', closeLightbox);
  lbPrev.addEventListener('click', prev);
  lbNext.addEventListener('click', next);

  // close when clicking on backdrop (but not when clicking inside lb-content)
  lightbox.addEventListener('click', function(e){
    if(e.target === lightbox) closeLightbox();
  });

  // keyboard navigation
  document.addEventListener('keydown',(e)=>{
    if(lightbox.getAttribute('aria-hidden')==='false'){
      if(e.key==='Escape') closeLightbox();
      if(e.key==='ArrowLeft') prev();
      if(e.key==='ArrowRight') next();
    }
  });

  // zoom on wheel
  let scale = 1;
  lbImage.addEventListener('wheel',(e)=>{
    e.preventDefault();
    const delta = -e.deltaY*0.0012;
    scale = Math.min(3, Math.max(0.6, scale + delta));
    lbImage.style.transform = `scale(${scale})`;
  });
  // reset scale on close or image change
  const resetScale = ()=>{ scale=1; lbImage.style.transform='scale(1)'; };
  lbPrev.addEventListener('click', resetScale);
  lbNext.addEventListener('click', resetScale);
  lbClose.addEventListener('click', resetScale);

})();
