import {test} from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {createRequire} from 'node:module';
import {JSDOM} from 'jsdom';
const require=createRequire(import.meta.url);
const d3path=path.join(path.dirname(require.resolve('d3')),'../dist/d3.min.js');
const topoPath=path.join(path.dirname(require.resolve('topojson-client')),'topojson-client.min.js');
const world=JSON.parse(fs.readFileSync('assets/world-countries.json','utf8'));
const rows=[
 {name:'Example German university',location:'Germany',rank_original:'=3',rank_lower_bound:3,academic_status:'Ranked',score_teaching_lower:0,score_research_lower:50,score_overall_lower:70,score_overall_upper:75,cluster:0},
 {name:'Example British university',location:'United Kingdom',rank_original:'2001+',rank_lower_bound:2001,academic_status:'Ranked',score_teaching_lower:80,score_research_lower:90,score_overall_lower:90,score_overall_upper:90,cluster:1},
 {name:'Example reporter',location:'Germany',rank_original:'Reporter',rank_lower_bound:null,academic_status:'Reporter',score_teaching_lower:null,score_research_lower:null,cluster:null}
];
function setup({charts=true}={}){
 const payload={rows,countries:{Germany:{iso:'DEU',numeric:'276'},'United Kingdom':{iso:'GBR',numeric:'826'}},provenance:'Synthetic test fixture',world};
 const html=fs.readFileSync('dashboard.html','utf8').replace('__PAYLOAD__',JSON.stringify(payload));
 const script=html.match(/<script>([\s\S]*?)<\/script>/)[1];
 const dom=new JSDOM(html.replace(/<script[\s\S]*?<\/script>/g,''),{runScripts:'outside-only'});
 const w=dom.window;const plots={};
 if(charts)w.Plotly={react:(id,data,layout)=>{plots[id]={data,layout}},Plots:{resize(){}}};
 w.matchMedia=()=>({matches:true});w.eval(fs.readFileSync(d3path,'utf8'));w.eval(fs.readFileSync(topoPath,'utf8'));w.eval(script);
 return {w,plots,dom};
}
test('dashboard renders sourced 2D geometry and handles chart/filter states',()=>{
 const {w,plots,dom}=setup();const $=id=>w.document.getElementById(id);
 assert.equal($('total').textContent,'3');assert.equal($('ranked').textContent,'2');
 const paths=w.document.querySelectorAll('#flat svg path');assert(paths.length>170);
 assert([...paths].every(p=>p.getAttribute('d')&&!p.getAttribute('d').includes('NaN')));
 assert.equal($('flat').style.display,'block');assert.match($('status').textContent,/3D globe unavailable/);
 $('search').value='impossible';w.render();assert.equal($('total').textContent,'0');assert.equal($('rows').innerHTML,'');
 $('search').value='';$('country').value='Germany';w.render();assert.equal($('total').textContent,'2');
 assert.equal(plots.scatter.data[0].x[0],0);assert.equal(plots.scatter.data[0].x.length,1);
 $('country').value='';$('cohort').value='Reporter';w.render();assert.equal(plots.distribution.data[0].x.length,0);assert.equal(plots.clusters.data.length,0);
 $('reset').click();assert.equal($('total').textContent,'3');
 const selects=w.document.querySelectorAll('#compareControls select');selects[0].value='0';selects[0].dispatchEvent(new w.Event('change'));assert.equal(plots.compare.data.length,1);assert.equal(plots.compare.data[0].y[0],0);assert.equal(plots.compare.data[0].y[2],null);
 const german=[...w.document.querySelectorAll('#flat svg path')].find(p=>p.getAttribute('aria-label').startsWith('Germany:'));german.dispatchEvent(new w.MouseEvent('click',{bubbles:true}));assert.equal($('country').value,'Germany');
 dom.window.close();
});
test('table and map remain available if Plotly fails to load',()=>{
 const {w,dom}=setup({charts:false});assert.equal(w.document.getElementById('total').textContent,'3');assert(w.document.querySelectorAll('#flat svg path').length>170);assert.match(w.document.getElementById('rows').innerHTML,/Example German/);dom.window.close();
});
