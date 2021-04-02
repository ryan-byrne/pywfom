(this.webpackJsonpclient=this.webpackJsonpclient||[]).push([[0],{83:function(e,t,n){"use strict";n.r(t);var c=n(0),a=n(26),s=n.n(a),i=(n(78),n(12)),r=n(43),j=n(24),o=n(14),l=n(19),d=n(11),b=n(32),u=n(30),O=n(8),h=n(6),x=n(10),m=n(9),f=n(18),p=n(28),g=n(39),v=n(73),y=n(1);function C(e){var t=Object(c.useState)(null),n=Object(i.a)(t,2),a=n[0],s=n[1],r=function(e){return s(Object(O.a)(Object(O.a)({},a),{},Object(u.a)({},e.target.id,e.target.value)))};return Object(c.useEffect)((function(){fetch("/api/settings/file").then((function(e){if(e.ok)return e.json();console.error(e)})).then((function(e){return s(e)}))}),[]),Object(y.jsx)("div",{children:a?Object(y.jsxs)(f.a,{children:[Object(y.jsx)(h.a.Group,{as:x.a,className:"mt-3 justify-content-center",children:[["Enter Username","user"],["Enter MouseID","mouse"]].map((function(e,t){var n=Object(i.a)(e,2),c=n[0],a=n[1];return Object(y.jsxs)(h.a.Group,{as:m.a,sm:1,md:2,children:[Object(y.jsx)(h.a.Control,{placeholder:c,id:a,onChange:r}),Object(y.jsx)(h.a.Text,{muted:!0,children:a.charAt(0).toUpperCase()+a.slice(1)})]},t)}))}),Object(y.jsxs)(h.a.Group,{as:x.a,className:"justify-content-center",children:[Object(y.jsxs)(h.a.Group,{as:m.a,xs:4,md:1,className:"pr-0",children:[Object(y.jsx)(h.a.Control,{type:"number",min:"0",step:"0.01",placeholder:"Enter Length of Run",id:"run_length",value:a.run_length,onChange:r}),Object(y.jsx)(h.a.Text,{muted:!0,children:"Run Duration"})]}),Object(y.jsx)(h.a.Group,{as:m.a,xs:4,md:1,className:"pl-0",children:Object(y.jsx)(h.a.Control,{as:"select",value:a.run_length_unit,onChange:r,id:"run_length_unit",custom:!0,children:["sec","min","hr"].map((function(e){return Object(y.jsx)("option",{children:e},e)}))})}),Object(y.jsxs)(h.a.Group,{as:m.a,xs:4,md:1,children:[Object(y.jsx)(h.a.Control,{type:"number",min:"0",step:"1",placeholder:"Enter Number of Runs",value:a.number_of_runs,onChange:r,id:"number_of_runs"}),Object(y.jsx)(h.a.Text,{muted:!0,children:"Number of Runs"})]})]}),Object(y.jsx)(h.a.Group,{as:x.a,className:"justify-content-center",children:Object(y.jsx)(m.a,{md:4,children:Object(y.jsxs)(l.a,{variant:"success",className:"text-center",children:["Files to be Saved to: ",Object(y.jsx)("b",{children:a.directory})]})})}),Object(y.jsx)(x.a,{className:"justify-content-center",children:Object(y.jsxs)(p.a,{children:[Object(y.jsx)(d.a,{variant:"danger",className:"ml-1",onClick:function(e){fetch("/api/settings",{method:"DELETE"}).then((function(e){e.ok&&console.log("Success")}))},children:"Close"}),Object(y.jsxs)(v.a,{variant:"secondary",className:"ml-1",as:p.a,title:"File",children:[Object(y.jsx)(g.a.Item,{eventKey:"1",onClick:function(e){},children:"Save Configuration"}),Object(y.jsx)(g.a.Item,{eventKey:"2",onClick:function(e){fetch("/api/file").then((function(e){return e.json().then((function(e){return console.log(e)}))}))},children:"Load Configuration"}),Object(y.jsx)(g.a.Item,{eventKey:"3",onClick:function(e){},children:"Load Default"}),Object(y.jsx)(g.a.Item,{eventKey:"4",onClick:function(e){},children:"Set As Default"})]}),Object(y.jsx)(d.a,{className:"ml-1",children:"Start Acquisition"})]})})]}):null})}var N=n(21),S=n(71);function k(e){var t=Object(c.useState)([]),n=Object(i.a)(t,2),a=n[0],s=n[1],r=Object(c.useState)(!1),j=Object(i.a)(r,2),h=j[0],p=j[1],g=function(t){s([]),p(!0),fetch("/api/devices/cameras").then((function(t){return t.json().then((function(t){var n=t;Object.values(e.cameras).map((function(e){console.log(e)})),s(n),p(!1)}))}))},v=function(t,n){t.target.textContent="Adding...",t.target.disabled=!0;var c=function(e){for(var t="",n="ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789",c=n.length,a=0;a<e;a++)t+=n.charAt(Math.floor(Math.random()*c));return t}(10);fetch("/api/settings/"+c,{method:"POST",headers:{Accept:"application/json","Content-Type":"application/json"},body:JSON.stringify(Object(O.a)(Object(O.a)({},a[n]),{},{id:c}))}).then((function(e){if(e.ok)return e.json();console.error(e.message)})).then((function(t){var i=Object(N.a)(a);i.splice(n,1),s(i),e.setCameras(Object(O.a)(Object(O.a)({},e.cameras),{},Object(u.a)({},c,t)))}))},C=function(t,n){fetch("/api/settings/"+n,{method:"DELETE",headers:{Accept:"application/json","Content-Type":"application/json"},body:JSON.stringify({config:null})}).then((function(t){if(t.ok){var c=Object(O.a)({},e.cameras);delete c[n],e.setCameras(c)}})).catch((function(e){return console.log(e)}))};Object(c.useEffect)((function(){g()}),[]);var k=function(t,n){return Object(y.jsx)(S.a,{className:"text-center",children:Object(y.jsxs)("tbody",{children:[Object(y.jsxs)("tr",{children:[Object(y.jsx)("th",{}),Object(y.jsx)("th",{children:"Interface"}),Object(y.jsx)("th",{children:"Index"}),Object(y.jsx)("th",{})]}),t.map((function(t,c){var a="Add"===n?[v,c]:[C,t.id],s=Object(i.a)(a,2),r=s[0],j=s[1];if("Add"===n&&!Object.values(e.cameras).map((function(e){return e.interface!==t.interface||e.index!==t.index})).every((function(e){return!0===e})))return null;return Object(y.jsxs)("tr",{children:[Object(y.jsx)("td",{children:Object(y.jsx)(d.a,{onClick:function(e){return r(e,j)},children:n})}),Object(y.jsx)("td",{children:t.interface}),Object(y.jsx)("td",{children:t.index}),Object(y.jsx)("td",{children:Object(y.jsx)(d.a,{variant:"secondary",children:"Show Info"})})]},c)}))]})})};return Object(y.jsx)("div",{children:Object(y.jsxs)(o.a,{show:e.show,onHide:e.hideEditing,children:[Object(y.jsx)(o.a.Header,{closeButton:!0,children:Object(y.jsx)(o.a.Title,{children:"Choosing Cameras"})}),Object(y.jsx)(o.a.Body,{children:Object(y.jsxs)(f.a,{children:[Object(y.jsxs)(x.a,{className:"mb-3",children:[Object(y.jsx)(m.a,{children:Object(y.jsx)(o.a.Title,{children:"Available Cameras"})}),Object(y.jsx)(m.a,{children:Object(y.jsx)(d.a,{onClick:g,children:"Search"})})]}),Object(y.jsxs)(x.a,{className:"justify-content-center",children:[h?Object(y.jsxs)(l.a,{variant:"info",children:[Object(y.jsx)(b.a,{animation:"border",size:"sm"}),"Searching for Cameras..."]}):null,a.length>0?k(a,"Add"):null]}),Object(y.jsx)(x.a,{className:"mb-3",children:Object(y.jsx)(m.a,{children:Object(y.jsx)(o.a.Title,{children:"Current Cameras"})})}),Object(y.jsx)(x.a,{className:"justify-content-center",children:Object.values(e.cameras).length>0?k(Object.values(e.cameras),"Remove"):Object(y.jsx)(l.a,{variant:"warning",children:"No Cameras Added"})})]})})]})})}var T=n(65),w=n(35),A=n(52),G=function(e){var t=Object(c.useState)({draw:!1,x:0,y:0,ix:0,iy:0}),n=Object(i.a)(t,2),a=n[0],s=n[1],r=Object(c.useState)({height:null,width:null,objectFit:"cover"}),j=Object(i.a)(r,2),o=j[0],l=j[1],d=Object(c.useRef)(),b=Object(c.useRef)();Object(c.useRef)();return Object(c.useEffect)((function(){var e=d.current,t=e.getContext("2d"),n=b.current,c=n.height,s=n.width;e.height=c,e.width=s,t.clearRect(0,0,e.width,e.height),t.strokeStyle="red";var i=a.ix,r=a.iy,j=a.x,o=a.y;a.draw&&t.strokeRect(i,r,j-i,o-r)})),Object(c.useEffect)((function(){b.current.naturalHeight,b.current.height}),[e.camera.aoi]),Object(y.jsxs)("div",{onMouseDown:function(e){var t=d.current.getBoundingClientRect(),n=t.left,c=t.top,a=e.clientX,i=e.clientY;s({ix:a-n,iy:i-c,x:a-n,y:i-c,draw:!0})},onMouseMove:function(e){var t=d.current.getBoundingClientRect(),n=t.left,c=t.top,i=e.clientX,r=e.clientY;a.draw&&s(Object(O.a)(Object(O.a)({},a),{},{x:i-n,y:r-c}))},onMouseUp:function(t){var n,c=b.current,i=c.height/c.naturalHeight,r=a.x,j=a.y,d=a.iy,u=a.ix,h=e.camera.aoi,x=h.fullHeight,m=h.fullWidth;2===t.button?n=Object(O.a)(Object(O.a)({},e.camera.aoi),{},{height:x,width:m,x:0,y:0}):(l(Object(O.a)(Object(O.a)({},o),{},{height:Math.abs(j-d)+"px",width:Math.abs(r-u)+"px"})),n=Object(O.a)(Object(O.a)({},e.camera.aoi),{},{height:parseInt(Math.abs(j-d)/i),width:parseInt(Math.abs(r-u)/i),x:parseInt(Math.min(r,u)/i),y:parseInt(Math.min(j,d)/i)})),e.setCamera(Object(O.a)(Object(O.a)({},e.camera),{},{aoi:n})),s({draw:!1,x:0,y:0,ix:0,iy:0})},children:[Object(y.jsx)("canvas",{ref:d,onContextMenu:function(e){return e.preventDefault()},className:"position-absolute",style:o}),Object(y.jsx)(T.a,{ref:b,src:"/api/feed/"+e.camera.id,fluid:!0,draggable:!1,style:o})]})};function E(e){var t=Object(c.useState)({aoi:{binning:null}}),n=Object(i.a)(t,2),a=n[0],s=n[1],l=function(e){if("primary"===e.target.id)s(Object(O.a)(Object(O.a)({},a),{},{primary:e.target.checked}));else{var t,n,c=a.aoi,i=c.fullWidth,r=c.fullHeight,j=c.x,o=c.y,l=c.height,d=c.width;e.target.checked?(t=(i-d)/2,n=(r-l)/2):(t=j,n=o),s(Object(O.a)(Object(O.a)({},a),{},{aoi:Object(O.a)(Object(O.a)({},a.aoi),{},{centered:e.target.checked,x:t,y:n})}))}},b=function(e){"binning"===e.target.id?s(Object(O.a)(Object(O.a)({},a),{},{aoi:Object(O.a)(Object(O.a)({},a.aoi),{},{binning:e.target.value})})):s(Object(O.a)(Object(O.a)({},a),{},{dtype:e.target.value}))},p=function(e){s(Object(O.a)(Object(O.a)({},a),{},{aoi:Object(O.a)(Object(O.a)({},a.aoi),{},Object(u.a)({},e.target.id,e.target.value))}))};return Object(c.useEffect)((function(){s(Object(O.a)({},e.cameras[e.selected]))}),[e.selected]),Object(y.jsx)("div",{children:Object(y.jsx)(o.a,{show:null!==e.selected,onHide:e.onHide,size:"xl",children:Object(y.jsxs)("div",{children:[Object(y.jsx)(o.a.Header,{closeButton:!0,children:Object(y.jsx)(o.a.Title,{children:"Configuring Camera"})}),a.aoi?Object(y.jsxs)(o.a.Body,{children:[Object(y.jsx)(x.a,{className:"justify-content-center",children:Object(y.jsx)(G,{camera:a,setCamera:s})}),Object(y.jsxs)(r.a,{className:"mt-3",children:[Object(y.jsx)(j.a,{eventKey:"aoiTab",title:"AOI",children:Object(y.jsxs)(f.a,{children:[Object(y.jsxs)(x.a,{className:"justify-content-center mt-3 align-items-center",xs:1,sm:4,children:[Object(y.jsxs)(w.a,{as:m.a,children:[Object(y.jsx)(w.a.Text,{children:"Binning"}),Object(y.jsx)(A.a,{as:"select",custom:!0,className:"text-center",value:a.aoi.binning,onChange:b,id:"binning",children:["1x1","2x2","4x4","8x8"].map((function(e){return Object(y.jsx)("option",{children:e},e)}))})]}),Object(y.jsx)(m.a,{className:"text-center",children:Object(y.jsx)(h.a.Check,{type:"switch",id:"centered",label:"Centered",value:a.aoi.centered,onChange:l})})]}),Object(y.jsx)(x.a,{className:"justify-content-center mt-3",xs:2,sm:6,children:["height","width","x","y"].map((function(e){return Object(y.jsxs)(h.a.Group,{as:m.a,children:[Object(y.jsx)(h.a.Control,{type:"number",min:"0",step:"1",className:"text-center",value:a.aoi[e],id:e,onChange:p}),Object(y.jsx)(h.a.Text,{muted:!0,children:e.charAt(0).toUpperCase()+e.slice(1)})]},e)}))})]})}),Object(y.jsx)(j.a,{eventKey:"framerateKey",title:"Framerate",children:Object(y.jsxs)(f.a,{className:"mt-3",children:[Object(y.jsx)(h.a.Group,{as:x.a,className:"justify-content-center",children:Object(y.jsx)(h.a.Check,{type:"switch",label:"Primary",value:a.primary,onChange:l,id:"primary"})}),Object(y.jsx)(h.a.Group,{as:x.a,xs:4,className:"justify-content-center",children:Object(y.jsxs)(h.a.Group,{children:[Object(y.jsx)(h.a.Control,{type:"number",min:"0",step:"0.01",value:a.framerate,disabled:!a.primary,onChange:p}),Object(y.jsx)(h.a.Text,{muted:!0,children:"Framerate"})]})})]})}),Object(y.jsx)(j.a,{eventKey:"pixelKey",title:"Pixel Format",children:Object(y.jsxs)(f.a,{className:"mt-3",children:[Object(y.jsx)(h.a.Group,{as:x.a,className:"justify-content-center",children:Object(y.jsxs)(h.a.Group,{children:[Object(y.jsx)(h.a.Control,{as:"select",custom:!0,value:a.dtype,onChange:b,children:["8-bit","12-bit","16-bit","32-bit"].map((function(e){return Object(y.jsx)("option",{children:e},e)}))}),Object(y.jsx)(h.a.Text,{muted:!0,children:"Bits Per Pixel"})]})}),Object(y.jsx)(h.a.Group,{as:x.a,className:"justify-content-center",children:Object(y.jsxs)(h.a.Group,{children:[Object(y.jsxs)(w.a.Prepend,{children:[Object(y.jsx)(w.a.Text,{children:"4898"}),Object(y.jsx)(w.a.Text,{children:"MB"})]}),Object(y.jsx)(h.a.Text,{muted:!0,children:"MB per Frame"})]})})]})})]})]}):null,Object(y.jsxs)(o.a.Footer,{children:[Object(y.jsx)(d.a,{variant:"secondary",onClick:e.onHide,children:"Close"}),Object(y.jsx)(d.a,{onClick:function(){return console.log(a)},children:"Save Changes"})]})]})})})}function R(e){var t=Object(c.useState)({}),n=Object(i.a)(t,2),a=n[0],s=n[1],r=Object(c.useState)(!1),j=Object(i.a)(r,2),o=j[0],l=j[1],b=Object(c.useState)(null),u=Object(i.a)(b,2),O=u[0],h=u[1];return Object(c.useEffect)((function(){fetch("/api/settings/cameras").then((function(e){if(e.ok)return e.json();console.error(e.message)})).then((function(e){return s(e)}))}),[]),console.log(a),Object(y.jsx)("div",{className:"mt-3",children:Object(y.jsxs)(f.a,{className:"text-center h-100",children:[Object(y.jsx)(x.a,{className:"align-items-center",children:Object.keys(a).map((function(e,t){var n=a[e];return Object(y.jsx)(m.a,{children:Object(y.jsx)(T.a,{src:"api/feed/"+n.id,fluid:!0,style:{cursor:"pointer"},onClick:function(){return h(n.id)},alt:n.id})},t)}))}),Object(y.jsx)(x.a,{className:"mt-3",children:Object(y.jsx)(m.a,{children:Object(y.jsx)(d.a,{onClick:function(){return l(!0)},children:0===Object.keys(a).length?"Add Camera(s)":"Edit Camera(s)"})})}),Object(y.jsx)(k,{cameras:a,setCameras:s,hideEditing:function(){return l(!1)},show:o}),Object(y.jsx)(E,{cameras:a,setCameras:s,selected:O,onHide:function(){return h(null)}})]})})}var I=function(e){var t=function(t,n){var c=t.target,a=c.value,s="text"===c.type?"name":"pin",i=Object(N.a)(e.config.leds);i[n][s]=a,e.setConfig(Object(O.a)(Object(O.a)({},e.config),{},{leds:i}))};return Object(y.jsx)("div",{children:Object(y.jsxs)(f.a,{className:"mt-3",children:[Object(y.jsx)(h.a.Group,{as:x.a,className:"justify-content-center",children:Object(y.jsxs)(m.a,{xs:4,sm:3,children:[Object(y.jsx)(h.a.Control,{type:"number",min:"0",max:"40",step:"1",value:e.config.trigger,onChange:function(t){return e.setConfig(Object(O.a)(Object(O.a)({},e.config),{},{trigger:t.target.value}))}}),Object(y.jsx)(h.a.Text,{muted:!0,children:"Trigger Pin"})]})}),Object(y.jsx)(h.a.Group,{children:e.config.leds.map((function(n,c){return Object(y.jsxs)(h.a.Group,{as:x.a,className:"justify-content-center",children:[Object(y.jsxs)(h.a.Group,{as:m.a,xs:5,children:[Object(y.jsx)(h.a.Control,{value:n.name,onChange:function(e){return t(e,c)}}),Object(y.jsx)(h.a.Text,{muted:!0,children:"LED Name"})]}),Object(y.jsxs)(h.a.Group,{as:m.a,xs:4,sm:3,children:[Object(y.jsx)(h.a.Control,{type:"number",min:"0",max:"40",step:"1",value:n.pin,onChange:function(e){return t(e,c)}}),Object(y.jsx)(h.a.Text,{muted:!0,children:"LED Pin"})]}),Object(y.jsxs)(p.a,{as:m.a,sm:4,className:"h-50",children:[Object(y.jsx)(d.a,{size:"sm",variant:"secondary",onClick:function(){return function(t){var n=Object(N.a)(e.config.leds);n.splice(t,1),e.setConfig(Object(O.a)(Object(O.a)({},e.config),{},{leds:n}))}(c)},children:"Remove"}),Object(y.jsx)(d.a,{size:"sm",onClick:function(){},children:"Test"})]})]},c)}))}),Object(y.jsx)(x.a,{className:"text-center",children:Object(y.jsx)(m.a,{children:Object(y.jsx)(d.a,{onClick:function(t){e.setConfig(Object(O.a)(Object(O.a)({},e.config),{},{leds:[].concat(Object(N.a)(e.config.leds),[{name:"New LED",pin:0}])}))},children:"Add LED"})})})]})})},K=function(e){var t=function(t,n){var c=t.target,a=c.type,s=c.value,i=c.id,r=(c.key,Object(N.a)(e.config.stim));"select-one"===a?r[n].type=s:"text"===a?r[n].name=s:"pin"===i.slice(0,3)?r[n].pins[parseInt(i.substring(3))]=s:r[n].stepSize=s,e.setConfig(Object(O.a)(Object(O.a)({},e.config),{},{stim:r}))};return Object(y.jsx)("div",{children:Object(y.jsxs)(f.a,{className:"mt-3",children:[e.config.stim.map((function(n,c){return Object(y.jsxs)(h.a.Group,{as:x.a,className:"justify-content-center",children:[Object(y.jsxs)(x.a,{className:"justify-content-center",children:[Object(y.jsxs)(h.a.Group,{as:m.a,xs:6,sm:5,children:[Object(y.jsx)(h.a.Control,{value:n.name,onChange:function(e){return t(e,c)}}),Object(y.jsx)(h.a.Text,{muted:!0,children:"Name"})]}),Object(y.jsxs)(h.a.Group,{as:m.a,xs:6,sm:5,children:[Object(y.jsxs)(h.a.Control,{as:"select",custom:!0,value:n.type,onChange:function(e){return t(e,c)},children:[Object(y.jsx)("option",{children:"2PinStepper"}),Object(y.jsx)("option",{children:"4PinStepper"})]}),Object(y.jsx)(h.a.Text,{muted:!0,children:"Type"})]}),Object(y.jsxs)(h.a.Group,{as:m.a,sm:10,children:[Object(y.jsx)(x.a,{children:Object(N.a)(Array(parseInt(n.type.charAt(0))).keys()).map((function(e,a){return Object(y.jsx)(m.a,{children:Object(y.jsx)(h.a.Control,{type:"number",id:"pin"+a,value:n.pins[a],onChange:function(e){return t(e,c)},min:"0",max:"40",step:"1"},a)},a)}))}),Object(y.jsx)(h.a.Text,{muted:!0,children:"Pins"})]}),Object(y.jsxs)(h.a.Group,{as:m.a,xs:4,sm:3,children:[Object(y.jsx)(h.a.Control,{type:"number",min:"1",step:"1",value:n.stepSize,onChange:function(e){return t(e,c)}}),Object(y.jsx)(h.a.Text,{muted:!0,children:"Step Size"})]})]}),Object(y.jsx)(x.a,{children:Object(y.jsxs)(p.a,{as:m.a,children:[Object(y.jsx)(d.a,{size:"sm",variant:"secondary",onClick:function(){return function(t){var n=Object(N.a)(e.config.stim);n.splice(t,1),e.setConfig(Object(O.a)(Object(O.a)({},e.config),{},{stim:n}))}(c)},children:"Remove"}),Object(y.jsx)(d.a,{size:"sm",children:"Test"})]})})]},c)})),Object(y.jsx)(x.a,{className:"mt-3 text-center",children:Object(y.jsx)(m.a,{children:Object(y.jsx)(d.a,{onClick:function(t){return e.setConfig(Object(O.a)(Object(O.a)({},e.config),{},{stim:[].concat(Object(N.a)(e.config.stim),[{type:"2PinStepper",name:"New Stim",pins:[0,1],stepSize:5}])}))},children:"Add Stim"})})})]})})},M=function(e){var t=function(t,n){var c=Object(N.a)(e.config.daq);"number"===t.target.type?c[n].pin=t.target.value:c[n].name=t.target.value,e.setConfig(Object(O.a)(Object(O.a)({},e.config),{},{daq:c}))};return Object(y.jsx)("div",{children:Object(y.jsxs)(f.a,{className:"mt-3",children:[e.config.daq.map((function(n,c){return Object(y.jsxs)(h.a.Group,{as:x.a,className:"justify-content-center",children:[Object(y.jsxs)(h.a.Group,{as:m.a,xs:5,children:[Object(y.jsx)(h.a.Control,{value:n.name,onChange:function(e){return t(e,c)}}),Object(y.jsx)(h.a.Text,{muted:!0,children:"Name"})]}),Object(y.jsxs)(h.a.Group,{as:m.a,xs:4,sm:3,children:[Object(y.jsx)(h.a.Control,{value:n.pin,type:"number",min:"0",max:"40",step:"1",onChange:function(e){return t(e,c)}}),Object(y.jsx)(h.a.Text,{muted:!0,children:"Pin"})]}),Object(y.jsxs)(p.a,{as:m.a,className:"h-50",children:[Object(y.jsx)(d.a,{size:"sm",variant:"secondary",onClick:function(){return function(t){var n=Object(N.a)(e.config.daq);n.splice(t,1),e.setConfig(Object(O.a)(Object(O.a)({},e.config),{},{daq:n}))}(c)},children:"Remove"}),Object(y.jsx)(d.a,{size:"sm",children:"Test"})]})]},c)})),Object(y.jsx)(x.a,{className:"justify-content-center",children:Object(y.jsx)(d.a,{onClick:function(t){return e.setConfig(Object(O.a)(Object(O.a)({},e.config),{},{daq:[].concat(Object(N.a)(e.config.daq),[{name:"New Daq",pin:0}])}))},children:"Add DAQ"})})]})})};function D(e){var t=Object(c.useState)(!1),n=Object(i.a)(t,2),a=n[0],s=(n[1],Object(c.useState)({})),l=Object(i.a)(s,2),u=l[0],O=l[1];return Object(c.useEffect)((function(){fetch("/api/settings/arduino").then((function(e){if(e.ok)return e.json();console.error(e)})).then((function(e){return O(e)}))}),[]),Object(y.jsxs)(o.a,{show:e.show,onHide:e.handleConfig,children:[Object(y.jsx)(o.a.Header,{closeButton:!0,children:Object(y.jsx)(o.a.Title,{children:"Arduino Configuration"})}),Object(y.jsx)(o.a.Body,{children:Object(y.jsxs)(r.a,{children:[Object(y.jsx)(j.a,{eventKey:"strobingTab",title:"Strobing",children:Object(y.jsx)(I,{config:u,setConfig:O})}),Object(y.jsx)(j.a,{eventKey:"stimTab",title:"Stim",children:Object(y.jsx)(K,{config:u,setConfig:O})}),Object(y.jsx)(j.a,{eventKey:"daqTab",title:"Data Acquisition",children:Object(y.jsx)(M,{config:u,setConfig:O})})]})}),Object(y.jsxs)(o.a.Footer,{children:[Object(y.jsx)(d.a,{variant:"secondary",onClick:e.handleConfig,children:"Close"}),a?Object(y.jsxs)(d.a,{variant:"primary",disabled:!0,children:[Object(y.jsx)(b.a,{as:"span",size:"sm",animation:"border",role:"status"}),"Sending to Arduino"]}):Object(y.jsx)(d.a,{variant:"primary",onClick:function(){fetch("/api/settings/arduino",{method:"POST",headers:{Accept:"application/json","Content-Type":"application/json"},body:JSON.stringify(u)}).then((function(e){if(e.ok)return e.json();console.error(e.message)})).then((function(e){return O(e)}))},children:"Configure"})]})]})}function P(e){var t=Object(c.useState)({}),n=Object(i.a)(t,2),a=n[0],s=n[1],r=Object(c.useState)([]),j=Object(i.a)(r,2),o=j[0],u=j[1],O=Object(c.useState)(0),g=Object(i.a)(O,2),v=g[0],C=g[1],N=Object(c.useState)(null),S=Object(i.a)(N,2),k=S[0],T=S[1],w=Object(c.useState)(!1),A=Object(i.a)(w,2),G=A[0],E=A[1],R=Object(c.useState)(!1),I=Object(i.a)(R,2),K=I[0],M=I[1],P=function(){return E(!G)},z=function(){u([]),fetch("/api/devices/arduinos").then((function(e){return e.json().then((function(e){0===e.length?T(Object(y.jsx)(l.a,{variant:"danger",children:"No Arduinos Found"})):(T(null),u(e))}))}))};Object(c.useEffect)((function(){0===o.length||function(){var e=o[v];T(Object(y.jsxs)(l.a,{variant:"warning",children:[Object(y.jsx)(b.a,{animation:"border",className:"mr-3",size:"sm"}),"Connecting to ",Object(y.jsx)("b",{children:e.device}),"..."]}));var t={key:"arduino",port:e.device};fetch("/api/settings/arduino",{method:"POST",headers:{Accept:"application/json","Content-Type":"application/json"},body:JSON.stringify(t)}).then((function(e){if(e.ok)return e.json();console.error(e.message)})).then((function(t){t.firmware_version?(s(t),T(Object(y.jsxs)(l.a,{variant:"success",children:[Object(y.jsxs)("p",{children:["Connected to the Arduino at ",Object(y.jsx)("b",{children:e.device})]}),Object(y.jsxs)("p",{children:["Firmware Version: ",Object(y.jsx)("b",{children:t.firmware_version})]})]}))):T(Object(y.jsx)(l.a,{variant:"danger",children:Object(y.jsxs)("p",{children:[Object(y.jsx)("b",{children:"ERROR:"})," Arduino at ",Object(y.jsx)("b",{children:e.device})," does not have compatible firmware.",Object(y.jsx)(d.a,{className:"ml-3",children:"Upload Firmware..."})]})}))}))}()}),[o,v]);return Object(c.useEffect)((function(){z()}),[]),Object(y.jsx)("div",{children:Object(y.jsxs)(f.a,{children:[Object(y.jsxs)(x.a,{className:"mt-3 justify-content-center",children:[Object(y.jsxs)(h.a.Group,{as:m.a,sm:1,lg:4,children:[Object(y.jsx)(h.a.Control,{as:"select",custom:!0,children:0===o.length?Object(y.jsx)("option",{disabled:!0,defaultValue:!0,children:"No Arduinos Found."}):o.map((function(e,t){return Object(y.jsxs)("option",{onClick:function(){return C(t)},children:[e.product," - ",e.device]},t)}))}),Object(y.jsx)(h.a.Text,{muted:!0,children:"Select an Arduino"})]}),Object(y.jsx)(h.a.Group,{as:m.a,sm:4,children:Object(y.jsxs)(p.a,{children:[Object(y.jsx)(d.a,{variant:"secondary",onClick:function(){return z()},children:"Refresh"}),Object(y.jsx)(d.a,{variant:"secondary",onClick:function(){return M(!K)},disabled:0===o.length,children:K?"Hide Info":"Show Info"}),Object(y.jsx)(d.a,{variant:"primary",disabled:!a.firmware_version,onClick:P,children:"Configure"})]})})]}),Object(y.jsx)(x.a,{className:"justify-content-center",children:Object(y.jsx)(m.a,{xs:12,md:8,children:k})}),Object(y.jsx)(D,{port:o[v],show:G,handleConfig:P})]})})}function z(){var e=Object(c.useState)({}),t=Object(i.a)(e,2),n=(t[0],t[1],Object(c.useState)({})),a=Object(i.a)(n,2),s=(a[0],a[1],Object(c.useState)(!1)),o=Object(i.a)(s,2);o[0],o[1];return Object(y.jsx)("div",{children:Object(y.jsxs)(r.a,{defaultActiveKey:"profile",id:"uncontrolled-tab-example",children:[Object(y.jsx)(j.a,{eventKey:"runTab",title:"Run",children:Object(y.jsx)(C,{})}),Object(y.jsx)(j.a,{eventKey:"camerasTab",title:"Cameras",children:Object(y.jsx)(R,{})}),Object(y.jsx)(j.a,{eventKey:"arduinoTab",title:"Arduino",children:Object(y.jsx)(P,{})})]})})}s.a.render(Object(y.jsx)(z,{}),document.getElementById("root"))}},[[83,1,2]]]);
//# sourceMappingURL=main.566e1484.chunk.js.map