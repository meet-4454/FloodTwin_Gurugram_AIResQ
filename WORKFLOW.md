# FloodTwin — Architecture & Workflow

> 3D Immersive Flood Visualization Engine for Gurugram region.  
> Simulates flood depth over **337 timesteps** (5-min intervals starting 09-July-2025) on a 3D map.

---

## 1. High-Level Architecture

```mermaid
graph TB
    subgraph CLIENT["🌐 Browser Client"]
        direction TB
        UI["Sidebar UI<br/>Time Control | Search | Assets | Opacity"]
        MAPPLS["Mappls Map SDK<br/>2D Map Tiles + Camera"]
        THREEJS["Three.js Engine<br/>3D Flood Mesh Rendering"]
        OSM_SEARCH["Nominatim API<br/>Forward & Reverse Geocoding"]
        OVERPASS["Overpass API<br/>Critical Assets from OSM"]
    end

    subgraph SERVER["⚙️ Flask + Gunicorn Backend  (port 9120)"]
        FLASK["Flask App<br/>server.py"]
        MAIN["Gunicorn Entry<br/>main.py"]
    end

    subgraph DATA["📦 Static Data Files"]
        HTML["Inline HTML/CSS/JS<br/>(served as single page)"]
        POLY["polygon_index.json<br/>Polygon Metadata"]
        COORDS["coordinates.bin<br/>Polygon Vertex Data"]
        CHUNKS["chunks/*.bin ×34<br/>Flood Depth Timeseries"]
    end

    subgraph INFRA["🖥️ Infrastructure"]
        SYSTEMD["systemd Service<br/>floodtwin.service"]
        CF["Cloudflare Tunnel<br/>Reverse Proxy"]
    end

    MAIN --> FLASK
    FLASK --> HTML
    FLASK --> POLY
    FLASK --> COORDS
    FLASK --> CHUNKS

    HTML --> UI
    UI --> MAPPLS
    UI --> THREEJS
    UI --> OSM_SEARCH
    UI --> OVERPASS

    SYSTEMD --> MAIN
    CF -.->|HTTPS| FLASK

    style CLIENT fill:#eef7f9,stroke:#5298A9,stroke-width:2px
    style SERVER fill:#fff8e1,stroke:#f59e0b,stroke-width:2px
    style DATA fill:#f0fdf4,stroke:#10b981,stroke-width:2px
    style INFRA fill:#faf5ff,stroke:#8b5cf6,stroke-width:2px
```

---

## 2. Data Flow — Request Sequence

```mermaid
sequenceDiagram
    participant U as User Browser
    participant F as Flask Server
    participant FS as Static Files
    participant N as Nominatim (OSM)
    participant O as Overpass (OSM)

    Note over U,F: 1. Page Load & Initialization
    U->>F: GET /
    F-->>U: HTML (inline CSS + JS)
    U->>F: GET /polygon_index.json
    F->>FS: Read polygon_index.json
    FS-->>F: JSON metadata
    F-->>U: Polygon count & metadata
    U->>F: GET /coordinates.bin
    F->>FS: Read coordinates.bin
    FS-->>F: Binary vertex data
    F-->>U: Polygon coordinates (binary)

    Note over U,F: 2. Chunk Loading (Lazy + Prefetch)
    U->>F: GET /chunks/chunk_000.bin
    F->>FS: Read chunk file
    FS-->>F: Binary depth data
    F-->>U: Flood depths for timesteps 0–9
    U->>F: GET /chunks/chunk_001.bin (prefetch)
    F-->>U: Flood depths for timesteps 10–19

    Note over U,N: 3. Search & Geocoding
    U->>N: Forward geocode query
    N-->>U: Lat/Lng results
    U->>U: Fly camera to location

    Note over U,O: 4. Critical Assets (Sequential)
    U->>O: Overpass QL — hospitals
    O-->>U: GeoJSON features
    U->>O: Overpass QL — schools, colleges, etc.
    O-->>U: GeoJSON features
    U->>U: Render DOM markers on map

    Note over U: 5. Runtime Interaction
    U->>U: Time slider → load chunk if needed → build 3D mesh
    U->>U: Map click → polygon hit-test → show flood depth popup
```

---

## 3. Project Structure Map

```mermaid
graph LR
    subgraph FILES["Project Files"]
        direction TB
        S1["server.py"]
        S2["main.py"]
        S3["requirements.txt"]
        S4["floodtwin.service"]
        S5[".gitignore"]
    end

    subgraph BINARY_DATA["Binary Data"]
        direction TB
        D1["polygon_index.json"]
        D2["coordinates.bin"]
        D3["chunks/<br/>chunk_000.bin … chunk_033.bin<br/>34 files × 10 timesteps = 336 steps"]
    end

    subgraph FRONTEND_IN_SERVER["Frontend (Inline in server.py)"]
        direction TB
        F1["HTML — Map div, sidebar, legend, popups"]
        F2["CSS — Sidebar, panels, markers, popups"]
        F3["JS — Map init, chunk loader, 3D engine,<br/>search, assets, time controls"]
    end

    S1 -->|contains| FRONTEND_IN_SERVER
    S2 -->|imports app from| S1
    S4 -->|launches via gunicorn| S2
    S1 -->|serves| BINARY_DATA

    style FILES fill:#fef3c7,stroke:#d97706,stroke-width:2px
    style BINARY_DATA fill:#dbeafe,stroke:#3b82f6,stroke-width:2px
    style FRONTEND_IN_SERVER fill:#fce7f3,stroke:#ec4899,stroke-width:2px
```

---

## 4. Component Explanations

### 4.1 Backend Components

