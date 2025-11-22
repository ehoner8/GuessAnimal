// app.js
// Handles canvas grids, feature maps, highlighting, clicks, and guess logic.

// constants (match your Python version)
const IMG_SIZE = 30;
const FILTER_SIZE = 3;
const STRIDE = 3;
const FM_SIZE = IMG_SIZE / STRIDE; // 10
const CELL_SIZE = 20;              // visual size in CSS; canvas uses pixels (we'll scale)
const SCALE = CELL_SIZE;           // one logical cell equals CELL_SIZE px

// features order (match server)
const FEATURES = Object.keys(HARDCODED_MAPS);

// Client-side data structures
const userMaps = {};
const savedPositions = {}; // per-feature saved cursor positions: { feature: [r,c] }
let selectedFeature = FEATURES[0];
let cursorRow = null, cursorCol = null;
let imageRevealed = false;
let giraffeImage = null;
let imgCanvas, imgCtx;

// Initialize userMaps and savedPositions
for (const f of FEATURES) {
  userMaps[f] = Array.from({length: FM_SIZE}, () => Array(FM_SIZE).fill(null));
  savedPositions[f] = [null, null];
}

// --- UI build ---
function makeFilterButtons() {
  const container = document.getElementById('filter-buttons');
  container.innerHTML = '';
  for (const f of FEATURES) {
    const btn = document.createElement('button');
    btn.textContent = f.charAt(0).toUpperCase() + f.slice(1);
    btn.className = 'filter-btn' + (f === selectedFeature ? ' selected' : '');
    btn.onclick = () => selectFeature(f);
    container.appendChild(btn);
  }
}

function makeFeatureMapCanvases() {
  const fmContainer = document.getElementById('feature-maps');
  fmContainer.innerHTML = '';
  for (const f of FEATURES) {
    const card = document.createElement('div');
    card.className = 'fm-card';
    const label = document.createElement('div');
    label.textContent = f.charAt(0).toUpperCase() + f.slice(1) + ' Map';
    label.style.marginBottom = '4px';
    card.appendChild(label);

    const canvas = document.createElement('canvas');
    canvas.width = FM_SIZE * SCALE;
    canvas.height = FM_SIZE * SCALE;
    canvas.className = 'fm-canvas';
    canvas.dataset.feature = f;
    // clicking a FM cell could optionally move the cursor; we won't enable that yet
    card.appendChild(canvas);
    fmContainer.appendChild(card);
  }
}

function drawMainGrid() {
  imgCanvas.width = IMG_SIZE * SCALE;
  imgCanvas.height = IMG_SIZE * SCALE;
  imgCtx = imgCanvas.getContext('2d');
  // background black
  imgCtx.fillStyle = '#000';
  imgCtx.fillRect(0,0,imgCanvas.width,imgCanvas.height);
  // draw thin grid lines
  imgCtx.strokeStyle = '#333';
  for (let i=0;i<=IMG_SIZE;i++){
    // horizontal
    imgCtx.beginPath();
    imgCtx.moveTo(0,i*SCALE+0.5);
    imgCtx.lineTo(imgCanvas.width,i*SCALE+0.5);
    imgCtx.stroke();
    // vertical
    imgCtx.beginPath();
    imgCtx.moveTo(i*SCALE+0.5,0);
    imgCtx.lineTo(i*SCALE+0.5,imgCanvas.height);
    imgCtx.stroke();
  }
}

function drawAllFeatureMaps() {
  for (const f of FEATURES) drawFeatureMap(f);
}

