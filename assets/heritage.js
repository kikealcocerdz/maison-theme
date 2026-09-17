(function () {
  function boot(container) {
    if (!container || container.dataset.init) return;
    container.dataset.init = '1';

    var assets = window.__HERITAGE_ASSETS || {};
    /* Live mockup builds paths via H='assets/heritage-2026/'; A=n=>H+'opt-'+n+'.webp'.
       The 50 real opt-*.webp photos now ship as heritage2026-opt-*.webp and are
       emitted into __HERITAGE_ASSETS keyed by their opt-*.webp basename (see Liquid
       above), so resolve() finds them directly. Only the Renacer composition still
       maps onto existing catalog assets. */
    function resolve(u) {
      if (!u) return u;
      var base = u.split('/').pop();
      return assets[base] || u;
    }

    var H = 'assets/heritage-2026/';
    var A = function (n) { return H + 'opt-' + n + '.webp'; };

    var milestones = [
      {id:'territorio', group:0, label:'Territorio', year:'S. XII  -  1398', title:'TIERRA\nY SILENCIO', kicker:'Antes de la fábrica', heading:'Un lugar unido al barro antes de llamarse La Cartuja', text:'El relato comienza antes de la marca. El entorno de Sevilla y el Guadalquivir ya estaban vinculados a una tradición alfarera antigua; después, el Monasterio de Santa María de las Cuevas fijó en el paisaje una memoria de silencio, arquitectura y trabajo paciente.', more:'La futura fábrica no nació en un lugar neutro. Heredó un territorio con arcilla, oficio y una arquitectura capaz de convertir el tiempo en identidad.', cap:'Territorio, monasterio y tradición alfarera', layout:'territorio',
        a:A('h01-territorio-a'), b:A('h01-territorio-b')},

      {id:'origen', group:0, label:'Origen', year:'1822  -  1841', title:'ORIGEN\nSEVILLANO', kicker:'Carlos Pickman', heading:'La técnica inglesa encuentra una casa en Sevilla', text:'Carlos Pickman llega a Sevilla desde el ámbito comercial británico y convierte el antiguo recinto cartujo en una fábrica de loza fina. En 1841 nace La Cartuja de Sevilla con una ambición clara: producir piezas capaces de competir con las grandes casas inglesas.', more:'En el origen conviven técnica, comercio, ciudad y monasterio: una mezcla irrepetible que explica por qué La Cartuja no fue solo una fábrica, sino una casa con carácter propio.', cap:'Fundación, monasterio y técnica inglesa', layout:'origen',
        a:A('h02-origen-a'), c:A('h02-origen-c'), b:A('h02-origen-b'),
        car:[A('h02-origen-car1'),A('h02-origen-car2'),A('h02-origen-car3')]},

      {id:'oficio', group:0, label:'Oficio', year:'1844  -  1852', title:'OFICIO\nY FUEGO', kicker:'Primeros catálogos', heading:'Hornos, maestros y una producción que toma escala', text:'Las primeras tarifas y repertorios consolidan el estilo de la casa. La fábrica crece con operarios especializados, hornos, almacenes y piezas destinadas tanto al uso doméstico como a fondas, paradores y mercados de exportación.', more:'En estos años aparecen algunos de los grandes signos de la casa: formas reconocibles, decorados duraderos y piezas singulares como la cabeza frenológica.', cap:'Producción, hornos y piezas tempranas', layout:'oficio',
        a:A('h03-oficio-a'), c:A('h03-oficio-c'), d:A('h03-oficio-d'),
        car:[A('h03-oficio-car1'),A('h03-oficio-car2')]},

      {id:'prestigio', group:1, label:'Prestigio', year:'1862  -  1873', title:'SELLO\nREAL', kicker:'Reconocimiento', heading:'La loza sevillana entra en el mapa internacional', text:'La Cartuja recibe visitas institucionales y reconocimientos en exposiciones. En 1871 se convierte en proveedora oficial de la Casa Real y, en 1873, Carlos Pickman recibe el título de Marqués.', more:'La casa deja de ser únicamente una promesa industrial y se convierte en símbolo de prestigio: Sevilla, Europa y la mesa institucional empiezan a compartir un mismo lenguaje de calidad.', cap:'Exposiciones, Casa Real y legitimidad', layout:'prestigio',
        a:A('h04-prestigio-a'), b:A('h04-prestigio-b'),
        car:[A('h04-prestigio-arte1'),A('h04-prestigio-arte2')],
        car2:[A('h04-prestigio-sello1'),A('h04-prestigio-sello2'),A('h04-prestigio-sello3'),A('h04-prestigio-sello4'),A('h04-prestigio-sello5')]},

      {id:'archivo', group:1, label:'Archivo ornamental', year:'1880  -  1907', title:'ARCHIVO\nORNAMENTAL', kicker:'Decorados y catálogo', heading:'El ornamento se convierte en memoria', text:'El repertorio visual de La Cartuja se amplía: escenas, grecas, flores, paisajes, objetos decorativos, piezas de tocador, botes, floreros y cerámica artística. La marca empieza a construir un archivo visual que trasciende generaciones.', more:'Cada plancha, cada sello y cada motivo decorativo funciona como una forma de memoria impresa sobre la mesa.', cap:'Catálogo, decorado y cerámica artística', layout:'archivo',
        car:[A('h05-archivo-1'),A('h05-archivo-2'),A('h05-archivo-3'),A('h05-archivo-4'),A('h05-archivo-5'),A('h05-archivo-6'),A('h05-archivo-7'),A('h05-archivo-8')]},

      {id:'tecnica', group:2, label:'Técnica y mano', year:'1910  -  1952', title:'TÉCNICA\nY MANO', kicker:'Proceso artesanal', heading:'La modernización convive con el gesto manual', text:'La casa incorpora hitos técnicos y mantiene una cadena de producción donde la mano sigue decidiendo. Moldeado, cocción, sellado, decoración, esmaltado y clasificación componen un proceso largo, preciso y exigente.', more:'La técnica no sustituye al oficio: lo sostiene. La pieza atraviesa temperatura, criterio y revisión antes de llegar a la mesa.', cap:'Proceso, cocción y clasificación', layout:'tecnica',
        a:A('h06-tecnica-a'),
        car:[A('h06-tecnica-car1'),A('h06-tecnica-car2'),A('h06-tecnica-car3'),A('h06-tecnica-car4'),A('h06-tecnica-car5'),A('h06-tecnica-car6')]},

      {id:'patrimonio', group:2, label:'Patrimonio', year:'1964  -  1998', title:'PATRIMONIO\nPROTEGIDO', kicker:'Museo y BIC', heading:'La fábrica empieza a leerse como patrimonio', text:'El conjunto de La Cartuja de Santa María de las Cuevas es declarado Conjunto Monumental Histórico Artístico en 1964. Décadas después, la Colección Histórica del Museo Pickman es declarada Bien de Interés Cultural.', more:'La Cartuja deja de ser solo una marca industrial: su archivo, sus planchas, sus piezas y su memoria pasan a formar parte de un legado protegido.', cap:'Monasterio, museo y reconocimiento patrimonial', layout:'patrimonio',
        a:A('h07-patrimonio-a'), b:A('h07-patrimonio-wide'),
        car:[A('h07-patrimonio-car1'),A('h07-patrimonio-car2')]},

      {id:'nueva-etapa', group:3, label:'Nueva etapa', year:'2003  -  2016', title:'CATALOGAR\nLA MEMORIA', kicker:'Archivo vivo', heading:'Describir, conservar y volver a mirar', text:'La catalogación de piezas, la conservación de fondos y la relectura del archivo permiten mirar La Cartuja desde una nueva perspectiva. La historia ya no es un peso, sino una herramienta para construir futuro.', more:'En 2016 se abre una etapa que busca recuperar el espíritu vanguardista de la casa desde su esencia: artesanía, marca España, diseño e innovación.', cap:'Artesanía, colaboraciones y nuevas mesas', layout:'nueva',
        a:A('h08-nueva-a'),
        car:[A('h08-nueva-carA1'),A('h08-nueva-carA2'),A('h08-nueva-carA3')],
        car2:[A('h08-nueva-carB1'),A('h08-nueva-carB2'),A('h08-nueva-carB3')],
        car3:[A('h08-nueva-carC1'),A('h08-nueva-carC2')]},

      {id:'renacer', group:4, label:'El Renacer', year:'2026', title:'EL\nRENACER', kicker:'Presente', heading:'Una casa histórica vuelve a ocupar su lugar', text:'El Renacer propone volver a mirar La Cartuja desde el presente: formas históricas, decorados icónicos y objetos de conversación reinterpretados para la vida contemporánea.', more:'La nueva etapa no parte de cero. Parte de un archivo, una ciudad, una colección histórica reconocida y una manera de entender la mesa como memoria viva.', cap:'Presente, colección y futuro', layout:'renacer',
        a:'assets/mesa_bodegon_lujo_el_renacer.webp', b:'assets/collection-aurora.webp', c:'assets/gifts-decor-vertical.webp'}
    ];

    var eras = milestones;
    var main = container.querySelector('.heritage-timeline-start');
    var timeline = container.querySelector('.heritage-timeline-links');
    var root = container;
    var light = { bg: [247, 244, 238], fg: [15, 26, 46], ghost: [15, 26, 46] };
    var dark = { bg: [15, 26, 46], fg: [244, 241, 234], ghost: [244, 241, 234] };
    var clamp = function (n, a, b) { a = (a === undefined ? 0 : a); b = (b === undefined ? 1 : b); return Math.max(a, Math.min(b, n)); };
    var lerp = function (a, b, t) { return a + (b - a) * t; };
    var ease = function (t) { return 1 - Math.pow(1 - clamp(t), 3); };
    var mixArr = function (a, b, t) { return a.map(function (v, i) { return Math.round(lerp(v, b[i], t)); }); };
    var rgb = function (a) { return a.join(','); };
    function toneForEra(i) { return Math.floor(((eras[i] && eras[i].group) || 0) % 2) === 1 ? dark : light; }
    /* v98/v99: en móvil el teatro de scroll se apaga y cada era se lee apilada. */
    var mobileHeritage = window.matchMedia('(max-width: 760px)').matches;

    function im(src, alt) { return '<img src="' + resolve(src) + '" alt="' + (alt || 'La Cartuja de Sevilla') + '" loading="lazy">'; }
    function f(src, cls) { return '<div class="frame ' + (cls || '') + '">' + im(src) + '</div>'; }
    function car(paths, cls, fit) {
      var slides = paths.map(function (p, i) { return '<figure class="cslide' + (i === 0 ? ' active' : '') + '">' + im(p) + '</figure>'; }).join('');
      var total = String(paths.length).length < 2 ? '0' + paths.length : String(paths.length);
      return '<div class="carousel-unit ' + (cls || '') + '">' +
        '<div class="frame cframe carousel" data-fit="' + (fit || 'cover') + '"><div class="ctrack">' + slides + '</div></div>' +
        '<div class="carousel-bar">' +
        '<span class="ccount"><b>01</b><i>/</i>' + total + '</span>' +
        '<div class="carrows">' +
        '<button type="button" class="cbtn cprev" aria-label="Foto anterior">‹</button>' +
        '<button type="button" class="cbtn cnext" aria-label="Foto siguiente">›</button>' +
        '</div></div></div>';
    }
    function note(e, cls) { return '<div class="comp-note ' + (cls || '') + '"><p class="note-cap">' + e.cap + '</p><p>' + e.text + '</p><p class="cn-2">' + e.more + '</p></div>'; }

    function allEraImages(e) {
      var sources = [];
      ['a', 'b', 'c', 'd'].forEach(function (k) { if (e[k]) sources.push(e[k]); });
      ['car', 'car2', 'car3'].forEach(function (k) { if (Array.isArray(e[k])) sources.push.apply(sources, e[k]); });
      return sources.filter(function (v, i) { return v && sources.indexOf(v) === i; });
    }

    function mobileMediaHtml(e) {
      return '<div class="media mobile-era-media">' + car(allEraImages(e), 'mobile-era-carousel', 'contain') +
        '<div class="mobile-era-note"><p class="note-cap">' + e.cap + '</p><p>' + e.text + '</p><p>' + e.more + '</p></div></div>';
    }

    function mediaHtml(e) {
      if (mobileHeritage) return mobileMediaHtml(e);
      switch (e.layout) {
        case 'territorio':
          return '<div class="media comp comp-territorio">' + f(e.a, 't-a') + f(e.b, 't-b') + note(e, 't-note') + '</div>';
        case 'origen':
          return '<div class="media comp comp-origen">' + f(e.a, 'o-a') + f(e.c, 'o-c') + car(e.car, 'o-car', 'contain') + note(e, 'o-note') + '</div>';
        case 'oficio':
          return '<div class="media comp comp-oficio">' + f(e.a, 'of-a') + f(e.c, 'of-c') + f(e.d, 'of-d') + car(e.car, 'of-car', 'contain') + note(e, 'of-note') + '</div>';
        case 'prestigio':
          return '<div class="media comp comp-prestigio">' + f(e.b, 'pr-b') + f(e.a, 'pr-a') + car(e.car, 'pr-arte', 'contain') + car(e.car2, 'pr-sello', 'contain') + note(e, 'pr-note') + '</div>';
        case 'archivo':
          return '<div class="media comp comp-archivo">' + note(e, 'ar-note') + car(e.car, 'ar-car', 'contain') + '</div>';
        case 'tecnica':
          return '<div class="media comp comp-tecnica">' + f(e.a, 'te-a') + car(e.car, 'te-car', 'contain') + note(e, 'te-note') + '</div>';
        case 'patrimonio':
          return '<div class="media comp comp-patrimonio">' + f(e.a, 'pa-a') + car(e.car, 'pa-car', 'contain') + f(e.b, 'pa-wide') + note(e, 'pa-note') + '</div>';
        case 'nueva':
          return '<div class="media comp comp-nueva">' + f(e.a, 'nu-a') + car(e.car, 'nu-carA', 'cover') + car(e.car3, 'nu-carC', 'cover') + car(e.car2, 'nu-carB', 'cover') + note(e, 'nu-note') + '</div>';
        case 'renacer':
          return '<div class="media comp comp-renacer">' + f(e.a, 're-a') + f(e.b, 're-b') + f(e.c, 're-c') + note(e, 're-note') + '</div>';
        default:
          return '<div class="media single"><div class="frame">' + im(e.a) + '</div></div>';
      }
    }

    var important = { 'origen': 1, 'oficio': 1, 'prestigio': 1, 'archivo': 1, 'nueva-etapa': 1 };
    eras.forEach(function (e, i) {
      var sec = document.createElement('section');
      sec.className = 'era ' + (important[e.id] ? 'era-long' : '');
      sec.id = 'era-' + e.id;
      sec.dataset.index = i;
      sec.setAttribute('data-screen-label', e.label);
      if (mobileHeritage) {
        var t = toneForEra(i);
        sec.style.setProperty('--bg', rgb(t.bg));
        sec.style.setProperty('--fg', rgb(t.fg));
        sec.style.backgroundColor = 'rgb(' + rgb(t.bg) + ')';
        sec.style.color = 'rgb(' + rgb(t.fg) + ')';
      }
      sec.innerHTML = '<div class="era-stage"><div class="era-year">' + e.year + '</div><div class="visual-block visual-' + e.layout + '" data-layout="' + e.layout + '"><div class="era-meta"><div><p class="kicker">' + e.kicker + '</p><p>' + e.year + '</p></div><h2>' + e.heading + '</h2></div>' + mediaHtml(e) + '</div></div>';
      main.appendChild(sec);
      timeline.insertAdjacentHTML('beforeend', '<a class="tl" href="#era-' + e.id + '"><span>' + e.label + '</span><small>' + e.year + '</small></a>');
    });

    /* Carrusel con clic: contador + flechas debajo */
    container.querySelectorAll('.carousel-unit').forEach(function (unit) {
      var slides = [].slice.call(unit.querySelectorAll('.cslide'));
      if (slides.length <= 1) { var bar = unit.querySelector('.carousel-bar'); if (bar) bar.style.visibility = 'hidden'; return; }
      var counter = unit.querySelector('.ccount b');
      var idx = 0;
      var show = function (i) { idx = (i + slides.length) % slides.length; slides.forEach(function (s, k) { s.classList.toggle('active', k === idx); }); counter.textContent = String(idx + 1).length < 2 ? '0' + (idx + 1) : String(idx + 1); };
      unit.querySelector('.cprev').addEventListener('click', function (ev) { ev.preventDefault(); ev.stopPropagation(); show(idx - 1); });
      unit.querySelector('.cnext').addEventListener('click', function (ev) { ev.preventDefault(); ev.stopPropagation(); show(idx + 1); });
    });

    /* Lightbox: clic en imagen para abrir, clic fuera / X / Esc para cerrar */
    var imageLightbox = document.createElement('div');
    imageLightbox.className = 'image-lightbox';
    imageLightbox.setAttribute('aria-hidden', 'true');
    imageLightbox.innerHTML = '<button class="lb-close" type="button" aria-label="Cerrar imagen">×</button><img alt="La Cartuja de Sevilla">';
    container.appendChild(imageLightbox);
    var lbImg = imageLightbox.querySelector('img');
    function openLightbox(src, alt) {
      if (!src) return;
      lbImg.src = src; lbImg.alt = alt || 'La Cartuja de Sevilla';
      imageLightbox.classList.add('open'); imageLightbox.setAttribute('aria-hidden', 'false');
      container.classList.add('lightbox-open');
    }
    function closeLightbox() {
      imageLightbox.classList.remove('open'); imageLightbox.setAttribute('aria-hidden', 'true');
      container.classList.remove('lightbox-open');
      setTimeout(function () { if (!imageLightbox.classList.contains('open')) lbImg.removeAttribute('src'); }, 260);
    }
    container.addEventListener('click', function (ev) {
      var arrow = ev.target.closest && ev.target.closest('.cbtn,a,button');
      if (arrow) return;
      var img = ev.target.closest && ev.target.closest('.visual-block .frame img, .visual-block .cslide img');
      if (!img) return;
      ev.preventDefault();
      openLightbox(img.currentSrc || img.src, img.alt);
    });
    imageLightbox.addEventListener('click', function (ev) { if (ev.target === imageLightbox || ev.target.classList.contains('lb-close')) closeLightbox(); });
    document.addEventListener('keydown', function (ev) { if (ev.key === 'Escape' && imageLightbox.classList.contains('open')) closeLightbox(); });

    var ghost = document.createElement('div');
    ghost.className = 'global-ghost-title';
    ghost.setAttribute('aria-hidden', 'true');
    ghost.innerHTML = '<div></div><div></div>';
    container.appendChild(ghost);
    var ghostA = ghost.children[0], ghostB = ghost.children[1];

    var sections = [].slice.call(container.querySelectorAll('.era'));
    var tlLinks = [].slice.call(container.querySelectorAll('.tl'));

    /* Reduced motion: render flat + skip the scroll animation entirely. */
    if (window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
      container.classList.add('is-static');
      return;
    }

    function setTheme(activeIndex, fade, presence) {
      fade = fade || 0; presence = (presence === undefined ? 1 : presence);
      var current = toneForEra(activeIndex), next = toneForEra(Math.min(activeIndex + 1, eras.length - 1));
      var t = ease(fade);
      root.style.setProperty('--bg', rgb(mixArr(current.bg, next.bg, t)));
      root.style.setProperty('--fg', rgb(mixArr(current.fg, next.fg, t)));
      root.style.setProperty('--ghost', rgb(mixArr(current.ghost, next.ghost, t)));
      var tone = (t > 0.5 ? next : current);
      var maxOpacity = tone === dark ? .15 : .12;
      ghostA.textContent = (eras[activeIndex] && eras[activeIndex].title) || '';
      ghostB.textContent = (eras[Math.min(activeIndex + 1, eras.length - 1)] && eras[Math.min(activeIndex + 1, eras.length - 1)].title) || '';
      ghostA.style.opacity = (presence * maxOpacity * (1 - t)).toFixed(3);
      ghostB.style.opacity = (presence * maxOpacity * t).toFixed(3);
      root.classList.toggle('heritage-dark', tone === dark);
      root.setAttribute('data-header-variant', tone === dark ? 'light' : 'dark');
    }

    function phaseStyles(sec, p) {
      var year = sec.querySelector('.era-year'), visual = sec.querySelector('.visual-block'),
          meta = sec.querySelector('.era-meta'), media = sec.querySelector('.media'), copy = sec.querySelector('.era-copy');
      if (year) {
        var yIn = ease(clamp((p - 0.02) / 0.12));
        var yGo = ease(clamp((p - 0.26) / 0.18));
        var yEnd = ease(clamp((p - 0.82) / 0.18));
        var yoff = lerp(72, 0, yIn) - yGo * 300;
        year.style.opacity = (yIn * (1 - yGo) * (1 - yEnd)).toFixed(3);
        year.style.transform = 'translate3d(-50%,-50%,0) translateY(' + yoff.toFixed(1) + 'px)';
        year.style.filter = 'blur(' + lerp(10, 0, yIn).toFixed(2) + 'px)';
      }
      var cAppear = ease(clamp((p - 0.30) / 0.16));
      var cLeave = ease(clamp((p - 0.84) / 0.16));
      var vis = cAppear * (1 - cLeave);
      var off;
      if (p < 0.46) off = lerp(200, 0, ease(clamp((p - 0.30) / 0.16)));
      else if (p < 0.84) off = lerp(0, -40, (p - 0.46) / 0.38);
      else off = lerp(-40, -440, ease((p - 0.84) / 0.16));
      if (visual) {
        visual.style.opacity = vis.toFixed(3);
        if (sec.id === 'era-patrimonio') {
          var patAppear = ease(clamp((p - 0.26) / 0.14));
          var patScroll = ease(clamp((p - 0.50) / 0.28));
          var patLeave = ease(clamp((p - 0.86) / 0.14));
          var revealShift = Math.min(innerHeight * 0.66, 680);
          var patY = lerp(52, -40, patAppear) - revealShift * patScroll - patLeave * 360;
          visual.style.transform = 'translate3d(-50%,0,0) translateY(' + patY.toFixed(1) + 'px)';
          visual.style.filter = 'blur(' + lerp(6, 0, patAppear).toFixed(2) + 'px)';
        } else {
          visual.style.transform = 'translate3d(-50%,-50%,0) translateY(' + off.toFixed(1) + 'px)';
          visual.style.filter = 'blur(' + lerp(6, 0, cAppear).toFixed(2) + 'px)';
        }
      }
      var visOut = 1 - cLeave;
      var m = ease(clamp((p - 0.34) / 0.12)) * visOut;
      if (meta) { meta.style.setProperty('--meta-o', m.toFixed(3)); meta.style.setProperty('--meta-y', lerp(38, 0, m).toFixed(1) + 'px'); }
      var c = ease(clamp((p - 0.38) / 0.14)) * visOut;
      if (copy) { copy.style.setProperty('--copy-o', c.toFixed(3)); copy.style.setProperty('--copy-y', lerp(34, 0, c).toFixed(1) + 'px'); }
      if (media) { var scale = lerp(.994, 1, ease(clamp((p - 0.30) / 0.28))); media.style.transform = 'scale(' + scale.toFixed(4) + ')'; }
      [].slice.call(sec.querySelectorAll('.frame,.mag-card,.card')).forEach(function (fr, i) {
        var d = ease(clamp((p - (.32 + i * .015)) / .15));
        fr.style.transform = 'translate3d(0,' + lerp(28, 0, d).toFixed(1) + 'px,0)';
      });
    }

    function state() {
      var active = 0, vh = innerHeight;
      sections.forEach(function (s, i) { if (s.getBoundingClientRect().top <= vh * .44) active = i; });
      var sec = sections[active];
      var r = sec.getBoundingClientRect();
      var p = clamp((-r.top) / Math.max(1, r.height - vh));
      var next = sections[active + 1];
      var fade = 0;
      if (next) { var nr = next.getBoundingClientRect(); fade = clamp((vh * .86 - nr.top) / (vh * .36)); }
      return { active: active, p: p, fade: fade, timelineIndex: fade > .55 ? Math.min(active + 1, sections.length - 1) : active };
    }
    function ghostPresence() {
      var vh = innerHeight;
      var start = main;
      var finale = container.querySelector('.heritage-finale');
      var startTop = start ? start.getBoundingClientRect().top : 0;
      var finaleTop = finale ? finale.getBoundingClientRect().top : Infinity;
      var fadeIn = ease(clamp((vh * .72 - startTop) / (vh * .38)));
      var fadeOut = 1 - ease(clamp((vh * 1.02 - finaleTop) / (vh * .45)));
      return clamp(fadeIn * fadeOut);
    }

    var progressBar = container.querySelector('.heritage-progress-bar');
    function update() {
      var max = Math.max(1, document.documentElement.scrollHeight - innerHeight);
      if (progressBar) progressBar.style.width = (scrollY / max) * 100 + '%';
      if (mobileHeritage) {
        var mst = state();
        setTheme(mst.active, 0, 0);
        tlLinks.forEach(function (a, i) { a.classList.toggle('active', i === mst.timelineIndex); });
        return;
      }
      sections.forEach(function (s) {
        var r = s.getBoundingClientRect();
        phaseStyles(s, clamp((-r.top) / Math.max(1, r.height - innerHeight)));
      });
      var st = state();
      setTheme(st.active, st.fade, ghostPresence());
      tlLinks.forEach(function (a, i) { a.classList.toggle('active', i === st.timelineIndex); });
    }
    addEventListener('scroll', update, { passive: true });
    addEventListener('resize', update);
    requestAnimationFrame(update);

    addEventListener('keydown', function (e) {
      if (['ArrowDown', 'ArrowRight', 'ArrowUp', 'ArrowLeft'].indexOf(e.key) === -1) return;
      if (['INPUT', 'TEXTAREA'].indexOf(e.target.tagName || '') !== -1) return;
      var active = tlLinks.findIndex(function (a) { return a.classList.contains('active'); });
      var n = (e.key === 'ArrowDown' || e.key === 'ArrowRight') ? active + 1 : active - 1;
      if (tlLinks[n]) { e.preventDefault(); tlLinks[n].click(); }
    });
  }

  document.querySelectorAll('.heritage-page').forEach(boot);
  document.addEventListener('shopify:section:load', function (e) { e.target.querySelectorAll('.heritage-page').forEach(boot); });
})();
