'use strict';
const t = (key,vars) => I18n.t(key,vars);
I18n.capture();
const $ = id => document.getElementById(id);
const state = {countries:[],selected:[],saved:[],feeds:{},region:'전세계',showUnavailable:false,focusedCountry:null,displayCounts:{world:1,regional:5},view:'home',expanded:new Set(),csrf:'',loading:new Set(),story:null};
const flag = code => String.fromCodePoint(...[...code].map(c=>127397+c.charCodeAt(0)));
const country = code => state.countries.find(c=>c.code===code);
function el(tag, cls, text){const n=document.createElement(tag);if(cls)n.className=cls;if(text!==undefined)n.textContent=t(text);return n;}
function link(text,url,cls){const a=el('a',cls,text);a.href=url;a.target='_blank';a.rel='noopener noreferrer';return a;}
function button(text,action,cls){const b=el('button',cls,text);b.type='button';b.onclick=action;return b;}
function toast(text){$('toast').textContent=t(text);$('toast').hidden=false;clearTimeout(toast.timer);toast.timer=setTimeout(()=>$('toast').hidden=true,3500);}
async function api(path,body){const opts={headers:{},signal:AbortSignal.timeout(path==='/api/translate'?90000:20000)};if(body){opts.method='POST';opts.headers={'Content-Type':'application/json','X-CSRF-Token':state.csrf};opts.body=JSON.stringify(body);}const r=await fetch(path,opts);if(r.status===401){$('error-banner').textContent=t('로그인이 만료되었습니다. 페이지를 새로고침해 주세요.');$('error-banner').hidden=false;throw Error(t('로그인이 필요합니다.'));}const data=await r.json();if(!r.ok)throw Error(t(data.error||'요청을 처리하지 못했습니다.'));return data;}
function visibleCodes(){return state.region==='전세계'?state.countries.map(c=>c.code):state.region==='내 국가'?state.selected:state.countries.filter(c=>c.region===state.region).map(c=>c.code);}
function countScope(){return state.region==='전세계'?'world':'regional';}
function displayLimit(){return state.displayCounts[countScope()] || Infinity;}
function sourceLabel(code){return t(country(code)?.source==='gdelt'?'현지 뉴스 · GDELT':'검색 화제 · Google');}
const countryName=code=>I18n.country(code);

function isSaved(item){return state.saved.some(x=>x.id===item.id);}
function dateLabel(date){if(!date)return '';const d=new Date(date);return Number.isNaN(d.getTime())?'':new Intl.DateTimeFormat(I18n.locale,{month:'short',day:'numeric',hour:'2-digit',minute:'2-digit'}).format(d);}
function matches(item){const q=$('filter').value.trim().toLocaleLowerCase();return !q||[item.title,...item.articles.map(a=>a.title)].some(t=>t.toLocaleLowerCase().includes(q));}
function renderRegions(){const box=$('regions');box.replaceChildren();['전세계','내 국가','아시아','유럽','아메리카','오세아니아','아프리카'].forEach(name=>{const b=button(name,()=>{state.focusedCountry=null;state.expanded.clear();state.region=name;state.view='home';$('filter').value='';render();loadFeeds();},name===state.region?'selected':'');b.setAttribute('aria-pressed',String(name===state.region));box.append(b);});}
function render(){renderRegions();const settings=state.view==='settings',saved=state.view==='saved';$('settings-panel').hidden=!settings;$('explore-panel').hidden=settings;document.querySelector('.intro').hidden=settings;$('settings-tab').classList.toggle('active',settings);$('settings-tab').setAttribute('aria-current',settings?'page':'false');$('board').classList.toggle('worldwide',!saved&&state.region==='전세계');$('display-options').hidden=saved;$('availability-options').hidden=saved;$('show-unavailable').checked=state.showUnavailable;$('display-count').value=String(state.displayCounts[countScope()]);$('home-tab').classList.toggle('active',!saved&&!settings);$('saved-tab').classList.toggle('active',saved);$('home-tab').setAttribute('aria-current',!saved&&!settings?'page':'false');$('saved-tab').setAttribute('aria-current',saved?'page':'false');$('saved-count').textContent=state.saved.length;$('board-title').textContent=saved?t('다시 보고 싶은 이야기'):state.region==='내 국가'?t('내가 보는 나라'):t('regionTitle',{region:t(state.region)});$('board').replaceChildren();if(saved)renderSaved();else visibleCodes().forEach(code=>renderCountry(code));updateSummary();}
function updateSummary(){
    if(state.view==='saved'){$('board-summary').textContent=t('savedSummary',{n:state.saved.length});return;}
    const codes=visibleCodes();
    const available=codes.filter(c=>state.feeds[c]?.items?.length).length;
    const count=codes.reduce((sum,c)=>sum+(state.feeds[c]?.items?.length||0),0);
    const loading=codes.filter(c=>state.loading.has(c)).length;
    const errors=codes.filter(c=>state.feeds[c]?.error).length;
    $('board-summary').textContent=t('summary',{available,total:codes.length,limit:displayLimit()===Infinity?t('전체'):t('upTo',{n:displayLimit()}),count})+(loading?t('loadingSuffix'):'')+(errors?t('errorsSuffix',{n:errors}):'');
    $('availability-message')?.remove();
    if(!$('board').querySelector('.country-card')){
        const empty=el('div','empty',loading?'화제가 있는 나라부터 불러오고 있습니다.':"현재 표시할 화제가 없습니다. ‘화제 없는 국가도 표시’를 켜면 수신 상태와 현지 뉴스 조회를 확인할 수 있습니다.");
        empty.id='availability-message';$('board').append(empty);
    }
}

