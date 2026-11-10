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
</style>
"""

# --------------------------------------------------------------------------- JS
JS = r"""<script id="wf-android-js">
(function(){
  /* ---- 1. Fechar "Ajustes e Qualidade" arrastando para baixo ---- */
  try{
    var sh=document.getElementById('sheet'),pn=sh&&sh.querySelector('.spn');
    if(pn){
      var x0=0,y0=0,dy=0,t0=0,arr=false,mov=false;
      var fechar=function(){try{fecharAj()}catch(e){sh.classList.remove('on')}};
      pn.addEventListener('touchstart',function(e){
        arr=false;mov=false;dy=0;
        if(e.touches.length!==1)return;
        if(e.target.closest&&e.target.closest('input,select,textarea'))return;
        if(pn.scrollTop>0)return;
        arr=true;x0=e.touches[0].clientX;y0=e.touches[0].clientY;t0=Date.now();
      },{passive:true});
      pn.addEventListener('touchmove',function(e){
        if(!arr)return;
        var t=e.touches[0],dx=t.clientX-x0;dy=t.clientY-y0;
        if(!mov){
          if(Math.abs(dx)>Math.abs(dy)||dy<-4){arr=false;return}
          if(dy<8)return;
          if(pn.scrollTop>0){arr=false;return}
          mov=true;pn.style.transition='none';
        }
        pn.style.transform='translateY('+Math.max(0,dy)+'px)';
        if(e.cancelable)e.preventDefault();
      },{passive:false});
      var soltar=function(){
        if(!mov){arr=false;return}
        var v=dy/Math.max(1,Date.now()-t0);
        arr=false;mov=false;
        pn.style.transition='transform .22s ease';
        if(dy>110||(dy>40&&v>0.5)){
          pn.style.transform='translateY(100%)';fechar();
          setTimeout(function(){pn.style.transition='';pn.style.transform=''},320);
        }else{
          pn.style.transform='';
          setTimeout(function(){pn.style.transition=''},260);
        }
      };
      pn.addEventListener('touchend',soltar);
      pn.addEventListener('touchcancel',soltar);
    }
  }catch(e){}

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
      WF.player(cur?1:0,toc?1:0,vid?1:0,txt('plt'),txt('pls'),pos,dur);
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
