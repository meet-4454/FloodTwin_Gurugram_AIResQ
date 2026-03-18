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
  <title>3D Flood Twin - AIRESQ</title>
  <link rel="icon" type="image/png" id="faviconLink">

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
    #titleBar{padding:18px 24px 16px;flex-shrink:0;border-bottom:1px solid #e2e8f0;text-align:center}
    #titleLogo{width:56px;height:56px;object-fit:contain;display:block;margin:0 auto 8px;border-radius:50%;background:#fff;padding:2px;box-shadow:0 2px 8px rgba(82,152,169,.2)}
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

    /* ── OSM MARKERS (DOM-based) ── */
    .osm-marker{
      width:32px;height:32px;border-radius:50% 50% 50% 4px;border:3px solid #fff;
      display:flex;align-items:center;justify-content:center;font-size:15px;cursor:pointer;
      box-shadow:0 3px 10px rgba(0,0,0,.3);position:fixed;z-index:500;
      transform:translate(-50%,-100%);transition:transform .15s;user-select:none
    }
    .osm-marker:hover{transform:translate(-50%,-100%) scale(1.15)}

    /* ── POPUP ── */
    .osm-popup{
      position:fixed;background:rgba(255,255,255,.98);border:2px solid #5298A9;
      border-radius:12px;color:#264351;padding:12px 14px;font-size:13px;
      box-shadow:0 4px 20px rgba(82,152,169,.3);max-width:220px;z-index:3000;pointer-events:auto
    }
    .popup-name{font-weight:700;color:#264351;margin-bottom:3px;font-size:14px;padding-right:18px}
    .popup-type{font-size:11px;color:#5298A9;text-transform:uppercase;letter-spacing:.5px;font-weight:700}
    .popup-addr{font-size:11px;color:#64748b;margin-top:5px;padding-top:5px;border-top:1px solid #e2e8f0}
    .popup-close{position:absolute;top:5px;right:8px;background:none;border:none;font-size:15px;cursor:pointer;color:#94a3b8}
    .popup-close:hover{color:#264351}

    /* ══ FLOOD DEPTH POPUP ══ */
    #floodPopup{
      position:fixed;z-index:99999;pointer-events:auto;display:none;
      transform:translate(-50%,-100%);
      animation:fpIn .18s cubic-bezier(.34,1.56,.64,1)
    }
    @keyframes fpIn{
      from{opacity:0;transform:translate(-50%,-88%)}
      to  {opacity:1;transform:translate(-50%,-100%)}
    }
    #floodPopup .fp-card{
      background:rgba(255,255,255,.98);border:2px solid #5298A9;
      border-radius:14px;padding:14px 18px 13px;
      box-shadow:0 8px 28px rgba(82,152,169,.35);min-width:190px;position:relative
    }
    #floodPopup .fp-card::after{
      content:'';position:absolute;bottom:-11px;left:50%;transform:translateX(-50%);
      border:10px solid transparent;border-top-color:#5298A9
    }
    #floodPopup .fp-card::before{
      content:'';position:absolute;bottom:-8px;left:50%;transform:translateX(-50%);
      border:8px solid transparent;border-top-color:rgba(255,255,255,.98);z-index:1
    }
    #floodPopup .fp-close{
      position:absolute;top:7px;right:9px;background:none;border:none;
      font-size:14px;cursor:pointer;color:#94a3b8;padding:2px 5px;border-radius:4px;line-height:1
    }
    #floodPopup .fp-close:hover{color:#264351;background:#f1f5f9}
    #floodPopup .fp-head{display:flex;align-items:center;gap:8px;margin-bottom:10px;padding-right:18px}
    #floodPopup .fp-head-icon{font-size:17px}
    #floodPopup .fp-head-title{font-size:12px;font-weight:700;color:#5298A9;text-transform:uppercase;letter-spacing:.8px}
    #floodPopup .fp-depth{display:flex;align-items:baseline;gap:5px;margin-bottom:8px}
    #floodPopup .fp-depth-val{font-size:30px;font-weight:800;color:#264351;font-variant-numeric:tabular-nums;line-height:1}
    #floodPopup .fp-depth-unit{font-size:13px;font-weight:600;color:#64748b}
    #floodPopup .fp-badge{
      display:inline-flex;align-items:center;gap:6px;
      padding:4px 11px;border-radius:20px;
      font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:.6px;margin-bottom:10px
    }
    #floodPopup .fp-badge .dot{width:7px;height:7px;border-radius:50%;flex-shrink:0}
    #floodPopup .fp-divider{height:1px;background:#e2e8f0;margin:0 0 8px}
    #floodPopup .fp-meta{font-size:11px;color:#64748b;line-height:1.7}
    #floodPopup .fp-meta b{color:#475569}

    /* ── LEGEND (TRANSLUCENT & COMPACT) ── */
    #legend{
      position:fixed;bottom:28px;left:28px;
      background:rgba(255,255,255,0.005);
      backdrop-filter:blur(12px);-webkit-backdrop-filter:blur(12px);
      border:1.5px solid rgba(82,152,169,0.50);border-radius:11px;
      padding:9px 11px;
      z-index:999;min-width:140px;max-width:170px;
      box-shadow:0 3px 14px rgba(82,152,169,.18)
    }
    .legend-header{display:flex;align-items:center;gap:6px;margin-bottom:7px}
    .legend-icon{font-size:13px;color:#264351}
    .legend-title{font-size:12px;font-weight:700;color:#264351;letter-spacing:.3px}
    .legend-row{display:flex;align-items:center;margin-bottom:5px;gap:6px}
    .legend-row:last-child{margin-bottom:0}
    .legend-swatch{width:26px;height:12px;border-radius:4px;flex-shrink:0;border:1px solid rgba(177,222,226,0.6)}
    .legend-range{font-size:11px;color:#264351;flex:1;font-weight:700;min-width:44px}
    .legend-severity{font-size:10px;font-weight:700;color:#264351;text-transform:uppercase;letter-spacing:.3px;min-width:48px;text-align:right}

    /* ── BOTTOM RIGHT CONTROLS ── */
    #mapControls{
      position:fixed;bottom:28px;right:28px;
      display:flex;flex-direction:column;gap:10px;
      z-index:998
    }
    .map-control-btn{
      width:44px;height:44px;background:rgba(255,255,255,.95);border:2px solid #5298A9;
      border-radius:10px;color:#5298A9;font-size:18px;cursor:pointer;
      display:flex;align-items:center;justify-content:center;
      transition:all .2s;box-shadow:0 3px 12px rgba(82,152,169,.25);
      backdrop-filter:blur(6px)
    }
    .map-control-btn:hover{background:#f8fafc;transform:scale(1.05)}
    .map-control-btn.active{background:#5298A9;color:#fff}

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
      position:fixed;bottom:130px;right:28px;background:rgba(255,255,255,.95);
      border:2px solid #5298A9;color:#5298A9;padding:10px 16px;border-radius:10px;
      font-size:14px;z-index:997;display:none;font-weight:600;box-shadow:0 4px 12px rgba(82,152,169,.2)
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
      position:fixed;z-index:600;transform:translate(-50%,-100%);font-size:28px;
      pointer-events:none;filter:drop-shadow(0 3px 6px rgba(82,152,169,.5));animation:pinDrop .3s ease-out
    }
    @keyframes pinDrop{
      from{transform:translate(-50%,-130%);opacity:0}
      to{transform:translate(-50%,-100%);opacity:1}
    }

    /* ── AIRESQ LOGO CONTAINER — hidden ── */
    #airesqLogoContainer{ display:none !important; }

    /* ── HIDE MAPPLS ATTRIBUTION ── */
    .mappls-copyright,
    .maplibregl-ctrl-attrib,
    .mappls-ctrl-attrib,
    [class*="mappls-ctrl"],
    [class*="maplibre-ctrl-attrib"],
    .maplibregl-ctrl-bottom-left,
    .maplibregl-ctrl-bottom-right,
    .mappls-ctrl-bottom-left,
    .mappls-ctrl-bottom-right {
      display:none !important;
      visibility:hidden !important;
      opacity:0 !important;
      pointer-events:none !important;
    }
  </style>
</head>
<body>

<button id="hamburgerBtn" class="open" aria-label="Toggle sidebar">
  <span></span><span></span><span></span>
</button>

<!-- AIRESQ LOGO (Top Right) -->
<div id="airesqLogoContainer" title="AIRESQ ClimSols Pvt. Ltd.">
  <img id="airesqLogoImg" src="" alt="AIRESQ Logo">
</div>

<div id="loadingOverlay">
  <div class="loader">
    <div class="spinner"></div>
    <h2>Initializing Flood Visualization…</h2>
    <p id="loadingProgress">0% – Loading metadata…</p>
  </div>
</div>

<div id="map"></div>
<div id="chunkLoadingIndicator">Loading timestep data…</div>

<!-- FLOOD DEPTH POPUP -->
<div id="floodPopup">
  <div class="fp-card">
    <button class="fp-close" id="fpClose">✕</button>
    <div class="fp-head">
      <span class="fp-head-icon">💧</span>
      <span class="fp-head-title">Flood Depth</span>
    </div>
    <div class="fp-depth">
      <span class="fp-depth-val" id="fpVal">—</span>
      <span class="fp-depth-unit">metres</span>
    </div>
    <div class="fp-badge" id="fpBadge">
      <span class="dot" id="fpDot"></span>
      <span id="fpLabel">—</span>
    </div>
    <div class="fp-divider"></div>
    <div class="fp-meta">
      <b>Time:</b> <span id="fpTime">—</span><br>
      <b>Location:</b> <span id="fpCoords">—</span>
    </div>
  </div>
</div>

<!-- SIDEBAR -->
<div id="sidebar">
  <button id="collapseBtn" title="Toggle sidebar">‹</button>

  <div id="titleBar">
    <img id="titleLogo" src="data:image/png;base64,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" alt="AIRESQ Logo">
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

<!-- BOTTOM RIGHT CONTROLS: zoom, 2D/3D all together -->
<div id="mapControls">
  <button class="map-control-btn" id="toggle3DBtn" title="Toggle 2D/3D">🏔️</button>
  <button class="map-control-btn" id="zoomInBtn" title="Zoom In">+</button>
  <button class="map-control-btn" id="zoomOutBtn" title="Zoom Out">−</button>
</div>

<script>
(function(){
'use strict';

// ── Set real logo from base64 ──
const LOGO_B64 = '/9j/4AAQSkZJRgABAQAAAQABAAD/4gHYSUNDX1BST0ZJTEUAAQEAAAHIAAAAAAQwAABtbnRyUkdCIFhZWiAH4AABAAEAAAAAAABhY3NwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAQAA9tYAAQAAAADTLQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAlkZXNjAAAA8AAAACRyWFlaAAABFAAAABRnWFlaAAABKAAAABRiWFlaAAABPAAAABR3dHB0AAABUAAAABRyVFJDAAABZAAAAChnVFJDAAABZAAAAChiVFJDAAABZAAAAChjcHJ0AAABjAAAADxtbHVjAAAAAAAAAAEAAAAMZW5VUwAAAAgAAAAcAHMAUgBHAEJYWVogAAAAAAAAb6IAADj1AAADkFhZWiAAAAAAAABimQAAt4UAABjaWFlaIAAAAAAAACSgAAAPhAAAts9YWVogAAAAAAAA9tYAAQAAAADTLXBhcmEAAAAAAAQAAAACZmYAAPKnAAANWQAAE9AAAApbAAAAAAAAAABtbHVjAAAAAAAAAAEAAAAMZW5VUwAAACAAAAAcAEcAbwBvAGcAbABlACAASQBuAGMALgAgADIAMAAxADb/2wBDAAUDBAQEAwUEBAQFBQUGBwwIBwcHBw8LCwkMEQ8SEhEPERETFhwXExQaFRERGCEYGh0dHx8fExciJCIeJBweHx7/2wBDAQUFBQcGBw4ICA4eFBEUHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh7/wAARCAdDBicDASIAAhEBAxEB/8QAHQABAAICAwEBAAAAAAAAAAAAAAYHBAUCAwgBCf/EAFgQAAEDAwEDCAUIBQgJAwMCBwABAgMEBREGEiExBxNBUWFxgZEUIjKhsSM2QlJicsHRFXN0krIIM0OCosLh8BYXJDQ1RVOD0lRVk0Rj8SVWo+JllaSzlP/EABoBAQEBAQEBAQAAAAAAAAAAAAABAgQFAwb/xAA2EQEAAgIBAgQEBQMEAgIDAAAAAQIDEQQFIRIxMkEiUWGhQnGBkdETseEUUsHwBhUjMxZTYv/aAAwDAQACEQMRAD8A8ZAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA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AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAH//Z';
const logoDataUrl = 'data:image/png;base64,' + LOGO_B64;
document.getElementById('airesqLogoImg').src = logoDataUrl;
document.getElementById('faviconLink').href  = logoDataUrl;

const CHUNK_SIZE    = 10;
const TOTAL_CHUNKS  = 34;
const MAX_CACHED    = 3;
const TOTAL_STEPS   = 336;
const REF_LAT       = 28.4595;
const REF_LNG       = 77.0266;
const NOM_UA        = 'FloodTwin/1.0 (research project)';
const MONTHS        = ['January','February','March','April','May','June','July','August','September','October','November','December'];

let map, glMap, scene, camera, renderer, modelTransform;
let currentStep = 0, isPlaying = false, playInterval = null, playSpeed = 500;
let floodOpacity = 0.70, depthScale = 1.0;
let waterMeshes = [], polygonCount = 0, coordinatesBuffer = null;
let is3DMode = false; // start in 2D
const chunkCache = new Map(), chunkQueue = new Set();

const sleep = ms => new Promise(r => setTimeout(r, ms));
const esc = s => String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');

let polygonRings = null;

function buildPolygonRings() {
  if (!coordinatesBuffer || polygonRings) return;
  const dv = new DataView(coordinatesBuffer);
  polygonRings = [];
  let off = 0;
  for (let p = 0; p < polygonCount; p++) {
    const pc = dv.getUint32(off, true); off += 4;
    const ring = [];
    for (let i = 0; i < pc; i++) {
      ring.push({ lng: dv.getFloat64(off, true), lat: dv.getFloat64(off + 8, true) });
      off += 16;
    }
    polygonRings.push(ring);
  }
}

function pointInPolygon(lng, lat, ring) {
  let inside = false;
  const n = ring.length;
  for (let i = 0, j = n - 1; i < n; j = i++) {
    const xi = ring[i].lng, yi = ring[i].lat;
    const xj = ring[j].lng, yj = ring[j].lat;
    if (((yi > lat) !== (yj > lat)) &&
        (lng < (xj - xi) * (lat - yi) / (yj - yi) + xi)) inside = !inside;
  }
  return inside;
}

const SEV = [
  { max:0.5,      label:'Low',      bg:'#e6f7f9', color:'#0e7490', dot:'#6BC3D2' },
  { max:1.0,      label:'Moderate', bg:'#cceef5', color:'#0369a1', dot:'#5298A9' },
  { max:2.0,      label:'High',     bg:'#b3dde8', color:'#155e75', dot:'#49879A' },
  { max:Infinity, label:'Severe',   bg:'#264351', color:'#ffffff', dot:'#264351' }
];

const fpPopup  = document.getElementById('floodPopup');
const fpVal    = document.getElementById('fpVal');
const fpBadge  = document.getElementById('fpBadge');
const fpDot    = document.getElementById('fpDot');
const fpLabel  = document.getElementById('fpLabel');
const fpTime   = document.getElementById('fpTime');
const fpCoords = document.getElementById('fpCoords');

let fpLat = null, fpLng = null;

document.getElementById('fpClose').addEventListener('click', () => {
  fpPopup.style.display = 'none'; fpLat = fpLng = null;
});

// Reposition flood popup — works in both normal and fullscreen mode
function repositionFloodPopup() {
  if (fpPopup.style.display === 'none' || fpLat === null) return;
  try {
    const pt = map.project({ lat: fpLat, lng: fpLng });
    fpPopup.style.left = pt.x + 'px';
    fpPopup.style.top  = (pt.y - 14) + 'px';
  } catch(e) {console.warn('Reposition error:', e);}
}

function showFloodPopup(lng, lat, depth) {
  const sev = SEV.find(s => depth < s.max);
  fpLat = lat; fpLng = lng;

  fpVal.textContent = depth.toFixed(2);
  fpBadge.style.background = sev.bg;
  fpBadge.style.color       = sev.color;
  fpDot.style.background    = sev.dot;
  fpLabel.textContent       = sev.label;

  fpTime.textContent   = document.getElementById('timeDisplay').textContent;
  fpCoords.textContent = `${lat.toFixed(4)}°N, ${lng.toFixed(4)}°E`;

  // Ensure popup is in correct container (document.body for fullscreen)
  if (!document.body.contains(fpPopup)) {
    document.body.appendChild(fpPopup);
  }

  fpPopup.style.display = 'block';
  repositionFloodPopup();
}

async function tryFloodHit(lat, lng) {
  if (!polygonRings) return false;
  const depths = await getDepth(currentStep);
  if (!depths) return false;
  for (let p = 0; p < polygonCount; p++) {
    if (depths[p] <= 0) continue;
    if (pointInPolygon(lng, lat, polygonRings[p])) {
      showFloodPopup(lng, lat, depths[p]);
      return true;
    }
  }
  return false;
}

// CRITICAL ASSETS
const ASSET_CATS = [
  { key:'hospital',     icon:'🏥', label:'Hospitals',      accent:'#ef4444', tags:'["amenity"="hospital"]'     },
  { key:'school',       icon:'🏫', label:'Schools',        accent:'#10b981', tags:'["amenity"="school"]'       },
  { key:'college',      icon:'🎓', label:'Colleges',       accent:'#06b6d4', tags:'(["amenity"="university"];["amenity"="college"];)' },
  { key:'fire_station', icon:'🚒', label:'Fire Stations',  accent:'#f43f5e', tags:'["amenity"="fire_station"]' },
  { key:'police',       icon:'🚔', label:'Police',         accent:'#6366f1', tags:'["amenity"="police"]'       },
  { key:'pharmacy',     icon:'💊', label:'Pharmacies',     accent:'#14b8a6', tags:'["amenity"="pharmacy"]'     }
];

const catMarkers  = {};
const catEnabled  = {};
const catFeatures = {};
ASSET_CATS.forEach(c => { catMarkers[c.key]=[]; catEnabled[c.key]=false; catFeatures[c.key]=null; });

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

function getMarkerContainer() {
  return document.fullscreenElement || document.getElementById('map');
}

function showMarkers(key) {
  if (catFeatures[key] && catFeatures[key].length > 0) {
    addMarkers(key, catFeatures[key]);
  }
}

function hideMarkers(key) {
  catMarkers[key].forEach(m => m.el.remove());
  catMarkers[key] = [];
  document.querySelectorAll('.osm-popup').forEach(p => p.remove());
}

function addMarkers(key, features) {
  hideMarkers(key);
  const cat   = ASSET_CATS.find(c => c.key === key);
  const mapEl = document.getElementById('map');

  features.forEach(f => {
    const [lng, lat] = f.geometry.coordinates;
    const p          = f.properties;

    const name = p.name || p['name:en'] || p['name:hi'] || p.operator || p.brand || 'Unnamed';
    const addrParts = [
      p['addr:housename'], p['addr:housenumber'],
      p['addr:street']  || p['addr:place'],
      p['addr:city']    || p['addr:district'],
      p['addr:state']
    ].filter(Boolean);
    const addrLine = addrParts.join(', ');

    const el = document.createElement('div');
    el.className = 'osm-marker';
    el.style.background = cat.accent;
    el.textContent = cat.icon;
    mapEl.appendChild(el);


    const posUpdate = () => {
      try {
        const pt = map.project({ lat, lng });
        el.style.left = pt.x + 'px';
        el.style.top  = pt.y + 'px';
      } catch(e) {}
    };
    posUpdate();

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

      const pt = map.project({ lat, lng });
      pop.style.left = pt.x + 'px';
      pop.style.top  = (pt.y - 44) + 'px';
      mapEl.appendChild(pop);

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

  const badge = document.getElementById('cnt-' + key);
  if (badge) badge.textContent = features.length;
}

function syncAllMarkers() {
  ASSET_CATS.forEach(c => {
    catMarkers[c.key].forEach(m => m.posUpdate());
  });
  repositionFloodPopup();
}

// ── Overpass endpoints tried in rotation if one fails / rate-limits ──────────
// ── ONE batched Overpass query for ALL categories ───────────────────────────
// Sending 6 separate requests hammers the rate-limiter; one request with
// all amenity types avoids that entirely. We tag each element with a
// synthetic "assetCategory" property so we can split client-side.

const OVERPASS_ENDPOINTS = [
  'https://overpass-api.de/api/interpreter',
  'https://overpass.kumi.systems/api/interpreter',
  'https://maps.mail.ru/osm/tools/overpass/api/interpreter'
];

// Map amenity value → ASSET_CATS key (used to bucket results)
const AMENITY_TO_KEY = {
  hospital:     'hospital',
  school:       'school',
  university:   'college',
  college:      'college',
  fire_station: 'fire_station',
  police:       'police',
  pharmacy:     'pharmacy'
};

function buildBatchQL(bbox) {
  // One union query: every amenity we care about, nodes + ways, bbox-filtered
  const amenities = ['hospital','school','university','college','fire_station','police','pharmacy'];
  const stmts = amenities.flatMap(a => [
    `node["amenity"="${a}"](${bbox});`,
    `way["amenity"="${a}"](${bbox});`
  ]).join('');
  return `[out:json][timeout:40];(${stmts});out center tags;`;
}

async function fetchAllOverpass(retries = 5) {
  const bbox = '28.20,76.70,28.60,77.30';
  const ql   = buildBatchQL(bbox);

  for (let attempt = 0; attempt < retries; attempt++) {
    const endpoint = OVERPASS_ENDPOINTS[attempt % OVERPASS_ENDPOINTS.length];
    const url      = endpoint + '?data=' + encodeURIComponent(ql);
    try {
      const ctrl = new AbortController();
      const tid  = setTimeout(() => ctrl.abort(), 42000);
      const res  = await fetch(url, { signal: ctrl.signal });
      clearTimeout(tid);

      if (res.status === 429 || res.status === 504 || res.status === 503) {
        await sleep(2000 * (attempt + 1));
        continue;
      }
      if (!res.ok) { await sleep(1500); continue; }

      const json = await res.json();
      return (json.elements || []).filter(el =>
        (el.lat != null && el.lon != null) || el.center
      );
    } catch (e) {
      if (attempt < retries - 1) await sleep(1500 * (attempt + 1));
    }
  }
  return [];
}

async function loadAllAssets() {
  renderAssetPills();

  const ab = document.getElementById('assetBadge');
  ab.textContent = 'Loading…';

  // Single request — fetch everything at once
  const elements = await fetchAllOverpass();

  // Bucket elements into per-category feature arrays
  const buckets = {};
  ASSET_CATS.forEach(c => { buckets[c.key] = []; });

  elements.forEach(el => {
    const amenity = (el.tags || {}).amenity;
    const key     = AMENITY_TO_KEY[amenity];
    if (!key) return;

    buckets[key].push({
      type: 'Feature',
      geometry: {
        type: 'Point',
        coordinates: [el.lon ?? el.center.lon, el.lat ?? el.center.lat]
      },
      properties: el.tags || {}
    });
  });

  // Apply to each category and update pill counts
  ASSET_CATS.forEach(c => {
    catFeatures[c.key] = buckets[c.key];

    const badge = document.getElementById('cnt-' + c.key);
    if (badge) badge.textContent = buckets[c.key].length;

    if (catEnabled[c.key] && buckets[c.key].length > 0) {
      addMarkers(c.key, buckets[c.key]);
    }
  });

  ab.textContent      = 'Ready';
  ab.style.background = '#B1DEE2';
  ab.style.color      = '#264351';
}

// SEARCH
let searchInitDone = false, searchDebounce = null;

function initSearch() {
  if (searchInitDone) return;
  searchInitDone = true;

  const input = document.getElementById('searchInput');
  const list  = document.getElementById('searchSuggestions');

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

  map.on('click', async e => {
    const { lat, lng } = e.lngLat;

    document.querySelectorAll('.osm-popup').forEach(p => p.remove());

    const hit = await tryFloodHit(lat, lng);
    if (hit) return;

    fpPopup.style.display = 'none'; fpLat = fpLng = null;
    const label = await nominatimReverse(lat, lng);
    input.value = label;
    flyPin(lat, lng, label);
  });
}

async function nominatimForward(query, list, input) {
  try {
    const url = `https://nominatim.openstreetmap.org/search?q=${encodeURIComponent(query)}&format=json&limit=6&addressdetails=1&viewbox=${REF_LNG-.15},${REF_LAT+.15},${REF_LNG+.15},${REF_LAT-.15}&bounded=0`;
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
  } catch(err) {}
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

// THREE.JS LAYER
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

function onSDKReady(fn) {
  if (window.mappls && typeof mappls.Map === 'function') { fn(); return; }
  const t = setInterval(() => {
    if (window.mappls && typeof mappls.Map === 'function') { clearInterval(t); fn(); }
  }, 100);
}

onSDKReady(() => {
  map = new mappls.Map('map', {
    center:{ lat:28.4595, lng:77.0266 },
    zoom:13, pitch:0, bearing:0, zoomControl:false, attributionControl:false
  });

  // Start in 2D mode — mark button active immediately
  const t3btn = document.getElementById('toggle3DBtn');
  if (t3btn) t3btn.classList.add('active');

  let threeReady = false;
  const boot3 = () => {
    if (threeReady) return; threeReady = true;
    glMap = map; modelTransform = buildTransform();
    try { map.addLayer(customLayer); } catch(e) { console.warn(e); }
  };
  map.on('load', boot3);
  map.on('style.load', boot3);
  setTimeout(() => { if (!threeReady) boot3(); }, 8000);

  ['move','zoom','pitch','rotate'].forEach(ev => map.on(ev, syncAllMarkers));

  map.on('load', () => {
    initSearch();
    loadAllAssets();
    // Remove attribution after load
    removeAttribution();
  });
  setTimeout(() => {
    initSearch();
    loadAllAssets();
    removeAttribution();
  }, 4000);
});

// Remove Mappls attribution
function removeAttribution() {
  const selectors = [
    '.mappls-copyright', '.maplibregl-ctrl-attrib', '.mappls-ctrl-attrib',
    '.maplibregl-ctrl-bottom-left', '.maplibregl-ctrl-bottom-right',
    '.mappls-ctrl-bottom-left', '.mappls-ctrl-bottom-right',
    '[class*="mappls-ctrl"]', '[class*="copyright"]', '[class*="attrib"]'
  ];
  selectors.forEach(sel => {
    document.querySelectorAll(sel).forEach(el => {
      el.style.cssText = 'display:none!important;visibility:hidden!important;opacity:0!important';
    });
  });
}

// Periodically remove attribution (it may re-appear after tile loads)
setInterval(removeAttribution, 2000);

// FLOOD DATA
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
    buildPolygonRings();

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

// ── SHADER-BASED 3 m grid lines on 30 m cells ─────────────────────────────
// Each 30 m polygon = ONE extruded box (8 verts, 12 tris).
// A custom ShaderMaterial draws a 10×10 grid of dark seams on top/sides
// via UV math — zero extra geometry, full visual fidelity.

function bboxOfRing(ring) {
  let minLng=Infinity,maxLng=-Infinity,minLat=Infinity,maxLat=-Infinity;
  ring.forEach(({lng,lat})=>{
    if(lng<minLng)minLng=lng; if(lng>maxLng)maxLng=lng;
    if(lat<minLat)minLat=lat; if(lat>maxLat)maxLat=lat;
  });
  return {minLng,maxLng,minLat,maxLat};
}

// One extruded box per polygon — 8 vertices, 12 triangles, UV-mapped for grid lines
function addExtrudedBox(verts, uvs, idx, x0, y0, x1, y1, h) {
  const b = verts.length / 3;
  // bottom quad (y=0), top quad (y=h)
  verts.push(
    x0,0,y0, x1,0,y0, x1,0,y1, x0,0,y1,
    x0,h,y0, x1,h,y0, x1,h,y1, x0,h,y1
  );
  // UVs: top face uses (0,0)→(1,1); sides use u=along-edge, v=0→1 height
  // bottom
  uvs.push(0,0, 1,0, 1,1, 0,1);
  // top — same horizontal UV so grid lines show
  uvs.push(0,0, 1,0, 1,1, 0,1);

  // bottom face
  idx.push(b,b+2,b+1, b,b+3,b+2);
  // top face
  idx.push(b+4,b+5,b+6, b+4,b+6,b+7);
  // sides — UV v = vertical 0→1 (so horizontal grid lines appear on sides too)
  idx.push(b,b+1,b+5, b,b+5,b+4);
  idx.push(b+1,b+2,b+6, b+1,b+6,b+5);
  idx.push(b+2,b+3,b+7, b+2,b+7,b+6);
  idx.push(b+3,b,b+4,   b+3,b+4,b+7);
}

// Vertex shader — passes UV and world-Y (for side grid) to fragment
const VERT_SRC = `
  varying vec2 vUv;
  varying float vY;
  void main(){
    vUv = uv;
    vY  = position.y;
    gl_Position = projectionMatrix * modelViewMatrix * vec4(position,1.0);
  }
`;

// Fragment shader — draws 10×10 grid seams using fract()
// seam width ~6% of cell so lines are crisp but thin
const FRAG_SRC = `
  uniform vec3  uColor;
  uniform float uOpacity;
  uniform float uGridN;    // 10.0
  uniform float uSeam;     // seam fraction 0.0–1.0
  varying vec2  vUv;
  varying float vY;
  void main(){
    vec2 f = fract(vUv * uGridN);
    float lineX = step(f.x, uSeam) + step(1.0-uSeam, f.x);
    float lineY = step(f.y, uSeam) + step(1.0-uSeam, f.y);
    float isLine = min(lineX + lineY, 1.0);
    // seam color = slightly darker than cell color
    vec3 seamColor = uColor * 0.55;
    vec3 col = mix(uColor, seamColor, isLine * 0.85);
    gl_FragColor = vec4(col, uOpacity);
  }
`;

function makeGridMaterial(hexColor) {
  const c = new THREE.Color(parseInt(hexColor));
  return new THREE.ShaderMaterial({
    uniforms: {
      uColor:   { value: c },
      uOpacity: { value: floodOpacity },
      uGridN:   { value: 10.0 },
      uSeam:    { value: 0.055 }
    },
    vertexShader:   VERT_SRC,
    fragmentShader: FRAG_SRC,
    transparent: true,
    side: THREE.DoubleSide,
    depthWrite: false
  });
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
    const verts=[], uvs=[], idx=[];

    polys.forEach(p => {
      const ring=[]; let ro=p.off;
      for(let i=0;i<p.pc;i++){
        ring.push({lng:dv.getFloat64(ro,true), lat:dv.getFloat64(ro+8,true)});
        ro+=16;
      }

      const bb  = bboxOfRing(ring);
      const mBL = merc(bb.minLng, bb.minLat);
      const mTR = merc(bb.maxLng, bb.maxLat);

      const mx0 = (mBL.x - modelTransform.translateX) / modelTransform.scale;
      const my0 = (mBL.y - modelTransform.translateY) / modelTransform.scale;
      const mx1 = (mTR.x - modelTransform.translateX) / modelTransform.scale;
      const my1 = (mTR.y - modelTransform.translateY) / modelTransform.scale;

      addExtrudedBox(verts, uvs, idx, mx0, my0, mx1, my1, p.d * depthScale);
    });

    if (!verts.length) return;

    const geo = new THREE.BufferGeometry();
    geo.setAttribute('position', new THREE.BufferAttribute(new Float32Array(verts), 3));
    geo.setAttribute('uv',       new THREE.BufferAttribute(new Float32Array(uvs),   2));
    geo.setIndex(new THREE.BufferAttribute(new Uint32Array(idx), 1));
    geo.computeVertexNormals();

    const mat  = makeGridMaterial(cs);
    const mesh = new THREE.Mesh(geo, mat);
    scene.add(mesh);
    waterMeshes.push(mesh);
  });
}

async function updateStep(step) {
  step = Math.max(0, Math.min(TOTAL_STEPS, step));
  const depths = await getDepth(step); if (!depths) return;
  currentStep = step; buildMesh(depths);
  fpPopup.style.display = 'none'; fpLat = fpLng = null;
  const nc = Math.floor(step/CHUNK_SIZE)+1;
  if (nc < TOTAL_CHUNKS && !chunkCache.has(nc) && !chunkQueue.has(nc)) loadChunk(nc).catch(()=>{});
  const b = new Date('2025-07-09T01:55:00'); b.setMinutes(b.getMinutes()+step*5);
  const z = n => String(n).padStart(2,'0');
  document.getElementById('timeDisplay').textContent =
    `${z(b.getDate())}-${MONTHS[b.getMonth()]}-${b.getFullYear()} ${z(b.getHours())}:${z(b.getMinutes())}:${z(b.getSeconds())}`;
  const sl = document.getElementById('timeSlider'); sl.value = step;
  const pct = (step/TOTAL_STEPS)*100;
  sl.style.background = `linear-gradient(to right,#5298A9 ${pct}%,#e2e8f0 ${pct}%)`;
}

// UI
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
  waterMeshes.forEach(m => {
    if (m.material) {
      // ShaderMaterial uses uniform; MeshPhongMaterial uses .opacity
      if (m.material.uniforms && m.material.uniforms.uOpacity) {
        m.material.uniforms.uOpacity.value = floodOpacity;
      } else {
        m.material.opacity = floodOpacity;
      }
    }
  });
});

document.getElementById('zoomInBtn').addEventListener('click', () => {
  map.setZoom(map.getZoom() + 1);
});

document.getElementById('zoomOutBtn').addEventListener('click', () => {
  map.setZoom(map.getZoom() - 1);
});

document.getElementById('toggle3DBtn').addEventListener('click', () => {
  is3DMode = !is3DMode;
  const btn = document.getElementById('toggle3DBtn');
  if (is3DMode) {
    map.setPitch(60);
    btn.classList.remove('active');
  } else {
    map.setPitch(0);
    btn.classList.add('active');
  }
});

// Fullscreen button removed — no listener needed

let _sidebarWasCollapsedBeforeFS = false;

document.addEventListener('fullscreenchange', () => {
  const fsEl    = document.fullscreenElement;
  const sidebar = document.getElementById('sidebar');
  const ham     = document.getElementById('hamburgerBtn');
  const chv     = document.getElementById('collapseBtn');
  const search  = document.getElementById('searchWrap');

  // These non-search UI elements move into the fullscreen container
  const uiEls = [
    document.getElementById('floodPopup'),
    document.getElementById('legend'),
    document.getElementById('mapControls'),
    document.getElementById('chunkLoadingIndicator'),
    ham,
    sidebar,
  ];

  if (fsEl) {
    // ── Entering fullscreen ──────────────────────────────────────────────────
    _sidebarWasCollapsedBeforeFS = sidebar.classList.contains('collapsed');
    sidebar.classList.add('collapsed');
    sidebar.style.display = 'none';
    ham.style.display = 'none';

    // Move standard UI into the fullscreen element
    uiEls.forEach(el => { if (el && !fsEl.contains(el)) fsEl.appendChild(el); });

    // Pull search out of the sidebar and float it as a fixed overlay
    if (search) {
      fsEl.appendChild(search);
      search.style.cssText = [
        'position:fixed',
        'top:18px',
        'left:50%',
        'transform:translateX(-50%)',
        'width:min(480px,90vw)',
        'z-index:10000',
        'background:rgba(255,255,255,0.97)',
        'border:2px solid #5298A9',
        'border-radius:14px',
        'box-shadow:0 4px 18px rgba(82,152,169,.35)',
        'padding:6px 12px',
      ].join(';');
    }
  } else {
    // ── Exiting fullscreen ───────────────────────────────────────────────────
    uiEls.forEach(el => { if (el && !document.body.contains(el)) document.body.appendChild(el); });

    // Restore search back inside the sidebar and clear the inline override
    if (search) {
      // Re-insert after titleBar inside sidebar
      const titleBar = sidebar.querySelector('#titleBar');
      if (titleBar) titleBar.after(search);
      else sidebar.prepend(search);
      search.style.cssText = '';
    }

    // Restore sidebar
    sidebar.style.display = '';
    ham.style.display = '';
    if (!_sidebarWasCollapsedBeforeFS) {
      sidebar.classList.remove('collapsed');
      ham.classList.add('open');
      chv.innerHTML = '‹';
    } else {
      ham.classList.remove('open');
      chv.innerHTML = '›';
    }
  }

  syncAllMarkers();
  removeAttribution();
});

setTimeout(initializeVisualization, 0);

})();
</script>
</body>
</html>
"""


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