function storyThumbnail(item) {
    const thumb=button('',()=>openStory(item),'story-thumbnail');
    thumb.setAttribute('aria-label',t('relatedLabel',{title:item.title}));
    const placeholder=el('span','thumbnail-placeholder');
    placeholder.append(el('span','','▧'),el('small','','관련 이미지 없음'));
    thumb.append(placeholder);
    const candidates=item.thumbnails || [];
    if(!candidates.length) return thumb;
    const img=el('img');
    img.alt='';img.loading='lazy';img.decoding='async';
    img.referrerPolicy='no-referrer';img.width=320;img.height=180;
    const source=el('span','thumbnail-source');
    let index=0;
    function attempt() {
        thumb.classList.remove('image-ready');
        if(index>=candidates.length) {
            img.remove();source.remove();thumb.classList.remove('image-loading');return;
        }
        const candidate=candidates[index++];
        source.textContent=candidate.source || t('관련 뉴스');
        thumb.title=(candidate.source?t('imageSource',{source:candidate.source}):'')+item.title;
        thumb.classList.add('image-loading');img.src=candidate.url;
    }
    img.onload=()=>{thumb.classList.remove('image-loading');thumb.classList.add('image-ready');};
    img.onerror=attempt;
    thumb.append(img,source);attempt();return thumb;
}
function storyNode(item,index) {
    const box=el('article','story');
    box.append(storyThumbnail(item));
    const content=el('div','story-content');
    const top=el('div','story-top');
    if(index!==undefined) top.append(el('span','story-index',String(index+1).padStart(2,'0')));
    top.append(button(item.title,()=>openStory(item),'story-title'));
    const save=button(isSaved(item)?'★':'☆',()=>toggleSave(item),'bookmark'+(isSaved(item)?' saved':''));
    save.setAttribute('aria-label',`${item.title} ${t(isSaved(item)?'저장 해제':'저장')}`);
    save.setAttribute('aria-pressed',String(isSaved(item)));
    top.append(save);content.append(top);
    const meta=el('div','story-meta');
    if(item.traffic) meta.append(el('span','traffic',t('traffic',{n:item.traffic})));
    meta.append(el('span','',dateLabel(item.published)));content.append(meta);
    if(item.articles[0]) {
        const preview=el('p','story-preview');
        preview.append(link(item.articles[0].title,item.articles[0].url));content.append(preview);
    }
    box.append(content);return box;
}
function renderCountry(code){if(!state.showUnavailable&&state.focusedCountry!==code&&!state.feeds[code]?.items?.length){$('country-'+code)?.remove();return;}const info=country(code);const card=el('section','country-card');card.id='country-'+code;card.setAttribute('aria-label',t('regionTitle',{region:countryName(code)}));const header=el('div','country-header');const name=el('div','country-name');name.append(el('span','flag',flag(code)));const names=el('div');names.append(el('h3','',countryName(code)),el('small','',t(info.region)+' / '+code+' · '+sourceLabel(code)));name.append(names);header.append(name);const feed=state.feeds[code];header.append(el('span','count-pill',feed?(feed.items.length?t('stories',{n:feed.items.length}):feed.error?'수신 지연':'현재 화제 없음'):info.source==='gdelt'&&!state.loading.has(code)?'선택 조회':'확인 중'));card.append(header);if(!feed){if(info.source==='gdelt'&&!state.loading.has(code)){card.append(el('p','card-message','현지 언론의 최근 24시간 보도입니다. 검색 인기 순위와 다릅니다.'),button('현지 뉴스 불러오기',()=>loadNews(code),'load-news'));}else{for(let i=0;i<3;i++)card.append(el('div','skeleton'));}}else{card.append(el('div','card-updated',feed.fetched?t('lastFetched',{date:dateLabel(feed.fetched*1000)}):'아직 수신한 데이터가 없습니다'));if(feed.error)card.append(el('div','stale',t(feed.error)+(feed.stale?t('staleSuffix'):'')));const rows=feed.items.filter(matches);if(!rows.length)card.append(el('div','card-message',feed.error?'새로고침으로 다시 확인할 수 있습니다.':$('filter').value?'일치하는 화제가 없습니다.':'현재 제공된 화제가 없습니다.'));const limit=state.expanded.has(code)?Infinity:displayLimit();const list=el('div');rows.slice(0,limit).forEach(item=>list.append(storyNode(item,feed.items.indexOf(item))));card.append(list);const bottom=el('div','card-bottom');if(rows.length>displayLimit())bottom.append(button(state.expanded.has(code)?'접기 ↑':t('allStories',{n:rows.length}),()=>{state.expanded.has(code)?state.expanded.delete(code):state.expanded.add(code);replaceCard(code);}));else bottom.append(el('span','',info.source==='gdelt'?'현지 보도 · 검색 순위 아님':'Google Trends RSS'));if(info.source==='gdelt')bottom.append(button('뉴스 다시 확인',()=>loadNews(code)));else bottom.append(link('Google에서 더 보기 ↗',`https://trends.google.com/trending?geo=${code}&hl=${I18n.language}`));card.append(bottom);}const old=$('country-'+code);if(old)old.replaceWith(card);else $('board').append(card);}
function replaceCard(code){if(state.view==='home'&&visibleCodes().includes(code))renderCountry(code);updateSummary();}
function renderSaved(){const rows=state.saved.filter(matches);if(!rows.length){const empty=el('div','empty');empty.append(el('strong','',state.saved.length?'일치하는 화제가 없습니다.':'마음에 남는 화제를 모아두세요.'),el('span','','화제 옆의 ☆를 누르면 여기에 보관됩니다.'));$('board').append(empty);return;}rows.forEach(item=>{const box=el('section','saved-card');box.append(el('div','saved-label',flag(item.country)+' '+countryName(item.country)),storyNode(item));$('board').append(box);});}
async function fetchCountry(code){
    try{state.feeds[code]=await api('/api/trending?geo='+code);}
    catch(e){state.feeds[code]={...(state.feeds[code]||{items:[],fetched:null}),stale:!!state.feeds[code]?.fetched,error:e.message};}
    finally{state.loading.delete(code);replaceCard(code);$('refresh').disabled=state.loading.size>0;}
}
async function loadNews(code){
    if(state.loading.has(code))return;
    state.loading.add(code);replaceCard(code);await fetchCountry(code);
}
async function loadFeeds(){
    const codes=visibleCodes().filter(c=>country(c).source!=='gdelt'&&!state.loading.has(c));
    codes.forEach(c=>state.loading.add(c));$('refresh').disabled=state.loading.size>0;updateSummary();
    let index=0;
    await Promise.all(Array.from({length:Math.min(4,codes.length)},async()=>{
        while(index<codes.length){const code=codes[index++];await fetchCountry(code);}
    }));
    $('refresh').disabled=state.loading.size>0;
}

