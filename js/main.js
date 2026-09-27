/**
 * 丹阳蓝星清洗 - 共享脚本
 * 导航滚动、移动端菜单、返回顶部、平滑滚动、动画、百度地图、悬浮客服、客户轮播
 */

// ==================== NAVBAR SCROLL ====================
const navbar = document.getElementById('navbar');
const backToTop = document.getElementById('backToTop');
window.addEventListener('scroll', function() {
    var y = window.scrollY;
    if (navbar) navbar.classList.toggle('scrolled', y > 80);
    if (backToTop) backToTop.classList.toggle('visible', y > 500);
});

// ==================== MOBILE MENU ====================
var hamburger = document.getElementById('hamburger');
var navLinks = document.getElementById('navLinks');
var navBackdrop = null;

function closeMobileMenu() {
    if (hamburger) { hamburger.classList.remove('active'); hamburger.setAttribute('aria-expanded', 'false'); }
    if (navLinks) navLinks.classList.remove('active');
    if (navBackdrop) navBackdrop.classList.remove('show');
    document.body.style.overflow = '';
}

function openMobileMenu() {
    if (hamburger) { hamburger.classList.add('active'); hamburger.setAttribute('aria-expanded', 'true'); }
    if (navLinks) navLinks.classList.add('active');
    if (navBackdrop) navBackdrop.classList.add('show');
    document.body.style.overflow = 'hidden';
}

if (hamburger && navLinks) {
    // Create backdrop element
    navBackdrop = document.createElement('div');
    navBackdrop.className = 'nav-backdrop';
    navBackdrop.setAttribute('aria-hidden', 'true');
    document.body.appendChild(navBackdrop);

    hamburger.addEventListener('click', function() {
        if (navLinks.classList.contains('active')) {
            closeMobileMenu();
        } else {
            openMobileMenu();
        }
    });

    // Close on backdrop click
    navBackdrop.addEventListener('click', closeMobileMenu);

    // Close on nav link click
    navLinks.querySelectorAll('a').forEach(function(l) {
        l.addEventListener('click', closeMobileMenu);
    });
}

// ==================== BACK TO TOP ====================
if (backToTop) {
    backToTop.addEventListener('click', function() {
        window.scrollTo({ top: 0, behavior: 'smooth' });
    });
}

// ==================== SMOOTH SCROLL (for same-page anchor links) ====================
document.querySelectorAll('a[href^="#"]').forEach(function(a) {
    a.addEventListener('click', function(e) {
        var target = document.querySelector(this.getAttribute('href'));
        if (target) {
            e.preventDefault();
            window.scrollTo({ top: target.getBoundingClientRect().top + window.pageYOffset - 80, behavior: 'smooth' });
        }
    });
});

// ==================== INTERSECTION OBSERVER ====================
var obs = new IntersectionObserver(function(entries) {
    entries.forEach(function(e) {
        if (e.isIntersecting) {
            e.target.classList.add('visible');
            obs.unobserve(e.target);
        }
    });
}, { threshold: 0.12, rootMargin: '0px 0px -40px 0px' });
document.querySelectorAll('.fade-in').forEach(function(el) { obs.observe(el); });

// Initial visible check
window.addEventListener('DOMContentLoaded', function() {
    setTimeout(function() {
        document.querySelectorAll('.fade-in').forEach(function(el) {
            if (el.getBoundingClientRect().top < window.innerHeight) {
                el.classList.add('visible');
            }
        });
    }, 100);
});

// ==================== BAIDU MAP ====================
function initBaiduMap() {
    if (typeof BMapGL === 'undefined' && typeof BMap === 'undefined') {
        console.warn('百度地图API未加载，请检查API密钥(ak)是否正确。');
        console.warn('获取密钥: https://lbsyun.baidu.com/apiconsole/key');
        return;
    }

    var mapContainer = document.getElementById('baiduMap');
    if (!mapContainer) return;

    var BMapLib = typeof BMapGL !== 'undefined' ? BMapGL : BMap;

    // 丹阳市丹北镇埤城坐标
    var lng = 119.8279;
    var lat = 32.0723;

    try {
        var map = new BMapLib.Map('baiduMap');
        var point = new BMapLib.Point(lng, lat);
        map.centerAndZoom(point, 15);
        map.enableScrollWheelZoom(true);
        map.addControl(new BMapLib.NavigationControl());
        map.addControl(new BMapLib.ScaleControl());

        var marker = new BMapLib.Marker(point);
        map.addOverlay(marker);

        var infoWindow = new BMapLib.InfoWindow(
            '<div style="padding:5px 8px;font-family:\'Noto Sans SC\',sans-serif;font-size:13px;line-height:1.7;">' +
            '<strong style="font-size:14px;color:#0066CC;">丹阳市蓝星防腐清洗有限公司</strong><br>' +
            '📍 丹阳市丹北镇埤城洪家埭98号<br>' +
            '📞 <a href="tel:18952832843" style="color:#0066CC;">18952832843</a>' +
            '</div>',
            { width: 260, title: '' }
        );
        marker.addEventListener('click', function() {
            marker.openInfoWindow(infoWindow);
        });
        marker.openInfoWindow(infoWindow);

        window.addEventListener('resize', function() {
            setTimeout(function() { map.reset(); }, 300);
        });

    } catch (e) {
        console.error('百度地图初始化失败:', e.message);
    }
}

