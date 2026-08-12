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
  const showLoader=()=>{
    if(!loader)return;
    const img=loader.querySelector('img');
    if(img&&img.src.includes('workspace-loader.svg'))img.src=img.src.replace('workspace-loader.svg','laptop-loader.svg');
    loader.classList.remove('done');
  };
  const hideLoader=()=>{
    if(!loader)return;
    const elapsed=performance.now()-loaderStarted;
    const remaining=Math.max(0,minLoaderTime-elapsed);
    setTimeout(()=>loader.classList.add('done'),remaining);
  };
  if(loader){
    if(document.readyState==='complete')hideLoader();
    else window.addEventListener('load',hideLoader,{once:true});
  }
  document.querySelectorAll('[data-sidebar-toggle]').forEach(b=>b.addEventListener('click',()=>document.querySelector('.app-sidebar')?.classList.toggle('show')));
  document.querySelectorAll('.alert').forEach(a=>setTimeout(()=>{a.classList.add('fade');setTimeout(()=>a.remove(),400)},4500));
  document.querySelectorAll('[data-confirm]').forEach(el=>el.addEventListener('click',e=>{if(!confirm(el.dataset.confirm))e.preventDefault()}));
  const photo=document.querySelector('#profile_photo'),preview=document.querySelector('#photoPreview');
  if(photo&&preview)photo.addEventListener('change',()=>{const file=photo.files[0];if(file){preview.src=URL.createObjectURL(file);preview.style.display='block'}});
  document.querySelectorAll('.forgot-link').forEach(link=>{link.href='/forgot-password/';});
  document.addEventListener('click',e=>{const link=e.target.closest('a[href]');if(!link||e.defaultPrevented||link.target==='_blank'||link.hasAttribute('download')||link.getAttribute('href')?.startsWith('#')||link.getAttribute('href')?.startsWith('javascript:')||link.closest('#page-loader')||link.matches('[data-no-loader]'))return;showLoader()});
  document.addEventListener('submit',e=>{if(e.defaultPrevented||e.target.matches('[data-no-loader]')||e.target.closest('#page-loader'))return;showLoader()});
});
