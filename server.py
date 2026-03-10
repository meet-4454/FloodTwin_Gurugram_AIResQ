from flask import Flask, send_from_directory
from waitress import serve
import os

app = Flask(__name__)

HTML_CONTENT="""
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>3D Flood Twin</title>

  <!-- Mappls Map SDK -->
  <script src="https://apis.mappls.com/advancedmaps/api/07ed2c801ad7e2fd64b3fdffd084b0be/map_sdk?v=3.0&layer=vector"></script>
  <!-- Three.js r128 -->
  <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>

  <style>
    /* ── RESET ── */
    *{box-sizing:border-box;margin:0;padding:0}
    body{overflow:hidden;font-family:'Segoe UI',system-ui,sans-serif;background:#f8fafc;color:#1e293b}
    #map{width:100vw;height:100vh}

    /* ── SIDEBAR ── */
    #sidebar{
      position:absolute;top:0;left:0;width:20vw;min-width:320px;height:100vh;
      background:linear-gradient(180deg,#ffffff 0%,#f1f5f9 100%);
      border-right:2px solid #5298A9;z-index:1000;
      display:flex;flex-direction:column;
      transition:transform .30s cubic-bezier(.4,0,.2,1);
      overflow-y:auto;overflow-x:hidden;
      scrollbar-width:thin;scrollbar-color:#5298A9 transparent;
      box-shadow:4px 0 12px rgba(82,152,169,.15)
    }
    #sidebar.collapsed{transform:translateX(-100%)}
    #sidebar::-webkit-scrollbar{width:8px}
    #sidebar::-webkit-scrollbar-thumb{background:#B1DEE2;border-radius:4px}

    /* ── TITLE ── */
    #titleBar{padding:24px 24px 18px;flex-shrink:0;border-bottom:1px solid #e2e8f0;text-align:center}
    #titleBar h1{font-size:28px;font-weight:800;color:#264351;letter-spacing:2px;text-transform:uppercase;line-height:1.1;margin-bottom:6px}
    #titleBar p{font-size:13px;font-weight:400;color:#64748b;line-height:1.4;letter-spacing:.2px}

    /* ── SEARCH ── */
    #searchWrap{padding:16px 24px 10px;flex-shrink:0;position:relative}
    #searchRow{position:relative}
    #searchInput{
      width:100%;height:50px;background:#fff;border:2px solid #B1DEE2;border-radius:10px;
      padding:0 14px 0 42px;font-size:15px;font-family:inherit;color:#1e293b;outline:none;
      box-shadow:0 2px 8px rgba(82,152,169,.1);transition:border-color .2s,box-shadow .2s
    }
    #searchInput:focus{border-color:#5298A9;box-shadow:0 0 0 3px rgba(82,152,169,.15)}
    #searchInput::placeholder{color:#94a3b8}
    #srchIcon{position:absolute;left:13px;top:50%;transform:translateY(-50%);font-size:16px;color:#5298A9;pointer-events:none;z-index:2}
    #searchSuggestions{
      position:absolute!important;width:100%!important;top:100%!important;left:0!important;
      background:#fff!important;border:2px solid #B1DEE2!important;border-top:none!important;
      border-radius:0 0 10px 10px!important;z-index:9999!important;max-height:280px!important;
      overflow-y:auto!important;box-shadow:0 8px 24px rgba(82,152,169,.2)!important;
      list-style:none!important;margin:0!important;padding:0!important;display:none
    }
    #searchSuggestions li{
      padding:11px 15px!important;font-size:13px!important;color:#1e293b!important;
      cursor:pointer!important;border-bottom:1px solid #f1f5f9!important;line-height:1.4!important
    }
    #searchSuggestions li:last-child{border-bottom:none!important}
    #searchSuggestions li:hover{background:#eef7f9!important;color:#264351!important}

    /* ── COLLAPSE BTN ── */
    #collapseBtn{
      position:absolute;top:50%;right:-20px;transform:translateY(-50%);
      width:40px;height:40px;background:#fff;border:2px solid #5298A9;border-radius:50%;
      color:#5298A9;font-size:20px;cursor:pointer;display:flex;align-items:center;justify-content:center;
      z-index:1001;box-shadow:2px 2px 8px rgba(82,152,169,.25);transition:background .2s
    }
    #collapseBtn:hover{background:#f1f5f9}
    #sidebar.collapsed #collapseBtn{right:-42px}

    /* ── PANEL ── */
    .panel{margin:0 24px 12px;background:#fff;border:2px solid #B1DEE2;border-radius:12px;padding:24px 20px;flex-shrink:0;box-shadow:0 2px 8px rgba(82,152,169,.08)}
    .panel-header{display:flex;align-items:center;justify-content:space-between;margin-bottom:18px}
    .panel-header-left{display:flex;align-items:center;gap:12px}
    .panel-icon{font-size:20px;color:#5298A9;width:28px;height:28px;display:flex;align-items:center;justify-content:center}
    .panel-title{font-size:18px;font-weight:700;color:#264351;letter-spacing:.3px}
    .panel-badge{font-size:13px;font-weight:700;background:#B1DEE2;color:#264351;padding:4px 12px;border-radius:12px;letter-spacing:.4px}
    .panel-divider{height:2px;background:linear-gradient(to right,transparent,#B1DEE2,transparent);margin:4px 24px 8px;flex-shrink:0}

    /* ── TIME BOX ── */
    #timeBox{background:#f8fafc;border:2px solid #B1DEE2;border-radius:10px;padding:12px 16px;text-align:center;margin-bottom:16px}
    #timeBoxLabel{font-size:11px;color:#64748b;text-transform:uppercase;letter-spacing:1px;margin-bottom:4px;font-weight:600}
    #timeDisplay{font-size:18px;font-weight:700;color:#264351;font-variant-numeric:tabular-nums}

    /* ── TIME SLIDER ── */
    #timeSlider{-webkit-appearance:none;appearance:none;width:100%;height:8px;border-radius:4px;background:#e2e8f0;outline:none;cursor:pointer;margin-bottom:4px}
    #timeSlider::-webkit-slider-thumb{-webkit-appearance:none;width:22px;height:22px;background:#5298A9;border:3px solid #fff;border-radius:50%;cursor:pointer;box-shadow:0 2px 8px rgba(82,152,169,.4)}

    /* ── TRANSPORT BTNS ── */
    #transportBtns{display:flex;gap:10px;justify-content:center;margin-top:16px}
    .tbtn{width:46px;height:46px;border-radius:50%;background:#fff;border:2px solid #B1DEE2;color:#5298A9;font-size:18px;cursor:pointer;display:flex;align-items:center;justify-content:center;transition:all .2s}
    .tbtn:hover{background:#f8fafc;border-color:#5298A9;transform:scale(1.05)}
    .tbtn.active{background:#5298A9;border-color:#5298A9;color:#fff}

    /* ── SPEED PILLS ── */
    #speedPills{display:flex;gap:8px}
    .speed-pill{flex:1;padding:10px 0;border-radius:8px;background:#fff;border:2px solid #B1DEE2;color:#5298A9;font-size:13px;font-weight:700;text-align:center;cursor:pointer;transition:all .2s}
    .speed-pill:hover{border-color:#5298A9;background:#f8fafc}
    .speed-pill.active{background:#5298A9;border-color:#5298A9;color:#fff}

    /* ── OPACITY ── */
    .opacity-row{display:flex;align-items:center;margin-bottom:10px}
    .opacity-dot{width:13px;height:13px;border-radius:50%;margin-right:10px;flex-shrink:0;border:2px solid #5298A9}
    .opacity-label{font-size:14px;color:#264351;flex:1;font-weight:600}
    .opacity-value{font-size:13px;color:#5298A9;font-weight:700;width:40px;text-align:right}
    .opacity-slider{-webkit-appearance:none;appearance:none;width:100%;height:6px;border-radius:3px;background:#e2e8f0;outline:none;cursor:pointer;margin-top:8px}
    .opacity-slider::-webkit-slider-thumb{-webkit-appearance:none;width:20px;height:20px;background:#5298A9;border:3px solid #fff;border-radius:50%;cursor:pointer}

    /* ── CRITICAL ASSETS ── */
    #assetGrid{display:grid;grid-template-columns:1fr;gap:8px}
    .asset-pill{
      display:flex;align-items:center;gap:12px;padding:12px 14px;border-radius:10px;
      background:#fff;border:2px solid #B1DEE2;cursor:pointer;transition:all .2s;user-select:none;min-height:46px
    }
    .asset-pill:hover{border-color:#5298A9;background:#f8fafc;transform:translateY(-1px);box-shadow:0 3px 8px rgba(82,152,169,.15)}
    .asset-pill.on{border-color:var(--pill-accent);background:color-mix(in srgb,var(--pill-accent) 8%,#fff);box-shadow:0 0 10px color-mix(in srgb,var(--pill-accent) 20%,transparent)}
    .pill-icon{font-size:17px;flex-shrink:0;width:22px;height:22px;display:flex;align-items:center;justify-content:center}
    .pill-label{font-size:13px;font-weight:700;color:#5298A9;flex:1;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
    .asset-pill.on .pill-label{color:#264351}
    .pill-count{margin-left:auto;font-size:11px;font-weight:700;background:#e2e8f0;color:#64748b;padding:2px 8px;border-radius:10px;flex-shrink:0;min-width:24px;text-align:center;display:none}
    .asset-pill.on .pill-count{display:block;background:color-mix(in srgb,var(--pill-accent) 15%,#fff);color:var(--pill-accent)}
    @keyframes skel{0%,100%{opacity:.2}50%{opacity:.45}}
    .asset-skel{height:46px;border-radius:10px;background:#e2e8f0;animation:skel 1.4s ease infinite}

    /* ── OSM MARKERS (DOM-based, since Mappls doesn't use maplibregl.Marker) ── */
    .osm-marker{
      width:32px;height:32px;border-radius:50% 50% 50% 4px;border:3px solid #fff;
      display:flex;align-items:center;justify-content:center;font-size:15px;cursor:pointer;
      box-shadow:0 3px 10px rgba(0,0,0,.3);position:absolute;z-index:500;
      transform:translate(-50%,-100%);transition:transform .15s;user-select:none
    }
    .osm-marker:hover{transform:translate(-50%,-100%) scale(1.15)}

    /* ── POPUP ── */
    .osm-popup{
      position:absolute;background:rgba(255,255,255,.98);border:2px solid #5298A9;
      border-radius:12px;color:#264351;padding:12px 14px;font-size:13px;
      box-shadow:0 4px 20px rgba(82,152,169,.3);max-width:220px;z-index:3000;pointer-events:auto
    }
    .popup-name{font-weight:700;color:#264351;margin-bottom:3px;font-size:14px;padding-right:18px}
    .popup-type{font-size:11px;color:#5298A9;text-transform:uppercase;letter-spacing:.5px;font-weight:700}
    .popup-addr{font-size:11px;color:#64748b;margin-top:5px;padding-top:5px;border-top:1px solid #e2e8f0}
    .popup-close{position:absolute;top:5px;right:8px;background:none;border:none;font-size:15px;cursor:pointer;color:#94a3b8}
    .popup-close:hover{color:#264351}

    /* ── LEGEND ── */
    #legend{
      position:absolute;top:28px;right:28px;
      background:rgba(255,255,255,0.95);
      backdrop-filter:blur(8px);border:2px solid #5298A9;border-radius:14px;padding:24px 28px;
      z-index:999;min-width:240px;box-shadow:0 4px 20px rgba(82,152,169,.2)
    }
    .legend-header{display:flex;align-items:center;gap:12px;margin-bottom:20px}
    .legend-icon{font-size:22px;color:#5298A9}
    .legend-title{font-size:19px;font-weight:700;color:#264351;letter-spacing:.3px}
    .legend-row{display:flex;align-items:center;margin-bottom:14px;gap:14px}
    .legend-row:last-child{margin-bottom:0}
    .legend-swatch{width:48px;height:24px;border-radius:6px;flex-shrink:0;border:1px solid #B1DEE2}
    .legend-range{font-size:16px;color:#264351;flex:1;font-weight:600;min-width:80px}
    .legend-severity{font-size:14px;font-weight:700;color:#5298A9;text-transform:uppercase;letter-spacing:.5px;min-width:85px;text-align:right}

    /* ── LOADING OVERLAY ── */
    #loadingOverlay{position:fixed;inset:0;background:rgba(255,255,255,.95);display:flex;align-items:center;justify-content:center;z-index:10000;flex-direction:column}
    #loadingOverlay.hidden{display:none}
    .spinner{border:5px solid #e2e8f0;border-top:5px solid #5298A9;border-radius:50%;width:50px;height:50px;animation:spin .8s linear infinite;margin:0 auto 20px}
    @keyframes spin{to{transform:rotate(360deg)}}
    .loader{text-align:center;color:#264351}
    .loader h2{font-size:24px;margin-top:16px;font-weight:700}
    #loadingProgress{font-size:14px;color:#64748b;margin-top:8px;font-weight:600}

    /* ── CHUNK TOAST ── */
    #chunkLoadingIndicator{
      position:absolute;bottom:70px;right:28px;background:rgba(255,255,255,.95);
      border:2px solid #5298A9;color:#5298A9;padding:10px 16px;border-radius:10px;
      font-size:14px;z-index:999;display:none;font-weight:600;box-shadow:0 4px 12px rgba(82,152,169,.2)
    }

    /* ── HAMBURGER ── */
    #hamburgerBtn{
      position:fixed;top:22px;left:22px;width:48px;height:48px;z-index:1002;
      background:rgba(255,255,255,.95);backdrop-filter:blur(6px);border:2px solid #5298A9;
      border-radius:12px;cursor:pointer;display:flex;flex-direction:column;
      align-items:center;justify-content:center;gap:6px;transition:all .2s;
      box-shadow:0 3px 12px rgba(82,152,169,.25)
    }
    #hamburgerBtn:hover{background:#f8fafc;transform:scale(1.05)}
    #hamburgerBtn span{display:block;width:24px;height:3px;background:#5298A9;border-radius:2px;transition:transform .25s,opacity .25s}
    #hamburgerBtn.open{opacity:0;pointer-events:none}

    /* ── SEARCH PIN ── */
    .search-pin{
      position:absolute;z-index:600;transform:translate(-50%,-100%);font-size:28px;
      pointer-events:none;filter:drop-shadow(0 3px 6px rgba(82,152,169,.5));animation:pinDrop .3s ease-out
    }
    @keyframes pinDrop{
      from{transform:translate(-50%,-130%);opacity:0}
      to{transform:translate(-50%,-100%);opacity:1}
    }
  </style>
</head>
<body>

<button id="hamburgerBtn" class="open" aria-label="Toggle sidebar">
  <span></span><span></span><span></span>
</button>

<div id="loadingOverlay">
  <div class="loader">
    <div class="spinner"></div>
    <h2>Initializing Flood Visualization…</h2>
    <p id="loadingProgress">0% – Loading metadata…</p>
  </div>
</div>

<div id="map"></div>
<div id="chunkLoadingIndicator">Loading timestep data…</div>

<!-- ════ SIDEBAR ════ -->
<div id="sidebar">
  <button id="collapseBtn" title="Toggle sidebar">‹</button>

  <div id="titleBar">
    <h1>Flood Twin</h1>
    <p>3D Immersive Flood Visualization Engine</p>
  </div>

  <!-- Search -->
  <div id="searchWrap">
    <div id="searchRow">
      <span id="srchIcon">🔍</span>
      <input id="searchInput" type="text" placeholder="Search location… (or click map)" autocomplete="off" spellcheck="false">
      <ul id="searchSuggestions"></ul>
    </div>
  </div>

  <!-- Time Control -->
  <div class="panel">
    <div class="panel-header">
      <div class="panel-header-left">
        <div class="panel-icon">🕐</div>
        <span class="panel-title">Time Control</span>
      </div>
    </div>
    <div id="timeBox">
      <div id="timeBoxLabel">Current Time</div>
      <div id="timeDisplay">09-July-2025 00:00:00</div>
    </div>
    <input type="range" id="timeSlider" min="0" max="336" value="0" step="1">
    <div id="transportBtns">
      <button class="tbtn" id="resetBtn" title="Reset">↺</button>
      <button class="tbtn" id="prevBtn"  title="Previous">⏮</button>
      <button class="tbtn" id="playBtn"  title="Play">▶</button>
      <button class="tbtn" id="nextBtn"  title="Next">⏭</button>
    </div>
  </div>

  <div class="panel-divider"></div>

  <!-- Playback Speed -->
  <div class="panel">
    <div class="panel-header">
      <div class="panel-header-left">
        <div class="panel-icon">🔄</div>
        <span class="panel-title">Playback Speed</span>
      </div>
    </div>
    <div id="speedPills">
      <div class="speed-pill" data-speed="1000">0.5×</div>
      <div class="speed-pill active" data-speed="500">Normal</div>
      <div class="speed-pill" data-speed="250">2×</div>
      <div class="speed-pill" data-speed="125">4×</div>
    </div>
  </div>

  <div class="panel-divider"></div>

  <!-- Layer Opacity -->
  <div class="panel">
    <div class="panel-header">
      <div class="panel-header-left">
        <div class="panel-icon">☰</div>
        <span class="panel-title">Layer Opacity</span>
      </div>
    </div>
    <div class="opacity-row">
      <div class="opacity-dot" style="background:#5298A9"></div>
      <span class="opacity-label">Flood Layer</span>
      <span class="opacity-value" id="floodOpVal">70%</span>
    </div>
    <input type="range" class="opacity-slider" id="floodOpSlider" min="0" max="100" value="70">
  </div>

  <div class="panel-divider"></div>

  <!-- Critical Assets -->
  <div class="panel" style="margin-bottom:32px">
    <div class="panel-header">
      <div class="panel-header-left">
        <div class="panel-icon">📍</div>
        <span class="panel-title">Critical Assets</span>
      </div>
      <span class="panel-badge" id="assetBadge">Loading…</span>
    </div>
    <div id="assetGrid">
      <div class="asset-skel"></div>
      <div class="asset-skel"></div>
      <div class="asset-skel"></div>
      <div class="asset-skel"></div>
      <div class="asset-skel"></div>
      <div class="asset-skel"></div>
    </div>
  </div>
</div>

<!-- LEGEND -->
<div id="legend">
  <div class="legend-header">
    <span class="legend-icon">💧</span>
    <span class="legend-title">Flood Depth</span>
  </div>
  <div class="legend-row">
    <div class="legend-swatch" style="background:linear-gradient(135deg,#B1DEE2,#6BC3D2);"></div>
    <span class="legend-range">&lt; 0.5m</span>
    <span class="legend-severity">Low</span>
  </div>
  <div class="legend-row">
    <div class="legend-swatch" style="background:linear-gradient(135deg,#64B8C1,#5298A9);"></div>
    <span class="legend-range">0.5–1m</span>
    <span class="legend-severity">Moderate</span>
  </div>
  <div class="legend-row">
    <div class="legend-swatch" style="background:linear-gradient(135deg,#5298A9,#49879A);"></div>
    <span class="legend-range">1–2m</span>
    <span class="legend-severity">High</span>
  </div>
  <div class="legend-row">
    <div class="legend-swatch" style="background:linear-gradient(135deg,#49879A,#264351);"></div>
    <span class="legend-range">&gt; 2m</span>
    <span class="legend-severity">Severe</span>
  </div>
</div>

<script>
(function(){
'use strict';

/* ══════════════════════════════════════════════════════════
   CONFIG
══════════════════════════════════════════════════════════ */
const CHUNK_SIZE    = 10;
const TOTAL_CHUNKS  = 34;
const MAX_CACHED    = 3;
const TOTAL_STEPS   = 336;
const REF_LAT       = 28.448;
const REF_LNG       = 77.027;
const NOM_UA        = 'FloodTwin/1.0 (research project)';
const MONTHS        = ['January','February','March','April','May','June','July',
                       'August','September','October','November','December'];

/* ══════════════════════════════════════════════════════════
   STATE
══════════════════════════════════════════════════════════ */
let map, glMap, scene, camera, renderer, modelTransform;
let currentStep = 0, isPlaying = false, playInterval = null, playSpeed = 500;
let floodOpacity = 0.70, depthScale = 1.0;
let waterMeshes = [], polygonCount = 0, coordinatesBuffer = null;
const chunkCache = new Map(), chunkQueue = new Set();

const sleep = ms => new Promise(r => setTimeout(r, ms));
const esc   = s  => String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');

/* ══════════════════════════════════════════════════════════
   CRITICAL ASSETS
   — Exact replication of the reference MapLibre code's
     OSM Overpass fetch, sequential loader, DOM markers
     and toggle pills. Only the marker placement is adapted
     for Mappls (which uses map.project() instead of
     maplibregl.Marker, since the Mappls SDK wraps MapLibre
     but doesn't expose its Marker class).
══════════════════════════════════════════════════════════ */

const ASSET_CATS = [
  { key:'hospital',     icon:'🏥', label:'Hospitals',      accent:'#ef4444', tags:'["amenity"="hospital"]'     },
  { key:'school',       icon:'🏫', label:'Schools',        accent:'#10b981', tags:'["amenity"="school"]'       },
  { key:'college',      icon:'🎓', label:'Colleges',       accent:'#06b6d4', tags:'(["amenity"="university"];["amenity"="college"];)' },
  { key:'fire_station', icon:'🚒', label:'Fire Stations',  accent:'#f43f5e', tags:'["amenity"="fire_station"]' },
  { key:'police',       icon:'🚔', label:'Police',         accent:'#6366f1', tags:'["amenity"="police"]'       },
  { key:'pharmacy',     icon:'💊', label:'Pharmacies',     accent:'#14b8a6', tags:'["amenity"="pharmacy"]'     }
];

/* Per-category runtime state */
const catMarkers  = {};   // key → [{el, lat, lng, posUpdate}]
const catEnabled  = {};   // key → bool
const catFeatures = {};   // key → GeoJSON-like feature array
ASSET_CATS.forEach(c => { catMarkers[c.key]=[]; catEnabled[c.key]=false; catFeatures[c.key]=null; });

/* ── Build sidebar pills (identical HTML to reference) ── */
function renderAssetPills() {
  const grid = document.getElementById('assetGrid');
  grid.innerHTML = ASSET_CATS.map(c => `
    <div class="asset-pill" data-cat="${c.key}" style="--pill-accent:${c.accent}">
      <span class="pill-icon">${c.icon}</span>
      <span class="pill-label">${c.label}</span>
      <span class="pill-count" id="cnt-${c.key}">0</span>
    </div>`).join('');

  grid.querySelectorAll('.asset-pill').forEach(pill => {
    pill.addEventListener('click', () => {
      const key = pill.dataset.cat;
      catEnabled[key] = !catEnabled[key];
      pill.classList.toggle('on', catEnabled[key]);
      catEnabled[key] ? showMarkers(key) : hideMarkers(key);
    });
  });
}

/* ── Show markers for a category ── */
function showMarkers(key) {
  if (catFeatures[key] && catFeatures[key].length > 0) {
    addMarkers(key, catFeatures[key]);
    return;
  }
  /* still loading — will be placed by loadAllAssets when data arrives */
}

/* ── Remove all DOM markers for a category ── */
function hideMarkers(key) {
  catMarkers[key].forEach(m => m.el.remove());
  catMarkers[key] = [];
  document.querySelectorAll('.osm-popup').forEach(p => p.remove());
}

/* ── Place DOM markers on the Mappls map ──
   Mappls's internal map object exposes map.project({lat,lng}) which
   returns {x,y} pixel coords — the same approach used by our search
   pin. We track each marker so syncMarkers() can reposition them on
   every camera movement (move, zoom, pitch, rotate).                  */
function addMarkers(key, features) {
  hideMarkers(key);
  const cat   = ASSET_CATS.find(c => c.key === key);
  const mapEl = document.getElementById('map');

  features.forEach(f => {
    const [lng, lat] = f.geometry.coordinates;
    const p          = f.properties;

    /* human-readable name — same fallback chain as reference */
    const name = p.name || p['name:en'] || p['name:hi'] || p.operator || p.brand || 'Unnamed';

    /* address parts — same as reference */
    const addrParts = [
      p['addr:housename'], p['addr:housenumber'],
      p['addr:street']  || p['addr:place'],
      p['addr:city']    || p['addr:district'],
      p['addr:state']
    ].filter(Boolean);
    const addrLine = addrParts.join(', ');

    /* Create DOM marker element */
    const el = document.createElement('div');
    el.className = 'osm-marker';
    el.style.background = cat.accent;
    el.textContent = cat.icon;
    mapEl.appendChild(el);

    /* Position helper — called on every camera event */
    const posUpdate = () => {
      try {
        const pt = map.project({ lat, lng });
        el.style.left = pt.x + 'px';
        el.style.top  = pt.y + 'px';
      } catch(e) {}
    };
    posUpdate();

    /* Click → popup (DOM-based, matching reference popup style) */
    el.addEventListener('click', e => {
      e.stopPropagation();
      document.querySelectorAll('.osm-popup').forEach(p => p.remove());

      const pop = document.createElement('div');
      pop.className = 'osm-popup';
      pop.innerHTML =
        `<button class="popup-close">✕</button>
         <div class="popup-name">${esc(name)}</div>
         <div class="popup-type">${esc(cat.label)}</div>
         ${addrLine ? `<div class="popup-addr">${esc(addrLine)}</div>` : ''}`;

      /* Position popup above marker */
      const pt = map.project({ lat, lng });
      pop.style.cssText = `left:${pt.x}px;top:${pt.y - 44}px;transform:translate(-50%,-100%)`;
      mapEl.appendChild(pop);

      /* Keep popup pinned while map moves */
      const mv = () => {
        try {
          const pt2 = map.project({ lat, lng });
          pop.style.left = pt2.x + 'px';
          pop.style.top  = (pt2.y - 44) + 'px';
        } catch(e) {}
      };
      map.on('move', mv);
      pop.querySelector('.popup-close').addEventListener('click', () => {
        pop.remove();
        try { map.off('move', mv); } catch(e) {}
      });
    });

    catMarkers[key].push({ el, lat, lng, posUpdate });
  });

  /* Update count badge */
  const badge = document.getElementById('cnt-' + key);
  if (badge) badge.textContent = features.length;
}

/* ── Reposition all visible markers on camera events ── */
function syncAllMarkers() {
  ASSET_CATS.forEach(c => {
    catMarkers[c.key].forEach(m => m.posUpdate());
  });
}

/* ── Fetch one category from Overpass (exact copy of reference logic) ── */
async function fetchCategory(key) {
  const cat = ASSET_CATS.find(c => c.key === key);
  if (!cat) return [];

  /* Bounding box that covers the flood study area — same as reference */
  const bbox = '28.20,76.70,28.60,77.30';

  let ql;
  const t = cat.tags;
  if (t.startsWith('(')) {
    /* compound tag like (["amenity"="university"];["amenity"="college"];) */
    const inner = t.slice(1, t.lastIndexOf(')'));
    const stmts = inner.split(';').filter(Boolean);
    ql = '[out:json];(' +
         stmts.map(s => `node${s}(${bbox});way${s}(${bbox});`).join('') +
         ');out center;';
  } else {
    ql = `[out:json];(node${t}(${bbox});way${t}(${bbox}););out center;`;
  }

  const url = 'https://overpass-api.de/api/interpreter?data=' + encodeURIComponent(ql);

  for (let attempt = 1; attempt <= 3; attempt++) {
    try {
      const res = await fetch(url);

      if (res.status === 429) {
        console.warn(`Overpass 429 for "${key}" – attempt ${attempt}/3, waiting…`);
        await sleep(attempt * 2000);
        continue;
      }
      if (!res.ok) {
        console.warn(`Overpass HTTP ${res.status} for "${key}"`);
        return [];
      }

      const json     = await res.json();
      const elements = (json.elements || [])
        .filter(el => (el.lat != null && el.lon != null) || el.center)
        .map(el => ({
          type: 'Feature',
          geometry: {
            type: 'Point',
            coordinates: [ el.lon ?? el.center.lon, el.lat ?? el.center.lat ]
          },
          properties: el.tags || {}
        }));

      console.log(`✅ Fetched ${elements.length} items for "${key}"`);
      return elements;

    } catch (e) {
      console.warn(`Overpass fetch error for "${key}" attempt ${attempt}:`, e);
      if (attempt < 3) await sleep(1500);
    }
  }
  return [];
}

/* ── Sequential loader — 1 s gap between requests (exact copy of reference) ── */
async function loadAllAssets() {
  renderAssetPills();

  for (let i = 0; i < ASSET_CATS.length; i++) {
    const c        = ASSET_CATS[i];
    const features = await fetchCategory(c.key);
    catFeatures[c.key] = features;

    /* Update count badge even if pill is off */
    const badge = document.getElementById('cnt-' + c.key);
    if (badge) badge.textContent = features.length;

    /* If the pill was toggled on while loading, place markers now */
    if (catEnabled[c.key] && features.length > 0) addMarkers(c.key, features);

    /* 1 s delay between Overpass requests (same as reference) */
    if (i < ASSET_CATS.length - 1) await sleep(1000);
  }

  const ab = document.getElementById('assetBadge');
  ab.textContent   = 'Ready';
  ab.style.background = '#B1DEE2';
  ab.style.color   = '#264351';
}

/* ══════════════════════════════════════════════════════════
   SEARCH  —  Nominatim forward + reverse geocoding (OSM)
══════════════════════════════════════════════════════════ */
let searchInitDone = false, searchDebounce = null;

function initSearch() {
  if (searchInitDone) return;
  searchInitDone = true;

  const input = document.getElementById('searchInput');
  const list  = document.getElementById('searchSuggestions');

  /* Forward geocoding */
  input.addEventListener('input', () => {
    clearTimeout(searchDebounce);
    const q = input.value.trim();
    if (q.length < 3) { list.style.display = 'none'; return; }
    searchDebounce = setTimeout(() => nominatimForward(q, list, input), 350);
  });

  document.addEventListener('click', e => {
    if (!document.getElementById('searchRow').contains(e.target))
      list.style.display = 'none';
  });

  /* Reverse geocoding on map click */
  map.on('click', async e => {
    const { lat, lng } = e.lngLat;
    const label = await nominatimReverse(lat, lng);
    input.value = label;
    flyPin(lat, lng, label);
  });
}

async function nominatimForward(query, list, input) {
  try {
    const url = `https://nominatim.openstreetmap.org/search`
      + `?q=${encodeURIComponent(query)}`
      + `&format=json&limit=6&addressdetails=1`
      + `&viewbox=${REF_LNG-.15},${REF_LAT+.15},${REF_LNG+.15},${REF_LAT-.15}&bounded=0`;
    const r = await fetch(url, { headers:{ 'User-Agent': NOM_UA } });
    if (!r.ok) return;
    const results = await r.json();
    if (!results.length) { list.style.display = 'none'; return; }
    list.innerHTML = results.map(res =>
      `<li data-lat="${res.lat}" data-lng="${res.lon}">${esc(res.display_name)}</li>`
    ).join('');
    list.style.display = 'block';
    list.querySelectorAll('li').forEach(li => {
      li.addEventListener('click', () => {
        const lat = +li.dataset.lat, lng = +li.dataset.lng;
        input.value = li.textContent.trim();
        list.style.display = 'none';
        flyPin(lat, lng, li.textContent.trim());
      });
    });
  } catch(err) { console.warn('Forward geocode failed:', err); }
}

async function nominatimReverse(lat, lng) {
  try {
    const r = await fetch(
      `https://nominatim.openstreetmap.org/reverse?lat=${lat}&lon=${lng}&format=json&zoom=18&addressdetails=1`,
      { headers:{ 'User-Agent': NOM_UA } }
    );
    if (!r.ok) throw new Error(r.status);
    const data = await r.json();
    const a = data.address || {};
    const parts = [
      a.road || a.pedestrian || a.footway || a.path,
      a.suburb || a.neighbourhood || a.quarter,
      a.city || a.town || a.village || a.county,
      a.state
    ].filter(Boolean);
    return parts.length ? parts.join(', ') : data.display_name || `${lat.toFixed(5)}, ${lng.toFixed(5)}`;
  } catch(err) { return `${lat.toFixed(5)}, ${lng.toFixed(5)}`; }
}

/* Drop a temporary search pin */
let currentPin = null;
function flyPin(lat, lng, name) {
  try { map.flyTo({ center:{ lat, lng }, zoom:15, pitch:50 }); } catch(e) {}
  if (currentPin) { currentPin(); currentPin = null; }
  const el = document.createElement('div');
  el.className = 'search-pin'; el.textContent = '📍'; el.title = name;
  document.getElementById('map').appendChild(el);
  const upd = () => {
    try { const p = map.project({ lat, lng }); el.style.left = p.x+'px'; el.style.top = p.y+'px'; } catch(e) {}
  };
  upd(); map.on('move', upd);
  const rm = () => { el.remove(); try { map.off('move', upd); } catch(e) {} };
  currentPin = rm;
  setTimeout(() => { if (currentPin === rm) { rm(); currentPin = null; } }, 10000);
}

/* ══════════════════════════════════════════════════════════
   THREE.JS CUSTOM LAYER
══════════════════════════════════════════════════════════ */
const customLayer = {
  id:'3d-flood', type:'custom', renderingMode:'3d',
  onAdd(m, gl) {
    camera = new THREE.Camera();
    scene  = new THREE.Scene();
    waterMeshes = [];
    scene.add(new THREE.AmbientLight(0xffffff, 0.7));
    const dl = new THREE.DirectionalLight(0xffffff, 0.8);
    dl.position.set(100, 200, 100); scene.add(dl);
    renderer = new THREE.WebGLRenderer({ canvas: m.getCanvas(), context: gl, antialias: true });
    renderer.autoClear = false;
  },
  render(gl, matrix) {
    const rx = new THREE.Matrix4().makeRotationAxis(new THREE.Vector3(1,0,0), modelTransform.rotateX);
    const ry = new THREE.Matrix4().makeRotationAxis(new THREE.Vector3(0,1,0), modelTransform.rotateY);
    const rz = new THREE.Matrix4().makeRotationAxis(new THREE.Vector3(0,0,1), modelTransform.rotateZ);
    const m  = new THREE.Matrix4().fromArray(matrix);
    const l  = new THREE.Matrix4()
      .makeTranslation(modelTransform.translateX, modelTransform.translateY, modelTransform.translateZ)
      .scale(new THREE.Vector3(modelTransform.scale, -modelTransform.scale, modelTransform.scale))
      .multiply(rx).multiply(ry).multiply(rz);
    camera.projectionMatrix = m.multiply(l);
    renderer.resetState(); renderer.render(scene, camera); glMap.triggerRepaint();
  }
};

function buildTransform() {
  const MC = window.maplibregl?.MercatorCoordinate;
  if (MC) {
    const c = MC.fromLngLat([REF_LNG, REF_LAT], 0);
    return { translateX:c.x, translateY:c.y, translateZ:c.z,
             rotateX:Math.PI/2, rotateY:0, rotateZ:0,
             scale:c.meterInMercatorCoordinateUnits() };
  }
  const x  = (REF_LNG+180)/360;
  const sl = Math.sin(REF_LAT*Math.PI/180);
  const y  = 0.5 - Math.log((1+sl)/(1-sl))/(4*Math.PI);
  return { translateX:x, translateY:y, translateZ:0,
           rotateX:Math.PI/2, rotateY:0, rotateZ:0,
           scale:1/(2*Math.PI*6378137*Math.cos(REF_LAT*Math.PI/180)) };
}

function merc(lng, lat) {
  if (window.maplibregl?.MercatorCoordinate)
    return maplibregl.MercatorCoordinate.fromLngLat([lng, lat]);
  const x  = (lng+180)/360;
  const sl = Math.sin(lat*Math.PI/180);
  return { x, y: 0.5 - Math.log((1+sl)/(1-sl))/(4*Math.PI) };
}

/* ══════════════════════════════════════════════════════════
   MAP INIT  (Mappls SDK)
══════════════════════════════════════════════════════════ */
function onSDKReady(fn) {
  if (window.mappls && typeof mappls.Map === 'function') { fn(); return; }
  const t = setInterval(() => {
    if (window.mappls && typeof mappls.Map === 'function') { clearInterval(t); fn(); }
  }, 100);
}

onSDKReady(() => {
  map = new mappls.Map('map', {
    center:{ lat:REF_LAT, lng:REF_LNG },
    zoom:14, pitch:60, bearing:-20, zoomControl:true
  });

  let threeReady = false;
  const boot3 = () => {
    if (threeReady) return; threeReady = true;
    glMap = map; modelTransform = buildTransform();
    try { map.addLayer(customLayer); } catch(e) { console.warn(e); }
  };
  map.on('load', boot3);
  map.on('style.load', boot3);
  setTimeout(() => { if (!threeReady) boot3(); }, 8000);

  /* Sync DOM markers on every camera change */
  ['move','zoom','pitch','rotate'].forEach(ev => map.on(ev, syncAllMarkers));

  map.on('load', () => {
    initSearch();
    loadAllAssets();   // ← starts the sequential Overpass fetch
  });
  /* Fallback if 'load' already fired before listeners attached */
  setTimeout(() => { initSearch(); loadAllAssets(); }, 4000);
});

/* ══════════════════════════════════════════════════════════
   FLOOD DATA LOADING
══════════════════════════════════════════════════════════ */
async function initializeVisualization() {
  try {
    setStatus('10% – Loading metadata…');
    const ir = await fetch('polygon_index.json');
    if (!ir.ok) throw new Error(`polygon_index.json ${ir.status}`);
    polygonCount = (await ir.json()).length;

    setStatus('30% – Loading coordinates…');
    const cr = await fetch('coordinates.bin');
    if (!cr.ok) throw new Error(`coordinates.bin ${cr.status}`);
    coordinatesBuffer = await cr.arrayBuffer();

    setStatus('50% – Preloading initial chunks…');
    await Promise.all([loadChunk(0), loadChunk(1)]);

    setStatus('100% – Ready!');
    setTimeout(() => {
      document.getElementById('loadingOverlay').classList.add('hidden');
      updateStep(0);
    }, 500);
  } catch(err) {
    console.error(err);
    setStatus('❌ ' + err.message);
    document.querySelector('.loader h2').textContent = 'Failed to Load';
  }
}

function setStatus(t) { document.getElementById('loadingProgress').textContent = t; }

async function loadChunk(idx) {
  if (chunkCache.has(idx)) return;
  if (chunkQueue.has(idx)) { while (chunkQueue.has(idx)) await sleep(50); return; }
  chunkQueue.add(idx);
  try {
    const r = await fetch(`chunks/chunk_${String(idx).padStart(3,'0')}.bin`);
    if (!r.ok) throw new Error(`chunk_${idx} missing`);
    const v = new Float32Array(await r.arrayBuffer());
    const d = {}, s = idx*CHUNK_SIZE, e = Math.min(s+CHUNK_SIZE, TOTAL_STEPS+1);
    for (let ts=s, i=0; ts<e; ts++, i++) d[ts] = v.slice(i*polygonCount, (i+1)*polygonCount);
    chunkCache.set(idx, d);
    if (chunkCache.size > MAX_CACHED) chunkCache.delete(chunkCache.keys().next().value);
  } catch(e) { console.error(e); } finally { chunkQueue.delete(idx); }
}

async function getDepth(step) {
  const ci = Math.floor(step/CHUNK_SIZE);
  if (!chunkCache.has(ci)) {
    document.getElementById('chunkLoadingIndicator').style.display = 'block';
    await loadChunk(ci);
    document.getElementById('chunkLoadingIndicator').style.display = 'none';
  }
  return chunkCache.get(ci)?.[step] ?? null;
}

function buildMesh(depths) {
  if (!scene || !depths) return;
  waterMeshes.forEach(m => { scene.remove(m); m.geometry?.dispose(); m.material?.dispose(); });
  waterMeshes = [];

  const dv = new DataView(coordinatesBuffer);
  let off = 0, flood = [];
  for (let p = 0; p < polygonCount; p++) {
    const pc = dv.getUint32(off, true); off += 4;
    if (depths[p] > 0) flood.push({ d:depths[p], off, pc });
    off += pc * 16;
  }
  if (!flood.length) return;

  const G = {};
  flood.forEach(f => {
    const k = f.d<.5?'0xB1DEE2':f.d<1?'0x5298A9':f.d<2?'0x49879A':'0x264351';
    (G[k]=G[k]||[]).push(f);
  });

  Object.entries(G).forEach(([cs, polys]) => {
    const verts=[],idx=[]; let vc=0;
    polys.forEach(p => {
      const c=[]; let ro=p.off;
      for (let i=0;i<p.pc;i++){c.push({lng:dv.getFloat64(ro,true),lat:dv.getFloat64(ro+8,true)});ro+=16;}
      const bot=[],top=[];
      c.forEach(({lng,lat})=>{
        const m=merc(lng,lat);
        const x=(m.x-modelTransform.translateX)/modelTransform.scale;
        const y=(m.y-modelTransform.translateY)/modelTransform.scale;
        verts.push(x,0,y); bot.push(vc++);
        verts.push(x,p.d*depthScale,y); top.push(vc++);
      });
      for(let i=1;i<bot.length-1;i++)idx.push(bot[0],bot[i],bot[i+1]);
      for(let i=1;i<top.length-1;i++)idx.push(top[0],top[i+1],top[i]);
      for(let i=0;i<c.length;i++){const j=(i+1)%c.length;idx.push(bot[i],bot[j],top[i],bot[j],top[j],top[i]);}
    });
    if (!verts.length) return;
    const geo = new THREE.BufferGeometry();
    geo.setAttribute('position', new THREE.BufferAttribute(new Float32Array(verts), 3));
    geo.setIndex(new THREE.BufferAttribute(new Uint32Array(idx), 1));
    geo.computeVertexNormals();
    const mat  = new THREE.MeshPhongMaterial({ color:parseInt(cs), transparent:true, opacity:floodOpacity, side:THREE.DoubleSide });
    const mesh = new THREE.Mesh(geo, mat); scene.add(mesh); waterMeshes.push(mesh);
  });
}

async function updateStep(step) {
  step = Math.max(0, Math.min(TOTAL_STEPS, step));
  const depths = await getDepth(step); if (!depths) return;
  currentStep = step; buildMesh(depths);
  /* preload next chunk */
  const nc = Math.floor(step/CHUNK_SIZE)+1;
  if (nc < TOTAL_CHUNKS && !chunkCache.has(nc) && !chunkQueue.has(nc)) loadChunk(nc).catch(()=>{});
  /* update time display */
  const b = new Date('2025-07-09T01:55:00'); b.setMinutes(b.getMinutes()+step*5);
  const z = n => String(n).padStart(2,'0');
  document.getElementById('timeDisplay').textContent =
    `${z(b.getDate())}-${MONTHS[b.getMonth()]}-${b.getFullYear()} ${z(b.getHours())}:${z(b.getMinutes())}:${z(b.getSeconds())}`;
  const sl = document.getElementById('timeSlider'); sl.value = step;
  const pct = (step/TOTAL_STEPS)*100;
  sl.style.background = `linear-gradient(to right,#5298A9 ${pct}%,#e2e8f0 ${pct}%)`;
}

/* ══════════════════════════════════════════════════════════
   UI WIRING
══════════════════════════════════════════════════════════ */
function toggleSidebar() {
  const sb  = document.getElementById('sidebar');
  const ham = document.getElementById('hamburgerBtn');
  const chv = document.getElementById('collapseBtn');
  const isCollapsed = sb.classList.toggle('collapsed');
  ham.classList.toggle('open', !isCollapsed);
  chv.innerHTML = isCollapsed ? '›' : '‹';
}
document.getElementById('hamburgerBtn').addEventListener('click', toggleSidebar);
document.getElementById('collapseBtn').addEventListener('click', toggleSidebar);
document.getElementById('timeSlider').addEventListener('input', e => updateStep(+e.target.value));

const playBtn = document.getElementById('playBtn');
playBtn.addEventListener('click', () => {
  isPlaying = !isPlaying;
  playBtn.classList.toggle('active', isPlaying);
  playBtn.innerHTML = isPlaying ? '⏸' : '▶';
  if (isPlaying) playInterval = setInterval(() => updateStep(currentStep >= TOTAL_STEPS ? 0 : currentStep+1), playSpeed);
  else clearInterval(playInterval);
});
document.getElementById('prevBtn').addEventListener('click', () => { if(currentStep>0) updateStep(currentStep-1); });
document.getElementById('nextBtn').addEventListener('click', () => { if(currentStep<TOTAL_STEPS) updateStep(currentStep+1); });
document.getElementById('resetBtn').addEventListener('click', () => { if(isPlaying) playBtn.click(); updateStep(0); });

document.querySelectorAll('.speed-pill').forEach(p => p.addEventListener('click', () => {
  document.querySelectorAll('.speed-pill').forEach(x => x.classList.remove('active'));
  p.classList.add('active'); playSpeed = +p.dataset.speed;
  if (isPlaying) { clearInterval(playInterval); playBtn.click(); }
}));

document.getElementById('floodOpSlider').addEventListener('input', e => {
  floodOpacity = +e.target.value / 100;
  document.getElementById('floodOpVal').textContent = e.target.value + '%';
  waterMeshes.forEach(m => { if(m.material) m.material.opacity = floodOpacity; });
});

/* ── kick off flood data ── */
setTimeout(initializeVisualization, 0);

})();
</script>
</body>
</html>"""


@app.route('/')
def home():
    return HTML_CONTENT

# Serve static files (e.g. flood_depth_master_slim.geojson, flood_depths.bin) from the same directory as this script
@app.route('/<path:filename>')
def static_files(filename):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    return send_from_directory(base_dir, filename)

if __name__ == '__main__':
    print("Starting FloodTwin server on http://0.0.0.0:9120")
    serve(
        app,
        host='0.0.0.0',
        port=9120,
        threads=8,              # User requested
        channel_timeout=300,    # User requested
        ident='3DFloodTwin',      # Server identity
        connection_limit=500,   # Limit connections for small scale
        cleanup_interval=30     # Cleanup inactive connections
    )