function drawFeatureMap(feature) {
  // find its canvas
  const canvases = document.querySelectorAll('.fm-canvas');
  let canvas = null;
  canvases.forEach(c => { if (c.dataset.feature === feature) canvas = c; });
  if (!canvas) return;
  const ctx = canvas.getContext('2d');

  // clear
  ctx.fillStyle = '#fff';
  ctx.fillRect(0,0,canvas.width,canvas.height);

  // cell outlines
  ctx.strokeStyle = '#999';
  for (let r=0;r<FM_SIZE;r++){
    for (let c=0;c<FM_SIZE;c++){
      ctx.strokeRect(c*SCALE+0.5, r*SCALE+0.5, SCALE, SCALE);
    }
  }

  // filled cells from userMaps (red for 1, blue for 0)
  for (let r=0;r<FM_SIZE;r++){
    for (let c=0;c<FM_SIZE;c++){
      const color = userMaps[feature][r][c];
      if (color) {
        ctx.fillStyle = color;
        ctx.fillRect(c*SCALE+1, r*SCALE+1, SCALE-1, SCALE-1);
      }
    }
  }

  // Draw highlight if this is selected feature and has a saved position
  // (we draw overlay border by drawing a rectangle outline in yellow)
  // We'll manage highlight separately in updateHighlights()
}

function updateHighlights() {
  // Remove any previous fm highlight by redrawing border area
  for (const f of FEATURES){
    // redraw feature map fully to clear any old highlight
    drawFeatureMap(f);
  }

  // Draw highlight on selected feature if there is cursorRow/Col for it
  const [sr, sc] = savedPositions[selectedFeature];
  if (sr !== null && sc !== null) {
    // find canvas for selectedFeature
    const canvases = document.querySelectorAll('.fm-canvas');
    let canvas = null;
    canvases.forEach(c => { if (c.dataset.feature === selectedFeature) canvas = c; });
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    ctx.strokeStyle = 'yellow';
    ctx.lineWidth = 1;
    ctx.strokeRect(sc*SCALE+2, sr*SCALE+2, SCALE-4, SCALE-4);
  }
  // Draw the patch highlight on the main image as well
  drawImagePatch();
}

function drawImagePatch() {
  // redraw the main grid background (image might be shown, keep it)
  if (!imageRevealed) {
    // just redraw grid background
    imgCtx.fillStyle = '#000';
    imgCtx.fillRect(0,0,imgCanvas.width,imgCanvas.height);
    imgCtx.strokeStyle = '#333';
    for (let i=0;i<=IMG_SIZE;i++){
      imgCtx.beginPath();
      imgCtx.moveTo(0,i*SCALE+0.5); imgCtx.lineTo(imgCanvas.width,i*SCALE+0.5); imgCtx.stroke();
      imgCtx.beginPath();
      imgCtx.moveTo(i*SCALE+0.5,0); imgCtx.lineTo(i*SCALE+0.5,imgCanvas.height); imgCtx.stroke();
    }
  } else {
    // if image revealed, redraw image first (we keep overlaying patch)
    if (giraffeImage) {
      imgCtx.clearRect(0,0,imgCanvas.width,imgCanvas.height);
      imgCtx.drawImage(giraffeImage, 0, 0, imgCanvas.width, imgCanvas.height);
    }
  }

  // draw the patch if we have cursor position for selectedFeature
  const [sr, sc] = savedPositions[selectedFeature];
  if (sr !== null && sc !== null) {
    const top = sr * STRIDE * SCALE;
    const left = sc * STRIDE * SCALE;
    imgCtx.lineWidth = 3;
    imgCtx.strokeStyle = 'yellow';
    imgCtx.strokeRect(left+2, top+2, FILTER_SIZE*SCALE-4, FILTER_SIZE*SCALE-4);
  }
}

// --- Event handlers & logic ---

function selectFeature(feature) {
  // Save current cursor position for current selectedFeature
  // (cursorRow/Col are already saved by click/move handlers)
  // switch selected
  selectedFeature = feature;
  // update UI selected button
  document.querySelectorAll('.filter-btn').forEach(btn => {
    btn.classList.toggle('selected', btn.textContent.toLowerCase() === feature);
  });

  // restore saved cursor for this feature
  const [sr, sc] = savedPositions[feature];
  if (sr !== null && sc !== null) {
    cursorRow = sr; cursorCol = sc;
  } else {
    cursorRow = null; cursorCol = null;
  }

  // redraw FM canvases and highlights
  drawAllFeatureMaps();
  updateHighlights();
}

