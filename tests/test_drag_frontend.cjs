// Run: node --test tests/test_drag_frontend.cjs
// DOM/protocol regression checks. Does not replace a real-browser drag smoke test.
const test=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const vm=require('node:vm');
const path=require('node:path');

function harness(){
 class Element{
  constructor(){this.children=[];this.style={setProperty(){}};this.classList={add(){},remove(){}};this.scrollHeight=100}
  append(...items){this.children.push(...items)}
  replaceChildren(){this.children=[]}
  setAttribute(){}
 }
 const board=new Element(),listeners={},messages=[];
 const context=vm.createContext({
  document:{body:new Element(),documentElement:new Element(),
            getElementById:()=>board,createElement:()=>new Element()},
  window:{parent:{postMessage:m=>messages.push(JSON.parse(JSON.stringify(m)))},
          addEventListener:(name,callback)=>{listeners[name]=callback}},
 });
 const source=fs.readFileSync(path.join(__dirname,'../ui/drag_frontend/index.html'),'utf8').match(/<script>([\s\S]*?)<\/script>/)[1];
 vm.runInContext(source,context);
 const render=args=>listeners.message({data:{type:'streamlit:render',args}});
 const value=()=>JSON.parse(JSON.stringify(vm.runInContext('values',context)));
 const cards=[{id:'a',text:'First sentence.'},{id:'b',text:'Second sentence.'},{id:'c',text:'Third sentence.'}];
 return {board,context,messages,render,value,cards};
}

test('ordering buttons, drag, protocol and rerender retain a unique permutation',()=>{
 const h=harness();
 assert.equal(h.messages[0].type,'streamlit:componentReady');
 h.render({cards:h.cards,mode:'order',boxes:[],initial:['b','a','c']});
 // Up on the second card.
 h.board.children[0].children[2].children[1].children[0].onclick();
 assert.deepEqual(h.value(),['a','b','c']);
 // Native drag handler from c onto a.
 const zone=h.board.children[0];
 zone.children[3].ondragstart({dataTransfer:{setData(){}}});
 zone.children[1].ondrop({preventDefault(){},stopPropagation(){}});
 assert.deepEqual(h.value(),['c','a','b']);
 const payload=h.messages.filter(x=>x.type==='streamlit:setComponentValue').at(-1);
 assert.equal(payload.dataType,'json');
 assert.deepEqual(payload.value,['c','a','b']);
 h.render({cards:h.cards,mode:'order',boxes:[],initial:['c','a','b']});
 assert.deepEqual(h.value(),['c','a','b']);
 assert.equal(h.board.children[0].children.length,4);
});

test('categorization supports dropdowns and native drag without duplicating cards',()=>{
 const h=harness();
 const boxes=[{id:'unassigned',label:'Not yet assigned'},{id:'intro',label:'Introduction'},{id:'body',label:'Body'}];
 h.render({cards:h.cards,mode:'category',boxes,initial:{a:'unassigned',b:'unassigned',c:'unassigned'}});
 const select=h.board.children[0].children[1].children[1].children[0];
 select.value='intro';select.onchange();
 assert.equal(h.value().a,'intro');
 const unassigned=h.board.children[0],body=h.board.children[2];
 unassigned.children[1].ondragstart({dataTransfer:{setData(){}}});
 body.ondrop({preventDefault(){}});
 assert.deepEqual(h.value(),{a:'intro',b:'body',c:'unassigned'});
 assert.equal(h.board.children.reduce((n,z)=>n+z.children.length-1,0),3);
});
