document.addEventListener('DOMContentLoaded',()=>{
  const nav=document.querySelector('.navbar');
  addEventListener('scroll',()=>nav.classList.toggle('scrolled',scrollY>30));

  const observer=new IntersectionObserver(entries=>entries.forEach(e=>{
    if(e.isIntersecting){
      e.target.classList.add('visible');
      observer.unobserve(e.target);
    }
  }),{threshold:.12});
  document.querySelectorAll('.reveal').forEach(el=>observer.observe(el));

  const stats=document.querySelector('.stats');
  let counted=false;
  if(stats){
    new IntersectionObserver(es=>{
      if(es[0].isIntersecting&&!counted){
        counted=true;
        document.querySelectorAll('[data-count]').forEach(el=>{
          const target=+el.dataset.count,suffix=el.dataset.suffix||'',duration=1400,start=performance.now();
          const tick=now=>{
            const n=Math.min(1,(now-start)/duration);
            el.textContent=Math.floor((1-Math.pow(1-n,3))*target).toLocaleString()+suffix;
            if(n<1)requestAnimationFrame(tick);
          };
          requestAnimationFrame(tick);
        });
      }
    },{threshold:.35}).observe(stats);
  }

  document.querySelectorAll('a[href^="#"]').forEach(a=>a.addEventListener('click',()=>{
    const menu=document.querySelector('.navbar-collapse');
    if(menu?.classList.contains('show'))bootstrap.Collapse.getOrCreateInstance(menu).hide();
  }));

  const contactForm=document.getElementById('contact-form');
  if(contactForm){
    contactForm.addEventListener('submit',async e=>{
      e.preventDefault();
      const form=e.currentTarget;
      const status=form.querySelector('.form-status');
      const button=form.querySelector('button[type="submit"]');

      if(!form.checkValidity()){
        status.textContent='Please complete all fields with a valid email address.';
        form.reportValidity();
        return;
      }

      button?.setAttribute('disabled','disabled');
      if(status)status.textContent='Sending...';

      try{
        const formData=new FormData();
        formData.append('name',form.querySelector('#name')?.value.trim()||'');
        formData.append('email',form.querySelector('#email')?.value.trim()||'');
        formData.append('message',form.querySelector('#message')?.value.trim()||'');

        const response=await fetch('/visitor-message/',{
          method:'POST',
          body:formData,
          headers:{'X-Requested-With':'XMLHttpRequest'}
        });
        const data=await response.json();
        if(!response.ok)throw new Error(data.message||'Unable to send your message.');
        if(status)status.textContent=data.message||'Your message has been sent successfully.';
        form.reset();
      }catch(error){
        if(status)status.textContent=error.message||'Unable to send your message. Please try again.';
      }finally{
        button?.removeAttribute('disabled');
      }
    });
  }
});
