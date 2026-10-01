/* Solar geometry: NOAA General Solar Position Calculations.
 * https://gml.noaa.gov/grad/solcalc/solareqns.PDF
 * Approximate geometric terminator; not a sunrise/sunset forecast.
 */
(function (root) {
    'use strict';
    const DEG = Math.PI / 180;
    const wrap = angle => ((angle + 180) % 360 + 360) % 360 - 180;

    function solarPosition(date) {
        const year = date.getUTCFullYear();
        const days = (Date.UTC(year + 1, 0, 1) - Date.UTC(year, 0, 1)) / 86400000;
        const day = Math.floor((date.getTime() - Date.UTC(year, 0, 1)) / 86400000) + 1;
        const hours = date.getUTCHours() + date.getUTCMinutes() / 60 + date.getUTCSeconds() / 3600;
        const gamma = 2 * Math.PI / days * (day - 1 + (hours - 12) / 24);
        const equation = 229.18 * (0.000075 + 0.001868 * Math.cos(gamma)
            - 0.032077 * Math.sin(gamma) - 0.014615 * Math.cos(2 * gamma)
            - 0.040849 * Math.sin(2 * gamma));
        const declination = 0.006918 - 0.399912 * Math.cos(gamma)
            + 0.070257 * Math.sin(gamma) - 0.006758 * Math.cos(2 * gamma)
            + 0.000907 * Math.sin(2 * gamma) - 0.002697 * Math.cos(3 * gamma)
            + 0.00148 * Math.sin(3 * gamma);
        return [wrap((720 - hours * 60 - equation) / 4), declination / DEG];
    }

    function isDay(coordinates, sun) {
        return Math.sin(coordinates[1] * DEG) * Math.sin(sun[1] * DEG)
            + Math.cos(coordinates[1] * DEG) * Math.cos(sun[1] * DEG)
            * Math.cos((coordinates[0] - sun[0]) * DEG) >= 0;
    }

    function localClock(zone, date) {
        const time = new Intl.DateTimeFormat('ko-KR', {
            timeZone: zone, hour: '2-digit', minute: '2-digit', hourCycle: 'h23'
        }).format(date);
        const day = new Intl.DateTimeFormat('ko-KR', {
            timeZone: zone, month: 'short', day: 'numeric'
        }).format(date);
        const offset = new Intl.DateTimeFormat('en', {
            timeZone: zone, timeZoneName: 'shortOffset'
        }).formatToParts(date).find(part => part.type === 'timeZoneName').value.replace('GMT', 'UTC');
        return { time, day, offset };
    }

    // Representative city clocks, not country-wide time-zone boundaries.
    // Multiple clocks are included for several countries spanning time zones.
    const CITIES = [
        ['서울','Asia/Seoul',126.98,37.57,'KR','410'],
        ['도쿄','Asia/Tokyo',139.69,35.68,'JP','392'],
        ['뉴욕','America/New_York',-74.01,40.71,'US','840'],
        ['로스앤젤레스','America/Los_Angeles',-118.24,34.05,'US','840'],
        ['런던','Europe/London',-0.13,51.51,'GB','826'],
        ['파리','Europe/Paris',2.35,48.86,'FR','250'],
        ['베를린','Europe/Berlin',13.40,52.52,'DE','276'],
        ['로마','Europe/Rome',12.50,41.90,'IT','380'],
        ['마드리드','Europe/Madrid',-3.70,40.42,'ES','724'],
        ['타이베이','Asia/Taipei',121.56,25.03,'TW','158'],
        ['뉴델리','Asia/Kolkata',77.21,28.61,'IN','356'],
        ['싱가포르','Asia/Singapore',103.82,1.35,'SG','702'],
        ['자카르타','Asia/Jakarta',106.85,-6.21,'ID','360'],
        ['시드니','Australia/Sydney',151.21,-33.87,'AU','036'],
        ['퍼스','Australia/Perth',115.86,-31.95,'AU','036'],
        ['토론토','America/Toronto',-79.38,43.65,'CA','124'],
        ['밴쿠버','America/Vancouver',-123.12,49.28,'CA','124'],
        ['상파울루','America/Sao_Paulo',-46.63,-23.55,'BR','076'],
        ['멕시코시티','America/Mexico_City',-99.13,19.43,'MX','484'],
        ['부에노스아이레스','America/Argentina/Buenos_Aires',-58.38,-34.60,'AR','032'],
        ['요하네스버그','Africa/Johannesburg',28.05,-26.20,'ZA','710'],
        ['베이징','Asia/Shanghai',116.41,39.90,'CN','156'],
        ['두바이','Asia/Dubai',55.27,25.20,'AE','784'],
        ['카이로','Africa/Cairo',31.24,30.04,'EG','818'],
        ['모스크바','Europe/Moscow',37.62,55.75,'RU','643'],
        ['오클랜드','Pacific/Auckland',174.76,-36.85,'NZ','554'],
        ['호놀룰루','Pacific/Honolulu',-157.86,21.31,'US','840'],
        ['앙카라','Europe/Istanbul',32.86,39.93,'TR','792']
    ].map(([name,zone,lon,lat,code,mapId]) => ({name,zone,point:[lon,lat],code,mapId}));

    class WorldGlobe {
        constructor({svg,features,countries,nameFor,onSelect}) {
            this.svg = d3.select(svg);
            this.features = features;
            this.countries = new Map(countries.map(c => [+c.mapId,c]));
            this.nameFor = nameFor;
            this.onSelect = onSelect;
            this.zoom = 1;
            this.running = false;
            this.dragging = false;
            this.now = new Date();
            this.sun = solarPosition(this.now);
            this.projection = d3.geoOrthographic().translate([400,330]).scale(294)
                .rotate([-115,-20,0]).clipAngle(90).precision(0.3);
            this.path = d3.geoPath(this.projection);
            this.svg.attr('viewBox','0 0 800 660').attr('tabindex',0)
                .attr('aria-label','회전 가능한 지구본. 방향키 또는 드래그로 회전하고 국가를 선택하세요.');
            this.svg.selectAll('*').remove();
            this.svg.append('circle').attr('class','globe-atmosphere').attr('cx',400).attr('cy',330).attr('r',300);
            this.ocean = this.svg.append('path').datum({type:'Sphere'}).attr('class','globe-ocean');
            this.land = this.svg.append('g').attr('class','globe-land').selectAll('path')
                .data(features).join('path').attr('class','globe-country')
                .attr('data-map-id',d=>d.id)
                .attr('data-code',d=>this.countries.get(+d.id)?.code || '')
                .attr('aria-label',d=>this.nameFor(d,this.countries.get(+d.id)))
                .attr('role',d=>this.countries.has(+d.id)?'button':null)
                .on('pointerenter pointermove',(event,d)=>this.hover(event,d))
                .on('pointerleave',()=>this.hideTooltip())
                .on('focus',(event,d)=>this.hover(event,d))
                .on('blur',()=>this.hideTooltip())
                .on('click',(event,d)=>{
                    if(event.defaultPrevented || this.dragging) return;
                    const c=this.countries.get(+d.id);
                    if(c) { this.setRunning(false); this.hideTooltip(); this.onSelect(c); }
                })
                .on('keydown',(event,d)=>{
                    if(event.key==='Enter'||event.key===' ') {
                        event.preventDefault();
                        const c=this.countries.get(+d.id);
                        if(c) { this.setRunning(false); this.hideTooltip(); this.onSelect(c); }
                    }
                });
            this.grid = this.svg.append('path').datum(d3.geoGraticule10()).attr('class','globe-grid');
            this.night = this.svg.append('path').attr('class','globe-night').attr('aria-label','현재 밤인 영역');
            this.deepNight = this.svg.append('path').attr('class','globe-deep-night');
            this.sunMarker = this.svg.append('g').attr('class','sun-marker');
            this.sunMarker.append('circle').attr('r',7);
            this.sunMarker.append('text').attr('x',13).attr('y',5).text('태양 직하점');
            this.cityLayer = this.svg.append('g').attr('class','globe-cities');
            this.tooltip = this.svg.append('g').attr('id','map-tooltip').attr('hidden','').attr('aria-hidden','true');
            this.tooltip.append('rect').attr('rx',7);
            this.tooltip.append('text').attr('x',12).attr('y',23).attr('class','tooltip-country');
            this.tooltip.append('text').attr('x',12).attr('y',44).attr('class','tooltip-clock');
            this.svg.call(d3.drag().clickDistance(5)
                .on('start',()=>{this.dragging=true;this.setRunning(false);this.hideTooltip();this.svg.classed('dragging',true);})
                .on('drag',event=>{
                    const rotation=this.projection.rotate();
                    const factor=0.25/this.zoom;
                    this.projection.rotate([wrap(rotation[0]+event.dx*factor),Math.max(-85,Math.min(85,rotation[1]-event.dy*factor)),0]);
                    this.draw();
                })
                .on('end',()=>{this.dragging=false;this.svg.classed('dragging',false);this.updateClocks();}));
            this.svg.on('keydown',event=>{
                const steps={ArrowLeft:[-12,0],ArrowRight:[12,0],ArrowUp:[0,8],ArrowDown:[0,-8]};
                if(steps[event.key]) {event.preventDefault();this.rotate(...steps[event.key]);}
            });
            this.bindControls();
            this.updateTime();
            this.timer=setInterval(()=>this.updateTime(),30000);
            this.resizeObserver=new ResizeObserver(()=>{this.hideTooltip();this.drawCities();});
            this.resizeObserver.observe(svg);
            this.setRunning(true);
        }

        visible(point) {
            const rotation=this.projection.rotate();
            return d3.geoDistance(point,[-rotation[0],-rotation[1]]) < Math.PI/2-0.03;
        }

        draw() {
            this.svg.select('.globe-atmosphere').attr('r',this.projection.scale()+6);
            this.ocean.attr('d',this.path);
            this.land.attr('d',this.path)
                .attr('tabindex',function(){return this.getAttribute('data-code')&&this.hasAttribute('d')?0:null;})
                .attr('aria-hidden',function(){return this.hasAttribute('d')?null:'true';});
            this.grid.attr('d',this.path);
            const anti=[wrap(this.sun[0]+180),-this.sun[1]];
            this.night.datum(d3.geoCircle().center(anti).radius(89.999).precision(1)()).attr('d',this.path);
            this.deepNight.datum(d3.geoCircle().center(anti).radius(84).precision(1)()).attr('d',this.path);
            this.sunMarker.attr('visibility',this.visible(this.sun)?'visible':'hidden')
                .attr('transform',`translate(${this.projection(this.sun)})`);
            this.drawCities();
        }

        drawCities() {
            const occupied=[];
            const size=Math.min(2,Math.max(1,650/Math.max(300,this.svg.node().getBoundingClientRect().width)));
            const display=[];
            const candidates=CITIES.filter(c=>this.visible(c.point));
            // Keep important clocks, but suppress labels that would overlap.
            for(const city of candidates) {
                const point=this.projection(city.point);
                const clock=this.clocks.get(city.zone);
                const label=city.name+' '+clock.time;
                const width=Math.max(96,city.name.length*12+53)*size;
                const x=Math.max(8,Math.min(point[0]+9,790-width));
                const y=point[1]-23*size;
                if(occupied.some(b=>Math.abs(b.y-y)<40*size && x<b.x+b.w && x+width>b.x)) continue;
                occupied.push({x,y,w:width});
                display.push({...city,x,y,width,point,label,day:isDay(city.point,this.sun)});
            }
            const groups=this.cityLayer.selectAll('g').data(display,c=>c.zone).join(enter=>{
                const g=enter.append('g');g.append('circle').attr('r',3);g.append('rect').attr('rx',5).attr('height',34);
                g.append('text').attr('class','city-name');g.append('text').attr('class','city-offset');return g;
            });
            groups.attr('class',d=>d.day?'city-day':'city-night');
            groups.select('circle').attr('cx',d=>d.point[0]).attr('cy',d=>d.point[1]);
            groups.select('rect').attr('x',d=>d.x).attr('y',d=>d.y).attr('width',d=>d.width).attr('height',34*size);
            groups.select('.city-name').attr('font-size',12*size).attr('x',d=>d.x+7*size).attr('y',d=>d.y+14*size).text(d=>d.label);
            groups.select('.city-offset').attr('font-size',9*size).attr('x',d=>d.x+7*size).attr('y',d=>d.y+27*size)
                .text(d=>(d.day?'☀ 낮 · ':'☾ 밤 · ')+this.clocks.get(d.zone).offset);
            this.cityLayer.attr('visibility',document.getElementById('globe-times').checked?'visible':'hidden');
        }

        hover(event,feature) {
            if(this.dragging || this.running) return;
            const name=this.nameFor(feature,this.countries.get(+feature.id));
            const cities=CITIES.filter(c=>+c.mapId===+feature.id);
            const details=cities.slice(0,2).map(c=>{
                const clock=this.clocks.get(c.zone);
                return `${c.name} ${clock.time} (${clock.offset})`;
            }).join(' · ');
            this.tooltip.select('.tooltip-country').text(name);
            this.tooltip.select('.tooltip-clock').text(details || '');
            this.tooltip.attr('hidden',null);
            const width=Math.max(...this.tooltip.selectAll('text').nodes().map(n=>n.getComputedTextLength()))+24;
            const height=details?56:36;
            let point=event.type==='focus'?this.projection(d3.geoCentroid(feature)):d3.pointer(event,this.svg.node());
            const x=Math.max(8,Math.min(point[0]+16,792-width));
            const y=Math.max(8,Math.min(point[1]-height-12,652-height));
            this.tooltip.select('rect').attr('width',width).attr('height',height);
            this.tooltip.attr('transform',`translate(${x},${y})`);
        }

        hideTooltip() { this.tooltip.attr('hidden',''); }

        updateTime() {
            this.now=new Date();this.sun=solarPosition(this.now);
            this.clocks=new Map(CITIES.map(c=>[c.zone,localClock(c.zone,this.now)]));
            const utc=localClock('UTC',this.now);
            document.getElementById('globe-utc').textContent=`${utc.day} ${utc.time} UTC`;
            this.draw();this.updateClocks();
        }

        updateClocks() {
            const list=document.getElementById('world-clocks');list.replaceChildren();
            const rotation=this.projection.rotate();
            const front=[-rotation[0],-rotation[1]];
            const closest=CITIES.filter(c=>this.visible(c.point))
                .sort((a,b)=>d3.geoDistance(a.point,front)-d3.geoDistance(b.point,front)).slice(0,6);
            for(const city of closest) {
                const clock=this.clocks.get(city.zone);
                const day=isDay(city.point,this.sun);
                const row=document.createElement('div');row.className='world-clock';
                const name=document.createElement('span');name.textContent=city.name;
                const status=document.createElement('small');status.textContent=day?'☀ 낮':'☾ 밤';status.className=day?'is-day':'is-night';name.append(status);
                const time=document.createElement('strong');time.textContent=clock.time;
                const meta=document.createElement('small');meta.className='clock-meta';meta.textContent=clock.day+' · '+clock.offset;
                row.append(name,time,meta);list.append(row);
            }
            if(!closest.length) {const text=document.createElement('p');text.textContent='지구본을 돌리면 보이는 지역의 도시 시각이 나타납니다.';list.append(text);}
        }

        rotate(lon,lat=0) {
            this.setRunning(false);this.hideTooltip();
            const r=this.projection.rotate();
            this.projection.rotate([wrap(r[0]+lon),Math.max(-85,Math.min(85,r[1]+lat)),0]);
            this.draw();this.updateClocks();
        }

        focus(point) {
            this.setRunning(false);this.hideTooltip();
            this.projection.rotate([-point[0],-point[1],0]);this.draw();this.updateClocks();
        }

        setRunning(value) {
            this.running=value;
            this.hideTooltip();
            const btn=document.getElementById('globe-spin');btn.textContent=value?'Ⅱ 회전 멈춤':'▷ 자동 회전';
            btn.setAttribute('aria-pressed',String(value));
            cancelAnimationFrame(this.frame);
            if(value) {
                let last=performance.now(),clockTick=0;
                const tick=now=>{
                    if(!this.running) return;
                    const delta=Math.min(now-last,100);last=now;
                    if(!document.hidden && !document.getElementById('map-panel').hidden) {
                        const r=this.projection.rotate();r[0]=wrap(r[0]+delta*0.004);
                        this.projection.rotate(r);this.draw();
                        if(now-clockTick>1000) {this.updateClocks();clockTick=now;}
                    }
                    this.frame=requestAnimationFrame(tick);
                };
                this.frame=requestAnimationFrame(tick);
            }
        }

        bindControls() {
            const bind=(id,fn)=>document.getElementById(id).onclick=fn;
            bind('globe-spin',()=>this.setRunning(!this.running));
            bind('globe-left',()=>this.rotate(-30));bind('globe-right',()=>this.rotate(30));
            bind('globe-up',()=>this.rotate(0,20));bind('globe-down',()=>this.rotate(0,-20));
            bind('globe-home',()=>{this.zoom=1;this.projection.scale(294);this.focus([115,20]);this.setRunning(true);});
            bind('globe-day',()=>this.focus(this.sun));
            bind('globe-night',()=>this.focus([wrap(this.sun[0]+180),-this.sun[1]]));
            const zoom=step=>{this.zoom=Math.max(.8,Math.min(1.65,this.zoom+step));this.projection.scale(294*this.zoom);this.hideTooltip();this.draw();};
            bind('globe-in',()=>zoom(.15));bind('globe-out',()=>zoom(-.15));
            document.getElementById('globe-times').onchange=()=>this.drawCities();
        }

        highlight(selected) {
            this.land.classed('available',d=>this.countries.has(+d.id))
                .classed('chosen',d=>selected.includes(this.countries.get(+d.id)?.code));
        }
    }

    if(typeof module!=='undefined'&&module.exports) module.exports={solarPosition,isDay,localClock};
    root.WorldGlobe=WorldGlobe;
})(typeof window==='undefined'?globalThis:window);
