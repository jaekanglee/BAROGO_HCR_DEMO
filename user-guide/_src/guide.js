(function(){
  /* ---------- lightbox ---------- */
  var lb=document.getElementById('lb'),lbi=document.getElementById('lbi');
  document.addEventListener('click',function(e){
    var t=e.target;
    if(t.tagName==='IMG'&&t.closest('figure')&&!t.closest('.sp')){lbi.src=t.src;lbi.alt=t.alt;lb.hidden=false;}
    else if(lb&&!lb.hidden&&!t.closest('.sp')){lb.hidden=true;}
  });

  /* ---------- search: text helpers ---------- */
  var CHO='ㄱㄲㄴㄷㄸㄹㅁㅂㅃㅅㅆㅇㅈㅉㅊㅋㅌㅍㅎ';
  function norm(s){return (s||'').toLowerCase().replace(/\s+/g,'');}
  // 한글 음절은 초성으로, 이미 자음인 글자는 그대로, 나머지는 소문자로
  function cho(s){
    var out='';
    for(var i=0;i<s.length;i++){
      var c=s.charCodeAt(i);
      if(c>=0xAC00&&c<=0xD7A3) out+=CHO[Math.floor((c-0xAC00)/588)];
      else if(!/\s/.test(s[i])) out+=s[i].toLowerCase();
    }
    return out;
  }
  function isChoQuery(q){return /^[ㄱ-ㅎ]+$/.test(q);}
  function esc(s){return s.replace(/[&<>"']/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c];});}
  // 원문에서 검색어(공백 무시)를 찾아 <mark>로 감싼다. 먼저 이스케이프한다.
  function mark(text,terms){
    var spans=[];
    terms.forEach(function(t){
      if(!t||isChoQuery(t))return;
      var pat=t.split('').map(function(ch){return ch.replace(/[.*+?^${}()|[\]\\]/g,'\\$&');}).join('\\s*');
      var re=new RegExp(pat,'gi'),m;
      while((m=re.exec(text))){spans.push([m.index,m.index+m[0].length]);if(!m[0].length)re.lastIndex++;}
    });
    if(!spans.length)return esc(text);
    spans.sort(function(a,b){return a[0]-b[0];});
    var out='',pos=0;
    spans.forEach(function(sp){if(sp[0]<pos)return;out+=esc(text.slice(pos,sp[0]))+'<mark>'+esc(text.slice(sp[0],sp[1]))+'</mark>';pos=sp[1];});
    return out+esc(text.slice(pos));
  }
  function snippet(text,terms,width){
    width=width||90;
    var low=text.toLowerCase(),idx=-1;
    for(var i=0;i<terms.length&&idx<0;i++){if(!isChoQuery(terms[i]))idx=low.indexOf(terms[i]);}
    if(idx<0)return mark(text.slice(0,width),terms)+(text.length>width?'…':'');
    var st=Math.max(0,idx-Math.floor(width/3)),en=Math.min(text.length,st+width);
    return (st>0?'…':'')+mark(text.slice(st,en),terms)+(en<text.length?'…':'');
  }

  /* ---------- search: index built from the page ---------- */
  var idx=[],uid=0;
  function idFor(el){if(!el.id)el.id='q'+(++uid);return el.id;}
  function txt(el){return (el.textContent||'').replace(/\s+/g,' ').trim();}
  function add(kind,el,title,body,keys,chap,weight){
    var t=title, k=keys||'', b=body||'';
    idx.push({kind:kind,el:el,title:t,body:b,chap:chap,w:weight,
      nt:norm(t),nk:norm(k),nb:norm(b),ct:cho(t),ck:cho(k),kt:k.toLowerCase().split(/\s+/).filter(Boolean)});
  }
  function build(){
    document.querySelectorAll('section.chap').forEach(function(sec){
      var h2=sec.querySelector('h2'),chap=txt(h2);
      var when=txt(sec.querySelector('.when')||document.createElement('i'));
      add('장',sec,chap,when,h2.getAttribute('data-k'),'',4);
      var cur=chap;
      sec.querySelectorAll('h3, figure:not(.dgwrap), .tablewrap tr, details, .note').forEach(function(el){
        if(el.tagName==='H3'){
          cur=txt(el);
          var p=el.nextElementSibling,body='';
          for(var n=0;p&&n<3&&p.tagName!=='H3';n++,p=p.nextElementSibling){body+=' '+txt(p);}
          add('항목',el,cur,body.trim().slice(0,400),el.getAttribute('data-k'),chap,3);
        }else if(el.tagName==='FIGURE'){
          add('화면',el,txt(el.querySelector('figcaption')),'',(el.querySelector('img')||{}).alt,chap+' › '+cur,1.5);
        }else if(el.tagName==='TR'){
          if(el.querySelector('th'))return;
          var cells=[].map.call(el.children,txt).filter(Boolean);
          if(!cells.length)return;
          add('표',el,cells[0],cells.slice(1).join(' · '),'',chap+' › '+cur,1.8);
        }else if(el.tagName==='DETAILS'){
          add('FAQ',el,txt(el.querySelector('summary')),txt(el).replace(txt(el.querySelector('summary')),''),'',chap,3);
        }else{
          var b=el.querySelector('b'),label=b?txt(b):'참고';
          add(label,el,txt(el.querySelector('p')).slice(0,60),txt(el.querySelector('p')),'',chap+' › '+cur,1.2);
        }
      });
    });
  }

  function buildMap(){
    document.querySelectorAll('.dg .dg-n').forEach(function(a){
      add('기능 지도',a,a.getAttribute('data-t'),'',a.getAttribute('data-k'),'시작하기 › 기능 지도',2.6);
    });
  }
  /* ---------- search: scoring ---------- */
  function scoreTerm(e,t){
    if(isChoQuery(t)){
      if(e.ct.indexOf(t)===0)return 6; if(e.ct.indexOf(t)>=0)return 4; if(e.ck.indexOf(t)>=0)return 2.5;
      return 0;
    }
    if(e.nt===t)return 12;
    if(e.nt.indexOf(t)===0)return 9;
    if(e.nt.indexOf(t)>=0)return 7;
    if(e.kt.indexOf(t)>=0)return 6;
    if(e.nk.indexOf(t)>=0)return 5;
    if(e.nb.indexOf(t)>=0)return 2;
    return 0;
  }
  function search(q){
    var raw=q.trim(); if(!raw)return [];
    var terms=raw.toLowerCase().split(/\s+/).filter(Boolean);
    var whole=norm(raw),res=[];
    idx.forEach(function(e){
      var s=0;
      for(var i=0;i<terms.length;i++){var v=scoreTerm(e,terms[i]);if(!v){s=0;break;}s+=v;}
      if(!s&&terms.length>1){s=scoreTerm(e,whole)*0.8;}       // "배차 요청" → "배차요청"
      if(s&&terms.length>1&&e.nt.indexOf(whole)>=0)s+=10;      // 검색어 전체가 제목에 그대로 있으면 우선
      if(s)res.push({e:e,s:s*e.w});
    });
    if(!res.length&&terms.length>1){
      // 모든 단어가 맞는 결과가 없으면, 한 단어라도 맞는 결과를 낮은 점수로 보여준다
      idx.forEach(function(e){
        var s=0,hit=0;
        terms.forEach(function(t){var v=scoreTerm(e,t);if(v){s+=v;hit++;}});
        if(hit)res.push({e:e,s:s*e.w*(hit/terms.length)*0.6});
      });
    }
    res.sort(function(a,b){return b.s-a.s;});
    // 같은 요소가 중복되지 않게, 최대 30개
    var seen=new Set(),out=[];
    for(var i=0;i<res.length&&out.length<30;i++){if(!seen.has(res[i].e.el)){seen.add(res[i].e.el);out.push(res[i].e);}}
    return out;
  }

  /* ---------- search: UI ---------- */
  var sp,inp,list,items=[],sel=0,timer,lastFocus;
  function ui(){
    sp=document.createElement('div');sp.className='sp';sp.hidden=true;
    sp.innerHTML='<div class="sp-box" role="dialog" aria-modal="true" aria-label="가이드 검색">'+
      '<div class="sp-in"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/></svg>'+
      '<input id="sq" type="search" autocomplete="off" spellcheck="false" placeholder="기능이나 화면 이름으로 찾기 (예: 즉시배차, 출금, ㅂㅊ)" role="combobox" aria-expanded="true" aria-controls="sres" aria-autocomplete="list">'+
      '<button type="button" class="sp-close" aria-label="검색 닫기">닫기</button></div>'+
      '<ul class="sp-list" id="sres" role="listbox"></ul>'+
      '<div class="sp-foot"><span><kbd>↑</kbd><kbd>↓</kbd> 이동</span><span><kbd>Enter</kbd> 열기</span><span><kbd>Esc</kbd> 닫기</span><span>초성 검색 지원</span></div></div>';
    document.body.appendChild(sp);
    inp=sp.querySelector('input');list=sp.querySelector('ul');
    inp.addEventListener('input',function(){clearTimeout(timer);timer=setTimeout(render,120);});
    inp.addEventListener('keydown',function(e){
      if(e.key==='ArrowDown'){e.preventDefault();move(1);}
      else if(e.key==='ArrowUp'){e.preventDefault();move(-1);}
      else if(e.key==='Enter'&&!e.isComposing){e.preventDefault();if(items[sel])go(items[sel]);}
      else if(e.key==='Escape'){e.preventDefault();close();}
    });
    list.addEventListener('mousemove',function(e){var li=e.target.closest('li[data-i]');if(li&&+li.dataset.i!==sel){sel=+li.dataset.i;paint();}});
    list.addEventListener('click',function(e){var li=e.target.closest('li[data-i]');if(li)go(items[+li.dataset.i]);});
    sp.querySelector('.sp-close').addEventListener('click',close);
    sp.addEventListener('mousedown',function(e){if(e.target===sp)close();});
  }
  function render(){
    var q=inp.value,terms=q.trim().toLowerCase().split(/\s+/).filter(Boolean);
    items=q.trim()?search(q):idx.filter(function(e){return e.kind==='장';});
    sel=0;
    if(!items.length){list.innerHTML='<li class="sp-empty" role="option" aria-disabled="true">&ldquo;'+esc(q)+'&rdquo;에 맞는 내용이 없습니다. 다른 말(예: 배차, 할증, 출금)로 찾아보세요.</li>';return;}
    list.innerHTML=items.map(function(e,i){
      var s=e.body?'<span class="sp-s">'+snippet(e.body,terms)+'</span>':'';
      var c=e.chap?'<span class="sp-c">'+esc(e.chap)+'</span>':'';
      return '<li role="option" id="so'+i+'" data-i="'+i+'"><span class="sp-t"><span class="sp-tag">'+esc(e.kind)+'</span>'+mark(e.title,terms)+'</span>'+c+s+'</li>';
    }).join('');
    paint();
  }
  function paint(){
    [].forEach.call(list.children,function(li,i){li.setAttribute('aria-selected',i===sel?'true':'false');});
    var cur=list.children[sel];
    if(cur){inp.setAttribute('aria-activedescendant',cur.id||'');cur.scrollIntoView({block:'nearest'});}
  }
  function move(d){if(!items.length)return;sel=Math.max(0,Math.min(items.length-1,sel+d));paint();}
  function open(prefill){
    lastFocus=document.activeElement;sp.hidden=false;document.documentElement.style.overflow='hidden';
    if(typeof prefill==='string')inp.value=prefill;
    render();setTimeout(function(){inp.focus();inp.select();},0);
  }
  function close(){sp.hidden=true;document.documentElement.style.overflow='';if(lastFocus&&lastFocus.focus)lastFocus.focus();}
  function go(e){
    close();
    var el=e.el,d=el.closest('details'),inSvg=!!el.closest('svg');
    if(d)d.open=true;
    var id=idFor(el);
    try{history.replaceState(null,'','#'+id);}catch(_){}
    el.scrollIntoView({block:inSvg?'center':'start',behavior:matchMedia('(prefers-reduced-motion: reduce)').matches?'auto':'smooth'});
    el.classList.remove('flash');void el.offsetWidth;el.classList.add('flash');
    setTimeout(function(){el.classList.remove('flash');},1900);
  }

  build();buildMap();ui();
  // 지도 노드·매트릭스 머리글처럼 페이지 안 링크를 누르면 도착한 곳을 잠깐 강조
  document.addEventListener('click',function(e){
    var a=e.target.closest&&e.target.closest('a[href^="#"]');
    if(!a||a.closest('.sp'))return;
    var id=(a.getAttribute('href')||'').slice(1),t=id&&document.getElementById(id);
    if(!t)return;
    var d=t.closest('details');if(d)d.open=true;
    setTimeout(function(){t.classList.remove('flash');void t.offsetWidth;t.classList.add('flash');setTimeout(function(){t.classList.remove('flash');},1900);},350);
  });
  var btn=document.getElementById('sbtn');
  if(btn)btn.addEventListener('click',function(){open();});
  document.addEventListener('keydown',function(e){
    if(!sp.hidden)return;
    var typing=/^(INPUT|TEXTAREA|SELECT)$/.test((document.activeElement||{}).tagName||'');
    if((e.key==='k'||e.key==='K')&&(e.metaKey||e.ctrlKey)){e.preventDefault();open();}
    else if(e.key==='/'&&!typing){e.preventDefault();open();}
  });
  // 공유 링크의 #id로 들어오면 그 위치를 강조
  if(location.hash.length>1){var t=document.getElementById(location.hash.slice(1));if(t){var d=t.closest('details');if(d)d.open=true;setTimeout(function(){t.scrollIntoView({block:'start'});t.classList.add('flash');},300);}}
  window.__guideSearch=search;
})();
