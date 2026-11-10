# -*- coding: utf-8 -*-
"""Ajustes específicos da versão Android do WaveFly.

São aplicados por cima do waveflysite.py na hora em que o app inicia (ver app_entry.start):
  - corrige a miniatura dos vídeos na biblioteca;
  - tira o botão "Forçar" de downloads cancelados;
  - conserta o botão de play que cobria as miniaturas da busca;
  - permite fechar "Ajustes e Qualidade" arrastando para baixo;
  - avisa o Android sobre o player (para a notificação) e recebe os comandos dela.
"""
import os
import sys

# --------------------------------------------------------------------------- CSS
CSS = """<style id="wf-android-css">
/* o botão 3D genérico pintava o play por cima da miniatura (busca por nome, dentro da playlist, lista) */
html body button.pp{background:rgba(0,0,0,.22)!important;border:0!important;border-radius:0!important;
 box-shadow:none!important;color:#fff!important;text-shadow:none!important}
html body button.pp:active{transform:none!important;box-shadow:none!important}
html body .rs.pvon .bd2>.tt:first-child{color:var(--t-ac2,#e46f22)!important;font-weight:700}
html body .rs.pvcarr .bd2>.tt:first-child{opacity:.6}
</style>
"""

# --------------------------------------------------------------------------- JS
JS = r"""<script id="wf-android-js">
(function(){
  /* ---- 1. Fechar "Ajustes e Qualidade" arrastando para baixo (acompanha o dedo, fecha com inércia) ---- */
  try{
    var sh=document.getElementById('sheet'),pn=sh&&sh.querySelector('.spn');
    if(pn){
      var x0=0,y0=0,off=0,arr=false,mov=false,vel=0,ly=0,lt=0,raf=0,LIM=10;
      pn.style.willChange='transform';pn.style.overscrollBehavior='contain';
      var fechar=function(){try{fecharAj()}catch(e){sh.classList.remove('on')}};
      var pinta=function(){raf=0;pn.style.transform='translate3d(0,'+off+'px,0)'};
      var limpa=function(){pn.style.transition='';pn.style.transform=''};
      pn.addEventListener('touchstart',function(e){
        arr=false;mov=false;off=0;vel=0;
        if(e.touches.length!==1)return;
        if(e.target.closest&&e.target.closest('input,select,textarea'))return;
        if(pn.scrollTop>0)return;
        arr=true;x0=e.touches[0].clientX;y0=ly=e.touches[0].clientY;lt=performance.now();
      },{passive:true});
      pn.addEventListener('touchmove',function(e){
        if(!arr)return;
        var t=e.touches[0],dx=t.clientX-x0,dy=t.clientY-y0,agora=performance.now();
        if(!mov){
          if(Math.abs(dx)>Math.abs(dy)||dy<-4){arr=false;return}
          if(dy<LIM)return;
          if(pn.scrollTop>0){arr=false;return}
          mov=true;pn.style.transition='none';
        }
        var dt=Math.max(1,agora-lt);vel=0.75*vel+0.25*((t.clientY-ly)/dt);ly=t.clientY;lt=agora;
        off=Math.max(0,dy-LIM);
        if(!raf)raf=requestAnimationFrame(pinta);
        if(e.cancelable)e.preventDefault();
      },{passive:false});
      var soltar=function(){
        if(!mov){arr=false;return}
        arr=false;mov=false;
        if(raf){cancelAnimationFrame(raf);raf=0}
        var h=pn.getBoundingClientRect().height||600;
        if(off>h*0.28||vel>0.55){
          var resta=Math.max(1,h-off),ms=Math.max(160,Math.min(320,resta/Math.max(0.6,vel)));
          pn.style.transition='transform '+ms+'ms cubic-bezier(.25,.8,.3,1)';
          pn.style.transform='translate3d(0,100%,0)';
          setTimeout(function(){fechar();setTimeout(limpa,60)},ms);
        }else{
          pn.style.transition='transform .32s cubic-bezier(.2,.9,.25,1)';
          pn.style.transform='translate3d(0,0,0)';
          setTimeout(limpa,340);
        }
        off=0;
      };
      pn.addEventListener('touchend',soltar);
      pn.addEventListener('touchcancel',soltar);
    }
  }catch(e){}

  /* ---- 1b. Prévia só com áudio na busca: toca no próprio lugar e destaca o título da faixa ---- */
  var PVID=null,PVAU=null;
  function pvStop(){
    if(PVAU){try{PVAU.pause()}catch(x){}PVAU.removeAttribute('src');try{PVAU.load()}catch(x){}PVAU=null}
    $$('.pp').forEach(function(x){x.innerHTML=ic('play',18);x.classList.remove('on')});
    $$('.pvon').forEach(function(r){r.classList.remove('pvon','pvcarr')});
    PVID=null;
  }
  window.addEventListener('click',function(e){
    try{
      var b=e.target.closest&&e.target.closest('[data-pv]');
      if(!b||!window.WF||!WF.stream)return;
      e.preventDefault();e.stopPropagation();e.stopImmediatePropagation();
      var id=b.dataset.pv;
      if(PVID===id){pvStop();return}
      pvStop();
      var au=aud();if(au&&!au.paused){try{togglePlay()}catch(x){}}   /* pausa o player da biblioteca */
      PVID=id;
      var row=b.closest('.rs,.tr');
      if(row)row.classList.add('pvon','pvcarr');
      b.innerHTML=ic('stop',18);b.classList.add('on');
      WF.stream(id);
    }catch(x){}
  },true);
  window.wfStream=function(id,url,err){
    if(PVID!==id)return;
    if(!url){toast(err||'Não foi possível tocar esta prévia.');pvStop();return}
    var row=document.querySelector('[data-pv="'+id+'"]');row=row&&row.closest('.rs,.tr');
    if(row)row.classList.remove('pvcarr');
    PVAU=new Audio(url);
    PVAU.onended=pvStop;
    PVAU.onerror=function(){toast('Não consegui tocar esta prévia.');pvStop()};
    var p=PVAU.play();if(p&&p.catch)p.catch(function(){toast('Não consegui tocar esta prévia.');pvStop()});
  };

  /* ---- 1c. Vídeo continua tocando (só o áudio) quando o app vai para segundo plano ---- */
  function trocarMidia(tag){
    try{
      var a=aud();if(!a||a.tagName.toLowerCase()===tag)return;
      var t=a.currentTime||0,tocando=!a.paused,src=a.currentSrc||a.src;
      var n=document.createElement(tag);n.id='au';
      if(tag==='video')n.setAttribute('playsinline','');
      n.volume=a.volume;
      ['onended','onerror','onplay','onpause','ontimeupdate','onloadedmetadata','ondurationchange'].forEach(function(k){n[k]=a[k]});
      a.onpause=null;a.onended=null;a.onerror=null;a.onplay=null;
      try{a.pause()}catch(x){}
      a.parentNode.replaceChild(n,a);
      n.addEventListener('loadedmetadata',function(){try{n.currentTime=t}catch(x){}if(tocando){var p=n.play();if(p&&p.catch)p.catch(function(){})}},{once:true});
      n.src=src;n.load();
    }catch(x){}
  }
  function ehVideo(){return typeof CUR!=='undefined'&&/\.(mp4|mkv)$/i.test(CUR||'')}
  var querTocar=false;
  document.addEventListener('play',function(e){if(e.target&&e.target.id==='au')querTocar=true},true);
  document.addEventListener('pause',function(e){
    if(!e.target||e.target.id!=='au')return;
    if(document.hidden&&ehVideo()&&querTocar&&!e.target.ended){trocarMidia('audio')}  /* o sistema pausou o vídeo ao sair: continua só com o áudio */
    else if(!document.hidden)querTocar=false;
  },true);
  document.addEventListener('visibilitychange',function(){
    if(!ehVideo())return;
    var a=aud();if(!a)return;
    if(document.hidden){if(!a.paused)trocarMidia('audio')}
    else if(a.tagName.toLowerCase()==='audio'){trocarMidia('video')}
  });

  /* ---- 2. Avisar o app Android sobre o player (a notificação usa isso) ---- */
  function aud(){return document.getElementById('au')}
  function txt(id){var el=document.getElementById(id);return el?(el.textContent||''):''}
  window.wfRep=function(){
    try{
      if(!window.WF||!WF.player)return;
      var a=aud(),cur=(typeof CUR!=='undefined'&&CUR)?CUR:'';
      var vid=/\.(mp4|mkv)$/i.test(cur);
      var toc=!!(a&&cur&&!a.paused&&!a.ended);
      var pos=a&&isFinite(a.currentTime)?Math.round(a.currentTime*1000):0;
      var dur=a&&isFinite(a.duration)?Math.round(a.duration*1000):0;
      WF.player(cur?1:0,toc?1:0,vid?1:0,txt('plt'),txt('pls'),pos,dur,cur);
    }catch(e){}
  };
  ['play','playing','pause','ended','seeked','loadedmetadata','durationchange','emptied'].forEach(function(n){
    document.addEventListener(n,function(){window.wfRep()},true);
  });
  try{var sp=stopPlayer;stopPlayer=function(){sp.apply(this,arguments);window.wfRep()}}catch(e){}
  var bx=document.getElementById('plx');
  if(bx)bx.addEventListener('click',function(){setTimeout(window.wfRep,50)});

  /* comandos vindos da notificação */
  window.wfCmd=function(c){
    try{
      var a=aud();
      if(c==='play'){if(a&&a.paused)togglePlay()}
      else if(c==='pause'){if(a&&!a.paused)togglePlay()}
      else if(c==='next')proxima(1);
      else if(c==='prev')proxima(-1);
      else if(c==='stop')stopPlayer();
      else if(c.indexOf('seek:')===0){try{toast('[teste] Comando de pular chegou na página')}catch(x){}var ms=parseInt(c.slice(5),10);if(a&&isFinite(ms)){a.currentTime=ms/1000;setTimeout(window.wfRep,200);try{toast('[teste] Player pulou para '+tf(ms/1000))}catch(x){}}}
    }catch(e){}
  };

  /* ---- 3. Não cola sozinho o que foi copiado (só o botão Colar cola) ---- */
  window.wfClip=function(){};

  setTimeout(window.wfRep,1500);
})();
</script>
"""

