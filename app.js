/* 🇮🇹意大利语实景会话 — 客户端逻辑
 * 数据分层：window.__IDX__（目录索引，首屏）由 data/index.js 提供；
 * 每个单元完整数据由 data/<id>.js 在点击时按需加载并缓存。
 */
// ====== AUDIO ENGINE ======
let curSpeed='m';
const RATE_FACTOR = {s:0.7, m:1.0, f:1.25};
let audioEl=new Audio();
audioEl.preload='none';
audioEl.playbackRate = RATE_FACTOR[curSpeed];
// 预加载缓冲：连播时提前拉取下一句音频，消除句间网络空档（提升加载/播放体验）
let prefetchEl=new Audio();
prefetchEl.preload='auto';
function prefetch(url){ try{ if(url) prefetchEl.src=url; }catch(e){} }
function cancelPrefetch(){ try{ prefetchEl.removeAttribute('src'); }catch(e){} }
let playingBtn=null;
function stopAudio(){
  audioEl.pause(); audioEl.currentTime=0;
  cancelPrefetch();
  // 清除所有高亮（词卡 / 句子 / 对话气泡 / 独白句），避免卡住
  document.querySelectorAll('.playing').forEach(el=>el.classList.remove('playing'));
  playingBtn=null;
}
function playUrl(url, btn){
  if(playingBtn===btn){ stopAudio(); return; }
  stopAudio();
  audioEl.src=url;
  audioEl.playbackRate = RATE_FACTOR[curSpeed];
  const p=audioEl.play();
  if(p&&p.catch) p.catch(()=>{});
  playingBtn=btn; if(btn) btn.classList.add('playing');
  audioEl.onended=()=>{ if(playingBtn){playingBtn.classList.remove('playing'); playingBtn=null;} };
}
function playVocab(btn){ playUrl(btn.dataset.url, btn); }
function playSentence(btn, uid, idx){ playUrl(`audio/s/${uid}_${idx}_m.mp3`, btn); }
function playDialogue(btn, uid, seg){ playUrl(`audio/d/${uid}_${seg}_m.mp3`, btn); }
function playConv(btn, base){ playUrl(`${base}_m.mp3`, btn); }
// 独白逐句独立播放：audio/d/<uid>_<seg>_<pidx>_m.mp3
function playMonoPair(btn, uid, seg, pidx){ playUrl(`audio/d/${uid}_${seg}_${pidx}_m.mp3`, btn); }
// 独白逐句连播：依次点亮每一句气泡
function playMonoSeq(btn, uid, seg, count){
  if(playingBtn===btn){ stopAudio(); return; }
  stopAudio();
  audioEl.playbackRate = RATE_FACTOR[curSpeed];
  const segEl = btn.parentElement.nextElementSibling;
  const lines = segEl ? Array.from(segEl.querySelectorAll('.pair-line')) : [];
  const urls = [];
  for(let i=0;i<count;i++) urls.push(`audio/d/${uid}_${seg}_${i}_m.mp3`);
  let i=0;
  playingBtn=btn; btn.classList.add('playing');
  function next(){
    if(i>=urls.length){
      btn.classList.remove('playing');
      lines.forEach(l=>l.classList.remove('playing'));
      playingBtn=null; return;
    }
    audioEl.src=urls[i];
    audioEl.play().catch(()=>{});
    audioEl.onended=()=>{ if(lines[i]) lines[i].classList.remove('playing'); i++; next(); };
    if(lines[i]){ lines[i].classList.add('playing'); lines[i].scrollIntoView({behavior:'smooth', block:'center'}); }
    prefetch(urls[i+1]);
  }
  audioEl.onended=next; next();
}
// 对话播放全部：依次播放每一句并点亮对应气泡
function playConvSeq(btn){
  if(playingBtn===btn){ stopAudio(); return; }
  stopAudio();
  audioEl.playbackRate = RATE_FACTOR[curSpeed];
  const card = btn.parentElement.nextElementSibling;
  const convEl = card ? card.querySelector('.conv') : null;
  const bubbles = convEl ? Array.from(convEl.querySelectorAll('.conv-bubble')) : [];
  let i=0;
  playingBtn=btn; btn.classList.add('playing');
  function next(){
    if(i>=bubbles.length){
      btn.classList.remove('playing');
      bubbles.forEach(b=>b.classList.remove('playing'));
      playingBtn=null; return;
    }
    const base = bubbles[i].closest('.conv-row').dataset.audio;
    audioEl.src = base + '_m.mp3';
    audioEl.play().catch(()=>{});
    audioEl.onended = ()=>{ bubbles[i].classList.remove('playing'); i++; next(); };
    bubbles[i].classList.add('playing');
    bubbles[i].scrollIntoView({behavior:'smooth', block:'center'});
    const nextBase = (bubbles[i+1] && bubbles[i+1].closest('.conv-row').dataset.audio) || '';
    prefetch(nextBase ? nextBase + '_m.mp3' : '');
  }
  audioEl.onended=next; next();
}
function playSeq(urls, btn){
  if(playingBtn===btn){ stopAudio(); return; }
  stopAudio();
  audioEl.playbackRate = RATE_FACTOR[curSpeed];
  let wrap = btn.parentElement;
  while(wrap && !wrap.querySelector('.sent-grid')) wrap = wrap.parentElement;
  const cards = wrap ? Array.from(wrap.querySelectorAll('.sentence-item')) : [];
  let i=0;
  playingBtn=btn; btn.classList.add('playing');
  function next(){
    if(i>=urls.length){ btn.classList.remove('playing'); playingBtn=null; return; }
    audioEl.src=urls[i];
    audioEl.play().catch(()=>{});
    audioEl.onended=()=>{ if(cards[i]) cards[i].classList.remove('playing'); i++; next(); };
    if(cards[i]){ cards[i].classList.add('playing'); cards[i].scrollIntoView({behavior:'smooth', block:'center'}); }
    prefetch(urls[i+1]);
  }
  audioEl.onended=next; next();
}