// 百度地图API加载完成后初始化
(function() {
    if (typeof BMapGL !== 'undefined' || typeof BMap !== 'undefined') {
        initBaiduMap();
    } else {
        var mapCheckCount = 0;
        var mapCheckTimer = setInterval(function() {
            if (typeof BMapGL !== 'undefined' || typeof BMap !== 'undefined') {
                clearInterval(mapCheckTimer);
                initBaiduMap();
            }
            mapCheckCount++;
            if (mapCheckCount > 60) {
                clearInterval(mapCheckTimer);
                console.warn('百度地图加载超时，请检查网络或API密钥。');
            }
        }, 500);
    }
})();

// ==================== FLOATING CONTACT WIDGET ====================

        e.preventDefault();
        toggleFc();

    if (fcClose) {
        fcClose.addEventListener('click', function(e) {
            e.preventDefault();
            toggleFc(false);
        });
    }

    document.addEventListener('click', function(e) {
            toggleFc(false);
    });
}

// ==================== CLIENT LOGO CAROUSEL ====================
function initClientCarousel() {
    var clientList = document.querySelector('.client-logos');
    if (!clientList) return;

    var tags = clientList.querySelectorAll('.client-tag');
    if (tags.length === 0) return;

    var tagArray = Array.from(tags);
    var totalClients = tagArray.length;
    var isMobile = window.innerWidth < 768;
    var perSlide = isMobile ? 3 : 5;
    var totalSlides = Math.ceil(totalClients / perSlide);

    // 构建轮播结构
    var wrap = document.createElement('div');
    wrap.className = 'carousel-wrap';
    var track = document.createElement('div');
    track.className = 'carousel-track';

    // 3轮实现无缝循环
    for (var round = 0; round < 3; round++) {
        for (var i = 0; i < totalSlides; i++) {
            var slide = document.createElement('div');
            slide.className = 'carousel-item';
            slide.style.display = 'flex';
            slide.style.flexWrap = 'wrap';
            slide.style.justifyContent = 'center';
            slide.style.alignItems = 'center';
            slide.style.gap = '0.8rem 1.5rem';
            slide.style.padding = '0.5rem';
            var batch = tagArray.slice(i * perSlide, (i + 1) * perSlide);
            batch.forEach(function(t) {
                var clone = t.cloneNode(true);
                slide.appendChild(clone);
            });
            track.appendChild(slide);
        }
    }
    wrap.appendChild(track);

    // 导航按钮
    var prevBtn = document.createElement('button');
    prevBtn.className = 'carousel-btn prev';
    prevBtn.innerHTML = '‹';
    prevBtn.setAttribute('aria-label', '上一页');
    var nextBtn = document.createElement('button');
    nextBtn.className = 'carousel-btn next';
    nextBtn.innerHTML = '›';
    nextBtn.setAttribute('aria-label', '下一页');
    wrap.appendChild(prevBtn);
    wrap.appendChild(nextBtn);

    // 指示点
    var dotsWrapper = document.createElement('div');
    dotsWrapper.className = 'carousel-dots';
    for (var j = 0; j < totalSlides; j++) {
        var dot = document.createElement('button');
        dot.className = 'dot' + (j === 0 ? ' active' : '');
        dot.setAttribute('aria-label', '第' + (j+1) + '页');
        dotsWrapper.appendChild(dot);
    }
    wrap.appendChild(dotsWrapper);

    // 替换原列表
    clientList.parentNode.replaceChild(wrap, clientList);

    var currentSlide = 0;
    var offsetSlides = totalSlides;
    var dots = dotsWrapper.querySelectorAll('.dot');
    var autoTimer, isDragging = false, startX = 0, startTranslate = 0;

    function updateCarousel(idx, animate) {
        if (animate === undefined) animate = true;
        track.style.transition = animate ? 'transform 0.5s ease' : 'none';
        track.style.transform = 'translateX(' + (-(offsetSlides + idx) * 100) + '%)';
        currentSlide = idx;
        dots.forEach(function(d, k) { d.classList.toggle('active', k === idx); });
    }

    function nextSlide() {
        var next = currentSlide + 1;
        updateCarousel(next, true);
        if (next >= totalSlides) {
            setTimeout(function() { updateCarousel(0, false); }, 500);
        }
    }

    function prevSlide() {
        if (currentSlide === 0) {
            updateCarousel(totalSlides, false);
            setTimeout(function() { updateCarousel(totalSlides - 1, true); }, 20);
        } else {
            updateCarousel(currentSlide - 1, true);
        }
    }

    updateCarousel(0, false);

    nextBtn.addEventListener('click', function() { nextSlide(); resetAuto(); });
    prevBtn.addEventListener('click', function() { prevSlide(); resetAuto(); });
    dots.forEach(function(d, i) {
        d.addEventListener('click', function() { updateCarousel(i, true); resetAuto(); });
    });

    // 触摸/拖动
    track.addEventListener('mousedown', function(e) { startDrag(e.clientX); });
    track.addEventListener('touchstart', function(e) { startDrag(e.touches[0].clientX); }, {passive: false});
    track.addEventListener('mousemove', function(e) { onDrag(e.clientX); });
    track.addEventListener('touchmove', function(e) { onDrag(e.touches[0].clientX); }, {passive: false});
    track.addEventListener('mouseup', endDrag);
    track.addEventListener('mouseleave', endDrag);
    track.addEventListener('touchend', endDrag);

    function startDrag(x) {
        isDragging = true; startX = x;
        startTranslate = - (offsetSlides + currentSlide) * wrap.offsetWidth;
        track.style.transition = 'none'; track.style.cursor = 'grabbing';
    }
    function onDrag(x) {
        if (!isDragging) return;
        track.style.transform = 'translateX(' + (startTranslate + (x - startX)) + 'px)';
    }
    function endDrag() {
        if (!isDragging) return;
        isDragging = false; track.style.cursor = '';
        var moved = parseFloat(track.style.transform.split('(')[1]) - startTranslate;
        if (Math.abs(moved) > 60) {
            moved < 0 ? nextSlide() : prevSlide();
        } else {
            updateCarousel(currentSlide, true);
        }
        resetAuto();
    }

    function startAuto() { autoTimer = setInterval(nextSlide, 3500); }
    function resetAuto() { clearInterval(autoTimer); startAuto(); }
    startAuto();
}

