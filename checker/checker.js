/* PHP2Shell passive banner checker widget (PL/EN/DE). Self-contained, no dependencies.
   Mount point: <div id="p2s-checker"></div>. API base URL comes from ../data/checker-config.json
   (relative to this script), so the backend can move without a rebuild. */
(function(){
"use strict";
var SCRIPT=document.currentScript;
var BASE=SCRIPT&&SCRIPT.src?new URL('.',SCRIPT.src).href:new URL('checker/',location.href).href;
var CONFIG_URL=new URL('../data/checker-config.json',BASE).href;
var LANGS=['pl','en','de'];
var S={
en:{heading:"Am I affected? Passive PHP banner check",
 intro:"Enter your website address. We send ONE ordinary GET request to its root page (like a browser) and read only what the server voluntarily discloses: the Server and X-Powered-By headers and whether a PHPSESSID cookie is set.",
 safe:"Defensive only: no exploit payloads, no scanning, no other paths or ports. Private and internal addresses are refused.",
 own:"Check only systems you own or are authorised to test.",
 ph:"https://example.com",btn:"Check",busy:"Checking…",
 e_empty:"Please enter a website address.",e_url:"That does not look like a valid public http(s) address.",e_scheme:"Only http:// and https:// addresses are supported.",
 e_local:"Local, private and internal addresses are not checked.",e_long:"The address is too long.",n_path:"Note: only the root page (/) of this host is checked; the path is ignored.",
 e_net:"The checker service could not be reached. Please try again later.",e_rate:"Too many checks. Please wait a minute and try again.",e_busy:"The checker is busy right now. Please try again in a few seconds.",e_srv:"The checker returned an error:",
 offline:"The live checker backend is not online yet. Until it is, check on your server: run php -v and compare it with the fixed versions below, and check your distribution's security tracker.",
 st_likely_vulnerable:"Likely vulnerable version",st_likely_patched:"Likely patched version",st_php_detected_version_hidden:"PHP detected, version hidden – unknown",st_no_php_detected:"No PHP detected / unknown",st_host_unreachable:"Host unreachable",
 sum_likely_vulnerable:"The disclosed PHP version is older than the upstream fix for its branch. Update now, or confirm a distribution backport.",
 sum_likely_patched:"The disclosed PHP version is at or above the upstream fix for its branch.",
 sum_php_detected_version_hidden:"The server appears to run PHP but does not disclose an exact version. This is NOT a sign of safety – verify on the server.",
 sum_no_php_detected:"The response does not reveal PHP. PHP may still be running behind a proxy, CDN or with expose_php=Off.",
 sum_host_unreachable:"The host could not be reached (DNS, timeout, TLS or connection error). Nothing could be determined.",
 k_host:"Host",k_ip:"IP",k_ver:"Detected version",k_fix:"Fixed in branch",k_server:"Server header",k_xpb:"X-Powered-By",k_sess:"PHPSESSID cookie",k_http:"HTTP status",k_time:"Checked at",k_redir:"Redirects followed",
 yes:"yes",no:"no",none:"(none)",
 n_distro:"A distribution build was detected (e.g. Debian/Ubuntu/RHEL). The fix may have been backported without changing the version string – check the distribution's security tracker.",
 n_eol:"PHP below 8.2 is end-of-life upstream and gets no official fixed release. For 7.4/8.0/8.1 the PHP team published minimal source backports, and some distributions (e.g. Ubuntu, Debian LTS/ELTS, RHEL, deb.sury.org) ship patched packages – check with your vendor.",n_minor:"Only major.minor is disclosed; the patch level is unknown.",
 fixed:"Fixed upstream in: 8.5.12 · 8.4.27 · 8.3.36 · 8.2.35. PHP 7.4/8.0/8.1 (end-of-life): no official release – the PHP team published only minimal source backports to build yourself; some distributions and LTS vendors ship patched packages. PHP ≤ 7.3: no upstream fix, vendor backports only.",
 cavh:"Important caveats",
 cav:["This only reads the public banner. It does not and cannot verify the actual patch status.","A hidden or missing banner is NOT safety: many patched and unpatched servers hide their version.","Debian, Ubuntu, RHEL and other distributions backport security fixes without bumping the upstream version string, so a version that looks old may actually be fixed.","Proxies, CDNs and WAFs can strip, change or fake these headers.","Reliable check: php -v on the server plus your package changelog, compared with the official advisory."]},
pl:{heading:"Czy mnie to dotyczy? Pasywne sprawdzenie banera PHP",
 intro:"Podaj adres swojej strony. Wysyłamy JEDNO zwykłe żądanie GET do strony głównej (jak przeglądarka) i odczytujemy tylko to, co serwer sam ujawnia: nagłówki Server i X-Powered-By oraz to, czy ustawia ciasteczko PHPSESSID.",
 safe:"Wyłącznie defensywnie: bez exploitów, bez skanowania, bez innych ścieżek i portów. Adresy prywatne i wewnętrzne są odrzucane.",
 own:"Sprawdzaj tylko własne systemy lub takie, na których test masz zgodę.",
 ph:"https://przyklad.pl",btn:"Sprawdź",busy:"Sprawdzam…",
 e_empty:"Wpisz adres strony.",e_url:"To nie wygląda na prawidłowy publiczny adres http(s).",e_scheme:"Obsługiwane są tylko adresy http:// i https://.",
 e_local:"Adresy lokalne, prywatne i wewnętrzne nie są sprawdzane.",e_long:"Adres jest za długi.",n_path:"Uwaga: sprawdzana jest tylko strona główna (/) tego hosta; ścieżka jest pomijana.",
 e_net:"Nie udało się połączyć z usługą sprawdzającą. Spróbuj ponownie później.",e_rate:"Zbyt wiele sprawdzeń. Odczekaj minutę i spróbuj ponownie.",e_busy:"Sprawdzarka jest teraz mocno obciążona. Spróbuj ponownie za kilka sekund.",e_srv:"Usługa zwróciła błąd:",
 offline:"Backend sprawdzarki nie jest jeszcze online. Do tego czasu sprawdź na serwerze: uruchom php -v, porównaj z wersjami z poprawką poniżej i zajrzyj do trackera bezpieczeństwa swojej dystrybucji.",
 st_likely_vulnerable:"Prawdopodobnie podatna wersja",st_likely_patched:"Prawdopodobnie załatana wersja",st_php_detected_version_hidden:"Wykryto PHP, wersja ukryta – nieznane",st_no_php_detected:"Nie wykryto PHP / nieznane",st_host_unreachable:"Host nieosiągalny",
 sum_likely_vulnerable:"Ujawniona wersja PHP jest starsza niż poprawka upstream dla tej gałęzi. Zaktualizuj teraz albo potwierdź backport w dystrybucji.",
 sum_likely_patched:"Ujawniona wersja PHP jest równa lub nowsza niż poprawka upstream dla tej gałęzi.",
 sum_php_detected_version_hidden:"Serwer najpewniej działa na PHP, ale nie ujawnia dokładnej wersji. To NIE oznacza bezpieczeństwa – sprawdź na serwerze.",
 sum_no_php_detected:"Odpowiedź nie zdradza PHP. PHP może nadal działać za proxy lub CDN albo z expose_php=Off.",
 sum_host_unreachable:"Nie udało się połączyć z hostem (DNS, limit czasu, TLS lub błąd połączenia). Nie da się nic ustalić.",
 k_host:"Host",k_ip:"IP",k_ver:"Wykryta wersja",k_fix:"Poprawka w gałęzi",k_server:"Nagłówek Server",k_xpb:"X-Powered-By",k_sess:"Ciasteczko PHPSESSID",k_http:"Status HTTP",k_time:"Sprawdzono",k_redir:"Przekierowania",
 yes:"tak",no:"nie",none:"(brak)",
 n_distro:"Wykryto kompilację dystrybucji (np. Debian/Ubuntu/RHEL). Poprawka mogła zostać przeniesiona bez zmiany numeru wersji – sprawdź tracker bezpieczeństwa dystrybucji.",
 n_eol:"PHP poniżej 8.2 nie jest już wspierane upstream i nie dostanie oficjalnego wydania z poprawką. Dla 7.4/8.0/8.1 są minimalne backporty źródłowe od zespołu PHP, a część dystrybucji (np. Ubuntu, Debian LTS/ELTS, RHEL, deb.sury.org) wydała poprawione paczki – sprawdź u swojego dostawcy.",n_minor:"Ujawniono tylko wersję główną i podrzędną; poziom poprawek jest nieznany.",
 fixed:"Poprawione upstream w: 8.5.12 · 8.4.27 · 8.3.36 · 8.2.35. PHP 7.4/8.0/8.1 (EOL): brak oficjalnego wydania – zespół PHP udostępnił tylko minimalne backporty źródłowe do samodzielnej kompilacji; część dystrybucji i dostawców LTS ma gotowe paczki. PHP ≤ 7.3: brak poprawki upstream, tylko backporty dostawców.",
 cavh:"Ważne zastrzeżenia",
 cav:["Sprawdzamy tylko publiczny baner. Nie weryfikujemy i nie możemy zweryfikować faktycznego stanu poprawek.","Ukryty lub brakujący baner to NIE bezpieczeństwo: wiele serwerów, załatanych i niezałatanych, ukrywa wersję.","Debian, Ubuntu, RHEL i inne dystrybucje przenoszą poprawki bezpieczeństwa bez zmiany numeru wersji upstream, więc wersja, która wygląda na starą, może być już naprawiona.","Proxy, CDN i WAF mogą usuwać, zmieniać lub fałszować te nagłówki.","Pewne sprawdzenie: php -v na serwerze plus changelog pakietu, porównane z oficjalnym komunikatem."]},
de:{heading:"Bin ich betroffen? Passive Prüfung des PHP-Banners",
 intro:"Geben Sie die Adresse Ihrer Website ein. Wir senden EINE gewöhnliche GET-Anfrage an die Startseite (wie ein Browser) und lesen nur, was der Server freiwillig preisgibt: die Header Server und X-Powered-By sowie, ob ein PHPSESSID-Cookie gesetzt wird.",
 safe:"Rein defensiv: keine Exploit-Payloads, kein Scannen, keine anderen Pfade oder Ports. Private und interne Adressen werden abgelehnt.",
 own:"Prüfen Sie nur eigene Systeme oder solche, für deren Test Sie eine Erlaubnis haben.",
 ph:"https://beispiel.de",btn:"Prüfen",busy:"Prüfe…",
 e_empty:"Bitte geben Sie eine Website-Adresse ein.",e_url:"Das sieht nicht nach einer gültigen öffentlichen http(s)-Adresse aus.",e_scheme:"Nur http://- und https://-Adressen werden unterstützt.",
 e_local:"Lokale, private und interne Adressen werden nicht geprüft.",e_long:"Die Adresse ist zu lang.",n_path:"Hinweis: Geprüft wird nur die Startseite (/) dieses Hosts; der Pfad wird ignoriert.",
 e_net:"Der Prüfdienst ist nicht erreichbar. Bitte versuchen Sie es später erneut.",e_rate:"Zu viele Prüfungen. Bitte warten Sie eine Minute.",e_busy:"Der Checker ist gerade ausgelastet. Bitte versuchen Sie es in ein paar Sekunden erneut.",e_srv:"Der Prüfdienst meldet einen Fehler:",
 offline:"Das Backend des Live-Checkers ist noch nicht online. Bis dahin prüfen Sie direkt auf dem Server: php -v ausführen, mit den unten genannten Versionen vergleichen und den Security-Tracker Ihrer Distribution ansehen.",
 st_likely_vulnerable:"Wahrscheinlich verwundbare Version",st_likely_patched:"Wahrscheinlich gepatchte Version",st_php_detected_version_hidden:"PHP erkannt, Version verborgen – unbekannt",st_no_php_detected:"Kein PHP erkannt / unbekannt",st_host_unreachable:"Host nicht erreichbar",
 sum_likely_vulnerable:"Die angezeigte PHP-Version ist älter als der Upstream-Fix ihres Zweigs. Jetzt aktualisieren oder einen Backport der Distribution bestätigen.",
 sum_likely_patched:"Die angezeigte PHP-Version entspricht dem Upstream-Fix ihres Zweigs oder ist neuer.",
 sum_php_detected_version_hidden:"Der Server läuft offenbar mit PHP, nennt aber keine genaue Version. Das ist KEIN Zeichen von Sicherheit – bitte auf dem Server prüfen.",
 sum_no_php_detected:"Die Antwort verrät kein PHP. PHP kann trotzdem hinter einem Proxy oder CDN oder mit expose_php=Off laufen.",
 sum_host_unreachable:"Der Host war nicht erreichbar (DNS, Zeitüberschreitung, TLS- oder Verbindungsfehler). Es ließ sich nichts feststellen.",
 k_host:"Host",k_ip:"IP",k_ver:"Erkannte Version",k_fix:"Behoben im Zweig",k_server:"Server-Header",k_xpb:"X-Powered-By",k_sess:"PHPSESSID-Cookie",k_http:"HTTP-Status",k_time:"Geprüft am",k_redir:"Weiterleitungen",
 yes:"ja",no:"nein",none:"(keiner)",
 n_distro:"Ein Distributions-Build wurde erkannt (z. B. Debian/Ubuntu/RHEL). Der Fix kann ohne Änderung der Versionsnummer zurückportiert worden sein – prüfen Sie den Security-Tracker der Distribution.",
 n_eol:"PHP unter 8.2 ist upstream end-of-life und erhält kein offizielles Release mit Fix. Für 7.4/8.0/8.1 hat das PHP-Team minimale Quell-Backports veröffentlicht, und einige Distributionen (z. B. Ubuntu, Debian LTS/ELTS, RHEL, deb.sury.org) liefern gepatchte Pakete – beim Anbieter prüfen.",n_minor:"Nur Haupt- und Nebenversion werden angezeigt; der Patch-Stand ist unbekannt.",
 fixed:"Upstream behoben in: 8.5.12 · 8.4.27 · 8.3.36 · 8.2.35. PHP 7.4/8.0/8.1 (end-of-life): kein offizielles Release – das PHP-Team hat nur minimale Quell-Backports zum Selbstkompilieren veröffentlicht; einige Distributionen und LTS-Anbieter liefern gepatchte Pakete. PHP ≤ 7.3: kein Upstream-Fix, nur Backports der Anbieter.",
 cavh:"Wichtige Einschränkungen",
 cav:["Geprüft wird nur das öffentliche Banner. Der tatsächliche Patch-Stand wird nicht verifiziert und kann so nicht verifiziert werden.","Ein verborgenes oder fehlendes Banner ist KEINE Sicherheit: Viele gepatchte und ungepatchte Server verbergen ihre Version.","Debian, Ubuntu, RHEL und andere Distributionen portieren Sicherheitsfixes zurück, ohne die Upstream-Versionsnummer zu erhöhen – eine alt wirkende Version kann also bereits behoben sein.","Proxys, CDNs und WAFs können diese Header entfernen, ändern oder fälschen.","Verlässlich ist nur: php -v auf dem Server plus Paket-Changelog, verglichen mit dem offiziellen Advisory."]}
};
var CLS={likely_vulnerable:'st-vuln',likely_patched:'st-ok',php_detected_version_hidden:'st-hidden',no_php_detected:'st-none',host_unreachable:'st-down'};
var root,api=null,cfgLoaded=false,last=null,lastErr=null,lastNote=null;

function lang(){var h=(document.documentElement.lang||'').slice(0,2).toLowerCase();if(LANGS.indexOf(h)>=0)return h;
 try{var q=new URLSearchParams(location.search).get('lang');if(LANGS.indexOf(q)>=0)return q;var s=localStorage.getItem('lang');if(LANGS.indexOf(s)>=0)return s}catch(e){}
 var n=(navigator.language||'en').toLowerCase();return n.indexOf('pl')===0?'pl':n.indexOf('de')===0?'de':'en'}
function t(k){var L=lang();return (S[L]&&S[L][k]!=null)?S[L][k]:S.en[k]}
function el(tag,attrs,text){var e=document.createElement(tag);if(attrs)for(var a in attrs)e.setAttribute(a,attrs[a]);if(text!=null)e.textContent=text;return e}

var PRIV=[/^127\./,/^10\./,/^192\.168\./,/^169\.254\./,/^172\.(1[6-9]|2\d|3[01])\./,/^0\./,/^100\.(6[4-9]|[7-9]\d|1[01]\d|12[0-7])\./];
function validate(raw){var s=(raw||'').trim();if(!s)return{err:'e_empty'};if(s.length>2048)return{err:'e_long'};
 if(!/^[a-z][a-z0-9+.-]*:\/\//i.test(s))s='https://'+s;var u;try{u=new URL(s)}catch(e){return{err:'e_url'}}
 if(u.protocol!=='http:'&&u.protocol!=='https:')return{err:'e_scheme'};if(u.username||u.password)return{err:'e_url'};
 var h=u.hostname.toLowerCase().replace(/\.$/,'');if(!h)return{err:'e_url'};
 if(h==='localhost'||/\.(localhost|local|internal|lan|home\.arpa)$/.test(h)||h.charAt(0)==='['||PRIV.some(function(r){return r.test(h)}))return{err:'e_local'};
 if(h.indexOf('.')<0)return{err:'e_url'};
 return{url:u.protocol+'//'+u.host+'/',pathIgnored:(u.pathname&&u.pathname!=='/')||!!u.search}}

function loadConfig(){
 try{var qa=new URLSearchParams(location.search).get('api');if(qa&&/^(127\.0\.0\.1|localhost)$/.test(location.hostname)&&/^https?:\/\//.test(qa))window.PHP2SHELL_CHECKER_API=qa.replace(/\/+$/,'')}catch(e){}
 if(window.PHP2SHELL_CHECKER_API){api=String(window.PHP2SHELL_CHECKER_API);cfgLoaded=true;return Promise.resolve()}
 return fetch(CONFIG_URL+'?t='+Date.now(),{cache:'no-store'}).then(function(r){return r.ok?r.json():{}}).then(function(c){
  var b=c&&typeof c.api_base==='string'?c.api_base.trim():'';api=/^https?:\/\//.test(b)?b.replace(/\/+$/,''):null;cfgLoaded=true}).catch(function(){api=null;cfgLoaded=true})}

function build(){root.textContent='';
 var card=el('div',{'class':'p2c-card'});
 card.appendChild(el('p',{'class':'p2c-intro'},t('intro')));card.appendChild(el('p',{'class':'p2c-safe'},t('safe')));
 var own=el('p',{'class':'p2c-own',id:'p2c-own'});own.appendChild(el('strong',null,'⚠ '+t('own')));card.appendChild(own);
 var f=el('form',{novalidate:'',autocomplete:'off'});
 var inp=el('input',{type:'text',inputmode:'url',spellcheck:'false',autocapitalize:'off','aria-label':t('ph'),'aria-describedby':'p2c-own',placeholder:t('ph'),maxlength:'2048',id:'p2c-url'});
 if(root._val)inp.value=root._val;inp.addEventListener('input',function(){root._val=inp.value;inp.removeAttribute('aria-invalid')});
 var btn=el('button',{type:'submit'},t('btn'));f.appendChild(inp);f.appendChild(btn);card.appendChild(f);
 var msg=el('p',{'class':'p2c-msg',role:'status','aria-live':'polite'});card.appendChild(msg);
 if(cfgLoaded&&!api)card.appendChild(el('div',{'class':'p2c-off'},t('offline')));
 var res=el('div',{'class':'p2c-res',hidden:'','aria-live':'polite'});card.appendChild(res);
 card.appendChild(el('p',{'class':'p2c-msg'},t('fixed')));
 root.appendChild(card);
 f.addEventListener('submit',function(ev){ev.preventDefault();run(inp,btn,msg,res)});
 if(lastErr){msg.textContent=lastErr.text();msg.className='p2c-msg err'}else if(lastNote){msg.textContent=t(lastNote)}
 if(last)render(res,last);
 var h=document.querySelector('[data-p2c="heading"]');if(h)h.textContent=t('heading')}

function run(inp,btn,msg,res){lastErr=null;lastNote=null;msg.className='p2c-msg';msg.textContent='';
 var v=validate(inp.value);if(v.err){inp.setAttribute('aria-invalid','true');lastErr={text:function(){return t(v.err)}};msg.className='p2c-msg err';msg.textContent=t(v.err);return}
 if(!api){lastErr={text:function(){return t('offline')}};msg.className='p2c-msg err';msg.textContent=t('offline');return}
 btn.disabled=true;btn.textContent=t('busy');if(v.pathIgnored){lastNote='n_path';msg.textContent=t('n_path')}
 var ctl=('AbortController' in window)?new AbortController():null;var timer=setTimeout(function(){if(ctl)ctl.abort()},15000);
 fetch(api+'/check?url='+encodeURIComponent(v.url),{signal:ctl?ctl.signal:undefined,headers:{Accept:'application/json'}})
 .then(function(r){return r.json().catch(function(){return{}}).then(function(j){return{s:r.status,j:j}})})
 .then(function(o){
   if(o.s===429){var busy=o.j&&o.j.error==='busy';lastErr={text:function(){return t(busy?'e_busy':'e_rate')}};throw 0}
   if(o.j&&o.j.classification){last=o.j;render(res,o.j);return}
   var m=(o.j&&(o.j.error==='blocked_ip'||o.j.error==='blocked_host'))?t('e_local'):(o.j&&o.j.error==='bad_scheme')?t('e_scheme'):(t('e_srv')+' '+((o.j&&o.j.message)||('HTTP '+o.s)));
   lastErr={text:function(){return m}};throw 0})
 .catch(function(e){if(!lastErr)lastErr={text:function(){return t('e_net')}};msg.className='p2c-msg err';msg.textContent=lastErr.text()})
 .then(function(){clearTimeout(timer);btn.disabled=false;btn.textContent=t('btn')})}

function row(dl,k,v){dl.appendChild(el('dt',null,t(k)));dl.appendChild(el('dd',null,v==null||v===''?t('none'):String(v)))}
function render(res,d){res.textContent='';res.hidden=false;res.className='p2c-res '+(CLS[d.classification]||'st-none');
 var st=el('div',{'class':'p2c-st'});st.appendChild(el('span',{'class':'p2c-dot','aria-hidden':'true'}));st.appendChild(el('span',null,t('st_'+d.classification)||d.classification_label));res.appendChild(st);
 res.appendChild(el('p',{'class':'p2c-sum'},t('sum_'+d.classification)||''));
 var x=d.details||{};var dl=el('dl');
 row(dl,'k_host',d.resolved_host||d.input);if(d.resolved_ip)row(dl,'k_ip',d.resolved_ip);
 row(dl,'k_ver',d.version);if(x.fixed_in_branch)row(dl,'k_fix',x.fixed_in_branch);
 if(d.classification!=='host_unreachable'){row(dl,'k_server',x.server_header);row(dl,'k_xpb',x.x_powered_by);row(dl,'k_sess',x.phpsessid_cookie?t('yes'):t('no'));if(x.http_status)row(dl,'k_http',x.http_status);
  if(x.hops&&x.hops.length>1)row(dl,'k_redir',x.hops.map(function(h){return h.url}).join(' → '))}
 var when=d.checked_at?new Date(d.checked_at):null;row(dl,'k_time',when&&!isNaN(when)?when.toLocaleString({pl:'pl-PL',en:'en-GB',de:'de-DE'}[lang()]):d.checked_at);
 res.appendChild(dl);
 if(x.distro_build_suspected)res.appendChild(el('p',{'class':'p2c-note'},t('n_distro')));
 if(x.eol)res.appendChild(el('p',{'class':'p2c-note'},t('n_eol')));
 if(d.classification==='php_detected_version_hidden'&&d.version)res.appendChild(el('p',{'class':'p2c-note'},t('n_minor')));
 res.appendChild(el('div',{'class':'p2c-cavh'},t('cavh')));var ul=el('ul',{'class':'p2c-cav'});t('cav').forEach(function(c){ul.appendChild(el('li',null,c))});res.appendChild(ul)}

function init(){root=document.getElementById('p2s-checker');if(!root)return;build();
 loadConfig().then(build);
 var curL=lang();new MutationObserver(function(){var n=lang();if(n!==curL){curL=n;build()}}).observe(document.documentElement,{attributes:true,attributeFilter:['lang']})}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init);else init();
})();
