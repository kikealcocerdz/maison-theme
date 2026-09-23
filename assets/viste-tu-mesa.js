(function () {
  'use strict';

  function boot(container) {
    if (!container || container.dataset.init) return;
    container.dataset.init = '1';

    var $ = function (s, c) { return (c || container).querySelector(s); };
    var $$ = function (s, c) { return Array.prototype.slice.call((c || container).querySelectorAll(s)); };
    var clamp = function (n, a, b) { return Math.max(a, Math.min(b, n)); };
    var reducedMotion = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    var scrollBehavior = reducedMotion ? 'auto' : 'smooth';

    /* Asset map: mockup logical paths (assets/…) → theme asset_url.
       Returns null when the logical file was not shipped, so the photo
       cascade can skip it (mirrors the mockup's onerror fall-through). */
    var ASSETS = window.__VT_ASSETS || {};
    function resolve(u) {
      if (!u) return null;
      return ASSETS[u.replace(/^assets\//, '')] || null;
    }

    /* ---------- Hero microparallax ---------- */
    var hero = $('#heroVTM');
    if (hero && !reducedMotion) {
      hero.addEventListener('pointermove', function (e) {
        var r = hero.getBoundingClientRect();
        var mx = ((e.clientX - r.left) / r.width - 0.5).toFixed(3);
        var my = ((e.clientY - r.top) / r.height - 0.5).toFixed(3);
        hero.style.setProperty('--mx', mx);
        hero.style.setProperty('--my', my);
      }, { passive: true });
    }

    /* ---------- Guía por pasos tipo tubelight ---------- */
    var guideExp = $('[data-guide-experience]');
    if (guideExp) {
      guideExp.dataset.active = 'base';
      $$('.tube-item', guideExp).forEach(function (btn) {
        btn.addEventListener('click', function () {
          var id = btn.dataset.guide;
          guideExp.dataset.active = id;
          $$('.tube-item', guideExp).forEach(function (b) {
            var active = b === btn;
            b.classList.toggle('is-active', active);
            b.setAttribute('aria-selected', active ? 'true' : 'false');
          });
          $$('.guide-panel', guideExp).forEach(function (panel) {
            panel.classList.toggle('is-active', panel.dataset.guidePanel === id);
          });
          $$('.guide-image-panel', guideExp).forEach(function (panel) {
            panel.classList.toggle('is-active', panel.dataset.guideImage === id);
          });
          var label = $('.guide-media-label', guideExp);
          if (label) {
            var no = btn.querySelector('span') ? btn.querySelector('span').textContent : '';
            var title = btn.querySelector('b') ? btn.querySelector('b').textContent : '';
            label.innerHTML = '<span>' + no + '</span><b>' + title + '</b>';
          }
        });
      });
    }

    /* ---------- Laboratorio de capas ---------- */
    function pulseLab(layer) {
      var labStage = $('.lab-stage');
      if (labStage) {
        labStage.classList.add('is-updating');
        window.setTimeout(function () { labStage.classList.remove('is-updating'); }, 520);
      }
      if (layer && layer.classList.contains('on')) {
        layer.classList.remove('just-toggled');
        void layer.offsetWidth;
        layer.classList.add('just-toggled');
        window.setTimeout(function () { layer.classList.remove('just-toggled'); }, 720);
      }
    }

    function updateLabStack() {
      var labStage = $('.lab-stage');
      var protagonista = $('.lab-protagonista');
      var bajoplato = $('.lab-bajoplato');
      var hasStack = !!(protagonista && bajoplato && protagonista.classList.contains('on') && bajoplato.classList.contains('on'));
      if (labStage) {
        labStage.classList.toggle('has-stack', hasStack);
        var mantel = $('.lab-mantel');
        labStage.classList.toggle('has-mantel', !!(mantel && mantel.classList.contains('on')));
      }
      var active = $$('.lab-toggle').filter(function (btn) { return btn.getAttribute('aria-pressed') === 'true'; }).length;
      var counter = $('#labCount');
      if (counter) counter.textContent = active === 1 ? '1 capa activa' : active + ' capas activas';
    }

    /* Un toggle puede gobernar más de una capa (cubertería = tenedor + cuchillo). */
    function labLayersFor(toggle) {
      if (toggle.dataset.layer === 'cuberteria') {
        return [$('.lab-tenedor'), $('.lab-cuchillo')].filter(Boolean);
      }
      var layer = $('.lab-' + toggle.dataset.layer);
      return layer ? [layer] : [];
    }

    function setLabToggle(toggle, next) {
      toggle.setAttribute('aria-pressed', next ? 'true' : 'false');
      labLayersFor(toggle).forEach(function (layer) {
        layer.classList.toggle('on', next);
      });
    }

    $$('.lab-toggle').forEach(function (btn) {
      btn.addEventListener('click', function () {
        var on = btn.getAttribute('aria-pressed') === 'true';
        var next = !on;

        // data-exclusive="textil": individual y mantel se excluyen entre sí.
        if (next && btn.dataset.exclusive) {
          $$('.lab-toggle[data-exclusive="' + btn.dataset.exclusive + '"]').forEach(function (other) {
            if (other !== btn) setLabToggle(other, false);
          });
        }

        setLabToggle(btn, next);
        updateLabStack();
        var layers = labLayersFor(btn);
        pulseLab(layers[0] || $('.lab-stage'));
      });
    });

    $$('.lab-quick-actions [data-lab-preset]').forEach(function (btn) {
      btn.addEventListener('click', function () {
        var full = btn.dataset.labPreset === 'full';
        $$('.lab-toggle').forEach(function (toggle) {
          var next = full;
          if (full && toggle.dataset.layer === 'individual') next = false;
          if (full && toggle.dataset.layer === 'mantel') next = true;
          setLabToggle(toggle, next);
        });
        updateLabStack();
        pulseLab($('.lab-stage'));
      });
    });
    updateLabStack();

    /* ============================================================
       WIZARD + PREVIEW (data ported verbatim from the mockup v59)
       ============================================================ */
    var COLORS = {
      woodLight: '#D8C3A2', woodDark: '#6E513A', stone: '#E7E3DB', graphite: '#2A2E36',
      none: 'transparent', linenWhite: '#F7F3EC', linenBeige: '#E7DCC8', pattern: '#D8D0C0', dark: '#242321'
    };

    var QUESTIONS = [
      {
        key: 'space', q: '¿Dónde va a estar esa mesa?', lead: 'El espacio cambia la luz y el tono visual.',
        options: [
          { id: 'luminoso', label: 'Interior luminoso', desc: 'Blancos, reflejos y equilibrio.' },
          { id: 'clasico', label: 'Casa clásica', desc: 'Molduras, memoria y gesto tradicional.' },
          { id: 'contemporaneo', label: 'Interior contemporáneo', desc: 'Líneas limpias y composición más depurada.' },
          { id: 'jardin', label: 'Jardín o terraza', desc: 'Exterior, aire y materia natural.' }
        ]
      },
      {
        key: 'occasion', q: '¿Para qué ocasión quieres vestir la mesa?', lead: 'Define el ritmo de la composición.',
        options: [
          { id: 'desayuno', label: 'Desayuno lento', desc: 'Luz suave, piezas serenas y una escena de mañana.' },
          { id: 'aperitivo', label: 'Aperitivo en casa', desc: 'Piezas de apoyo, fuentes y objetos para compartir.' },
          { id: 'comidaFormal', label: 'Comida formal', desc: 'Más estructura, capas completas y presencia clásica.' },
          { id: 'cenaEspecial', label: 'Cena especial', desc: 'Contraste, profundidad y vajilla con carácter.' }
        ]
      },
      {
        key: 'base', q: '¿Cómo es la base de tu mesa?', lead: 'La superficie condiciona la presencia de la vajilla.',
        options: [
          { id: 'woodLight', label: 'Madera clara', desc: 'Natural, cálida y ligera.', swatch: COLORS.woodLight },
          { id: 'woodDark', label: 'Madera oscura', desc: 'Más contraste y profundidad.', swatch: COLORS.woodDark },
          { id: 'stone', label: 'Blanca o piedra', desc: 'Limpia, mineral y luminosa.', swatch: COLORS.stone },
          { id: 'graphite', label: 'Negra / grafito', desc: 'Sofisticada y teatral.', swatch: COLORS.graphite }
        ]
      },
      {
        key: 'textil', q: '¿Qué textil imaginas?', lead: 'El textil suaviza la escena y añade temperatura.',
        options: [
          { id: 'none', label: 'Sin mantel', desc: 'Mantiene visible la mesa que acabas de elegir.', swatch: '#EDEAE4' },
          { id: 'linenWhite', label: 'Lino blanco', desc: 'Clásico, limpio y luminoso.', swatch: COLORS.linenWhite },
          { id: 'linenBeige', label: 'Lino beige', desc: 'Cálido y muy natural.', swatch: COLORS.linenBeige },
          { id: 'pattern', label: 'Patrón', desc: 'Un motivo textil que añade ritmo y personalidad.', swatch: COLORS.pattern },
          { id: 'dark', label: 'Oscuro', desc: 'Más contraste y presencia.', swatch: COLORS.dark }
        ]
      },
      {
        key: 'style', q: '¿Qué estilo quieres transmitir?', lead: 'La misma vajilla cambia según la intención.',
        options: [
          { id: 'clasico', label: 'Clásico', desc: 'Herencia, calma y simetría.', icon: 'I' },
          { id: 'contemporaneo', label: 'Contemporáneo', desc: 'Más aire y menos ornamento.', icon: 'II' },
          { id: 'mediterraneo', label: 'Mediterráneo', desc: 'Luz, color y naturalidad.', icon: 'III' },
          { id: 'sobrio', label: 'Sobrio y elegante', desc: 'Pocas piezas, mucho carácter.', icon: 'IV' }
        ]
      },
      {
        key: 'presence', q: '¿Cuánta presencia debe tener la vajilla?', lead: 'Ajusta si quieres que acompañe o que lidere la mesa.',
        options: [
          { id: 'sutil', label: 'Sutil', desc: 'La vajilla acompaña sin imponerse.', icon: '·' },
          { id: 'equilibrada', label: 'Equilibrada', desc: 'Presencia media, fácil de recibir.', icon: '○' },
          { id: 'protagonista', label: 'Muy protagonista', desc: 'El decorado marca la escena.', icon: '●' }
        ]
      }
    ];

    var FORM_ROOT = 'assets/viste-tu-mesa/formulario';
    var DEFAULT_FORM_PHOTO = FORM_ROOT + '/01-espacio/luminoso.webp';

    /* Copy editorial de cada colección candidata (curación hardcodeada, decisión
       del cliente). Nombre, url, precios, fotos y variantes NO viven aquí: se
       inyectan desde window.__VT_COLLECTIONS con el catálogo real. `ambient` es
       solo el respaldo si la colección no tiene imagen en el admin. */
    var COLLECTIONS = {
      'aurora-blanca': {
        tag: 'Serena · Luminosa', eyebrow: 'La base atemporal', ambient: 'assets/sets/aurora-blanca/vajilla.webp',
        reason: 'Esmalte blanco roto y líneas suaves: la base atemporal sobre la que se dibuja todo lo demás. Perfecta para desayunos lentos y mesas serenas donde la vajilla acompaña sin alzar la voz.'
      },
      'ochavada-blanca': {
        tag: 'Geométrica · Sobria', eyebrow: 'Modernidad de 1841', ambient: 'assets/sets/ochavada-blanca/vajilla.webp',
        reason: 'La silueta octogonal que nació moderna. Líneas limpias para mesas contemporáneas y bases despejadas, sin ornamento que sobre.'
      },
      'bellavista': {
        tag: 'Luminosa · Equilibrada', eyebrow: 'Decorado sobre Aurora', ambient: 'assets/sets/bellavista/vajilla.webp',
        reason: 'Luminosa y equilibrada, donde la tradición y la contemporaneidad se encuentran. La vajilla que funciona igual de bien en una mesa de diario que en una puesta con intención.'
      },
      '202-rosa': {
        tag: 'Clásica · Memoria', eyebrow: 'Emblema de la casa', ambient: 'assets/sets/202-rosa/vajilla.webp',
        reason: 'Paisajes suaves, motivos florales y grecas exquisitas en el rosa eterno de La Cartuja. Convierte cualquier celebración en un recuerdo que permanece.'
      },
      'negro-vistas': {
        tag: 'Contraste · Carácter', eyebrow: 'Drama gráfico', ambient: 'assets/sets/negro-vistas/vajilla.webp',
        reason: 'Fondo negro profundo y vistas paisajísticas en blanco puro: clásico y moderno a la vez. Brilla en cenas especiales y sobre mesas oscuras.'
      },
      'ceilan': {
        tag: 'Oriental · Andaluza', eyebrow: 'Grecas y palmeras', ambient: 'assets/sets/ceilan/vajilla.webp',
        reason: 'Motivos florales, palmeras y grecas orientales reinterpretadas con luz andaluza. Pide exterior, sobremesa larga y ganas de mirar el plato.'
      },
      'oaxaca': {
        tag: 'Colorista · Tropical', eyebrow: 'Edición de autor', ambient: 'assets/mesa_aurora_oaxaca.webp',
        reason: 'Aves exóticas, vegetación tropical y color contemporáneo sobre tradición cerámica. Para mesas de exterior donde la vajilla es la fiesta.'
      },
      'negro-vistas-ash-blue': {
        tag: 'De autor · Azul', eyebrow: 'Aaron Stewart Home', ambient: 'assets/sets/negro-vistas-ash-blue/vajilla.webp',
        reason: 'La mirada de Aaron Stewart Home sobre uno de los decorados más sofisticados de la casa. Azul profundo para mesas que buscan conversación.'
      },
      'negro-vistas-ash-yellow': {
        tag: 'De autor · Amarillo', eyebrow: 'Aaron Stewart Home', ambient: 'assets/sets/negro-vistas-ash-yellow/vajilla.webp',
        reason: 'La fuerza de Negro Vistas reinterpretada desde una sensibilidad decorativa contemporánea. Amarillo cálido que pide madera oscura debajo.'
      },
      'flor-de-lis-azul': {
        tag: 'Francesa · Intensa', eyebrow: 'Flor de Lis', ambient: 'assets/sets/flor-de-lis-azul/vajilla.webp',
        reason: 'Un decorado de inspiración francesa con azul intenso sobre loza fina sevillana. Estructura y presencia para una comida con mantel.'
      },
      'flor-de-lis-rosa': {
        tag: 'Cálida · Delicada', eyebrow: 'Flor de Lis', ambient: 'assets/sets/flor-de-lis-rosa/vajilla.webp',
        reason: 'La flor de lis en un tono rosado, luminoso y delicado, lleno de calidez. Pide luz de mañana y mesas sin prisa.'
      },
      'viejo-molino': {
        tag: 'Rural · Cálida', eyebrow: 'Archivo de la casa', ambient: 'assets/sets/viejo-molino/vajilla.webp',
        reason: 'Una escena rural evocadora en tonos tierra, ocres y azules suaves. La mesa de campo bien puesta: natural, cálida y sin esfuerzo.'
      }
    };

    /* Merge del catálogo real. Una colección sin datos vivos (despublicada,
       vacía o con el handle renombrado) se cae del pool de candidatos. */
    var LIVE = window.__VT_COLLECTIONS || {};
    Object.keys(COLLECTIONS).forEach(function (h) {
      var live = LIVE[h];
      if (!live) { delete COLLECTIONS[h]; return; }
      var c = COLLECTIONS[h];
      c.name = live.name;
      c.collectionUrl = live.url;
      c.products = live.products || [];
      c.vajilla = live.vajilla || [];
      c.plate = c.products[0] ? c.products[0].img : c.ambient;
      // Imagen grande: bodegón de la vajilla > imagen de la colección > respaldo editorial.
      c.ambient = resolve('assets/sets/' + h + '/vajilla.webp') || live.image || c.ambient;
    });

    /* Matriz de afinidad: respuesta → peso por colección. Curación editorial,
       hardcodeada a propósito. Invariante: toda opción de QUESTIONS aparece
       aquí, si no esa pregunta deja de mover el resultado. Los pesos de
       flor-lis, vistas-stewart y viejo-molino son nuevos (no existían en el
       mockup) y salen de la descripción real de cada colección. */
    /* Matriz de afinidad: respuesta → peso por colección. Curación editorial,
       hardcodeada a propósito. Invariante: toda opción de QUESTIONS aparece
       aquí, si no esa pregunta deja de mover el resultado. Los pesos salen de
       la descripción real de cada colección en el admin; los de Bellavista,
       Ceilán, Flor Lis, Vistas A. Stewart y Viejo Molino no existían en el
       mockup y están pendientes de validar por la casa. */
    /* Matriz de afinidad: respuesta → peso por colección. Curación editorial,
       hardcodeada a propósito. Trabaja a nivel HOJA: los padres Flor Lis y
       Vistas A. Stewart no entran, porque competirían contra sus propias
       versiones de color. Dos invariantes que verifica el check:
       toda opción de QUESTIONS reparte puntos, y toda colección llega a 4 en
       alguna respuesta (sin eso nunca batiría a quien sí lo tiene).
       Pesos derivados de la descripción real de cada colección: pendientes de
       validar por la casa. */
    var SCORE = {
      occasion: {
        desayuno:      { 'aurora-blanca': 4, 'flor-de-lis-rosa': 3, 'bellavista': 3, 'viejo-molino': 2 },
        aperitivo:     { 'oaxaca': 4, 'negro-vistas-ash-yellow': 3, 'ceilan': 3, 'ochavada-blanca': 2, 'negro-vistas-ash-blue': 2 },
        comidaFormal:  { 'flor-de-lis-azul': 4, '202-rosa': 3, 'bellavista': 2, 'aurora-blanca': 2 },
        cenaEspecial:  { 'negro-vistas': 4, 'negro-vistas-ash-blue': 3, 'ochavada-blanca': 2, 'flor-de-lis-azul': 1 }
      },
      space: {
        luminoso:      { 'flor-de-lis-rosa': 4, 'aurora-blanca': 3, 'bellavista': 3, 'ceilan': 1, 'negro-vistas-ash-blue': 1 },
        clasico:       { '202-rosa': 4, 'flor-de-lis-azul': 3, 'viejo-molino': 3, 'ceilan': 2 },
        contemporaneo: { 'ochavada-blanca': 4, 'negro-vistas': 3, 'negro-vistas-ash-yellow': 3, 'bellavista': 2 },
        jardin:        { 'ceilan': 4, 'oaxaca': 3, 'viejo-molino': 3, 'flor-de-lis-rosa': 1 }
      },
      base: {
        woodLight: { 'aurora-blanca': 2, 'ceilan': 2, 'viejo-molino': 2, 'oaxaca': 2, 'flor-de-lis-rosa': 2, 'bellavista': 1 },
        woodDark:  { 'negro-vistas-ash-yellow': 4, 'negro-vistas': 3, 'viejo-molino': 2, 'ochavada-blanca': 1 },
        stone:     { 'aurora-blanca': 3, 'ochavada-blanca': 3, 'flor-de-lis-azul': 3, 'bellavista': 2, 'negro-vistas-ash-blue': 2 },
        graphite:  { 'negro-vistas': 4, 'negro-vistas-ash-blue': 3, 'ochavada-blanca': 2, 'oaxaca': 1 }
      },
      textil: {
        none:       { 'ochavada-blanca': 3, 'bellavista': 2, 'negro-vistas': 2, 'aurora-blanca': 1 },
        linenWhite: { 'aurora-blanca': 3, 'bellavista': 3, 'flor-de-lis-rosa': 3, 'ochavada-blanca': 2, 'negro-vistas-ash-blue': 1 },
        linenBeige: { 'viejo-molino': 4, 'ceilan': 2, 'negro-vistas-ash-yellow': 2, 'aurora-blanca': 1, 'oaxaca': 1 },
        pattern:    { 'flor-de-lis-rosa': 4, 'flor-de-lis-azul': 4, 'ceilan': 3, 'oaxaca': 2, '202-rosa': 1 },
        dark:       { 'negro-vistas': 3, 'negro-vistas-ash-blue': 3, 'flor-de-lis-azul': 1, 'ochavada-blanca': 1 }
      },
      style: {
        clasico:       { '202-rosa': 4, 'flor-de-lis-azul': 3, 'viejo-molino': 2, 'ceilan': 1 },
        contemporaneo: { 'ochavada-blanca': 4, 'negro-vistas': 3, 'bellavista': 3, 'negro-vistas-ash-blue': 3, 'negro-vistas-ash-yellow': 2 },
        mediterraneo:  { 'ceilan': 4, 'oaxaca': 4, 'negro-vistas-ash-yellow': 3, 'flor-de-lis-rosa': 3, 'viejo-molino': 1 },
        sobrio:        { 'aurora-blanca': 3, 'ochavada-blanca': 3, 'bellavista': 3, 'negro-vistas': 1 }
      },
      presence: {
        sutil:        { 'aurora-blanca': 3, 'bellavista': 3, 'ochavada-blanca': 2, 'viejo-molino': 1 },
        equilibrada:  { 'bellavista': 4, 'flor-de-lis-rosa': 3, '202-rosa': 2, 'viejo-molino': 2, 'ceilan': 1, 'aurora-blanca': 1 },
        protagonista: { 'negro-vistas-ash-blue': 4, 'oaxaca': 3, 'negro-vistas': 3, 'negro-vistas-ash-yellow': 3, '202-rosa': 2 }
      }
    };

    /* Respuestas guardadas durante la sesión de la pestaña: entrar en una ficha
       de producto y volver atrás no obliga a rellenar el asesor otra vez.
       sessionStorage y no cookie: mismo alcance (la sesión) con menos código y
       sin viajar en cada petición al servidor. */
    var STORE_KEY = 'vt-mesa-answers';
    function saveAnswers() {
      try { sessionStorage.setItem(STORE_KEY, JSON.stringify(answers)); } catch (e) { /* modo privado */ }
    }
    function loadAnswers() {
      var saved;
      try { saved = JSON.parse(sessionStorage.getItem(STORE_KEY)); } catch (e) { return {}; }
      if (!saved || typeof saved !== 'object') return {};
      /* Solo hasta el primer hueco: los pasos se desbloquean en orden, y una
         respuesta que ya no existe en QUESTIONS se descarta con todo lo que va detrás. */
      var clean = {};
      for (var i = 0; i < QUESTIONS.length; i++) {
        var Q = QUESTIONS[i];
        var hit = Q.options.filter(function (o) { return o.id === saved[Q.key]; })[0];
        if (!hit) break;
        clean[Q.key] = hit.id;
      }
      return clean;
    }

    var answers = loadAnswers();
    var totalSteps = QUESTIONS.length;
    var panel = $('#wzPanel');
    var progress = $('#wzProgress');
    var stage = $('#wzStage');
    var elPhoto = $('#wzPhoto');
    var elCaption = $('#wzCaption');
    var liveSummary = $('#wzLiveSummary');
    var miniStatus = $('#wzMiniStatus');
    var stepStatus = $('#wzStepStatus');
    var resultSection = $('#result');
    var tabsWrap = $('#resultTabs');
    var cardsWrap = $('#resultCards');
    var currentPhoto = elPhoto ? elPhoto.getAttribute('src') : '';
    /* v98: en móvil el wizard muestra una pregunta por pantalla en vez del acordeón. */
    var mobileWizardIndex = 0;
    var isMobileWizard = function () { return window.matchMedia && window.matchMedia('(max-width: 760px)').matches; };

    function labelFor(key, id) {
      var Q = QUESTIONS.filter(function (q) { return q.key === key; })[0];
      var o = Q && Q.options.filter(function (x) { return x.id === id; })[0];
      return o ? o.label : id;
    }

    function iconSvg(key, id) {
      var icons = {
        occasion: {
          desayuno: '<path d="M20 50h44"/><path d="M28 50c0-10 7-18 14-18s14 8 14 18"/><path d="M31 27c5-5 17-5 22 0"/>',
          aperitivo: '<circle cx="31" cy="42" r="9"/><circle cx="53" cy="42" r="9"/><path d="M31 51v13M53 51v13M25 64h12M47 64h12"/>',
          comidaFormal: '<circle cx="42" cy="42" r="24"/><circle cx="42" cy="42" r="14"/><path d="M14 24v36M70 24v36"/>',
          cenaEspecial: '<path d="M22 62h40"/><path d="M34 62V36a8 8 0 0 1 16 0v26"/><path d="M42 21v9"/><path d="M34 22c6-5 10-5 16 0"/>'
        },
        space: {
          luminoso: '<circle cx="42" cy="42" r="12"/><path d="M42 12v10M42 62v10M12 42h10M62 42h10M21 21l7 7M56 56l7 7M63 21l-7 7M28 56l-7 7"/>',
          clasico: '<path d="M18 64h48M24 64V28h36v36"/><path d="M30 34h24M30 45h24"/><path d="M18 28h48"/>',
          contemporaneo: '<path d="M20 58h44V26H20z"/><path d="M28 34h28M28 44h18"/>',
          jardin: '<path d="M42 66V34"/><path d="M42 45c-12 0-18-8-18-18 12 0 18 8 18 18z"/><path d="M42 41c12 0 18-8 18-18-12 0-18 8-18 18z"/>'
        },
        base: {
          woodLight: '<path d="M18 30h48M18 42h48M18 54h48"/><path d="M28 24c8 8 8 36 0 44M50 20c-7 10-7 38 2 46"/>',
          woodDark: '<path d="M18 30h48M18 42h48M18 54h48"/><path d="M24 24c12 10 9 30 0 42M58 22c-10 12-9 31 0 43"/>',
          stone: '<path d="M18 28h48v30H18z"/><path d="M26 35h14M46 35h12M30 47h24"/>',
          graphite: '<rect x="20" y="24" width="44" height="36" rx="2"/><path d="M28 32h28M28 44h22"/>'
        },
        textil: {
          none: '<path d="M20 42h44"/><path d="M24 50h36"/>',
          linenWhite: '<path d="M24 20h36v44H24z"/><path d="M32 20v44M52 20v44"/>',
          linenBeige: '<path d="M22 24h40v36H22z"/><path d="M30 24c8 8 8 28 0 36M54 24c-8 8-8 28 0 36"/>',
          pattern: '<path d="M22 26h40v32H22z"/><path d="M22 34h40M22 50h40M30 26v32M46 26v32M62 26v32"/>',
          dark: '<path d="M24 22h36v40H24z"/><path d="M32 30h20M32 42h20M32 54h20"/>'
        },
        style: {
          clasico: '<path d="M42 18l6 14 15 2-11 10 3 15-13-8-13 8 3-15-11-10 15-2z"/>',
          contemporaneo: '<path d="M22 24h40v12H22zM22 48h40v12H22z"/>',
          mediterraneo: '<circle cx="42" cy="42" r="22"/><path d="M20 42c11-8 33 8 44 0"/>',
          sobrio: '<path d="M24 24h36v36H24z"/><path d="M32 32h20v20H32z"/>'
        },
        presence: {
          sutil: '<circle cx="42" cy="42" r="6"/><circle cx="42" cy="42" r="24" opacity=".35"/>',
          equilibrada: '<circle cx="42" cy="42" r="14"/><circle cx="42" cy="42" r="26"/>',
          protagonista: '<circle cx="42" cy="42" r="8"/><circle cx="42" cy="42" r="18"/><circle cx="42" cy="42" r="30"/>'
        }
      };
      var path = icons[key] && icons[key][id] ? icons[key][id] : '<circle cx="42" cy="42" r="20"/>';
      return '<svg viewBox="0 0 84 84" aria-hidden="true">' + path + '</svg>';
    }

    function optionMarkup(Q, o) {
      var media = '<span class="wz-opt-media wz-opt-lineicon">' + iconSvg(Q.key, o.id) + '</span>';
      return '<button class="wz-opt wz-opt--visual" type="button" role="radio" aria-checked="false" aria-pressed="false" data-key="' + Q.key + '" data-id="' + o.id + '">' +
        media +
        '<span class="wz-opt-copy"><b>' + o.label + '</b><small>' + (o.desc || '') + '</small></span>' +
        '<span class="wz-check" aria-hidden="true"></span>' +
        '</button>';
    }

    function buildWizard() {
      if (!panel || !progress) return;
      panel.innerHTML = '';
      progress.innerHTML = '';
      QUESTIONS.forEach(function (Q, i) {
        var step = document.createElement('section');
        step.className = 'wz-step wz-step-card';
        step.dataset.step = i;
        step.dataset.key = Q.key;
        var opts = Q.options.map(function (o) { return optionMarkup(Q, o); }).join('');
        step.innerHTML = '<div class="wz-step__head"><span class="wz-q-no">Paso ' + (i + 1) + ' de ' + totalSteps + '</span><span class="wz-step__chosen" data-chosen>Sin seleccionar</span></div>' +
          '<h3>' + Q.q + '</h3><p>' + Q.lead + '</p>' +
          '<div class="wz-options" role="radiogroup" aria-label="' + Q.q + '">' + opts + '</div>';
        panel.appendChild(step);
        var bar = document.createElement('span');
        progress.appendChild(bar);
      });
      var builder = panel.closest('.wz-builder');
      if (builder && !builder.querySelector('.wz-mobile-nav')) {
        var nav = document.createElement('div');
        nav.className = 'wz-mobile-nav';
        nav.innerHTML = '<button type="button" class="wz-mobile-prev" aria-label="Pregunta anterior">← Pregunta anterior</button><span class="wz-mobile-step"></span>';
        builder.appendChild(nav);
        nav.querySelector('.wz-mobile-prev').addEventListener('click', function () {
          mobileWizardIndex = Math.max(0, mobileWizardIndex - 1);
          renderWizard();
          scrollToMobileStep();
        });
      }
      renderWizard();
    }

    // Móvil: la vista previa es sticky y tapaba el título de la pregunta. Se deja la
    // pregunta actual justo debajo de ella en vez de subir al inicio de la sección.
    function scrollToMobileStep() {
      var step = $('.wz-step.is-mobile-current', panel);
      var preview = $('.wz-preview--redesign');
      if (!step) return;
      var offset = preview ? (parseFloat(getComputedStyle(preview).top) || 0) + preview.offsetHeight + 10 : 80;
      window.scrollTo({ top: step.getBoundingClientRect().top + window.scrollY - offset, behavior: scrollBehavior });
    }

    function firstUnansweredIndex() {
      for (var i = 0; i < QUESTIONS.length; i++) {
        if (!answers[QUESTIONS[i].key]) return i;
      }
      return totalSteps;
    }

    function isUnlocked(i) {
      if (i === 0) return true;
      return !!answers[QUESTIONS[i - 1].key];
    }

    function renderWizard() {
      var firstOpen = firstUnansweredIndex();
      var steps = $$('.wz-step', panel);
      steps.forEach(function (s, idx) {
        var Q = QUESTIONS[idx];
        var unlocked = isUnlocked(idx);
        var complete = !!answers[Q.key];
        s.classList.toggle('is-locked', !unlocked);
        s.classList.toggle('is-complete', complete);
        var desktopActive = unlocked && idx === firstOpen;
        var mobileActive = isMobileWizard() && idx === mobileWizardIndex;
        s.classList.toggle('is-active', isMobileWizard() ? mobileActive : desktopActive);
        s.classList.toggle('is-mobile-current', mobileActive);
        $$('button', s).forEach(function (btn) { btn.disabled = !unlocked; });
        $$('.wz-opt', s).forEach(function (btn) {
          var sel = answers[Q.key] === btn.dataset.id;
          btn.setAttribute('aria-pressed', sel ? 'true' : 'false');
          btn.setAttribute('aria-checked', sel ? 'true' : 'false');
        });
        var chosen = $('[data-chosen]', s);
        if (chosen) chosen.textContent = complete ? labelFor(Q.key, answers[Q.key]) : (unlocked ? 'Elige una opción' : 'Pendiente');
      });
      var bars = $$('#wzProgress span');
      bars.forEach(function (b, idx) {
        b.className = idx < firstOpen ? 'done' : (idx === firstOpen ? 'active' : '');
      });
      if (stepStatus) stepStatus.textContent = firstOpen >= totalSteps ? 'Propuesta lista' : 'Paso ' + (firstOpen + 1) + ' de ' + totalSteps;
      if (miniStatus) {
        var count = Object.keys(answers).length;
        miniStatus.textContent = count ? count + ' de ' + totalSteps + ' respuestas' : 'Sin respuestas todavía';
      }
      var mnav = container.querySelector('.wz-mobile-nav');
      if (mnav) {
        var prevBtn = mnav.querySelector('.wz-mobile-prev');
        var stepLabel = mnav.querySelector('.wz-mobile-step');
        if (prevBtn) prevBtn.disabled = mobileWizardIndex <= 0;
        if (stepLabel) stepLabel.textContent = 'Pregunta ' + (mobileWizardIndex + 1) + ' de ' + totalSteps;
      }
    }

    function getPhotoCandidates() {
      var space = answers.space || '';
      var occasion = answers.occasion || '';
      var base = answers.base || '';
      var textil = answers.textil || '';
      var style = answers.style || '';
      var presence = answers.presence || '';
      var candidates = [];

      // Future images: resolve() skips them until they ship in the asset map.
      if (space && occasion && base && textil && style && presence) {
        candidates.push(FORM_ROOT + '/06-presencia/' + space + '/' + occasion + '/' + base + '/' + textil + '/' + style + '/' + presence + '.webp');
      }
      if (space && occasion && base && textil && style) {
        candidates.push(FORM_ROOT + '/05-estilo/' + space + '/' + occasion + '/' + base + '/' + textil + '/' + style + '.webp');
      }
      // Textiles are common to all table bases. «Sin mantel» deliberately keeps step 3.
      if (space && occasion && textil && textil !== 'none') {
        candidates.push(FORM_ROOT + '/04-textil/' + space + '/' + occasion + '/' + textil + '.webp');
      }
      if (space && occasion && base) {
        candidates.push(FORM_ROOT + '/03-base/' + space + '/' + occasion + '/' + base + '.webp');
      }
      if (space && occasion) {
        candidates.push(FORM_ROOT + '/02-ocasion/' + space + '/' + occasion + '.webp');
      }
      if (space) candidates.push(FORM_ROOT + '/01-espacio/' + space + '.webp');
      candidates.push(DEFAULT_FORM_PHOTO);
      return candidates.filter(function (src, index, all) { return all.indexOf(src) === index; });
    }

    var photoRequestId = 0;
    function setPhotoCandidates(candidates) {
      if (!elPhoto || !candidates || !candidates.length) return;
      // Map logical paths through the asset bridge; unmapped (unshipped)
      // candidates are skipped so the cascade lands on the closest shipped
      // photo. The Image onload/onerror below stays as a second safety net.
      var resolved = [];
      candidates.forEach(function (u) {
        var url = resolve(u);
        if (url && resolved.indexOf(url) === -1) resolved.push(url);
      });
      if (!resolved.length) return;
      var requestId = ++photoRequestId;
      if (stage) stage.classList.add('is-loading');
      elPhoto.classList.add('is-changing');

      function tryCandidate(index) {
        if (requestId !== photoRequestId) return;
        if (index >= resolved.length) {
          elPhoto.classList.remove('is-changing');
          if (stage) stage.classList.remove('is-loading');
          return;
        }
        var src = resolved[index];
        if (src === currentPhoto) {
          elPhoto.classList.remove('is-changing');
          if (stage) stage.classList.remove('is-loading');
          return;
        }
        var next = new Image();
        next.onload = function () {
          if (requestId !== photoRequestId) return;
          currentPhoto = src;
          elPhoto.src = src;
          requestAnimationFrame(function () {
            elPhoto.classList.remove('is-changing');
            if (stage) stage.classList.remove('is-loading');
          });
        };
        next.onerror = function () { tryCandidate(index + 1); };
        next.src = src;
      }
      tryCandidate(0);
    }

    function updatePreview() {
      if (!stage) return;
      stage.dataset.style = answers.style || '';
      stage.dataset.presence = answers.presence || '';
      stage.dataset.base = answers.base || '';
      stage.dataset.textil = answers.textil || '';
      setPhotoCandidates(getPhotoCandidates());

      var labels = [];
      ['space', 'occasion', 'base', 'textil', 'style', 'presence'].forEach(function (key) {
        if (answers[key]) labels.push(labelFor(key, answers[key]));
      });
      if (elCaption) {
        elCaption.innerHTML = labels.length ? '<b>Tu mesa</b> · ' + labels.join(' · ') : '<b>Tu mesa</b> · responde para verla tomar forma';
      }
      if (liveSummary) {
        liveSummary.innerHTML = labels.length ? labels.map(function (t) { return '<span>' + t + '</span>'; }).join('') : '<span>Selecciona el espacio para empezar</span>';
      }
    }

    if (panel) {
      mobileWizardIndex = Math.min(totalSteps - 1, firstUnansweredIndex());
      buildWizard();
      if (firstUnansweredIndex() >= totalSteps) buildResult(true);
      panel.addEventListener('click', function (e) {
        var opt = e.target.closest('.wz-opt');
        if (!opt || opt.disabled) return;
        var idx = QUESTIONS.findIndex(function (q) { return q.key === opt.dataset.key; });
        var changed = answers[opt.dataset.key] !== opt.dataset.id;
        if (changed && idx > -1) {
          for (var i = idx + 1; i < QUESTIONS.length; i++) delete answers[QUESTIONS[i].key];
        }
        answers[opt.dataset.key] = opt.dataset.id;
        saveAnswers();
        if (resultSection) resultSection.hidden = true;
        if (isMobileWizard()) mobileWizardIndex = Math.min(totalSteps - 1, idx + 1);
        updatePreview();
        renderWizard();
        var nextIdx = firstUnansweredIndex();
        var nextStep = nextIdx < totalSteps ? $('.wz-step[data-step="' + nextIdx + '"]', panel) : null;
        if (nextStep && !isMobileWizard()) {
          window.setTimeout(function () { nextStep.scrollIntoView({ behavior: scrollBehavior, block: window.innerWidth <= 1180 ? 'center' : 'nearest' }); }, 160);
        }
        if (isMobileWizard()) window.setTimeout(scrollToMobileStep, 100);
        if (nextIdx >= totalSteps) window.setTimeout(buildResult, 320);
      });
    }

    function recommend() {
      var pool = Object.keys(COLLECTIONS);
      var totals = {};
      var max = 0;
      pool.forEach(function (k) { totals[k] = 0; });
      Object.keys(answers).forEach(function (key) {
        var map = SCORE[key] && SCORE[key][answers[key]];
        if (!map) return;
        var best = 0;
        Object.keys(map).forEach(function (col) {
          if (totals[col] === undefined) return;   // colección fuera del pool
          totals[col] += map[col];
          if (map[col] > best) best = map[col];
        });
        max += best;                               // techo alcanzable con ESTAS respuestas
      });
      return pool.slice().sort(function (a, b) {
        if (totals[b] !== totals[a]) return totals[b] - totals[a];
        return pool.indexOf(a) - pool.indexOf(b);  // desempate estable
      }).slice(0, 3).map(function (id) {
        var score = totals[id] || 0;
        // Reescalado afín a la banda 55-99: monótono con la puntuación y sin
        // recortes (un suelo duro hacía que dos scores distintos mostrasen el
        // mismo %). ponytail: cambiar por Math.round(score / max * 100) si el
        // cliente prefiere el porcentaje crudo sobre el máximo alcanzable.
        var pct = max ? Math.round(55 + 44 * score / max) : 0;
        return { id: id, score: score, pct: pct };
      });
    }

    function animateMatchNumbers() {
      $$('.match-number', cardsWrap).forEach(function (el) {
        var target = parseInt(el.getAttribute('data-match') || '0', 10);
        if (reducedMotion) { el.textContent = target + '%'; return; }
        var start = null;
        var duration = 1150;
        function tick(ts) {
          if (!start) start = ts;
          var p = clamp((ts - start) / duration, 0, 1);
          var eased = 1 - Math.pow(1 - p, 3);
          el.textContent = Math.round(target * eased) + '%';
          if (p < 1) requestAnimationFrame(tick);
        }
        requestAnimationFrame(tick);
      });
    }

    /* Los títulos y precios vienen del catálogo del comercio: escapar antes de
       meterlos en atributos y en el HTML que se inyecta. */
    function esc(t) {
      return String(t == null ? '' : t).replace(/[&<>"]/g, function (m) {
        return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[m];
      });
    }

    function buildResult(restored) {
      if (!resultSection || !tabsWrap || !cardsWrap) return;
      var top3 = recommend();
      var answerSummary = ['space', 'occasion', 'base', 'textil', 'style', 'presence'].map(function (key) {
        return answers[key] ? '<span>' + labelFor(key, answers[key]) + '</span>' : '';
      }).join('');
      tabsWrap.innerHTML = top3.map(function (item, i) {
        var c = COLLECTIONS[item.id];
        return '<button class="result-tab" role="tab" data-target="' + item.id + '" aria-selected="' + (i === 0) + '"><span class="rank">0' + (i + 1) + '</span><span>' + esc(c.name) + '</span></button>';
      }).join('');
      cardsWrap.innerHTML = '<div class="result-summary">' + answerSummary + '</div>' + top3.map(function (item, i) {
        var c = COLLECTIONS[item.id];
        var prods = c.products.map(function (p) {
          var href = p.url ? ' href="' + esc(p.url) + '"' : '';
          return '<a class="result-product"' + href + '><div class="result-product__img"><img src="' + (resolve(p.img) || p.img) + '" alt="' + esc(p.n) + '" loading="lazy"></div><b>' + esc(p.n) + '</b><small>' + esc(p.p) + '</small></a>';
        }).join('');
        // Un botón por variante de la vajilla completa ("42 P." → "Comprar vajilla 42 piezas").
        var buy = c.vajilla.map(function (v) {
          var label = 'Comprar vajilla ' + String(v.t).replace(/\s*P\.?$/i, ' piezas');
          return '<button class="ghost-btn" type="button" data-add="' + esc(c.name) + '" data-variant-id="' + esc(v.vid) + '">' + esc(label) + '</button>';
        }).join('');
        return '<article class="result-card result-card--editorial' + (i === 0 ? ' active' : '') + '" data-card="' + item.id + '">' +
          '<div class="result-ambient"><span class="result-ambient__tag">Recomendación 0' + (i + 1) + '</span><img src="' + (resolve(c.ambient) || c.ambient) + '" alt="Carátula de la vajilla ' + esc(c.name) + '" loading="lazy"></div>' +
          '<div class="result-body"><span class="eyebrow">' + c.eyebrow + '</span><h3>' + esc(c.name) + '</h3><div class="result-match"><b>Ajuste visual</b><span class="match-number" data-match="' + item.pct + '">0%</span></div><p class="result-reason">' + c.reason + '</p><div class="result-products">' + prods + '</div><div class="result-ctas"><a class="ghost-btn solid" href="' + c.collectionUrl + '">Ver colección</a>' + buy + '</div></div>' +
          '</article>';
      }).join('');
      resultSection.hidden = false;
      resultSection.classList.add('is-visible');
      animateMatchNumbers();
      if (!restored) resultSection.scrollIntoView({ behavior: scrollBehavior, block: 'start' });
    }

    if (resultSection) {
      resultSection.addEventListener('click', function (e) {
        var tab = e.target.closest('.result-tab');
        if (!tab) return;
        var id = tab.dataset.target;
        $$('.result-tab', tabsWrap).forEach(function (t) { t.setAttribute('aria-selected', t === tab ? 'true' : 'false'); });
        $$('.result-card', cardsWrap).forEach(function (card) { card.classList.toggle('active', card.dataset.card === id); });
      });
    }

    /* ---------- Add to cart (real /cart/add.js, no fake counter) ---------- */
    var toast = $('#vtToast');
    function showToast(name, msg) {
      if (!toast) return;
      toast.textContent = name + (msg || ' · añadido a la cesta');
      toast.classList.add('show');
      clearTimeout(showToast._t);
      showToast._t = setTimeout(function () { toast.classList.remove('show'); }, 2200);
    }
    function openCartDrawer() {
      var toggle = document.querySelector('[data-cart-toggle]');
      if (toggle) { toggle.click(); }              // reuses cart-drawer open+refresh
    }
    container.addEventListener('click', function (e) {
      var add = e.target.closest('[data-add]');
      if (!add) return;
      e.preventDefault();
      // Build the /cart/add.js body: a multi-item pack (data-items) or a single variant.
      var body = null;
      var itemsAttr = add.getAttribute('data-items');
      if (itemsAttr) {
        try {
          var items = JSON.parse(itemsAttr);
          if (items && items.length) { body = { items: items }; }
        } catch (err) { body = null; }
      }
      if (!body) {
        var vid = add.getAttribute('data-variant-id');
        if (vid) { body = { id: vid, quantity: 1 }; }
      }
      if (!body) { showToast(add.dataset.add); return; }   // demo card w/o real product → toast only
      if (add.dataset.busy) return;
      add.dataset.busy = '1';
      add.setAttribute('disabled', 'disabled');
      fetch('/cart/add.js', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' },
        body: JSON.stringify(body)
      }).then(function (r) {
        if (!r.ok) { throw new Error('add failed'); }
        return r.json();
      }).then(function () {
        showToast(add.dataset.add);
        openCartDrawer();
      }).catch(function () {
        showToast(add.dataset.add, ' · no se pudo añadir');
      }).then(function () {
        delete add.dataset.busy;
        add.removeAttribute('disabled');
      });
    });

    /* ---------- Smooth-scroll CTAs ---------- */
    $$('[data-scroll-to]').forEach(function (a) {
      a.addEventListener('click', function (e) {
        var target = $(a.dataset.scrollTo);
        if (target) { e.preventDefault(); target.scrollIntoView({ behavior: scrollBehavior, block: 'start' }); }
      });
    });

    updatePreview();
  }

  function initAll() {
    document.querySelectorAll('.vt-page').forEach(boot);
  }
  initAll();
  document.addEventListener('shopify:section:load', initAll);
})();
