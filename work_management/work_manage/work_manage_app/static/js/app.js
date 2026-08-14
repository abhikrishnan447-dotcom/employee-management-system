(()=>{
  const loader=document.getElementById('page-loader');
  if(loader){
    const img=loader.querySelector('img');
    if(img&&img.src.includes('workspace-loader.svg'))img.src=img.src.replace('workspace-loader.svg','laptop-loader.svg');
  }
})();

document.addEventListener('DOMContentLoaded',()=>{
  const loader=document.getElementById('page-loader');
  const landingPage=window.location.pathname==='/'||window.location.pathname==='/home/';
  const minLoaderTime=landingPage?0:1000;
  const loaderStarted=performance.now();
  let hidden=false;
  let hideTimer=null;
  const finishLoader=()=>{
    if(!loader||hidden)return;
    hidden=true;
    if(hideTimer)clearTimeout(hideTimer);
    loader.classList.add('done');
  };
  const hideLoader=()=>{
    if(!loader||hidden)return;
    const elapsed=performance.now()-loaderStarted;
    const remaining=Math.max(0,minLoaderTime-elapsed);
    hideTimer=setTimeout(finishLoader,remaining);
  };
  const showLoader=()=>{
    if(!loader)return;
    hidden=false;
    if(hideTimer)clearTimeout(hideTimer);
    const img=loader.querySelector('img');
    if(img&&img.src.includes('workspace-loader.svg'))img.src=img.src.replace('workspace-loader.svg','laptop-loader.svg');
    loader.classList.remove('done');
  };
  if(loader){
    window.addEventListener('load',hideLoader,{once:true});
    hideLoader();
    setTimeout(finishLoader,landingPage?1500:5000);
  }
  window.addEventListener('pageshow',()=>{if(loader)finishLoader()});
  document.querySelectorAll('[data-sidebar-toggle]').forEach(b=>b.addEventListener('click',()=>document.querySelector('.app-sidebar')?.classList.toggle('show')));
  document.querySelectorAll('.alert').forEach(a=>setTimeout(()=>{a.classList.add('fade');setTimeout(()=>a.remove(),400)},4500));
  document.querySelectorAll('[data-confirm]').forEach(el=>el.addEventListener('click',e=>{if(!confirm(el.dataset.confirm))e.preventDefault()}));
  document.querySelectorAll('[data-progress]').forEach(el=>{const value=Math.max(0,Math.min(100,Number(el.dataset.progress)||0));el.style.width=value+'%';});
  const photo=document.querySelector('#profile_photo'),preview=document.querySelector('#photoPreview');
  if(photo&&preview)photo.addEventListener('change',()=>{const file=photo.files[0];if(file){preview.src=URL.createObjectURL(file);preview.style.display='block'}});
  document.querySelectorAll('.forgot-link').forEach(link=>{link.href='/forgot-password/';});

  const contactForm=document.querySelector('#contact-form');
  if(contactForm){
    contactForm.addEventListener('submit',async e=>{
      e.preventDefault();
      const status=contactForm.querySelector('.form-status');
      const button=contactForm.querySelector('button[type="submit"]');
      const formData=new FormData();
      formData.append('name',document.querySelector('#name')?.value.trim()||'');
      formData.append('email',document.querySelector('#email')?.value.trim()||'');
      formData.append('message',document.querySelector('#message')?.value.trim()||'');
      button?.setAttribute('disabled','disabled');
      if(status)status.textContent='Sending...';
      try{
        const response=await fetch('/visitor-message/',{method:'POST',body:formData,headers:{'X-Requested-With':'XMLHttpRequest'}});
        const data=await response.json();
        if(!response.ok)throw new Error(data.message||'Unable to send your message.');
        if(status)status.textContent=data.message;
        contactForm.reset();
      }catch(error){
        if(status)status.textContent=error.message||'Unable to send your message. Please try again.';
      }finally{
        button?.removeAttribute('disabled');
      }
    });
  }

  document.addEventListener('click',e=>{const link=e.target.closest('a[href]');if(!link||e.defaultPrevented||link.target==='_blank'||link.hasAttribute('download')||link.getAttribute('href')?.startsWith('#')||link.getAttribute('href')?.startsWith('javascript:')||link.closest('#page-loader')||link.matches('[data-no-loader]'))return;showLoader()});
  document.addEventListener('submit',e=>{if(e.defaultPrevented||e.target.matches('[data-no-loader]')||e.target.closest('#page-loader'))return;showLoader()});
});
