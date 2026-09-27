/**
 * AI 智能客服聊天组件 — 丹阳蓝星清洗
 *
 * 使用方法: 在 HTML 页面 </body> 前添加
 *   <script src="js/ai-chat.js"></script>
 *
 * 后端: Cloudflare Worker 代理 DeepSeek API
 * 部署 Worker 后修改下方 PROXY_URL
 */

(function () {
  'use strict';

  // ==================== 配置 ====================

  const CONFIG = {
    // PHP 代理（相对路径，.com/.cn 通用）
    // API key is server-side at lanxingqingxi.cn/ai-proxy.php

    // 界面文本
    title: { zh: '💬 AI 智能客服', en: '💬 AI Assistant' },
    subtitle: { zh: '25年清洗经验，随时为您解答', en: '25+ years expertise, ask us anything' },
    placeholder: { zh: '请输入您的问题…', en: 'Type your message…' },
    sendBtn: { zh: '发送', en: 'Send' },
    thinking: { zh: '正在输入…', en: 'Typing…' },
    errorMsg: { zh: '抱歉，网络出错了，请稍后重试或直接拨打 18952832843', en: 'Sorry, connection error. Please call +86 18952832843' },
    rateLimitMsg: { zh: '您发送得太快了，请稍等片刻再提问', en: 'Please wait a moment before sending again' },
    powered: { zh: '由 AI 驱动 · 最终信息请与客服确认', en: 'Powered by AI · Verify with our team' },
    greeting: {
      zh: '您好！我是丹阳蓝星清洗的 AI 客服助手 👋\n\n我可以帮您解答工业设备清洗相关的问题，比如：\n• 换热器/锅炉/管道清洗工艺\n• 高压水射流与化学清洗\n• 服务报价与覆盖区域\n\n请问有什么可以帮您的？',
      en: 'Hello! I\'m the AI assistant of DanYang LanXing Cleaning 👋\n\nI can help you with:\n• Industrial equipment cleaning services\n• Heat exchanger / boiler / pipeline cleaning\n• Service quotes and coverage areas\n\nHow can I help you today?'
    },
    leadMsg: {
      zh: '📋 请填写以下信息，提交后我们将尽快联系您：',
      en: '📋 Please fill in below and we\'ll contact you shortly:'
    },
    leadFormLabels: {
      name: { zh: '联系人姓名', en: 'Contact Name' },
      phone: { zh: '联系电话', en: 'Phone' },
      need: { zh: '设备类型及需求描述', en: 'Equipment & Requirements' },
    },
    leadFormSubmit: { zh: '提交', en: 'Submit' },
    leadFormThanks: { zh: '感谢您的提交！我们将尽快与您联系，或直接拨打 18952832843', en: 'Thank you! We\'ll contact you shortly, or call +86 18952832843' },

    quickQuestions: {
      zh: [
        '换热器清洗多少钱？',
        '你们服务哪些地区？',
        '锅炉清洗用什么工艺？',
        '高压水射流和化学清洗哪个好？',
        '可以上门勘察吗？',
      ],
      en: [
        'How much for heat exchanger cleaning?',
        'Which areas do you serve?',
        'What cleaning methods do you use?',
        'Can you do on-site inspection?',
        'How long does cleaning take?',
      ],
    },

    maxHistory: 30,    // localStorage 最多保存条数
    maxTokens: 800,    // 每次回复最大 token
  };

  // ==================== 微信客服入口 (企微 AI 自动报价) ====================
  const WECOM = {
    // 带 enc_scene 的官方客服链接 (由 kf/add_contact_way 生成, 2026-09-28 换):
    // 必须用这种链接才能再拼 scene_param —— 后台直接复制的裸链接拼参数, 企微进会话事件会校验失败
    link: 'https://work.weixin.qq.com/kfid/kfcbd2c895281e8910e?enc_scene=ENC2gsh3oGsivPf8AR5TjoPKTxf2wNrAUWGmHJFggh1FZQS',
    qr: '/images/kf-qrcode.png',
    btnText: { zh: '📱 微信咨询 · 获取报价', en: '📱 WeChat · Get Quote' },
    tip: { zh: '微信扫一扫，添加客服微信获取清洗报价', en: 'Scan with WeChat to get a cleaning quote' },
    phone: '18952832843',
  };

  // ==================== 渠道归因 (scene_param -> 工单来源) ====================
  // 链接拼上 scene_param=xxx 后, 客户进入客服会话时企微原样回传, 后端记入工单「来源」。
  // 来源码与 /tools/*.html 的 SOURCE_RULES 同一套(后端 engine.SOURCE_NAMES 也同一套), 改码三处同步。
  var SRC_RULES = [
    ['/services/heat-exchanger', 'hx'], ['/services/boiler', 'gl'],
    ['/services/pipeline', 'gd'], ['/services/condenser', 'nq'],
    ['/services/reactor', 'fj'], ['/services/central-ac', 'kt'],
    ['/services/cooling-water', 'lq'], ['/services/evaporative-condenser', 'zfl'],
    ['/services/storage-tank', 'cg'], ['/services/gas-cooler', 'mq'],
    ['/services.html', 'svc'],
    ['/knowledge/heat-exchanger', 'khx'], ['/knowledge/chemical-cleaning', 'khx'],
    ['/knowledge/hp-water-jetting', 'kgd'], ['/knowledge', 'knw'],
    ['/blog/', 'blog'], ['/tech', 'tech'], ['/tools/', 'tool'],
    ['/calc/', 'calc'], ['/cases', 'case'], ['/faq', 'faq'],
    ['/about', 'abt'], ['/contact', 'con'], ['/landing/', 'land'],
  ];
  var SEARCH_HOSTS = /(baidu|google|bing|sogou|so\.com|sm\.cn|yandex|duckduckgo|chatgpt|openai|perplexity|doubao|deepseek|kimi|moonshot|zhipu|tongyi|qwen|yuanbao|wenxin)/i;

  function resolveSource() {
    try {
      var q = new URLSearchParams(window.location.search);
      var f = q.get('from') || q.get('src');   // 广告/活动可用 ?from=xx 强制指定
      if (f) return String(f).toLowerCase().replace(/[^a-z0-9_-]/g, '').slice(0, 12) || 'other';
    } catch (e) {}
    var ref = document.referrer || '';
    if (ref) {
      try {
        var u = new URL(ref);
        var isSelf = (u.hostname === location.hostname) || /(^|\.)lanxingqingxi\.com$/.test(u.hostname);
        if (!isSelf) return SEARCH_HOSTS.test(u.hostname) ? 'seo' : 'ext';
      } catch (e) {}
    }
    var p = location.pathname + location.search;
    for (var i = 0; i < SRC_RULES.length; i++) {
      if (p.indexOf(SRC_RULES[i][0]) !== -1) return SRC_RULES[i][1];
    }
    if (location.pathname === '/' || location.pathname === '/index.html') return 'home';
    return 'other';
  }

  var PAGE_SRC = resolveSource();

  function wecomLink() {
    return WECOM.link + (WECOM.link.indexOf('?') > -1 ? '&' : '?') +
           'scene_param=' + encodeURIComponent(PAGE_SRC);
  }

  // 页面上静态写死的客服链接(报价横条/首页卡片等)统一补来源参数。
  // 工具页自带更细参数(来源码_报告编号) -> 跳过, 不覆盖。
  function applySourceToKfLinks() {
    try {
      var as = document.querySelectorAll('a[href*="work.weixin.qq.com/kfid/"]');
      for (var i = 0; i < as.length; i++) {
        if ((as[i].getAttribute('href') || '').indexOf('scene_param=') !== -1) continue;
        as[i].setAttribute('href', wecomLink());
      }
    } catch (e) {}
  }

  function isWeChatBrowser() {
    return /MicroMessenger/i.test(navigator.userAgent);
  }

  function isMobileUA() {
    return /Android|iPhone|iPad|iPod|Windows Phone|HarmonyOS|Mobile/i.test(navigator.userAgent);
  }

  function openWecomEntry() {
    // 微信内: 直接跳转客服会话 (零摩擦)
    if (isWeChatBrowser()) {
      window.location.href = wecomLink();
      return;
    }
    // 手机浏览器(非微信): 先尝试直接拉起微信(腾讯落地页自行唤起), 再弹二维码/电话兜底
    if (isMobileUA()) {
      try { window.open(wecomLink(), '_blank'); } catch (e) {}
    }
    // 微信外: 弹二维码浮层
    var mask = document.getElementById('ai-wecom-mask');
    if (mask) { mask.classList.add('open'); return; }
    mask = document.createElement('div');
    mask.id = 'ai-wecom-mask';
    mask.className = 'ai-wecom-mask open';
    mask.innerHTML =
      '<div class="ai-wecom-card">' +
        '<div class="ai-wecom-hd"><span>' + (WECOM.tip[lang] || WECOM.tip.zh) +
        '</span><button class="ai-wecom-x" aria-label="close">✕</button></div>' +
        '<img src="' + WECOM.qr + '" alt="丹阳蓝星清洗工程师微信报价二维码：扫码加微信，发送设备资料获取工业设备清洗报价" loading="lazy">' +
        '<div class="ai-wecom-ft">或电话咨询：<a href="tel:' + WECOM.phone + '">' + WECOM.phone + '</a></div>' +
      '</div>';
    document.body.appendChild(mask);
    mask.addEventListener('click', function (ev) {
      if (ev.target === mask || ev.target.className === 'ai-wecom-x') {
        mask.classList.remove('open');
      }
    });
  }

  // ==================== 页面主题 → 专属提问 ====================
  // 根据当前页面 URL / H1 / Title 自动匹配设备类型，让快捷提问贴合用户正在看的设备
  const PAGE_QUESTIONS = {
    'heat-exchanger': {
      zh: [
        '板式换热器和列管式换热器清洗有什么区别？',
        '换热器清洗一般多少钱？',
        '换热器结垢严重要停机吗？',
        '你们能清洗哪些类型的换热器？',
        '换热器多久清洗一次比较好？',
      ],
      en: [
        'Difference between plate and shell-and-tube heat exchanger cleaning?',
        'How much does heat exchanger cleaning cost?',
        'Does heavy fouling require shutdown for cleaning?',
        'What types of heat exchangers do you clean?',
        'How often should heat exchangers be cleaned?',
      ],
    },
    'boiler': {
      zh: [
        '锅炉清洗用什么工艺？',
        '蒸汽锅炉和导热油锅炉清洗有什么区别？',
        '锅炉除垢一般多久做一次？',
        '锅炉清洗多少钱？',
        '锅炉不停机能清洗吗？',
      ],
      en: [
        'What methods do you use for boiler cleaning?',
        'Difference between steam boiler and thermal oil boiler cleaning?',
        'How often should boilers be descaled?',
        'How much does boiler cleaning cost?',
        'Can boilers be cleaned without shutdown?',
      ],
    },
    'pipeline': {
      zh: [
        '管道清洗用什么方法？',
        '化工管道能在线清洗吗？',
        'PIG清管适合什么管道？',
        '管道清洗多少钱一米？',
        '管道脱脂钝化怎么做？',
      ],
      en: [
        'What methods are used for pipeline cleaning?',
        'Can chemical pipelines be cleaned online?',
        'What pipelines are suitable for PIG pigging?',
        'How much does pipeline cleaning cost per meter?',
        'How do you do pipeline degreasing and passivation?',
      ],
    },
    'central-ac': {
      zh: [
        '中央空调多久清洗一次？',
        '溴化锂机组和氟利昂机组清洗有什么区别？',
        '中央空调清洗多少钱？',
        '空调清洗能不停业进行吗？',
        '冷却塔需要一起清洗吗？',
      ],
      en: [
        'How often should central AC be cleaned?',
        'Difference between lithium bromide and Freon unit cleaning?',
        'How much does central AC cleaning cost?',
        'Can AC cleaning be done without interrupting business?',
        'Do cooling towers need cleaning too?',
      ],
    },
    'condenser': {
      zh: [
        '电厂凝汽器清洗用什么工艺？',
        '凝汽器真空度下降怎么处理？',
        '凝汽器清洗多少钱？',
        '空冷器清洗和凝汽器清洗一样吗？',
        '凝汽器能不停机清洗吗？',
      ],
      en: [
        'What methods are used for power plant condenser cleaning?',
        'How to fix condenser vacuum drop?',
        'How much does condenser cleaning cost?',
        'Is air cooler cleaning the same as condenser cleaning?',
        'Can condensers be cleaned without shutdown?',
      ],
    },
    'reactor': {
      zh: [
        '反应釜清洗用什么工艺？',
        '搪瓷反应釜清洗会损伤搪瓷吗？',
        '不锈钢反应釜酸洗钝化怎么做？',
        '反应釜清洗多少钱？',
        '钛材反应釜能清洗吗？',
      ],
      en: [
        'What methods are used for reactor cleaning?',
        'Will glass-lined reactor cleaning damage the lining?',
        'How to do stainless steel reactor pickling and passivation?',
        'How much does reactor cleaning cost?',
        'Can titanium reactors be cleaned?',
      ],
    },
    'gas-cooler': {
      zh: [
        '煤气初冷器能不停车清洗吗？',
        '初冷器焦油垢萘垢怎么清除？',
        '横管式和立管式初冷器清洗有什么区别？',
        '初冷器清洗多少钱？',
        '清洗后煤气出口温度能降到多少？',
      ],
      en: [
        'Can the primary gas cooler be cleaned without shutdown?',
        'How to remove tar and naphthalene fouling in the cooler?',
        'Difference between horizontal and vertical primary cooler cleaning?',
        'How much does primary cooler cleaning cost?',
        'How low can the gas outlet temperature drop after cleaning?',
      ],
    },
    'evaporative-condenser': {
      zh: [
        '蒸发式冷凝器清洗用什么工艺？',
        '镀锌层能化学清洗吗？会不会腐蚀锌层？',
        '蒸发式冷凝器清洗多少钱？',
        '蒸发式冷凝器多久清洗一次？',
        '蒸发式冷却器能不停机清洗吗？',
      ],
      en: [
        'What methods are used for evaporative condenser cleaning?',
        'Can the galvanized zinc layer be cleaned without corrosion?',
        'How much does evaporative condenser cleaning cost?',
        'How often should evaporative condensers be cleaned?',
        'Can evaporative coolers be cleaned without shutdown?',
      ],
    },
  };

  function detectPageType() {
    const url = location.pathname.toLowerCase();
    const h1El = document.querySelector('h1');
    const h1 = (h1El ? h1El.textContent : '').toLowerCase();
    const title = document.title.toLowerCase();

    // 首页等综合入口：回退通用提问（覆盖更广）
    if (url === '/' || /\/index\.html$/.test(url)) return null;

    // 1. URL slug 精确匹配（服务页最可靠）
    const urlMap = {
      'evaporative-condenser': 'evaporative-condenser',
      'heat-exchanger': 'heat-exchanger',
      'boiler': 'boiler',
      'pipeline': 'pipeline',
      'central-ac': 'central-ac',
      'condenser': 'condenser',
      'reactor': 'reactor',
      'gas-cooler': 'gas-cooler',
    };
    for (const slug in urlMap) {
      if (url.indexOf('/' + slug) !== -1) return urlMap[slug];
    }

    // 2. H1 + Title 关键词匹配（博客文章 / 知识词条 / 落地页）
    const text = h1 + ' ' + title;
    const kwMap = [
      ['evaporative-condenser', /蒸发式冷凝器|蒸发式冷却器|蒸发冷|镀锌层/],
      ['gas-cooler', /煤气初冷器|初冷器|焦油垢|萘垢/],
      ['condenser', /凝汽器|空冷器/],
      ['central-ac', /中央空调|溴化锂|氟利昂|冷却塔/],
      ['reactor', /反应釜|搪瓷|钛材/],
      ['boiler', /锅炉|导热油炉|余热锅炉/],
      ['heat-exchanger', /换热器/],
      ['pipeline', /管道|清管|脱脂|钝化/],
    ];
    for (const pair of kwMap) {
      if (pair[1].test(text)) return pair[0];
    }
    return null;
  }

  // ==================== 语言检测 ====================
  const lang = (document.documentElement.lang || '').startsWith('en') ? 'en' : 'zh';
  const t = function (key) {
    const val = CONFIG[key];
    if (!val) return key;
    if (typeof val === 'object' && val.zh) return val[lang] || val.zh;
    return val;
  };

  // ==================== System Prompt ====================
  const SYSTEM_PROMPT = {
    zh: `你是丹阳蓝星清洗（全称：丹阳市蓝星防腐清洗有限公司）的AI客服助手。请严格遵循以下规则：

【公司信息】
- 公司名称：丹阳市蓝星防腐清洗有限公司
- 成立：2001年，25年工业清洗经验
- 资质：中国工业清洗协会成员单位、化学清洗B级资质、高压水射流清洗资质
- 地址：江苏省丹阳市丹北镇埤城洪家埭98号
- 电话：18952832843（24小时热线）
- 联系人：罗会永

【核心服务】
换热器清洗（列管式/板式/螺旋板式）、锅炉清洗（蒸汽/导热油/热水）、管道清洗（工艺/循环水/蒸汽）、中央空调清洗、反应釜清洗、高压水射流清洗（500-2800bar）、化学清洗工程、蒸发式冷凝器清洗、气体冷却器清洗、导热油系统清洗、电厂凝汽器清洗、PIG管道清管、循环水系统清洗预膜

【服务区域】江苏、浙江、上海、安徽、山东、河南等全国范围
【覆盖行业】化工、电力、钢铁、制药、食品、商业建筑
【业绩】500+企业客户、1000+工程项目

【回复规则】
1. 简洁专业，2-5句话为宜，不要太长
2. 价格问题：说明需根据设备类型、规格、结垢程度评估，建议来电18952832843或留联系方式
3. 可提供免费上门勘察服务
4. 用户有明确意向时，主动建议留联系方式或拨打电话
5. 无法回答的问题建议拨打电话咨询工程师
6. 专业术语要简要解释

【禁止】
1. 绝对禁止虚构或编造任何电话号码，只能使用 18952832843
2. 绝对禁止输出 0511-86343343 或任何其他号码
3. 不捏造价格、不承诺工期、不透露客户信息、不讨论与清洗无关话题`,

    en: `You are the AI assistant for Danyang Lanxing Anti-corrosion Cleaning Co., Ltd. Follow these rules:

【Company】
- Name: Danyang Lanxing Anti-corrosion Cleaning Co., Ltd.
- Est. 2001, 25+ years industrial cleaning experience
- Member: China Industrial Cleaning Association
- Location: No.98 Hongjiadai, Picheng, Danbei Town, Danyang City, Jiangsu Province, China
- Phone: +86 18952832843 (24/7 hotline)
- Contact: Mr. Luo Huiyong

【Services】
Heat exchanger cleaning, boiler cleaning, pipeline cleaning, central AC cleaning, reactor cleaning, high-pressure water jetting (500-2800 bar), chemical cleaning, evaporative condenser cleaning, gas cooler cleaning, thermal oil system cleaning, power plant condenser cleaning, PIG pipeline pigging, circulating water system cleaning

【Service areas】Jiangsu, Zhejiang, Shanghai, Anhui, Shandong, Henan (nationwide)
【Industries】Chemical, power, steel, pharmaceutical, food, commercial buildings
【Experience】500+ corporate clients, 1000+ projects

【Rules】
1. Keep responses concise (2-5 sentences)
2. For pricing: explain it depends on equipment type/size/fouling, suggest calling +86 18952832843
3. We offer free on-site inspection
4. When user shows intent, proactively suggest leaving contact info
5. For questions beyond your knowledge, suggest calling the hotline
6. Briefly explain technical terms
7. NEVER invent phone numbers. Only use +86 18952832843.
8. Stay on topic — industrial cleaning only`
  };

  // ==================== CSS 注入 ====================
  function injectCSS() {
    const css = `
.ai-wecom-entry{display:block;width:calc(100% - 32px);margin:12px 16px 2px;padding:11px 14px;
  border:none;border-radius:10px;cursor:pointer;font-family:inherit;
  background:linear-gradient(135deg,#0066CC,#00A8E8);color:#fff;font-size:14px;font-weight:700;
  box-shadow:0 3px 12px rgba(0,102,204,0.30);transition:all .2s;letter-spacing:.2px}
.ai-wecom-entry:hover{transform:translateY(-1px);box-shadow:0 6px 18px rgba(0,102,204,0.42)}
.ai-wecom-entry:active{transform:translateY(0) scale(.99)}
.ai-wecom-mask{position:fixed;top:0;left:0;right:0;bottom:0;z-index:9999;
  background:rgba(15,23,42,0.55);display:flex;align-items:center;justify-content:center;
  opacity:0;visibility:hidden;transition:all .2s;-webkit-backdrop-filter:blur(2px);backdrop-filter:blur(2px)}
.ai-wecom-mask.open{opacity:1;visibility:visible}
.ai-wecom-card{background:#fff;border-radius:16px;padding:20px 22px 16px;text-align:center;
  box-shadow:0 25px 60px rgba(0,0,0,0.3);max-width:280px;font-family:inherit}
.ai-wecom-hd{display:flex;align-items:flex-start;gap:8px;justify-content:space-between;margin-bottom:12px}
.ai-wecom-hd span{font-size:13px;color:#334155;line-height:1.4;text-align:left;flex:1}
.ai-wecom-x{border:none;background:#F1F5F9;color:#64748B;width:24px;height:24px;border-radius:50%;
  cursor:pointer;font-size:12px;flex-shrink:0;line-height:1;font-family:inherit}
.ai-wecom-card img{width:180px;height:180px;display:block;margin:0 auto;border-radius:8px}
.ai-wecom-ft{margin-top:10px;font-size:12px;color:#64748B}
.ai-wecom-ft a{color:#0066CC;font-weight:700;text-decoration:none}
@media (max-width:480px){.ai-wecom-card{max-width:88vw}.ai-wecom-card img{width:150px;height:150px}}
.ai-chat-bubble{position:fixed;bottom:52px;right:24px;z-index:997;width:56px;height:56px;
  border-radius:50%;background:linear-gradient(135deg,#0066CC,#00A8E8);color:#fff;border:none;
  cursor:pointer;font-size:26px;box-shadow:0 4px 20px rgba(0,102,204,0.45);
  transition:all 0.3s cubic-bezier(0.4,0,0.2,1);display:flex;align-items:center;
  justify-content:center;animation:ai-pulse 2s ease-in-out infinite;line-height:1}
.ai-chat-bubble:hover{transform:scale(1.12);box-shadow:0 8px 30px rgba(0,168,232,0.55)}
.ai-chat-bubble:active{transform:scale(0.95)}
/* ===== 移动端固定底部操作栏 (仅 ≤768px; PC 不受影响) ===== */
.lx-mobile-bar{display:none}
@media (max-width:768px){
  .lx-mobile-bar{display:flex;position:fixed;left:0;right:0;bottom:0;z-index:995;background:#fff;
    border-top:1px solid #e2e8f0;box-shadow:0 -2px 12px rgba(0,0,0,.10);
    padding:6px 8px calc(6px + env(safe-area-inset-bottom,0px));gap:8px;box-sizing:border-box}
  .lx-mobile-bar a{flex:1;display:flex;flex-direction:column;align-items:center;justify-content:center;
    gap:2px;padding:8px 2px;border-radius:10px;text-decoration:none;font-size:12.5px;font-weight:800;
    min-height:48px;line-height:1.2;box-sizing:border-box}
  .lx-mobile-bar a .lx-ico{font-size:18px;line-height:1}
  .lx-mobile-bar a.lx-tel{background:#eef6ff;color:#0066CC}
  .lx-mobile-bar a.lx-diag{background:#fff7ed;color:#c2410c}
  .lx-mobile-bar a.lx-wx{background:#07C160;color:#fff}
  body.lx-has-mobilebar{padding-bottom:66px}
  /* 提高特异性并 d用 !important: 覆盖文件内既有 480px 规则(气泡 bottom:20px) */
  html body .ai-chat-bubble{bottom:calc(78px + env(safe-area-inset-bottom,0px)) !important;right:14px;
    width:50px !important;height:50px !important;font-size:22px !important;z-index:994 !important}
}
@media (min-width:481px) and (max-width:768px){
  html body .ai-chat-panel{left:12px;right:12px;width:auto;bottom:76px;max-height:72vh}
}
@keyframes ai-pulse{0%,100%{box-shadow:0 0 0 0 rgba(0,102,204,0.6),0 0 0 0 rgba(0,168,232,0.4)}
50%{box-shadow:0 0 0 14px rgba(0,102,204,0),0 0 0 6px rgba(0,168,232,0)}}
.ai-chat-bubble .ai-badge{position:absolute;top:-2px;right:-2px;width:16px;height:16px;
  background:#10B981;border-radius:50%;border:2px solid #fff;animation:ai-dot 1.5s ease-in-out infinite}
@keyframes ai-dot{0%,100%{opacity:1}50%{opacity:0.5}}

.ai-chat-panel{position:fixed;bottom:116px;right:24px;z-index:996;width:380px;max-height:520px;
  background:#fff;border-radius:16px;box-shadow:0 25px 60px rgba(0,0,0,0.18);
  border:1px solid #E4E0DA;display:flex;flex-direction:column;overflow:hidden;
  opacity:0;visibility:hidden;transform:translateY(12px) scale(0.96);
  transition:all 0.25s cubic-bezier(0.4,0,0.2,1)}
.ai-chat-panel.open{opacity:1;visibility:visible;transform:translateY(0) scale(1)}

.ai-chat-header{background:linear-gradient(135deg,#0066CC,#00A8E8);color:#fff;
  padding:14px 18px;display:flex;align-items:center;gap:12px;flex-shrink:0}
.ai-chat-header .ai-avatar{width:40px;height:40px;border-radius:50%;background:rgba(255,255,255,0.2);
  display:flex;align-items:center;justify-content:center;font-size:20px;flex-shrink:0}
.ai-chat-header .ai-info{flex:1;min-width:0}
.ai-chat-header .ai-name{font-size:15px;font-weight:700;line-height:1.2}
.ai-chat-header .ai-desc{font-size:12px;opacity:0.85;line-height:1.3}
.ai-chat-close{width:32px;height:32px;border-radius:50%;background:rgba(255,255,255,0.2);
  border:none;color:#fff;font-size:18px;cursor:pointer;display:flex;align-items:center;
  justify-content:center;transition:background 0.2s;flex-shrink:0;line-height:1}
.ai-chat-close:hover{background:rgba(255,255,255,0.35)}

.ai-chat-body{flex:1;overflow-y:auto;padding:16px;display:flex;flex-direction:column;gap:10px;
  background:#F8F6F3;min-height:0;scroll-behavior:smooth}
.ai-chat-body::-webkit-scrollbar{width:5px}
.ai-chat-body::-webkit-scrollbar-thumb{background:#D4CFC8;border-radius:10px}

.ai-msg{max-width:85%;padding:10px 14px;border-radius:16px;font-size:14px;
  line-height:1.6;word-break:break-word;animation:ai-msg-in 0.3s ease-out}
@keyframes ai-msg-in{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:translateY(0)}}
.ai-msg.user{align-self:flex-end;background:linear-gradient(135deg,#0066CC,#0088DD);color:#fff;
  border-bottom-right-radius:4px}
.ai-msg.assistant{align-self:flex-start;background:#fff;color:#252220;
  border:1px solid #E4E0DA;border-bottom-left-radius:4px;white-space:pre-wrap}
.ai-msg.typing{align-self:flex-start;background:#fff;color:#6B6560;
  border:1px solid #E4E0DA;border-bottom-left-radius:4px;padding:12px 16px}
.ai-msg.typing .ai-dots{display:flex;gap:4px}
.ai-msg.typing .ai-dots span{width:7px;height:7px;background:#A0998F;border-radius:50%;
  animation:ai-bounce 1.4s ease-in-out infinite}
.ai-msg.typing .ai-dots span:nth-child(2){animation-delay:0.2s}
.ai-msg.typing .ai-dots span:nth-child(3){animation-delay:0.4s}
@keyframes ai-bounce{0%,80%,100%{transform:translateY(0)}40%{transform:translateY(-6px)}}

.ai-lead-form{background:#fff;border:1px solid #E4E0DA;border-radius:12px;padding:14px;margin:4px 0;display:flex;flex-direction:column;gap:10px}
.ai-lead-form input,.ai-lead-form textarea{width:100%;padding:10px 12px;border:1.5px solid #D4CFC8;border-radius:8px;font-size:14px;font-family:inherit;outline:none;transition:border 0.2s;background:#FCFBF9;box-sizing:border-box}
.ai-lead-form input:focus,.ai-lead-form textarea:focus{border-color:#0066CC}
.ai-lead-form textarea{resize:vertical;min-height:60px}
.ai-lead-form .ai-form-submit{width:100%;padding:10px;background:linear-gradient(135deg,#0066CC,#00A8E8);color:#fff;border:none;border-radius:8px;font-size:14px;font-weight:600;cursor:pointer;transition:all 0.2s}
.ai-lead-form .ai-form-submit:hover{box-shadow:0 4px 12px rgba(0,102,204,0.4);transform:translateY(-1px)}
.ai-lead-form .ai-form-submit:disabled{opacity:0.6;cursor:not-allowed;transform:none}
.ai-form-phone{display:flex;gap:8px}
.ai-form-phone input{flex:1}
.ai-form-note{font-size:11px;color:#A0998F;text-align:center}

.ai-quick-questions{display:flex;flex-wrap:wrap;gap:6px;padding:8px 16px 2px;flex-shrink:0}
.ai-quick-btn{font-size:12px;padding:6px 12px;border-radius:20px;border:1px solid #D4CFC8;
  background:#fff;color:#4D4845;cursor:pointer;transition:all 0.2s;white-space:nowrap;
  font-family:inherit}
.ai-quick-btn:hover{background:#0066CC;color:#fff;border-color:#0066CC}

.ai-chat-footer{display:flex;align-items:center;gap:8px;padding:12px 16px;
  border-top:1px solid #EFECE8;flex-shrink:0;background:#fff}
.ai-chat-input{flex:1;border:1.5px solid #E4E0DA;border-radius:24px;padding:10px 16px;
  font-size:14px;font-family:inherit;resize:none;outline:none;transition:border 0.2s;
  line-height:1.4;max-height:80px;background:#FCFBF9}
.ai-chat-input:focus{border-color:#0066CC}
.ai-chat-send{width:40px;height:40px;border-radius:50%;background:linear-gradient(135deg,#0066CC,#00A8E8);
  color:#fff;border:none;cursor:pointer;font-size:18px;display:flex;align-items:center;
  justify-content:center;transition:all 0.2s;flex-shrink:0;line-height:1}
.ai-chat-send:hover{transform:scale(1.08);box-shadow:0 4px 12px rgba(0,102,204,0.4)}
.ai-chat-send:disabled{opacity:0.5;cursor:not-allowed;transform:none}
.ai-chat-send svg{width:20px;height:20px;fill:#fff}

.ai-powered{text-align:center;font-size:11px;color:#A0998F;padding:6px 16px 4px;flex-shrink:0;
  background:#F8F6F3}

@media(max-width:480px){
  .ai-chat-panel{position:fixed;top:env(safe-area-inset-top,0);left:0;right:0;bottom:0;z-index:1002;width:100%;max-height:none;
    border-radius:0;border:none}
  .ai-chat-panel .ai-chat-header{padding:14px 14px;padding-top:calc(14px + env(safe-area-inset-top, 0));border-radius:0}
  .ai-chat-bubble{bottom:calc(20px + env(safe-area-inset-bottom, 0));right:12px;width:50px;height:50px;font-size:22px}
  .ai-chat-body{font-size:16px;-webkit-overflow-scrolling:touch}
  .ai-chat-footer{padding:10px 12px;padding-bottom:calc(10px + env(safe-area-inset-bottom, 0))}
  .ai-lead-form input,.ai-lead-form textarea{font-size:16px}
  .ai-chat-input{font-size:16px}
  .ai-quick-btn{font-size:13px;padding:8px 14px}
  .ai-chat-send{width:44px;height:44px}
  .ai-chat-close{width:36px;height:36px;font-size:20px}
  .ai-form-submit{min-height:44px;font-size:16px}
  .ai-msg{max-width:90%}
}
`;
    const style = document.createElement('style');
    style.id = 'ai-chat-style';
    style.textContent = css;
    document.head.appendChild(style);
  }

  // ==================== DOM 构建 ====================
  function buildDOM() {
    // 浮动按钮
    const bubble = document.createElement('button');
    bubble.className = 'ai-chat-bubble';
    bubble.setAttribute('aria-label', t('title'));
    bubble.innerHTML = '<span style="font-weight:800;font-size:18px;letter-spacing:-0.5px">AI</span><span class="ai-badge"></span>';

    // 聊天面板
    const panel = document.createElement('div');
    panel.className = 'ai-chat-panel';
    panel.innerHTML = `
      <div class="ai-chat-header">
        <div class="ai-avatar" style="font-weight:800;font-size:14px;letter-spacing:-0.5px">AI</div>
        <div class="ai-info">
          <div class="ai-name">${t('title')}</div>
          <div class="ai-desc">${t('subtitle')}</div>
        </div>
        <button class="ai-chat-close" aria-label="关闭">✕</button>
      </div>
      <button class="ai-wecom-entry" type="button">${WECOM.btnText[lang] || WECOM.btnText.zh}</button>
      <div class="ai-quick-questions"></div>
      <div class="ai-chat-body"></div>
      <div class="ai-powered">${t('powered')}</div>
      <div class="ai-chat-footer">
        <textarea class="ai-chat-input" rows="1" placeholder="${t('placeholder')}"></textarea>
        <button class="ai-chat-send" aria-label="${t('sendBtn')}">
          <svg viewBox="0 0 24 24"><path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/></svg>
        </button>
      </div>
    `;

    document.body.appendChild(bubble);
    document.body.appendChild(panel);

    // ===== 移动端固定底部操作栏 (电话 / 免费诊断 / 微信报价) =====
    (function () {
      try {
        if (document.querySelector('.lx-mobile-bar')) return;
        var bar = document.createElement('div');
        bar.className = 'lx-mobile-bar';
        bar.innerHTML =
          '<a class="lx-tel" href="tel:18952832843" aria-label="电话咨询"><span class="lx-ico">\ud83d\udcde</span>电话咨询</a>' +
          '<a class="lx-diag" href="/calc/" aria-label="免费设备诊断"><span class="lx-ico">\ud83e\uddea</span>免费诊断</a>' +
          '<a class="lx-wx" href="' + wecomLink() + '" target="_blank" rel="noopener" aria-label="微信获取报价"><span class="lx-ico">\ud83d\udcac</span>微信报价</a>';
        document.body.appendChild(bar);
        var wxBtn = bar.querySelector('.lx-wx');
        if (wxBtn) {
          wxBtn.addEventListener('click', function (e) {
            // 微信外浏览器点「微信报价」：kfid 是 weixin:// 深链，非微信环境是死链 → 改弹二维码
            if (!isWeChatBrowser()) {
              e.preventDefault();
              openWecomEntry();
            }
          });
        }
        document.body.classList.add('lx-has-mobilebar');
      } catch (e) {}
    })();

    return { bubble, panel };
  }

  // ==================== 对话重置 ====================
  function createGreeting() {
    var greet = t('greeting');
    return [{ role: 'assistant', content: greet }];
  }

  // ==================== 流式请求 ====================
  async function* streamChat(messages) {
    const apiMessages = [
      { role: 'system', content: SYSTEM_PROMPT[lang] },
      ...messages.map(function (m) { return { role: m.role, content: m.content }; }),
    ];

    const payload = JSON.stringify({ messages: apiMessages });
    const url = 'https://www.lanxingqingxi.cn/ai-proxy.php?q=' + encodeURIComponent(payload);

    const response = await fetch(url);
    if (!response.ok) { throw new Error('API error: ' + response.status); }

    const data = await response.json();
    const content = data.choices?.[0]?.message?.content;
    if (content) { yield content; }
  }

  // ==================== 线索检测 ====================
  const LEAD_KEYWORDS = {
    zh: ['价格', '多少钱', '报价', '费用', '收费', '便宜', '贵吗', '预约', '下单', '怎么联系',
      '上门', '勘察', '检测', '方案', '合同', '合作', '采购', '招标'],
    en: ['price', 'cost', 'quote', 'how much', 'fee', 'cheap', 'expensive', 'booking',
      'schedule', 'order', 'contact', 'on-site', 'inspection', 'proposal', 'contract'],
  };

  function detectLeadIntent(text) {
    const keywords = LEAD_KEYWORDS[lang] || LEAD_KEYWORDS.zh;
    const lower = text.toLowerCase();
    return keywords.some(function (kw) { return lower.includes(kw.toLowerCase()); });
  }

  // 渲染线索表单
  function renderLeadForm() {
    var div = document.createElement('div');
    div.className = 'ai-lead-form';
    var labels = CONFIG.leadFormLabels;
    var submitTxt = CONFIG.leadFormSubmit[lang] || CONFIG.leadFormSubmit.zh;
    var phoneTxt = CONFIG.leadFormLabels.phone[lang] || CONFIG.leadFormLabels.phone.zh;
    div.innerHTML =
      '<input type="text" class="ai-form-name" placeholder="' + (labels.name[lang] || labels.name.zh) + '">' +
      '<input type="tel" class="ai-form-phone" placeholder="' + phoneTxt + '">' +
      '<textarea class="ai-form-need" placeholder="' + (labels.need[lang] || labels.need.zh) + '" rows="2"></textarea>' +
      '<button class="ai-form-submit">' + submitTxt + '</button>' +
      '<div class="ai-form-note">或拨打 18952832843</div>';
    return div;
  }

  // 直接发送表单字段到服务器
  function sendLeadFields(name, phone, need) {
    var params = 'name=' + encodeURIComponent(name) +
      '&phone=' + encodeURIComponent(phone) +
      '&need=' + encodeURIComponent(need) +
      '&page=' + encodeURIComponent(window.location.href);
    var img = new Image();
    img.src = '/save-lead.php?' + params;
  }

  // ==================== 消息渲染 ====================
  function renderMessage(role, content) {
    const div = document.createElement('div');
    div.className = 'ai-msg ' + role;
    div.textContent = content;
    return div;
  }

  function renderTyping() {
    const div = document.createElement('div');
    div.className = 'ai-msg typing';
    div.innerHTML = '<div class="ai-dots"><span></span><span></span><span></span></div>';
    return div;
  }

  // ==================== 主逻辑 ====================
  function initChat(bubble, panel) {
    const body = panel.querySelector('.ai-chat-body');
    const input = panel.querySelector('.ai-chat-input');
    const sendBtn = panel.querySelector('.ai-chat-send');
    const closeBtn = panel.querySelector('.ai-chat-close');
    const quickContainer = panel.querySelector('.ai-quick-questions');

    let messages = createGreeting();
    let isStreaming = false;
    let leadPromptShown = false;

    // 渲染快捷问题
    function renderQuickQuestions() {
      quickContainer.innerHTML = '';
      const pageType = detectPageType();
      const pageQs = (pageType && PAGE_QUESTIONS[pageType]) ? PAGE_QUESTIONS[pageType] : null;
      const questions = pageQs ? (pageQs[lang] || pageQs.zh) : (CONFIG.quickQuestions[lang] || CONFIG.quickQuestions.zh);
      questions.forEach(function (q) {
        const btn = document.createElement('button');
        btn.className = 'ai-quick-btn';
        btn.textContent = q;
        btn.addEventListener('click', function () {
          sendMessage(q);
        });
        quickContainer.appendChild(btn);
      });
    }
    renderQuickQuestions();

    // 初始欢迎语
    body.appendChild(renderMessage('assistant', messages[0].content));
    scrollBottom();

    // 滚动到底部
    function scrollBottom() {
      requestAnimationFrame(function () {
        body.scrollTop = body.scrollHeight;
      });
    }

    // 发送消息
    async function sendMessage(text) {
      if (isStreaming || !text.trim()) return;
      text = text.trim();

      // 添加用户消息
      messages.push({ role: 'user', content: text });
      body.appendChild(renderMessage('user', text));

      scrollBottom();

      leadPromptShown = false;

      // 清空输入框
      input.value = '';
      input.style.height = 'auto';
      sendBtn.disabled = true;
      isStreaming = true;

      // 显示打字动画
      const typingEl = renderTyping();
      body.appendChild(typingEl);
      scrollBottom();

      try {
        // 流式读取 AI 回复
        let fullContent = '';
        let replyEl = null;

        for await (const chunk of streamChat(messages)) {
          if (!replyEl) {
            typingEl.remove();
            replyEl = renderMessage('assistant', '');
            body.appendChild(replyEl);
          }
          fullContent += chunk;
          replyEl.textContent = fullContent;
          scrollBottom();
        }

        if (!replyEl) {
          typingEl.remove();
          const fallback = t('errorMsg');
          replyEl = renderMessage('assistant', fallback);
          body.appendChild(replyEl);
          fullContent = fallback;
        }

        messages.push({ role: 'assistant', content: fullContent });
  
        scrollBottom();

        // 检测线索意图
        if (detectLeadIntent(text) || detectLeadIntent(fullContent)) {
          const hadLeadRecently = messages.slice(-4).some(function (m) {
            return m.role === 'assistant' && m.content.includes('📋');
          });
          if (!hadLeadRecently) {
            // 先显示提示文字
            var tipText = t('leadMsg');
            body.appendChild(renderMessage('assistant', tipText));
            messages.push({ role: 'assistant', content: tipText });

            // 再插入可填写表单
            var formEl = renderLeadForm();
            body.appendChild(formEl);
            scrollBottom();

            // 表单提交事件
            var submitted = false;
            formEl.querySelector('.ai-form-submit').addEventListener('click', function () {
              if (submitted) return;
              var name = formEl.querySelector('.ai-form-name').value.trim();
              var phone = formEl.querySelector('.ai-form-phone').value.trim();
              var need = formEl.querySelector('.ai-form-need').value.trim();
              if (!name && !phone) return;

              submitted = true;
              var info = '联系人姓名：' + name + '\n联系电话：' + phone + '\n设备类型及需求描述：' + need;
              messages.push({ role: 'user', content: info });
              body.appendChild(renderMessage('user', info));

              formEl.querySelectorAll('input,textarea,button').forEach(function (el) { el.disabled = true; });

        
              // 直接发送表单字段
              sendLeadFields(name, phone, need);
              leadPromptShown = false;
              scrollBottom();

              // AI 确认回复
              var thanks = CONFIG.leadFormThanks[lang] || CONFIG.leadFormThanks.zh;
              messages.push({ role: 'assistant', content: thanks });
              body.appendChild(renderMessage('assistant', thanks));
        
              scrollBottom();
            });

      
            leadPromptShown = true;
            scrollBottom();
          }
        }
      } catch (err) {
        typingEl.remove();
        console.error('AI Chat error:', err);
        const errText = err.message === 'rate_limit' ? t('rateLimitMsg') : t('errorMsg');
        body.appendChild(renderMessage('assistant', errText));
        messages.push({ role: 'assistant', content: errText });
  
        scrollBottom();
      } finally {
        isStreaming = false;
        sendBtn.disabled = false;
        input.focus();
      }
    }

    // 事件绑定
    sendBtn.addEventListener('click', function () {
      sendMessage(input.value);
    });

    input.addEventListener('keydown', function (e) {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage(input.value);
      }
    });

    // 自动调整输入框高度
    input.addEventListener('input', function () {
      input.style.height = 'auto';
      input.style.height = Math.min(input.scrollHeight, 80) + 'px';
    });

    bubble.addEventListener('click', function () {
      const wasClosed = !panel.classList.contains('open');
      panel.classList.toggle('open');
      if (wasClosed) {
        // 重新渲染快捷问题（语言可能变了）
        renderQuickQuestions();
        input.focus();
        scrollBottom();
      }
    });

    // 重置对话
    function resetChat() {
      messages = createGreeting();
      leadPromptShown = false;
      isStreaming = false;
      body.innerHTML = '';
      body.appendChild(renderMessage('assistant', messages[0].content));
      input.value = '';
      input.style.height = 'auto';
      sendBtn.disabled = false;
      renderQuickQuestions();
      scrollBottom();
    }

    closeBtn.addEventListener('click', function () {
      panel.classList.remove('open');
      resetChat();
    });

    // 微信客服入口: 微信内跳会话 / 微信外弹二维码
    var wecomBtn = panel.querySelector('.ai-wecom-entry');
    if (wecomBtn) {
      wecomBtn.addEventListener('click', function (e) {
        e.stopPropagation();
        openWecomEntry();
      });
    }

    // 点击外部关闭（桌面端）
    document.addEventListener('click', function (e) {
      if (panel.classList.contains('open') &&
          !panel.contains(e.target) &&
          !bubble.contains(e.target)) {
        panel.classList.remove('open');
        resetChat();
      }
    });

    // ESC 关闭
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && panel.classList.contains('open')) {
        panel.classList.remove('open');
        resetChat();
        bubble.focus();
      }
    });
  }

  // ==================== 入口 ====================
  function init() {
    injectCSS();
    applySourceToKfLinks();
    const { bubble, panel } = buildDOM();
    initChat(bubble, panel);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