async function toggleSave(item){try{const data=await api('/api/saved',{country:item.country,id:item.id,save:!isSaved(item)});state.saved=data.saved;render();if(state.story?.id===item.id)updateStorySave();toast(isSaved(item)?'화제를 저장했습니다.':'저장을 해제했습니다.');}catch(e){toast(e.message);}}
function updateStorySave(){$('story-save').textContent=t(isSaved(state.story)?'★ 저장됨 · 해제하기':'☆ 이 화제 저장');$('story-save').setAttribute('aria-pressed',String(isSaved(state.story)));}
let storyGeneration=0;
function translatedHeadline(text, container, target, generation) {
    container.replaceChildren();
    const label=el('small','translation-label','기계 번역 · MyMemory');
    const value=el('p','','번역 중…');value.lang=target;value.dir='auto';
    const fallback=link(t('번역 열기 ↗'),`https://translate.google.com/?sl=auto&tl=${target}&text=${encodeURIComponent(text)}&op=translate`);
    container.append(label,value);
    return api('/api/translate',{text,target}).then(data=>{
        if(generation!==storyGeneration||!container.isConnected)return;
        value.textContent=data.text;
        if(data.text.trim()===text.trim()) label.textContent=t('원문과 동일합니다.');
    }).catch(()=>{
        if(generation!==storyGeneration||!container.isConnected)return;
        value.textContent=t('번역을 불러오지 못했습니다.');
        container.append(fallback,button(t('번역 다시 시도'),()=>translatedHeadline(text,container,target,generation),'translation-retry'));
    });
}
function openStory(item){
    state.story=item;const generation=++storyGeneration,target=I18n.language;
    $('story-country').textContent=flag(item.country)+' '+countryName(item.country)+' · '+(item.source==='gdelt'?t('현지 뉴스 · GDELT'):'GOOGLE TRENDS');
    $('story-title').textContent=item.title;
    $('story-meta').textContent=(item.traffic?t('approxTraffic',{n:item.traffic}):'')+dateLabel(item.published)+(item.source==='gdelt'?t('newsTime'):'');
    updateStorySave();$('story-articles').replaceChildren();
    const queue=[[item.title,$('story-translation')]];
    $('story-translation').replaceChildren(el('p','','번역 중…'));
    if(!item.articles.length)$('story-articles').append(el('p','muted','이 화제에 연결된 기사가 없습니다. 아래 검색을 이용해 주세요.'));
    item.articles.forEach(a=>{
        const box=el('article','article'), original=link(a.title+' ↗',a.url);original.dir='auto';box.append(original);
        const translation=el('div','headline-translation');translation.setAttribute('aria-live','polite');translation.append(el('p','','번역 중…'));box.append(translation);queue.push([a.title,translation]);
        const meta=el('p');meta.append(el('span','',a.source),link(t('한국어로 읽기 ↗'),'https://translate.google.com/translate?sl=auto&tl='+target+'&u='+encodeURIComponent(a.url)));box.append(meta);$('story-articles').append(box);
    });
    $('story-search').replaceChildren(link(t('Google 검색 ↗'),'https://www.google.com/search?q='+encodeURIComponent(item.title)),link(t('뉴스 검색 ↗'),'https://www.google.com/search?tbm=nws&q='+encodeURIComponent(item.title)),link('YouTube ↗','https://www.youtube.com/results?search_query='+encodeURIComponent(item.title)));
    if(!$('story-dialog').open)$('story-dialog').showModal();
    $('story-dialog').scrollTop=0;
    (async()=>{for(const [text,container] of queue){if(generation!==storyGeneration||!$('story-dialog').open)break;await translatedHeadline(text,container,target,generation);}})();
}
function chooseCountries(){$('country-options').replaceChildren();[...new Set(state.countries.map(c=>c.region))].forEach(region=>{const group=el('div','country-group');group.append(el('h3','',region));const options=el('div','country-options');state.countries.filter(c=>c.region===region).forEach(c=>{const label=el('label','country-option');const check=el('input');check.type='checkbox';check.value=c.code;check.checked=state.selected.includes(c.code);check.onchange=updateChoiceCount;label.append(check,document.createTextNode(flag(c.code)+' '+countryName(c.code)+(c.source==='gdelt'?t('localSuffix'):'')));options.append(label);});group.append(options);$('country-options').append(group);});updateChoiceCount();$('country-dialog').showModal();}
function chosen(){return [...$('country-options').querySelectorAll('input:checked')].map(n=>n.value);}
function updateChoiceCount(){const n=chosen().length;$('country-message').textContent=t('countryCount',{n});$('apply-countries').disabled=n<1||n>8;}
async function applyCountries(){$('apply-countries').disabled=true;try{const data=await api('/api/preferences',{countries:chosen()});state.selected=data.selected;state.expanded.clear();state.region='내 국가';state.view='home';$('country-dialog').close();render();loadFeeds();if(mapLoaded)paintMap();}catch(e){$('country-message').textContent=e.message;}finally{$('apply-countries').disabled=false;}}
let mapLoaded=false;
let globe=null;
let mapNames = new Map();
function rebuildMapNames(){
mapNames.clear();
if (typeof Intl.DisplayNames === 'function') {
    const english = new Intl.DisplayNames(['en'], {type:'region'});
    const korean = new Intl.DisplayNames([I18n.language], {type:'region'});
    for (let a=65; a<=90; a++) {
        for (let b=65; b<=90; b++) {
            const code=String.fromCharCode(a,b);
            const name=english.of(code);
            if (name!==code) mapNames.set(name,korean.of(code));
        }
    }
}
}
rebuildMapNames();
const mapNameAliases = {
    'United States of America':'United States', 'Dem. Rep. Congo':'Congo - Kinshasa',
    'Congo':'Congo - Brazzaville', 'Central African Rep.':'Central African Republic',
    'Dominican Rep.':'Dominican Republic', 'Eq. Guinea':'Equatorial Guinea',
    'S. Sudan':'South Sudan', 'Solomon Is.':'Solomon Islands',
    'Falkland Is.':'Falkland Islands', 'W. Sahara':'Western Sahara',
    'Bosnia and Herz.':'Bosnia & Herzegovina', 'Czechia':'Czechia',
    'eSwatini':'Eswatini', 'Macedonia':'North Macedonia', 'Fr. S. Antarctic Lands':'French Southern Territories'
};
function mapCountryName(feature, info) {
    const original=feature.properties.name;
    const specialNames={'N. Cyprus':'북키프로스','Somaliland':'소말릴란드'};
    return (info?countryName(info.code):'') || (specialNames[original]?t(specialNames[original]):'') || mapNames.get(mapNameAliases[original] || original) || original;
}
function hideMapTooltip() { globe?.hideTooltip(); }
async function showMap() {
    $('map-panel').hidden=false;
    $('map-toggle').setAttribute('aria-expanded','true');
    $('map-toggle').textContent=t('◎ 지구본 접기');
    if(mapLoaded) { paintMap(); globe.startAutomatic(); return; }
    try {
        if(!window.d3||!window.topojson||!window.WorldGlobe) throw Error();
        const r=await fetch('/vendor/countries.json');
        if(!r.ok) throw Error();
        const world=await r.json();
        const features=topojson.feature(world,world.objects.countries);
        globe=new WorldGlobe({svg:$('world-map'),features:features.features,
            countries:state.countries,nameFor:mapCountryName,onSelect:selectMapCountry});
        mapLoaded=true;
        $('map-status').hidden=true;
        paintMap();
    } catch(e) {
        $('map-status').textContent=t('지구본을 불러오지 못했습니다. 아래 국가 버튼으로 탐색할 수 있습니다.');
    }
    const box=$('map-countries');
    box.replaceChildren();
    state.countries.forEach(c=>box.append(button(flag(c.code)+' '+countryName(c.code),()=>selectMapCountry(c),state.selected.includes(c.code)?'selected':'')));
}
function paintMap(){globe?.highlight(state.selected);}
function selectMapCountry(c){state.focusedCountry=c.code;state.expanded.clear();state.region=c.region;state.view='home';$('filter').value='';render();loadFeeds();if(c.source==='gdelt')loadNews(c.code);$('country-'+c.code)?.scrollIntoView({behavior:'smooth',block:'start'});}
function closeMap(){globe?.setRunning(false);hideMapTooltip();$('map-panel').hidden=true;$('map-toggle').setAttribute('aria-expanded','false');$('map-toggle').textContent=t('◎ 지구본 보기');}
$('today').textContent=new Intl.DateTimeFormat(I18n.locale,{year:'numeric',month:'long',day:'numeric',weekday:'long'}).format(new Date());
$('portal').href=location.protocol+'//'+location.hostname+':49410/';
$('refresh').onclick=()=>{loadFeeds();toast('새 소식을 확인합니다. 10분 이내에는 받은 목록을 재사용합니다.');};
$('show-unavailable').onchange=async()=>{const previous=state.showUnavailable;state.showUnavailable=$('show-unavailable').checked;state.focusedCountry=null;render();$('show-unavailable').disabled=true;try{await api('/api/ui-preferences',{showUnavailable:state.showUnavailable});}catch(e){state.showUnavailable=previous;render();toast(e.message);}finally{$('show-unavailable').disabled=false;}};
$('display-count').onchange=async()=>{
    const scope=countScope(), value=Number($('display-count').value);
    const previous=state.displayCounts[scope];
    state.displayCounts[scope]=value;state.expanded.clear();render();
    $('display-count').disabled=true;
    try{await api('/api/display-preferences',{scope,count:value});}
    catch(e){state.displayCounts[scope]=previous;render();toast(e.message);}
    finally{$('display-count').disabled=false;}
};
$('filter').addEventListener('input',render);
$('choose-countries').onclick=chooseCountries;$('apply-countries').onclick=applyCountries;
$('home-tab').onclick=()=>{state.view='home';$('filter').value='';render();loadFeeds();};
$('saved-tab').onclick=async()=>{state.view='saved';$('filter').value='';render();try{state.saved=await api('/api/saved');render();}catch(e){toast(e.message);}};
$('story-dialog').addEventListener('close',()=>storyGeneration++);
$('story-close').onclick=()=>$('story-dialog').close();$('story-save').onclick=()=>toggleSave(state.story);
$('map-toggle').onclick=()=>$('map-panel').hidden?showMap():closeMap();$('map-close').onclick=closeMap;
function applyLanguage(language){
    I18n.setLanguage(language);$('language-select').value=I18n.language;
    $('today').textContent=new Intl.DateTimeFormat(I18n.locale,{year:'numeric',month:'long',day:'numeric',weekday:'long'}).format(new Date());
    rebuildMapNames();render();
    $('map-toggle').textContent=t($('map-panel').hidden?'◎ 지구본 보기':'◎ 지구본 접기');
    if(globe){globe.localize();}
    $('map-countries').replaceChildren(...state.countries.map(c=>button(flag(c.code)+' '+countryName(c.code),()=>selectMapCountry(c),state.selected.includes(c.code)?'selected':'')));
    if($('story-dialog').open)openStory(state.story);
}
$('settings-tab').onclick=()=>{state.view='settings';render();};
$('language-select').onchange=async()=>{
    const language=$('language-select').value,previous=I18n.language;
    $('language-select').disabled=true;$('settings-message').textContent='';
    try{const data=await api('/api/ui-preferences',{language});applyLanguage(data.uiPreferences.language);$('settings-message').textContent=t('언어 설정을 저장했습니다.');}
    catch(e){$('language-select').value=previous;$('settings-message').textContent=t(e.message);}
    finally{$('language-select').disabled=false;}
};
async function boot(){try{const data=await api('/api/bootstrap');Object.assign(state,{feeds:data.newsFeeds||{},countries:data.countries,selected:data.selected,saved:data.saved,csrf:data.csrf,displayCounts:data.displayCounts,showUnavailable:data.uiPreferences?.showUnavailable||false});applyLanguage(data.uiPreferences?.language||'ko');await Promise.all([showMap(),loadFeeds()]);}catch(e){$('board').replaceChildren(el('div','empty','화면을 준비하지 못했습니다. 페이지를 새로고침해 주세요.'));$('error-banner').textContent=e.message;$('error-banner').hidden=false;}}
boot();setInterval(()=>{if(!document.hidden&&state.view==='home'&&state.countries.length)loadFeeds();},600000);