// 页面加载完成后初始化轮播
window.addEventListener('DOMContentLoaded', function() {
    setTimeout(initClientCarousel, 500);
});

// ==================== ACTIVE NAV HIGHLIGHT ====================
(function() {
    var currentPath = window.location.pathname;
    var pageName = currentPath.split('/').pop() || 'index.html';
    if (pageName === '' || pageName === '/') pageName = 'index.html';

    // 判断是否为单页锚点页面 (index.html 使用 #anchor 导航)
    var isAnchorPage = (pageName === 'index.html' || pageName === '' || pageName === '/');

    var navLinksAll = document.querySelectorAll('.nav-links a');
    navLinksAll.forEach(function(link) {
        var href = link.getAttribute('href');
        if (!href) return;

        // 多页面模式：URL路径匹配
        if (!isAnchorPage) {
            if (href === pageName || href === './' + pageName || href === pageName) {
                link.classList.add('active');
            }
        }
    });

    // 单页锚点页面：基于滚动位置高亮
    if (isAnchorPage) {
        function updateActiveNav() {
            var sections = document.querySelectorAll('section[id]');
            var y = window.scrollY + 150;
            sections.forEach(function(s) {
                if (y >= s.offsetTop && y < s.offsetTop + s.offsetHeight) {
                    navLinksAll.forEach(function(l) {
                        l.classList.toggle('active', l.getAttribute('href') === '#' + s.id);
                    });
                }
            });
        }
        window.addEventListener('scroll', updateActiveNav);
        updateActiveNav();
    }
})();