function applyFilterAt(r, c) {
  // r,c are fm indices (0..FM_SIZE-1)
  const truth = HARDCODED_MAPS[selectedFeature][r][c]; // 0/1
  const color = truth ? 'red' : 'blue'; // 1->red, 0->blue (matches your Tkinter)
  userMaps[selectedFeature][r][c] = color;
  savedPositions[selectedFeature] = [r, c]; // update memory
  drawFeatureMap(selectedFeature);
  updateHighlights();
}

function onCanvasClick(ev) {
  // compute clicked pixel -> cell index
  const rect = imgCanvas.getBoundingClientRect();
  const x = ev.clientX - rect.left;
  const y = ev.clientY - rect.top;
  const col = Math.floor(x / SCALE);
  const row = Math.floor(y / SCALE);
  const fmCol = Math.floor(col / STRIDE);
  const fmRow = Math.floor(row / STRIDE);
  if (fmRow < 0 || fmRow >= FM_SIZE || fmCol < 0 || fmCol >= FM_SIZE) return;

  cursorRow = fmRow; cursorCol = fmCol;
  // apply & save
  applyFilterAt(fmRow, fmCol);
}

function onKey(e) {
  if (e.key === 'ArrowLeft') {
    if (cursorCol === null) { cursorCol = 0; cursorRow = 0; }
    if (cursorCol > 0) cursorCol -= 1;
    applyFilterAt(cursorRow, cursorCol);
  } else if (e.key === 'ArrowRight') {
    if (cursorCol === null) { cursorCol = 0; cursorRow = 0; }
    if (cursorCol < FM_SIZE - 1) cursorCol += 1;
    applyFilterAt(cursorRow, cursorCol);
  } else if (e.key === 'ArrowUp') {
    if (cursorRow === null) { cursorRow = 0; cursorCol = 0; }
    if (cursorRow > 0) cursorRow -= 1;
    applyFilterAt(cursorRow, cursorCol);
  } else if (e.key === 'ArrowDown') {
    if (cursorRow === null) { cursorRow = 0; cursorCol = 0; }
    if (cursorRow < FM_SIZE - 1) cursorRow += 1;
    applyFilterAt(cursorRow, cursorCol);
  }
}

// Guess handling
function onGuess() {
  const input = document.getElementById('guessInput');
  const feedback = document.getElementById('guessFeedback');
  const val = (input.value || '').trim().toLowerCase();
  if (val === 'giraffe') {
    feedback.textContent = 'Correct!';
    feedback.style.color = 'green';
    revealImage();
  } else {
    feedback.textContent = '❌ Incorrect!';
    feedback.style.color = 'red';
  }
}

function revealImage() {
  // load image and draw on main canvas, but keep drawing overlays (patch highlight)
  if (!GIRAFFE_URL) return;
  giraffeImage = new Image();
  giraffeImage.crossOrigin = "anonymous";
  giraffeImage.onload = () => {
    imageRevealed = true;
    drawImagePatch();
  };
  giraffeImage.onerror = () => {
    // fallback: keep black background and show message
    const fb = document.getElementById('guessFeedback');
    fb.textContent = '(unable to load giraffe image)';
    fb.style.color = 'orange';
  };
  giraffeImage.src = GIRAFFE_URL;
}

// --- startup ---
function init() {
  // build UI
  makeFilterButtons();
  makeFeatureMapCanvases();

  imgCanvas = document.getElementById('imgCanvas');
  drawMainGrid();
  drawAllFeatureMaps();
  updateHighlights();

  // attach events
  imgCanvas.addEventListener('click', onCanvasClick);
  window.addEventListener('keydown', onKey);
  document.getElementById('guessBtn').addEventListener('click', onGuess);
}

window.addEventListener('load', init);
