from pathlib import Path
import re, shutil, zipfile, json, hashlib
root=Path(__file__).resolve().parents[1]
source=root/'dist'
dest=root/'build/yandex'
dest.mkdir(parents=True,exist_ok=True)
(root/'build').mkdir(exist_ok=True)
s= (source/'index.html').read_text()
s=s.replace('Пробная версия · прогресс сохраняется в этом браузере · цены вымышленные','Прогресс сохраняется в этом браузере · Все цены и деньги — игровые')
s=s.replace('<div class="wrap"><nav','<div class="wrap game-shell"><nav')
css='''
html,body{height:100%;overflow:hidden;overscroll-behavior:none;user-select:none;-webkit-user-select:none;-webkit-touch-callout:none}body{display:flex;flex-direction:column}header{flex:none;padding:14px 0}.game-shell{width:100%;flex:1;min-height:0;display:flex;flex-direction:column}.game-shell nav{flex:none;padding:14px 0}.game-shell main{flex:1;min-height:0;overflow:auto;overscroll-behavior:contain;padding-bottom:24px;scrollbar-gutter:stable}.game-shell footer{flex:none;padding:8px 0}dialog{max-height:90dvh;overflow:auto}body.platform-paused .game-shell,body.sdk-loading .game-shell{pointer-events:none}body.sdk-loading .game-shell{opacity:.6}.sdk-status{position:fixed;inset:0;z-index:100;display:grid;place-content:center;text-align:center;background:#101113e8;gap:16px}.sdk-status[hidden]{display:none}
@media(min-width:761px) and (max-height:800px){h1{font-size:32px;margin:6px 0}.panel{padding:18px}.stage{padding:24px 0 16px}.actions{margin-top:14px}.hero .panel hr{margin:12px 0!important}.hero .panel p{margin:10px 0}.hero .panel h2{font-size:20px}.hero .panel .value{margin:8px 0}.tag{margin:6px 0}.game-shell nav{padding:10px 0}header{padding:10px 0}}
'''
s=s.replace('</style>',css+'</style>')
s=s.replace('<header>','<div id="sdk-status" class="sdk-status"><strong>Загрузка игры…</strong><button id="sdk-retry" hidden>Повторить подключение</button></div><header>',1)
s=s.replace('let sdk=null,adBusy=false;','let sdk=null,adBusy=false,platformPaused=false,sdkLoading=true;')
s=s.replace("if(busy||adBusy)return", "if(busy||adBusy||platformPaused||sdkLoading)return")
s=s.replace("if(!b||b.disabled||adBusy)return", "if(!b||b.disabled||adBusy||platformPaused||sdkLoading)return")
s=s.replace("if(adBusy||freeSequence&&!free||spinningParts.has(part))return", "if(platformPaused||sdkLoading||adBusy||freeSequence&&!free||spinningParts.has(part))return")
s=s.replace("refreshFree();\n}", "refreshFree();syncGameplay();\n}")
s=s.replace("sdk.features?.GameplayAPI?.start();render()", "syncGameplay();render()")
a=s.index('function initAds()');b=s.index("document.addEventListener('click'",a)
s=s[:a]+'''let gameplayRunning=false;
function syncGameplay(){if(!sdk)return;const active=!sdkLoading&&!platformPaused&&!adBusy&&!document.hidden&&tab==='Крутка'&&!document.querySelector('dialog[open]');if(active===gameplayRunning)return;gameplayRunning=active;const api=sdk.features?.GameplayAPI;active?api?.start():api?.stop()}
function pauseGame(){platformPaused=true;document.body.classList.add('platform-paused');document.getAnimations().forEach(a=>{if(a.playState==='running'){a.pause();a.platformPaused=true}});syncGameplay()}
function resumeGame(){platformPaused=false;document.body.classList.remove('platform-paused');document.getAnimations().forEach(a=>{if(a.platformPaused){a.platformPaused=false;a.play()}});syncGameplay()}
function initAds(){document.body.classList.add('sdk-loading');const script=document.createElement('script');script.src='/sdk.js';const fail=()=>{sdkLoading=true;const status=document.querySelector('#sdk-status');status.hidden=false;status.querySelector('strong').textContent='Не удалось подключиться. Проверь интернет.';document.querySelector('#sdk-retry').hidden=false};script.onerror=fail;script.onload=async()=>{try{sdk=await YaGames.init();const portalLanguage=sdk.environment.i18n.lang;document.documentElement.lang=portalLanguage==='ru'?'ru':'ru';sdk.on('game_api_pause',pauseGame);sdk.on('game_api_resume',resumeGame);sdkLoading=false;document.body.classList.remove('sdk-loading');render();document.querySelector('#sdk-status').hidden=true;sdk.features?.LoadingAPI?.ready();syncGameplay()}catch{sdk=null;fail()}};document.head.appendChild(script)}
document.querySelector('#sdk-retry').addEventListener('click',()=>location.reload());
document.addEventListener('contextmenu',e=>e.preventDefault());document.addEventListener('dragstart',e=>e.preventDefault());
document.addEventListener('visibilitychange',()=>{document.hidden?pauseGame():resumeGame()});
new MutationObserver(syncGameplay).observe(document.body,{subtree:true,attributes:true,attributeFilter:['open']});
''' +s[b:]
# Only Russian is declared; unsupported portal languages fall back to the actual Russian UI.
s=s.replace("const portalLanguage=sdk.environment.i18n.lang;document.documentElement.lang=portalLanguage==='ru'?'ru':'ru';", "const portalLanguage=sdk.environment.i18n.lang;const supportedLanguages=['ru'];document.documentElement.lang=supportedLanguages.includes(portalLanguage)?portalLanguage:supportedLanguages[0];")
(dest/'index.html').write_text(s)
assets=sorted(set(re.findall(r'images/[A-Za-z0-9-]+\.png',s)))
for rel in assets:
 p=dest/rel;p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source/rel,p)
shutil.copytree(source/'licenses',dest/'licenses',dirs_exist_ok=True)
archive=root/'build/nomernoy-dvizh-yandex.zip'
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
 for p in sorted(dest.rglob('*')):
  if p.is_file():z.write(p,p.relative_to(dest))
script=s.split('<script>')[1].split('</script>')[0]
(root/'build/yandex-script.js').write_text(script)
manifest={'archive':str(archive),'files':len(list(dest.rglob('*'))),'assets':len(assets),'uncompressed_bytes':sum(p.stat().st_size for p in dest.rglob('*') if p.is_file()),'compressed_bytes':archive.stat().st_size,'sha256':hashlib.sha256(archive.read_bytes()).hexdigest()}
(root/'build/build-manifest.json').write_text(json.dumps(manifest,indent=2))
print(json.dumps(manifest,indent=2))
