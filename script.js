// 模式切换
function switchMode(m){
    document.getElementById('btn-brief').classList.toggle('active',m==='brief');
    document.getElementById('btn-deep').classList.toggle('active',m==='deep');
    location.href=m==='deep'?'deep.html':'index.html';
}
// 条目展开
function toggleDetail(el){el.classList.toggle('expanded')}
// 板块收起
function toggleSection(el){
    const s=el.closest('.section');
    s.classList.toggle('collapsed');
    el.textContent=s.classList.contains('collapsed')?'+':'−';
}
document.addEventListener('DOMContentLoaded',function(){
    document.querySelectorAll('a[href^="http"]').forEach(a=>a.setAttribute('rel','noopener noreferrer'));
});
