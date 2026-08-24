/* ============================================================================
   La Cartuja de Sevilla — Artesanía · Plato 3D
   Un plato (perfil torneado + decal top-down de Aurora 202 Rosa) que cae con
   gravedad girando, y cuya MATERIA evoluciona con el scroll:
   barbotina → moldeado → bizcocho (1ª cocción) → sellado → decoración
   (calcomanía) → esmaltado/vidriado (brillo) → pieza final mirando al frente.
   Requiere THREE r147 (UMD global) cargado antes.
   ============================================================================ */
(function () {
  const API = { ready:false, _p:0, setProgress(p){ this._p = Math.max(0,Math.min(1,p)); } };
  window.LCPlate = API;

  const lerp=(a,b,t)=>a+(b-a)*t;
  const smooth=(t)=>t*t*(3-2*t);
  function track(stops,p){
    if(p<=stops[0].at) return stops[0].val;
    if(p>=stops[stops.length-1].at) return stops[stops.length-1].val;
    for(let i=0;i<stops.length-1;i++){const a=stops[i],b=stops[i+1];
      if(p>=a.at&&p<=b.at){return lerp(a.val,b.val,smooth((p-a.at)/(b.at-a.at)));}}
    return stops[stops.length-1].val;
  }
  function colorTrack(stops,p,out){
    if(p<=stops[0].at) return out.copy(stops[0].c);
    if(p>=stops[stops.length-1].at) return out.copy(stops[stops.length-1].c);
    for(let i=0;i<stops.length-1;i++){const a=stops[i],b=stops[i+1];
      if(p>=a.at&&p<=b.at){return out.copy(a.c).lerp(b.c,smooth((p-a.at)/(b.at-a.at)));}}
    return out.copy(stops[stops.length-1].c);
  }

  function init(){
    const wrap=document.querySelector('.plate-wrap');
    const canvas=document.getElementById('plate-canvas');
    const fallback=document.querySelector('.plate-fallback');
    function showFallback(){ if(fallback) fallback.classList.add('show'); }
    if(!wrap||!canvas||typeof THREE==='undefined'){ showFallback(); return; }

    let renderer;
    try{ renderer=new THREE.WebGLRenderer({canvas,antialias:true,alpha:true,preserveDrawingBuffer:true,powerPreference:'high-performance'}); }
    catch(e){ showFallback(); return; }

    renderer.setPixelRatio(Math.min(window.devicePixelRatio||1,2));
    renderer.outputEncoding=THREE.sRGBEncoding;
    renderer.toneMapping=THREE.ACESFilmicToneMapping;
    renderer.toneMappingExposure=0.92;

    const scene=new THREE.Scene();
    const camera=new THREE.PerspectiveCamera(32,1,0.1,100);
    camera.position.set(0,0.1,10.6);
    camera.lookAt(0,0,0);

    // ---- luz: estudio sobrio. Intensidades contenidas para que el blanco
    //      conserve sombra y forma (no se quema). El env aporta el brillo. --
    scene.add(new THREE.HemisphereLight(0xeef2ff,0x1a1009,0.22));
    const key=new THREE.DirectionalLight(0xffffff,0.92); key.position.set(-5,6,4.5); scene.add(key);
    const warm=new THREE.DirectionalLight(0xffd9b0,0.32); warm.position.set(6,1.5,3); scene.add(warm);
    const rim=new THREE.DirectionalLight(0xeaf2ff,0.7); rim.position.set(2.5,4,-6); scene.add(rim);

    // ---- entorno: gradiente de estudio (claro arriba, oscuro abajo) para
    //      que el vidriado refleje y el blanco conserve sombra y forma ------
    function makeEnv(){
      const c=document.createElement('canvas');c.width=16;c.height=256;
      const x=c.getContext('2d');const g=x.createLinearGradient(0,0,0,256);
      g.addColorStop(0,'#f4f7ff');g.addColorStop(.38,'#ffffff');g.addColorStop(.5,'#d7d2c7');
      g.addColorStop(.66,'#4a3a2c');g.addColorStop(1,'#160d09');
      x.fillStyle=g;x.fillRect(0,0,16,256);
      const t=new THREE.CanvasTexture(c);t.mapping=THREE.EquirectangularReflectionMapping;t.encoding=THREE.sRGBEncoding;
      const pm=new THREE.PMREMGenerator(renderer);const env=pm.fromEquirectangular(t).texture;t.dispose();pm.dispose();return env;
    }
    try{ scene.environment=makeEnv(); }catch(e){}

    // ---- geometría: plato llano (plano, borde fino que sube), según vistas
    const R=2.0;
    const profile=[
      [0.00,0.00],[0.52,0.00],[1.02,0.015],[1.40,0.05],[1.66,0.13],[1.86,0.22],
      [1.96,0.265],[2.00,0.25],                       // borde superior
      [1.975,0.215],[1.88,0.155],[1.60,0.05],[1.30,-0.005],
      [0.92,-0.04],[0.62,-0.075],[0.60,-0.125],[0.42,-0.13],[0.32,-0.085],[0.18,-0.02],[0.00,-0.02],
    ].map(p=>new THREE.Vector2(p[0],p[1]));
    const baseGeo=new THREE.LatheGeometry(profile,200); baseGeo.computeVertexNormals();

    // UVs planares top-down para proyectar el decal
    const patGeo=baseGeo.clone();
    {
      const pos=patGeo.attributes.position;const uv=new Float32Array(pos.count*2);
      for(let i=0;i<pos.count;i++){const x=pos.getX(i),z=pos.getZ(i);
        uv[i*2]=0.5+x/(2*R);uv[i*2+1]=0.5-z/(2*R);}
      patGeo.setAttribute('uv',new THREE.BufferAttribute(uv,2));
    }

    // base de loza: tono crema (no blanco puro) para que no aparezca borde blanco
    const baseMat=new THREE.MeshPhysicalMaterial({color:0x6b5443,roughness:0.96,metalness:0,clearcoat:0,clearcoatRoughness:0.06,side:THREE.DoubleSide,envMapIntensity:0.45});

    function loadTex(url,cb){const t=new THREE.TextureLoader().load(url,()=>render(),undefined,cb||(()=>{}));t.encoding=THREE.sRGBEncoding;t.wrapS=t.wrapT=THREE.ClampToEdgeWrapping;t.center.set(0.5,0.5);return t;}
    // FRENTE: decal Aurora (más rosa y brillante), llena el disco hasta el borde
    const texFront=loadTex((window.__resources&&window.__resources.plateFront)||'assets/plate-front-decal.png');
    texFront.repeat.set(1.0,1.0);
    // REVERSO: sello de La Cartuja; espejado en Y (el plato voltea sobre X) para leerse bien
    const texBack=loadTex((window.__resources&&window.__resources.plateBack)||'assets/plate-back-decal.jpg');
    texBack.repeat.set(1.0,-1.0); texBack.offset.set(0.0,0.0);

    // un único decal sobre la geometría (DoubleSide, sin z-fighting). Cambia su
    // textura entre sello (reverso, fases 1-5) y Aurora (frente, fase 6).
    const patMat=new THREE.MeshPhysicalMaterial({
      color:0xffffff,map:texBack,roughness:0.4,metalness:0,clearcoat:0,clearcoatRoughness:0.08,
      transparent:true,opacity:0,side:THREE.DoubleSide,depthWrite:false,depthTest:false,envMapIntensity:0.7,
    });
    let curMap='back';

    const group=new THREE.Group();
    const baseMesh=new THREE.Mesh(baseGeo,baseMat);
    const patMesh=new THREE.Mesh(patGeo,patMat); patMesh.scale.setScalar(1.004); patMesh.renderOrder=2;
    group.add(baseMesh,patMesh);
    scene.add(group);

    // ---- pistas de evolución --------------------------------------------
    const C=(h)=>new THREE.Color(h);
    // materia: barbotina (barro húmedo) → seco → bizcocho crema → esmaltado
    const colorStops=[
      {at:0.00,c:C('#5a4233')}, // barbotina húmeda
      {at:0.16,c:C('#7d6450')}, // moldeado, secando
      {at:0.30,c:C('#ece5d8')}, // bizcocho (1ª cocción) crema
      {at:0.50,c:C('#f1ebe1')}, // sellado
      {at:0.66,c:C('#f6f1e8')}, // esmaltado crema cálido
      {at:1.00,c:C('#f7f2ea')},
    ];
    // brillo de esmaltado YA desde el bizcocho (punto 3 ≈ raw 0.33)
    const roughStops=[
      {at:0.00,val:0.97},{at:0.30,val:0.62},{at:0.45,val:0.32},
      {at:0.6,val:0.16},{at:0.74,val:0.06},{at:1.0,val:0.05},
    ];
    const coatStops=[ {at:0.0,val:0},{at:0.30,val:0.5},{at:0.5,val:0.85},{at:0.7,val:1},{at:1.0,val:1} ];
    // reflejo del vidriado: empieza en el bizcocho y crece
    const envStops=[ {at:0.0,val:0.45},{at:0.30,val:1.0},{at:0.5,val:1.4},{at:0.74,val:1.9},{at:1.0,val:2.1} ];
    // sello del reverso: aparece en SELLAR (raw≈0.46) y permanece
    const backStops=[ {at:0.0,val:0},{at:0.42,val:0},{at:0.50,val:1},{at:1.0,val:1} ];
    // calcomanía Aurora del frente: aparece en DECORAR (raw≈0.7) y permanece
    const frontStops=[ {at:0.0,val:0},{at:0.66,val:0},{at:0.76,val:1},{at:1.0,val:1} ];
    const patRoughStops=[ {at:0.0,val:0.45},{at:0.70,val:0.4},{at:0.8,val:0.06},{at:1.0,val:0.05} ];
    const patCoatStops=[ {at:0.0,val:0},{at:0.7,val:0.3},{at:0.8,val:1},{at:1.0,val:1} ];

    const _c=new THREE.Color();
    function applyState(p){
      colorTrack(colorStops,p,_c); baseMat.color.copy(_c);
      baseMat.roughness=track(roughStops,p);
      baseMat.clearcoat=track(coatStops,p);
      baseMat.envMapIntensity=track(envStops,p);
      // pose() ya corrió: sabemos la rotación. La cara que mira a cámara decide
      // qué textura (reverso=sello con rx<0, frente=Aurora con rx>0) y el decal
      // se desvanece cuando el plato está de canto (evita el rosa prematuro y el
      // artefacto de "ver dentro" del 3D).
      const rx=group.rotation.x;
      const faceOn=Math.abs(Math.sin(rx));                 // 1 de cara, 0 de canto
      const gate=smooth(Math.max(0,Math.min(1,(faceOn-0.55)/0.30)));
      const wantFront = rx>0;
      if(wantFront && curMap!=='front'){ patMat.map=texFront; patMat.needsUpdate=true; curMap='front'; }
      else if(!wantFront && curMap!=='back'){ patMat.map=texBack; patMat.needsUpdate=true; curMap='back'; }
      if(wantFront){
        patMat.opacity=track(frontStops,p)*gate;
        patMat.roughness=track(patRoughStops,p);
        patMat.clearcoat=track(patCoatStops,p);
      }else{
        patMat.opacity=track(backStops,p)*gate;
        patMat.roughness=0.4; patMat.clearcoat=track(coatStops,p)*0.6;
      }
      patMat.envMapIntensity=track(envStops,p)*0.8;
      patMesh.visible=patMat.opacity>0.001;
    }

    // ---- caída con gravedad + giro orgánico, asentando de frente ----------
    // Coreografía: el plato cae girando (barro), muestra el SELLO de espaldas
    // en el punto 04 (raw≈0.5), gira sobre sí y aterriza de FRENTE en el 06.
    // Siempre centrado, siempre encuadrado, con reposo final.
    function pose(p){
      // tumbo orgánico de la caída (barro→bizcocho), se desvanece hacia 0.45
      const fall=Math.min(1,p/0.45);
      const fe=smooth(fall);
      // rotación X coreografiada por keyframes
      const HALF=Math.PI/2;
      const rxStops=[
        {at:0.00,val: 0.50},          // 3/4, barro
        {at:0.30,val:-0.40},          // empieza a voltear hacia el reverso
        {at:0.50,val:-HALF},          // 04 · SELLAR — de espaldas (sello a cámara)
        {at:0.62,val:-HALF},          // mantiene el reverso durante Sellar
        {at:0.84,val: HALF},          // 06 — vuelta y de FRENTE (Aurora)
        {at:1.00,val: HALF},          // reposo de frente
      ];
      group.rotation.x = track(rxStops,p) + (1-fe)*Math.PI*2*1.0;   // vueltas extra sólo al caer
      group.rotation.y = (1-fe)*Math.PI*2*1.4;
      group.rotation.z = Math.sin(fall*Math.PI*2)*0.12*(1-fe);
      group.position.y = 0;                              // siempre centrado
      group.scale.setScalar(lerp(0.9, 1.0, smooth(Math.min(1,p/0.82))));
    }

    let raf=null;
    function render(){
      const p=API._p;
      pose(p);
      applyState(p);
      renderer.render(scene,camera);
    }
    function resize(){
      // El canvas se muestra como un cuadrado para que el plato conserve su geometría circular.
      // Antes se usaba el tamaño completo de .plate-wrap (normalmente 16:9) y el buffer se
      // comprimía dentro de un canvas cuadrado, deformando el plato verticalmente.
      const rect=canvas.getBoundingClientRect();
      let w=Math.round(rect.width||canvas.clientWidth||Math.min(wrap.clientWidth,wrap.clientHeight)||720);
      let h=Math.round(rect.height||canvas.clientHeight||w);
      const size=Math.max(1,Math.min(w,h));
      w=size; h=size;
      renderer.setSize(w,h,false);
      camera.aspect=1; camera.updateProjectionMatrix();
    }
    // sólo renderiza cerca del viewport
    const trackEl=document.querySelector('.process-track');
    function loop(){
      const vh=window.innerHeight||800;
      const r=trackEl?trackEl.getBoundingClientRect():{top:0,bottom:1};
      if(r.bottom>-vh*0.5 && r.top<vh*1.5) render();
      raf=requestAnimationFrame(loop);
    }
    loop();

    window.addEventListener('resize',()=>{resize();render();},{passive:true});
    resize();
    API.ready=true; API.renderOnce=render; API._refs={baseMat,patMat,group};
    render();
  }

  if(document.readyState==='loading') document.addEventListener('DOMContentLoaded',init);
  else init();
})();
