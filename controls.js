// Pure parameter updates shared by the UI and its tests.
const StudioMath = {
  history(initial, limit=100) {
    const clone=value=>JSON.parse(JSON.stringify(value));
    let past=[clone(initial)],future=[];
    return {
      get canUndo(){return past.length>1;},get canRedo(){return future.length>0;},
      record(value){
        if(JSON.stringify(value)===JSON.stringify(past.at(-1)))return;
        past.push(clone(value));if(past.length>limit)past.shift();future=[];
      },
      undo(){if(past.length<2)return null;future.push(past.pop());return clone(past.at(-1));},
      redo(){if(!future.length)return null;past.push(future.pop());return clone(past.at(-1));}
    };
  },
  shares(weights, changed, value, available, locks={}) {
    if (locks[changed]) return {...weights};
    const fixed=available.filter(key=>key!==changed&&locks[key]);
    const fixedTotal=fixed.reduce((sum,key)=>sum+(weights[key]||0),0);
    value = Math.min(100-fixedTotal, Math.max(0, Math.round(Number(value) || 0)));
    const result = Object.fromEntries(Object.keys(weights).map(key => [key, 0]));
    result[changed] = value;
    for(const key of fixed)result[key]=weights[key]||0;
    const others = available.filter(key => key !== changed&&!locks[key]), remaining = 100-fixedTotal-value;
    const total = others.reduce((sum,key) => sum + Math.max(0, weights[key] || 0), 0);
    if (!total) {
      const fallback = others.includes('rectangle') ? 'rectangle' : others[0];
      if (fallback) result[fallback] = remaining;
      else result[changed] = 100-fixedTotal;
      return result;
    }
    const fractions = others.map(key => ({key, exact: remaining * Math.max(0, weights[key] || 0) / total}));
    for (const item of fractions) result[item.key] = Math.floor(item.exact);
    let extra = remaining - others.reduce((sum,key) => sum + result[key], 0);
    fractions.sort((a,b) => (b.exact-Math.floor(b.exact)) - (a.exact-Math.floor(a.exact)));
    for (const item of fractions) if (extra-- > 0) result[item.key]++;
    return result;
  },
  viewerPosition(left,top,width,height,viewportWidth,viewportHeight) {
    return {left:Math.min(Math.max(8,viewportWidth-width-8),Math.max(8,left)),
            top:Math.min(Math.max(8,viewportHeight-height-8),Math.max(8,top))};
  },
  dimensions(valueMm, axis, aspect) {
    if (!Number.isFinite(valueMm) || valueMm <= 0 || !Number.isFinite(aspect) || aspect <= 0) return null;
    const width = axis === 'width' ? valueMm : valueMm / aspect;
    const minimum = Math.max(1, 1 / aspect), maximum = Math.min(5000, 5000 / aspect);
    if (minimum > maximum) return null;
    const w = Math.min(maximum, Math.max(minimum, width));
    return {width_mm: w, height_mm: w * aspect};
  }
};
if (typeof module !== 'undefined') module.exports = StudioMath;