// 关键词全局连播：依次播放每个单词并点亮对应卡片
function playVocabSeq(btn){
  if(playingBtn===btn){ stopAudio(); return; }
  stopAudio();
  audioEl.playbackRate = RATE_FACTOR[curSpeed];
  let wrap = btn.parentElement;
  while(wrap && !wrap.querySelector('.vocab-grid')) wrap = wrap.parentElement;
  const cards = wrap ? Array.from(wrap.querySelectorAll('.vocab-item')) : [];
  // 直接从 data-url 读取，避免解析 onclick 字符串（原正则因末尾 ')' 导致匹配失败崩溃）
  const urls = cards.map(c=>(c.dataset.url||'').trim()).filter(Boolean);
  let i=0;
  playingBtn=btn; btn.classList.add('playing');
  function next(){
    if(i>=urls.length){ btn.classList.remove('playing'); playingBtn=null; return; }
    audioEl.src=urls[i];
    audioEl.play().catch(()=>{});
    audioEl.onended=()=>{ cards[i].classList.remove('playing'); i++; next(); };
    cards[i].classList.add('playing'); cards[i].scrollIntoView({behavior:'smooth', block:'center'});
    prefetch(urls[i+1]);
  }
  audioEl.onended=next; next();
}

// ====== TOC（基于 __IDX__ 目录索引）======
function buildTOC(){
  const c = document.getElementById('tocContainer');
  c.innerHTML = '';
  const idx = window.__IDX__;
  if(!idx || !idx.chapters) return;
  idx.chapters.forEach((chap)=>{
    const ct = document.createElement('div');
    ct.className = 'chapter-title';
    ct.innerHTML = `<span>${chap.title} <span class="sub">${chap.subtitle}</span></span><span class="arrow">▼</span>`;
    const ul = document.createElement('div');
    ul.className = 'unit-list';
    (chap.units||[]).forEach(u=>{
      const it = document.createElement('div');
      it.className = 'unit-item';
      it.dataset.uid = u.id;
      it.dataset.search = (u.title+' '+u.subtitle+' '+chap.title+' '+chap.subtitle).toLowerCase();
      it.innerHTML = `<span class="unit-num">${u.num}</span>${u.title} <span style="opacity:.6">${u.subtitle}</span>`;
      it.onclick = ()=>showUnit(u.id);
      ul.appendChild(it);
    });
    ct.onclick = ()=>{ ct.classList.toggle('collapsed'); ul.classList.toggle('collapsed'); };
    c.appendChild(ct); c.appendChild(ul);
  });
}
function filterTOC(q){
  q=q.trim().toLowerCase();
  document.querySelectorAll('.unit-item').forEach(it=>{
    it.style.display = (!q || it.dataset.search.includes(q)) ? '' : 'none';
  });
}

