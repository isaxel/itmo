/* Тренажёр карточек: логика колоды, переворот, прогресс. Данные приходят из cards.json или window.CARDS. */
function startApp(CARDS){
  CARDS.forEach(function(c,i){c.id=i+1;});

  var KEY="arch-cards-learned-v1";
  var learned={};
  try{ learned=JSON.parse(localStorage.getItem(KEY)||"{}")||{}; }catch(e){ learned={}; }
  function save(){ try{ localStorage.setItem(KEY,JSON.stringify(learned)); }catch(e){} }

  var el=function(id){return document.getElementById(id);};
  var card=el("card"), deck=[], idx=0, flipped=false;

  /* --- фильтр по разделам --- */
  var topics={};
  CARDS.forEach(function(c){topics[c.t]=(topics[c.t]||0)+1;});
  var names=Object.keys(topics).sort(function(a,b){return topics[b]-topics[a];});
  var sel=el("topic");
  var optAll=document.createElement("option");
  optAll.value="*"; optAll.textContent="Все разделы ("+CARDS.length+")";
  sel.appendChild(optAll);
  names.forEach(function(n){
    var o=document.createElement("option"); o.value=n; o.textContent=n+" ("+topics[n]+")"; sel.appendChild(o);
  });

  function buildDeck(keepId){
    var t=sel.value, onlyNew=el("onlyNew").checked;
    deck=CARDS.filter(function(c){
      if(t!=="*" && c.t!==t) return false;
      if(onlyNew && learned[c.id]) return false;
      return true;
    });
    if(!deck.length) deck=CARDS.filter(function(c){return t==="*"||c.t===t;});
    if(el("shuffle").checked){
      for(var i=deck.length-1;i>0;i--){var j=Math.floor(Math.random()*(i+1));var s=deck[i];deck[i]=deck[j];deck[j]=s;}
    }
    idx=0;
    if(keepId){ var p=deck.findIndex(function(c){return c.id===keepId;}); if(p>=0) idx=p; }
    buildBus();
    render();
  }

  function buildBus(){
    var line=el("busLine"); line.textContent="";
    var frag=document.createDocumentFragment();
    deck.forEach(function(c,i){
      var d=document.createElement("i"); d.className="tick"; d.dataset.i=i; frag.appendChild(d);
    });
    line.appendChild(frag);
  }

  function paintBus(){
    var ticks=el("busLine").children;
    for(var i=0;i<ticks.length;i++){
      var c=deck[i], cl="tick";
      if(learned[c.id]) cl+=" done";
      if(i===idx) cl+=" here";
      ticks[i].className=cl;
    }
  }

  function render(){
    var c=deck[idx]; if(!c) return;
    flipped=false; card.classList.remove("flipped");
    card.classList.toggle("is-learned", !!learned[c.id]);
    var no=String(c.id).padStart(3,"0");
    el("frontNo").textContent=no; el("backNo").textContent=no;
    el("frontTopic").textContent=c.t; el("backTopic").textContent=c.t;
    el("qText").textContent=c.q;
    var a=el("aText"); a.textContent="";
    c.a.forEach(function(line){ var p=document.createElement("p"); p.textContent=line; a.appendChild(p); });
    el("pos").textContent=idx+1;
    el("total").textContent=deck.length;
    el("deckCount").textContent=deck.length;
    el("qno").textContent="Вопрос №"+c.id;
    var done=deck.filter(function(x){return learned[x.id];}).length;
    el("doneCount").textContent=done;
    el("knowBtn").textContent=learned[c.id]?"↺ Не знаю":"✓ Знаю";
    paintBus();
  }

  function go(step){
    if(!deck.length) return;
    idx=(idx+step+deck.length)%deck.length;
    render();
  }
  function flip(){
    flipped=!flipped;
    card.classList.toggle("flipped",flipped);
  }
  function toggleKnown(){
    var c=deck[idx]; if(!c) return;
    if(learned[c.id]) delete learned[c.id]; else learned[c.id]=1;
    save();
    card.classList.toggle("is-learned", !!learned[c.id]);
    el("knowBtn").textContent=learned[c.id]?"↺ Не знаю":"✓ Знаю";
    var done=deck.filter(function(x){return learned[x.id];}).length;
    el("doneCount").textContent=done;
    paintBus();
  }

  card.addEventListener("click",flip);
  el("flipBtn").addEventListener("click",function(e){e.stopPropagation();flip();});
  el("prevBtn").addEventListener("click",function(){go(-1);});
  el("nextBtn").addEventListener("click",function(){go(1);});
  el("knowBtn").addEventListener("click",toggleKnown);
  sel.addEventListener("change",function(){buildDeck();});
  el("onlyNew").addEventListener("change",function(){buildDeck();});
  el("shuffle").addEventListener("change",function(){buildDeck(deck[idx]&&deck[idx].id);});
  el("resetBtn").addEventListener("click",function(){
    learned={}; save(); buildDeck(deck[idx]&&deck[idx].id);
  });
  el("busLine").addEventListener("click",function(e){
    var t=e.target.closest(".tick"); if(!t) return;
    idx=+t.dataset.i; render();
  });

  document.addEventListener("keydown",function(e){
    if(e.target.tagName==="SELECT"||e.target.tagName==="INPUT") return;
    var k=e.key;
    if(k===" "||k==="Spacebar"){e.preventDefault();flip();}
    else if(k==="ArrowRight"){e.preventDefault();go(1);}
    else if(k==="ArrowLeft"){e.preventDefault();go(-1);}
    else if(k==="Enter"){e.preventDefault();toggleKnown();}
    else if(k==="s"||k==="S"||k==="ы"||k==="Ы"){
      var cb=el("shuffle"); cb.checked=!cb.checked; buildDeck(deck[idx]&&deck[idx].id);
    }
    else if(k==="r"||k==="R"||k==="к"||k==="К"){
      idx=Math.floor(Math.random()*deck.length); render();
    }
  });

  /* свайпы на телефоне */
  var x0=null;
  card.addEventListener("touchstart",function(e){x0=e.touches[0].clientX;},{passive:true});
  card.addEventListener("touchend",function(e){
    if(x0===null) return;
    var dx=e.changedTouches[0].clientX-x0; x0=null;
    if(Math.abs(dx)>60){ go(dx<0?1:-1); }
  },{passive:true});

  /* тема */
  var tb=el("themeBtn");
  tb.addEventListener("click",function(){
    var cur=document.documentElement.getAttribute("data-theme");
    var isDark = cur ? cur==="dark" : window.matchMedia("(prefers-color-scheme: dark)").matches;
    document.documentElement.setAttribute("data-theme", isDark?"light":"dark");
  });

  buildDeck();
}

/* --- загрузка данных --- */
(function bootstrap(){
  if (window.CARDS && window.CARDS.length) { startApp(window.CARDS); return; }
  var tries = ["./cards.json", "../data/cards.json", "./data/cards.json"];
  (function next(i){
    if (i >= tries.length) {
      document.getElementById("qText").textContent =
        "Не удалось загрузить cards.json. Откройте dist/index.html (там данные встроены) или запустите локальный сервер: npm start";
      return;
    }
    fetch(tries[i]).then(function(r){ if(!r.ok) throw 0; return r.json(); })
      .then(function(d){ startApp(d); })
      .catch(function(){ next(i+1); });
  })(0);
})();
