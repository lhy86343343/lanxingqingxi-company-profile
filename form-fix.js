document.addEventListener('submit', function(e) {
    var form = e.target.closest('.elementor-form');
    if (!form) return;
    e.preventDefault();
    var fd = new FormData(form);
    fd.append('website', '');
    fetch('/sendmail.php', {method: 'POST', body: fd})
    .then(function(r) {
        if (r.ok || r.status === 302) {
            form.innerHTML = '<div style="text-align:center;padding:2rem;color:#0066CC;font-size:1.1rem">✔ 感谢您的咨询，我们会尽快与您联系！</div>';
        } else {
            form.innerHTML = '<div style="text-align:center;padding:2rem;color:red">提交失败，请拨打 18952832843 直接联系</div>';
        }
    }).catch(function() {
        form.innerHTML = '<div style="text-align:center;padding:2rem;color:red">提交失败，请拨打 18952832843 直接联系</div>';
    });
});