const {test} = require('node:test');
const assert = require('node:assert/strict');
const {solarPosition,isDay,localClock} = require('../frontend/desk/globe.js');

test('equinox noon and midnight illuminate opposite longitudes',()=>{
    const noon=solarPosition(new Date('2026-03-20T12:00:00Z'));
    const midnight=solarPosition(new Date('2026-03-20T00:00:00Z'));
    assert.ok(Math.abs(noon[1])<1);
    assert.ok(Math.abs(noon[0])<3);
    assert.equal(isDay([0,0],noon),true);
    assert.equal(isDay([180,0],noon),false);
    assert.equal(isDay([0,0],midnight),false);
    assert.equal(isDay([180,0],midnight),true);
});

test('solstices produce polar day and polar night',()=>{
    const summer=solarPosition(new Date('2026-06-21T12:00:00Z'));
    const winter=solarPosition(new Date('2026-12-21T12:00:00Z'));
    assert.ok(Math.abs(summer[1]-23.44)<0.5);
    assert.ok(Math.abs(winter[1]+23.44)<0.5);
    for(const longitude of [-180,-90,0,90]) {
        assert.equal(isDay([longitude,85],summer),true);
        assert.equal(isDay([longitude,85],winter),false);
        assert.equal(isDay([longitude,-85],winter),true);
    }
});

test('city clocks respect DST and fractional-hour time zones',()=>{
    const summer=new Date('2026-07-01T12:00:00Z');
    const winter=new Date('2026-01-01T12:00:00Z');
    assert.equal(localClock('America/New_York',summer).offset,'UTC-4');
    assert.equal(localClock('America/New_York',winter).offset,'UTC-5');
    assert.equal(localClock('Asia/Kolkata',summer).time,'17:30');
    assert.equal(localClock('Asia/Kathmandu',summer).offset,'UTC+5:45');
    assert.equal(localClock('Asia/Seoul',summer).time,'21:00');
});

test('leap-day geometry remains finite and clocks cross dates correctly',()=>{
    for(const date of ['2028-02-29T00:00:00Z','2028-12-31T23:59:59Z']) {
        const sun=solarPosition(new Date(date));
        assert.ok(sun.every(Number.isFinite));
        assert.ok(sun[0]>=-180&&sun[0]<180);
        assert.ok(Math.abs(sun[1])<24);
    }
    assert.equal(localClock('Asia/Seoul',new Date('2026-10-01T18:00:00Z')).time,'03:00');
    assert.match(localClock('Asia/Seoul',new Date('2026-10-01T18:00:00Z')).day,/2/);
});
