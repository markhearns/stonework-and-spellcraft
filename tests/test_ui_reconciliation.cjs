// DOM reconciliation contract tests, using a small deterministic tree double.
// These do not claim rendered browser coverage.
const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
class Node {
 constructor(tag,attrs={},children=[]){this.nodeType=tag==='#text'?3:1;this.nodeName=tag;this.tagName=tag;this.attrs={...attrs};this.childNodes=[];this.dataset={};this.value=attrs.value||'';this.checked=false;this.nodeValue=attrs.text||'';children.forEach(n=>this.appendChild(n));}
 get attributes(){return Object.entries(this.attrs).map(([name,value])=>({name,value}));}
 get id(){return this.attrs.id||'';} get name(){return this.attrs.name||'';} get type(){return this.attrs.type||'';}
 get firstChild(){return this.childNodes[0]||null;}get nextSibling(){return this.parentNode?.childNodes[this.parentNode.childNodes.indexOf(this)+1]||null;}
 getAttribute(n){return this.attrs[n]??null;}hasAttribute(n){return n in this.attrs;}setAttribute(n,v){this.attrs[n]=v;}removeAttribute(n){delete this.attrs[n];}
 closest(tag){let n=this;while(n){if(n.tagName===tag.toUpperCase())return n;n=n.parentNode;}return null;}
 appendChild(n){this.insertBefore(n,null);return n;}insertBefore(n,b){n.remove();const i=b?this.childNodes.indexOf(b):this.childNodes.length;assert.ok(i>=0);this.childNodes.splice(i,0,n);n.parentNode=this;}
 remove(){if(this.parentNode){const a=this.parentNode.childNodes;a.splice(a.indexOf(this),1);this.parentNode=null;}}
 replaceWith(n){const p=this.parentNode;p.insertBefore(n,this);this.remove();}
 cloneNode(deep){const n=new Node(this.tagName,this.attrs,deep?this.childNodes.map(c=>c.cloneNode(true)):[]);n.value=this.value;n.checked=this.checked;return n;}
 setSelectionRange(a,b){this.selectionStart=a;this.selectionEnd=b;}
}
const context=vm.createContext({document:{activeElement:null},uiRenderedContext:'castle',uiDrafts:new Map()});
const source=fs.readFileSync('static/app.js','utf8');vm.runInContext(source.slice(source.indexOf('function uiFieldKey('),source.indexOf('function mountUnifiedUI(')),context);
const el=(tag,id,children=[])=>new Node(tag,id?{'data-ui-key':id}:{},children);
const text=s=>new Node('#text',{text:s});
const a=el('SECTION','a',[text('old')]),b=el('SECTION','b'),old=el('MAIN',null,[a,b]);
context.patchUiChildren(old,el('MAIN',null,[el('SECTION','b'),el('SECTION','a',[text('new')])]));
assert.equal(old.childNodes[0],b);assert.equal(old.childNodes[1],a);assert.equal(a.firstChild.nodeValue,'new');
context.patchUiChildren(old,el('MAIN',null,[el('ARTICLE','a')]));assert.equal(old.childNodes.length,1);assert.equal(old.firstChild.tagName,'ARTICLE');
const input=new Node('INPUT',{id:'name',name:'name',value:'saved'}),form=new Node('FORM',{id:'profile'},[input]);
input.value='unfinished';input.selectionStart=3;input.selectionEnd=5;context.document.activeElement=input;context.rememberUiDraft(input);
context.patchUiNode(form,new Node('FORM',{id:'profile'},[new Node('INPUT',{id:'name',name:'name',value:'server'})]));
assert.equal(form.firstChild,input);assert.equal(input.value,'unfinished');assert.equal(context.document.activeElement,input);assert.deepEqual([input.selectionStart,input.selectionEnd],[3,5]);
context.clearUiDrafts({context:'castle',id:'profile'});context.patchUiNode(input,new Node('INPUT',{id:'name',name:'name',value:'committed'}));assert.equal(input.value,'committed');
const check=new Node('INPUT',{type:'checkbox',name:'worker-mira',value:'yes'});form.appendChild(check);check.checked=true;context.rememberUiDraft(check);context.patchUiNode(check,new Node('INPUT',{type:'checkbox',name:'worker-mira',value:'yes'}));assert.equal(check.checked,true);
const details=new Node('DETAILS',{open:''});context.patchUiNode(details,new Node('DETAILS'));assert.equal(details.hasAttribute('open'),true);
// Changing a screen identity replaces the main subtree, preventing cross-screen form reuse.
const shell=el('DIV',null,[el('MAIN','screen:one',[input])]);const original=shell.firstChild;
context.patchUiChildren(shell,el('DIV',null,[el('MAIN','screen:two',[new Node('INPUT',{value:'other'})])]));
assert.notEqual(shell.firstChild,original);assert.equal(shell.firstChild.firstChild.value,'other');
const memoryDetails=key=>({getAttribute(){return null;},parentElement:{closest(){return {getAttribute(){return key;}};}},querySelector(){return {textContent:'Read this remembered moment'};}});
assert.notEqual(context.uiDetailIdentity(memoryDetails('memory:one')),context.uiDetailIdentity(memoryDetails('memory:two')));
console.log('PASS: keyed identity/reordering, replacement/removal, focused input selection, draft preservation/clearing, expanded details and screen isolation. Tree double, not visual QA.');