// ====== 单元懒加载 ======
const UNIT_CACHE = {};
function loadUnit(id){
  if(UNIT_CACHE[id]) return Promise.resolve(UNIT_CACHE[id]);
  return new Promise((resolve,reject)=>{
    const s=document.createElement('script');
    s.src='data/'+id+'.js';
    s.onload=()=>{
      const u=(window.__UNITS__ && window.__UNITS__[id]) || null;
      if(u){ UNIT_CACHE[id]=u; resolve(u); } else { reject(new Error('unit data missing: '+id)); }
    };
    s.onerror=()=>reject(new Error('unit load failed: '+id));
    document.head.appendChild(s);
  });
}

// ====== RENDER UNIT ======
function esc(s){ return (s||'').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;'); }
// 场景人物：括号内的中文译文降级显示，保持「意语（中文）」的统一层次
function luogoVal(s){
  return esc(s).replace(/（[^（）]*）/g, function(m){ return '<span class="lg-zh">'+m+'</span>'; });
}
const LS_LAST_UNIT = 'ital_conv_last_unit';
function saveLastUnit(id){
  try{ localStorage.setItem(LS_LAST_UNIT, id); }catch(e){}
}
function readLastUnit(){
  try{ return localStorage.getItem(LS_LAST_UNIT); }catch(e){ return null; }
}
function showUnit(id){
  document.getElementById('welcomePanel').style.display='none';
  saveLastUnit(id);
  let activeItem=null;
  document.querySelectorAll('.unit-item').forEach(it=>{
    it.classList.toggle('active', it.dataset.uid===id);
    if(it.dataset.uid===id) activeItem=it;
  });
  const box = document.getElementById('unitContentContainer');
  box.innerHTML = '<div class="unit-content"><div class="welcome" style="padding:40px 0">⏳ 正在加载本单元…</div></div>';
  loadUnit(id).then(u=>{
    box.innerHTML = renderUnit(u);
    box.firstChild.classList.add('active');
    // 移动端：选完单元立即收起导航，无需再点一次
    closeSidebar();
    // 让侧栏目录滚到当前单元（仅首次直接载入时才有实际效果）
    if(activeItem && activeItem.scrollIntoView) activeItem.scrollIntoView({block:'nearest'});
    document.getElementById('main').scrollTop=0;
    window.scrollTo(0,0);
  }).catch(()=>{
    box.innerHTML = '<div class="unit-content"><div class="welcome" style="padding:40px 0">❌ 单元加载失败，请重试</div></div>';
  });
}
function renderUnit(u){
  let html = `<div class="unit-content">`;
  html += `<div class="unit-header">
    <div><div class="label">${u.num}</div><h2>${esc(u.title)}</h2><div class="sub">${esc(u.subtitle)}</div></div>
    <div class="speed-bar"><span class="slabel">语速</span>
      <button class="speed-btn" data-s="s" onclick="setSpeed('s',this)">慢</button>
      <button class="speed-btn active" data-s="m" onclick="setSpeed('m',this)">中</button>
      <button class="speed-btn" data-s="f" onclick="setSpeed('f',this)">快</button>
    </div></div>`;

  // Luogo
  if(u.luogo && (u.luogo.place || u.luogo.people)){
    html += `<div class="section-title">Luogo e Personaggi <span class="it">场景及人物</span></div>`;
    html += `<div class="luogo-box">`;
    if(u.luogo.place) html += `<div class="lg-row"><span class="lg-key">地点：</span><span class="lg-val">${luogoVal(u.luogo.place)}</span></div>`;
    if(u.luogo.people) html += `<div class="lg-row"><span class="lg-key">人物：</span><span class="lg-val">${luogoVal(u.luogo.people)}</span></div>`;
    html += `</div>`;
  }
  // Vocab
  if(u.vocab && u.vocab.length){
    html += `<div class="section-title">Parole chiave <span class="it">关键词</span></div>`;
    html += `<div style="margin-bottom:8px"><button class="speed-btn" style="background:#1a1a2e;color:#fff" onclick="playVocabSeq(this)">▶ 播放全部</button></div>`;
    html += `<div class="vocab-grid">`;
    u.vocab.forEach(v=>{
      const url = v.audio || '';
      html += `<div class="vocab-item" data-url="${url}" onclick="playVocab(this)">
        <span class="it">${esc(v.it)}</span><span class="zh">${esc(v.zh)}</span></div>`;
    });
    html += `</div>`;
  }
  // Sentences
  if(u.sentences && u.sentences.length){
    const urls = u.sentences.map((s,i)=>`audio/s/${u.id}_${i}_m.mp3`);
    html += `<div class="section-title">Frasi d'uso comune <span class="it">常用句</span></div>`;
    html += `<div style="margin-bottom:8px"><button class="speed-btn" style="background:#1a1a2e;color:#fff" onclick="playSeq([${urls.map(x=>`'${x}'`).join(',')}],this)">▶ 播放全部</button></div>`;
    html += `<div class="sent-grid">`;
    u.sentences.forEach((s,i)=>{
      html += `<div class="sentence-item" onclick="playSentence(this,'${u.id}',${i})">
        <div class="s-text"><div class="it">${esc(s.it)}</div><div class="zh">${esc(s.zh)}</div></div></div>`;
    });
    html += `</div>`;
  }
  // Custom sections layout (e.g. c1u1: 旁白 / 词法解析 / 对话 / 词法解析)
  // Falls back to the legacy 视频文本 + 词法解析 rendering for other units.
  if(u.sections && u.sections.length){
    u.sections.forEach(sec=>{
      if(sec.type==='text'){
        html += `<div class="section-title">${esc(sec.title)}</div>`;
        (sec.segs||[]).forEach(seg=>{
          const d = u.dialogue[seg]; if(!d) return;
          const nPairs = (d.pairs && d.pairs.length) ? d.pairs.length : 0;
          const playAll = nPairs>0
            ? `playMonoSeq(this,'${u.id}',${seg},${nPairs})`
            : `playDialogue(this,'${u.id}',${seg})`;
          html += `<div style="margin-bottom:8px"><button class="speed-btn" style="background:#1a1a2e;color:#fff" onclick="${playAll}">▶ 播放全部</button></div>`;
          html += `<div class="dialogue-seg">`;
          if(d.pairs && d.pairs.length){
            d.pairs.forEach((p,pi)=>{
              html += `<div class="pair-line" onclick="playMonoPair(this,'${u.id}',${seg},${pi})"><div class="d-it">${esc(p.it)}</div><div class="d-zh">${esc(p.zh)}</div></div>`;
            });
          } else {
            html += `<div class="d-it">${esc(d.it)}</div>`;
            if(d.zh) html += `<div class="d-zh">${esc(d.zh)}</div>`;
          }
          html += `</div>`;
        });
      } else if(sec.type==='conversation'){
        const conv = u.conversation||[];
        const rng = sec.range || [0, conv.length];
        const lines = conv.slice(rng[0], rng[1]);
        if(lines.length){
          html += `<div class="section-title">${esc(sec.title)}</div>`;
          html += `<div style="margin-bottom:8px"><button class="speed-btn" style="background:#1a1a2e;color:#fff" onclick="playConvSeq(this)">▶ 播放全部</button></div>`;
          html += `<div class="conv-card">`;
          html += `<div class="conv">`;
          lines.forEach((ln)=>{
            const isAldo = ln.speaker==='aldo';
            const who = ln.who || (isAldo ? 'Aldo Sparice' : 'Signora');
            const cls = isAldo ? 'aldo' : 'signora';
            html += `<div class="conv-row ${cls}" data-audio="${ln.audio}">`
              + `<div class="conv-head"><span class="conv-who">${esc(who)}</span></div>`
              + `<div class="conv-bubble" onclick="playUrl('${ln.audio}_m.mp3',this)"><div class="d-it">${esc(ln.it)}</div><div class="d-zh">${esc(ln.zh)}</div></div>`
              + `</div>`;
          });
          html += `</div></div>`;
        }
      } else if(sec.type==='info'){
        if(sec.blocks && sec.blocks.length){
          html += `<div class="section-title">${esc(sec.title)}</div><div class="info-card">`;
          sec.blocks.forEach(b=>{
            html += `<div class="info-block">`;
            if(b.subtitle) html += `<div class="info-sub">${esc(b.subtitle)}</div>`;
            if(b.intro) html += `<div class="info-intro">${esc(b.intro)}</div>`;
            (b.items||[]).forEach(it=>{
              html += `<div class="info-item"><span class="info-term">${esc(it.term)}</span> <span class="info-text">${esc(it.text)}</span></div>`;
            });
            html += `</div>`;
          });
          html += `</div>`;
        }
      } else {
        const idxs = sec.notes||[];
        if(idxs.length){
          html += `<div class="section-title">${esc(sec.title)}</div><div class="note-grid">`;
          idxs.forEach(ni=>{
            const n = u.notes[ni]; if(!n) return;
            const tm = (n.term||'').split('：');
            const itPart = tm[0];
            const zhPart = tm.length>1 ? tm.slice(1).join('：') : '';
            const parts = itPart.split('/').map(s=>s.trim()).filter(s=>s);
            const ta = (n.audio && n.audio.term) || [];
            html += `<div class="note-item"><div class="term">`;
            parts.forEach((p,k)=>{
              const path = ta[k] || (ta[0]||'');
              html += `<span class="term-word" onclick="playUrl('${path}',this)">${esc(p)}</span>`;
              if(k<parts.length-1) html += ` <span class="term-slash">/</span> `;
            });
            if(zhPart) html += `<span class="term-zh">：${esc(zhPart)}</span>`;
            html += `</div>`;
            if(n.explain) html += `<div class="explain">${esc(n.explain)}</div>`;
            const exs = Array.isArray(n.examples) ? n.examples : (n.example ? [n.example] : []);
            const ea = (n.audio && n.audio.examples) || [];
            if(exs.length){
              html += `<div class="examples">`;
              exs.forEach((ex,ei)=>{
                const exLines = ex.split('\n');
                const exIt = exLines[0];
                const exZh = exLines.slice(1).join('\n');
                const exPath = ea[ei] || '';
                html += `<div class="note-ex" onclick="playUrl('${exPath}',this)"><span class="ex-it">${esc(exIt)}</span>` + (exZh?`<span class="ex-zh">${esc(exZh)}</span>`:'') + `</div>`;
              });
              html += `</div>`;
            }
            html += `</div>`;
          });
          html += `</div>`;
        }
      }
    });
  } else {
    // Legacy: 视频文本 (dialogue) + 词法解析 (notes)
    if(u.dialogue && u.dialogue.length){
      const n = u.dialogue.length;
      u.dialogue.forEach((d,i)=>{
        const lbl = n>1 ? `Testo ${i+1}` : 'Testo';
        const zl  = n>1 ? `视频文本 ${i+1}` : '视频文本';
        html += `<div class="section-title">${lbl} <span class="it">${zl}</span></div>`;
        html += `<div class="dialogue-seg">
          <div class="d-head"><button class="d-play" onclick="playDialogue(this,'${u.id}',${i})">▶</button><span class="d-tag">播放本段</span></div>
          <div class="d-it">${esc(d.it)}</div>`;
        if(d.zh) html += `<div class="d-zh">${esc(d.zh)}</div>`;
        html += `</div>`;
      });
    }
    if(u.notes && u.notes.length){
      html += `<div class="section-title">Note lessicali <span class="it">词法解析</span></div><div class="note-grid">`;
      u.notes.forEach(n=>{
        const tm = (n.term||'').split('：');
        const itPart = tm[0];
        const zhPart = tm.length>1 ? tm.slice(1).join('：') : '';
        const parts = itPart.split('/').map(s=>s.trim()).filter(s=>s);
        const ta = (n.audio && n.audio.term) || [];
        html += `<div class="note-item"><div class="term">`;
        parts.forEach((p,k)=>{
          const path = ta[k] || (ta[0]||'');
          html += `<span class="term-word" onclick="playUrl('${path}',this)">${esc(p)}</span>`;
          if(k<parts.length-1) html += ` <span class="term-slash">/</span> `;
        });
        if(zhPart) html += `<span class="term-zh">：${esc(zhPart)}</span>`;
        html += `</div>`;
        if(n.explain) html += `<div class="explain">${esc(n.explain)}</div>`;
        const exs = Array.isArray(n.examples) ? n.examples : (n.example ? [n.example] : []);
        const ea = (n.audio && n.audio.examples) || [];
        if(exs.length){
          html += `<div class="examples">`;
          exs.forEach((ex,ei)=>{
            const exLines = ex.split('\n');
            const exIt = exLines[0];
            const exZh = exLines.slice(1).join('\n');
            const exPath = ea[ei] || '';
            html += `<div class="note-ex" onclick="playUrl('${exPath}',this)"><span class="ex-it">${esc(exIt)}</span>` + (exZh?`<span class="ex-zh">${esc(exZh)}</span>`:'') + `</div>`;
          });
          html += `</div>`;
        }
        html += `</div>`;
      });
      html += `</div>`;
    }
  }
  html += `</div>`;
  return html;
}
function setSpeed(s, btn){
  curSpeed=s;
  document.querySelectorAll('.speed-bar .speed-btn').forEach(b=>b.classList.toggle('active', b===btn));
  // 播放中实时变速：立即改变 playbackRate，不暂停、不丢进度
  if(audioEl && !audioEl.paused){ audioEl.playbackRate = RATE_FACTOR[s]; }
}

// ====== MOBILE ======
function closeSidebar(){
  document.getElementById('sidebar').classList.remove('open');
  document.getElementById('sidebarOverlay').classList.remove('show');
}
function toggleSidebar(){
  const sb = document.getElementById('sidebar');
  if(sb.classList.contains('open')) closeSidebar();
  else { sb.classList.add('open'); document.getElementById('sidebarOverlay').classList.add('show'); }
}

// ====== INIT ======
buildTOC();
// 首次打开进入 Unità 1；之后打开回到上次浏览的单元
(function restoreLastUnit(){
  const idx = window.__IDX__;
  if(!idx || !idx.chapters || !idx.chapters.length) return;
  const first = idx.chapters[0].units[0].id;
  const saved = readLastUnit();
  const target = (saved && idx.chapters.some(ch=>ch.units.some(u=>u.id===saved))) ? saved : first;
  showUnit(target);
})();

// ====== SERVICE WORKER（仅缓存音频 mp3，提升重复播放与离线体验）======
if ('serviceWorker' in navigator) {
  window.addEventListener('load', function () {
    navigator.serviceWorker.register('./sw.js', { updateViaCache: 'none' })
      .catch(function (e) { console.warn('SW register failed:', e); });
  });
}
