// ========== 模式切换（简报版 ↔ 深度版） ==========
function switchMode(mode) {
    // 更新按钮状态
    document.getElementById('btn-brief').classList.toggle('active', mode === 'brief');
    document.getElementById('btn-deep').classList.toggle('active', mode === 'deep');

    // 切换页面
    const targetUrl = mode === 'deep' ? 'deep.html' : 'index.html';
    window.location.href = targetUrl;
}

// ========== 条目展开/收起 ==========
function toggleDetail(el) {
    el.classList.toggle('expanded');
}

// ========== 板块收起/展开 ==========
function toggleSection(el) {
    const section = el.closest('.section');
    section.classList.toggle('collapsed');
    el.textContent = section.classList.contains('collapsed') ? '展开' : '收起';
}

// ========== 页面加载动画 ==========
document.addEventListener('DOMContentLoaded', function() {
    const container = document.querySelector('.container');
    if (container) {
        container.style.opacity = '0';
        container.style.transition = 'opacity 0.3s ease';
        requestAnimationFrame(() => {
            container.style.opacity = '1';
        });
    }

    // 给所有外部链接添加安全属性
    document.querySelectorAll('a[href^="http"]').forEach(a => {
        a.setAttribute('rel', 'noopener noreferrer');
    });
});
