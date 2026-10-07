/* ============================================================================
   La Cartuja de Sevilla — Artesanía · Plato 3D
   Plato llano 202 Rosa de 28 cm modelado por Adrián (Cartuja_Plato_3D_28cm_v2,
   `artesania-plato-202-rosa.glb`, sin compresión Draco). Cae girando mientras
   su materia evoluciona con el scroll: barro → bizcocho blanco → sello y
   decorado 202 Rosa. El aro de apoyo aparece con el esmalte (morph del GLB).
   Requiere THREE r147 (UMD global) + THREE.GLTFLoader cargados antes, y
   `window.LCPlateModel` con la URL del GLB.
   ============================================================================ */
(function () {
  const API = { ready:false, _p:0, setProgress(p){ this._p = Math.max(0,Math.min(1,p)); } };
  window.LCPlate = API;

  const lerp=(a,b,t)=>a+(b-a)*t;
  const smooth=(t)=>t*t*(3-2*t);
  const ss=(a,b,t)=>{const x=Math.max(0,Math.min(1,(t-a)/(b-a)));return x*x*(3-2*x);};
  function track(stops,p){
    if(p<=stops[0].at) return stops[0].val;
    if(p>=stops[stops.length-1].at) return stops[stops.length-1].val;
    for(let i=0;i<stops.length-1;i++){const a=stops[i],b=stops[i+1];
      if(p>=a.at&&p<=b.at){return lerp(a.val,b.val,smooth((p-a.at)/(b.at-a.at)));}}
    return stops[stops.length-1].val;
  }

  function init(){
    const wrap=document.querySelector('.plate-wrap');
    const canvas=document.getElementById('plate-canvas');
    const fallback=document.querySelector('.plate-fallback');
    function showFallback(){ if(fallback) fallback.classList.add('show'); }
    if(!wrap||!canvas||typeof THREE==='undefined'||!THREE.GLTFLoader||!window.LCPlateModel){ showFallback(); return; }

    let renderer;
    try{ renderer=new THREE.WebGLRenderer({canvas,antialias:true,alpha:true,powerPreference:'high-performance'}); }
    catch(e){ showFallback(); return; }

    renderer.setPixelRatio(Math.min(window.devicePixelRatio||1,1.75));
    renderer.outputEncoding=THREE.sRGBEncoding;
    renderer.toneMapping=THREE.ACESFilmicToneMapping;
    renderer.toneMappingExposure=0.95;

    const scene=new THREE.Scene();
    const camera=new THREE.PerspectiveCamera(32,1,0.1,100);
    camera.position.set(0,0.1,10.6);
    camera.lookAt(0,0,0);

    // Luz neutra (como pide el modelo: metalness 0, reflejos suaves).
    scene.add(new THREE.HemisphereLight(0xf3f5ff,0x2a2018,0.35));
    const key=new THREE.DirectionalLight(0xffffff,0.95); key.position.set(-5,6,4.5); scene.add(key);
    const fill=new THREE.DirectionalLight(0xfff1e2,0.3); fill.position.set(6,1.5,3); scene.add(fill);
    const rim=new THREE.DirectionalLight(0xeaf2ff,0.6); rim.position.set(2.5,4,-6); scene.add(rim);

    function makeEnv(){
      const c=document.createElement('canvas');c.width=16;c.height=256;
      const x=c.getContext('2d');const g=x.createLinearGradient(0,0,0,256);
      g.addColorStop(0,'#f4f7ff');g.addColorStop(.38,'#ffffff');g.addColorStop(.5,'#d9d6cf');
      g.addColorStop(.66,'#5a5048');g.addColorStop(1,'#1a1612');
      x.fillStyle=g;x.fillRect(0,0,16,256);
      const t=new THREE.CanvasTexture(c);t.mapping=THREE.EquirectangularReflectionMapping;t.encoding=THREE.sRGBEncoding;
      const pm=new THREE.PMREMGenerator(renderer);const env=pm.fromEquirectangular(t).texture;t.dispose();pm.dispose();return env;
    }
    try{ scene.environment=makeEnv(); }catch(e){}

    // group = pose coreografiada (el frente mira a +Y, como el plato anterior);
    // holder lleva el GLB (frente en +Z, 0,28 m) a ese sistema y a radio 2.
    const group=new THREE.Group();
    const holder=new THREE.Group();
    holder.rotation.x=-Math.PI/2;
    holder.scale.setScalar(4/0.28);
    group.add(holder);
    scene.add(group);

    // Transición de materia del cargador de Adrián (fuentes/cargar-plato.js),
    // portada a r147 (vUv en vez de vMapUv). stage: 0 barro, .5 blanco, 1 decorado.
    const materials=[]; let stage=0; let morphs=[];
    function setStage(value){
      stage=Math.max(0,Math.min(1,value));
      const glaze=ss(0,.5,stage);
      materials.forEach(m=>{
        if(m.userData.shader) m.userData.shader.uniforms.stage.value=stage;
        m.roughness=lerp(1,.28,glaze);
        m.clearcoat=Math.max(.0001,.65*glaze);
        if(m.normalScale) m.normalScale.setScalar(.6*(1-glaze));
      });
      morphs.forEach(o=>{o.morphTargetInfluences[0]=1-glaze;});
    }

    new THREE.GLTFLoader().load(window.LCPlateModel, (gltf)=>{
      const parser=gltf.parser;
      Promise.all(parser.json.materials.map((_,i)=>parser.getDependency('material',i))).then((all)=>{
        const clay=all.find(m=>m.name.indexOf('Barro')>-1);
        const white=all.find(m=>m.name.indexOf('blanco')>-1);
        if(!clay||!white){ showFallback(); return; }
        gltf.scene.traverse(o=>{
          if(!o.isMesh) return;
          const mat=o.material.clone();
          mat.metalness=0;
          mat.normalMap=clay.normalMap;
          mat.normalScale=new THREE.Vector2(0,0);
          mat.clearcoat=.65; mat.clearcoatRoughness=.19;
          mat.onBeforeCompile=(shader)=>{
            shader.uniforms.stage={value:stage};
            shader.uniforms.clayTex={value:clay.map};
            shader.uniforms.clayRough={value:clay.roughnessMap};
            shader.uniforms.ivory={value:white.color};
            shader.fragmentShader='uniform float stage;uniform sampler2D clayTex;uniform sampler2D clayRough;uniform vec3 ivory;\n'+shader.fragmentShader;
            shader.fragmentShader=shader.fragmentShader.replace('#include <map_fragment>',
              'vec4 photographed = texture2D(map, vUv);\n'+
              'vec3 base = mix(texture2D(clayTex, vUv).rgb, ivory, smoothstep(0.0, 0.5, stage));\n'+
              'diffuseColor *= vec4(mix(base, photographed.rgb, smoothstep(0.5, 1.0, stage)), 1.0);');
            shader.fragmentShader=shader.fragmentShader.replace('#include <roughnessmap_fragment>',
              '#include <roughnessmap_fragment>\nroughnessFactor *= mix(texture2D(clayRough, vUv).g, 1.0, smoothstep(0.0, 0.5, stage));');
            mat.userData.shader=shader;
          };
          mat.customProgramCacheKey=()=>'cartuja-transition-v2';
          o.material=mat;
          materials.push(mat);
          if(o.morphTargetInfluences) morphs.push(o);
        });
        holder.add(gltf.scene);
        setStage(0);
        API.ready=true;
        resize(); render();
      });
    }, undefined, showFallback);

    // Materia según la fase (6 fases, p 0..1): barro en materia prima y moldeado,
    // bizcocho blanco al cocer, y sello + decorado a partir del sellado.
    const stageStops=[
      {at:0.00,val:0.0},{at:0.16,val:0.05},{at:0.30,val:0.5},
      {at:0.42,val:0.5},{at:0.52,val:1.0},{at:1.00,val:1.0},
    ];

    // Caída con giro orgánico que se asienta de espaldas (sello) en el 04 y
    // aterriza de frente (202 Rosa) en el 06. Igual que el plato anterior.
    function pose(p){
      const fall=Math.min(1,p/0.45);
      const fe=smooth(fall);
      const HALF=Math.PI/2;
      const rxStops=[
        {at:0.00,val: 0.50},{at:0.30,val:-0.40},{at:0.50,val:-HALF},
        {at:0.62,val:-HALF},{at:0.84,val: HALF},{at:1.00,val: HALF},
      ];
      group.rotation.x = track(rxStops,p) + (1-fe)*Math.PI*2*1.0;
      // Media vuelta en su plano (Y local = normal del plato) mientras enseña el
      // reverso, para que el sello se lea derecho; otra media al volverse de frente.
      const ryStops=[
        {at:0.00,val:0},{at:0.32,val:0},{at:0.48,val:Math.PI},
        {at:0.62,val:Math.PI},{at:0.84,val:Math.PI*2},{at:1.00,val:Math.PI*2},
      ];
      group.rotation.y = (1-fe)*Math.PI*2*1.4 + track(ryStops,p);
      group.rotation.z = Math.sin(fall*Math.PI*2)*0.12*(1-fe);
      group.scale.setScalar(lerp(0.9, 1.0, smooth(Math.min(1,p/0.82))));
    }

    function render(){
      const p=API._p;
      pose(p);
      if(API.ready) setStage(track(stageStops,p));
      renderer.render(scene,camera);
    }
    function resize(){
      // Canvas cuadrado: el plato conserva su forma circular.
      const rect=canvas.getBoundingClientRect();
      const w=Math.round(rect.width||canvas.clientWidth||720);
      const h=Math.round(rect.height||canvas.clientHeight||w);
      const size=Math.max(1,Math.min(w,h));
      renderer.setSize(size,size,false);
      camera.aspect=1; camera.updateProjectionMatrix();
    }
    // Sólo renderiza con la sección cerca de pantalla.
    const trackEl=document.querySelector('.process-track');
    function loop(){
      const vh=window.innerHeight||800;
      const r=trackEl?trackEl.getBoundingClientRect():{top:0,bottom:1};
      if(r.bottom>-vh*0.5 && r.top<vh*1.5) render();
      requestAnimationFrame(loop);
    }
    window.addEventListener('resize',()=>{resize();render();},{passive:true});
    resize();
    API.renderOnce=render;
    loop();
  }

  if(document.readyState==='loading') document.addEventListener('DOMContentLoaded',init);
  else init();
})();