# Troca de texto no HTML: (antigo, novo). Cada "antigo" tem que existir exatamente uma vez.
TROCAS = [
    # download cancelado pelo usuário não é falha: sem o botão "Forçar"
    ("if(i.status==='duplicada'||i.status==='cancelada'||i.status==='falha')a+=",
     "if(i.status==='duplicada'||i.status==='falha')a+="),
]


def _log(msg):
    try:
        sys.stderr.write("[wavefly_android] %s\n" % msg)
    except Exception:
        pass


def ajustar_html(html):
    """Devolve o HTML da página com os ajustes. Quem não encontrar o trecho só avisa no log."""
    for antigo, novo in TROCAS:
        if html.count(antigo) != 1:
            _log("trecho não encontrado (ou repetido) no HTML: %r" % antigo[:60])
            continue
        html = html.replace(antigo, novo, 1)
    extra = CSS + JS
    pos = html.rfind("</body>")
    if pos < 0:
        return html + extra
    return html[:pos] + extra + html[pos:]


def corrigir_capas(w):
    """_vid_do_arquivo quebrava: o índice guarda LISTAS de caminhos e o código tratava como texto.
    O erro derrubava a capa de todo arquivo sem imagem embutida (vídeos, principalmente)."""

    def _vid_do_arquivo(pth):
        try:
            if not w.REV:
                with w.LOCK:
                    for vid, tipos in list(w.INDEX.items()):
                        for caminhos in (tipos or {}).values():
                            if isinstance(caminhos, str):
                                caminhos = [caminhos]
                            for c in caminhos or []:
                                if isinstance(c, str):
                                    w.REV[os.path.realpath(c)] = vid
            return w.REV.get(os.path.realpath(pth))
        except Exception as e:
            _log("falha ao consultar o índice de capas: %s" % e)
            return None

    w._vid_do_arquivo = _vid_do_arquivo


def aplicar(w):
    """Aplica tudo sobre o módulo waveflysite já importado. Nunca levanta exceção."""
    try:
        w.HTML = ajustar_html(w.HTML)
    except Exception as e:
        _log("falha ao ajustar o HTML: %s" % e)
    try:
        corrigir_capas(w)
    except Exception as e:
        _log("falha ao corrigir as capas: %s" % e)