| Component | File | Purpose |
|-----------|------|---------|
| **Flask App** | `server.py` | Core web server. Defines two routes: `/` serves the full HTML page (inline); `/<path>` serves any static file (binary data, chunks) from the project directory. |
| **Gunicorn Entry** | `main.py` | Thin wrapper that imports `app` from `server.py` and exposes it as `application` for Gunicorn's WSGI interface. |
| **Systemd Service** | `floodtwin.service` | Manages the process lifecycle — auto-starts on boot, restarts on crash (every 30s), runs 4 Gunicorn workers bound to port `9120`. |
| **Dependencies** | `requirements.txt` | Python packages: Flask, Gunicorn, Waitress (dev fallback), and their transitive deps. |

### 4.2 Data Components

| Component | File(s) | Purpose |
|-----------|---------|---------|
| **Polygon Index** | `polygon_index.json` | JSON array describing the flood simulation polygons. Used at startup to determine `polygonCount`. |
| **Coordinates Binary** | `coordinates.bin` | Binary file containing vertex coordinates (lng, lat as Float64) for every polygon. Parsed once at load; also used for click hit-testing via ray-cast. |
| **Depth Chunks** | `chunks/chunk_000.bin` … `chunk_033.bin` (34 files) | Each chunk holds flood depth values (Float32) for **10 consecutive timesteps**. 34 chunks × 10 = 340 slots, covering all 337 simulation steps. Loaded lazily with an LRU cache of 3 chunks max. |

### 4.3 Frontend Components (all inline in `server.py`)

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Mappls Map SDK** | Mappls JS SDK (v3.0 vector) | Renders the 2D base map (vector tiles), handles camera events (pan, zoom, pitch, rotate), and provides `map.project()` for coordinate-to-pixel conversion. |
| **Three.js 3D Engine** | Three.js r128 | Renders the 3D flood water meshes as a custom map layer. Builds extruded polygon geometry from depth data, colors by severity bands, and composites onto the map's WebGL canvas. |
| **Time Control Panel** | Vanilla JS | Slider (0–336), play/pause/step buttons, and speed pills (0.5×–4×). Moving the slider triggers `updateStep()` which loads the required chunk and rebuilds the 3D mesh. |
| **Search / Geocoding** | Nominatim (OSM) | Forward geocoding (type-ahead suggestions) and reverse geocoding (click on map → address). Places a temporary pin and flies the camera to the result. |
| **Critical Assets Overlay** | Overpass API (OSM) | Fetches 6 categories of infrastructure (hospitals, schools, colleges, fire stations, police, pharmacies) within the study area bounding box. Renders as DOM-based markers with click-to-popup details. Categories are toggled via sidebar pills. |
| **Flood Depth Popup** | Vanilla JS + CSS | On map click, performs a point-in-polygon ray-cast against all flooded polygons at the current timestep. If a hit is found, shows a styled popup with depth value, severity badge, time, and coordinates. |
| **Legend** | HTML + CSS | Fixed card (top-right) showing 4 flood depth severity bands: Low (<0.5m), Moderate (0.5–1m), High (1–2m), Severe (>2m) with matching color swatches. |
| **Layer Opacity Control** | Range slider | Adjusts the transparency of the Three.js water mesh material in real-time (0–100%). |

### 4.4 External Services

| Service | Endpoint | Usage |
|---------|----------|-------|
| **Mappls Map SDK** | `apis.mappls.com` | Vector map tiles and spatial SDK. API key embedded in the script tag. |
| **Nominatim** | `nominatim.openstreetmap.org` | Free geocoding — address search and reverse lookup on map click. |
| **Overpass** | `overpass-api.de` | OSM data query engine — fetches nearby critical infrastructure. Sequential requests with 1s delay and retry on 429. |
| **Three.js CDN** | `cdnjs.cloudflare.com` | Three.js r128 library loaded from CDN. |

### 4.5 Infrastructure

| Component | Detail |
|-----------|--------|
| **Runtime** | Python 3 (Miniconda `floodtwin` env) |
| **WSGI Server** | Gunicorn with 4 workers |
| **Dev Server** | Waitress (8 threads, port 9120) — used when running `server.py` directly |
| **Process Manager** | systemd (`floodtwin.service`) — auto-restart, runs as `production` user |
| **Reverse Proxy** | Cloudflare Tunnel for HTTPS termination and public access |

---

## 5. Key Design Decisions

| Decision | Rationale |
|----------|-----------|
| **Binary chunk format** | Float32 arrays are ~4× smaller than JSON for numeric grids and parse instantly via `Float32Array`. |
| **Lazy loading + LRU cache (3 chunks)** | Only 3 of 34 chunks stay in memory. The next chunk is prefetched while the current one plays, giving seamless playback without loading all 34 files upfront. |
| **Inline HTML** | The entire frontend is a single HTML string inside `server.py` — zero build tooling, no separate static assets to manage, trivially deployable. |
| **DOM-based markers** | Mappls SDK doesn't expose `maplibregl.Marker`, so asset markers are plain `<div>` elements repositioned on every camera event via `map.project()`. |
| **Point-in-polygon hit-test** | Classic even-odd ray-cast algorithm against pre-parsed polygon rings. Runs entirely client-side with no server round-trip. |

---

## 6. Startup Flow

```
systemd start → gunicorn (main.py)
                    ↓
              imports server.py → Flask app created
                    ↓
              Binds 0.0.0.0:9120 with 4 workers
                    ↓
         Browser requests GET /
                    ↓
         Receives full HTML page
                    ↓
     ┌──────────────┼──────────────┐
     ↓              ↓              ↓
  Init Mappls    Fetch polygon   Load assets
  Map + Three.js  index + coords  from Overpass
     ↓              ↓
  Add 3D layer   Prefetch chunks
     ↓           0 & 1
  Ready — user interacts with
  time slider, search, layers
```
