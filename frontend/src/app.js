import { fetchSnapshots, fetchMetadata, fetchComparison } from './api.js';

// --- APPLICATION STATE ---
const state = {
  currentUrl: '',
  normalizedUrl: '',
  snapshotsData: null,
  selectedYear: null,
  selectedTimestamp: null,
  viewMode: 'single', // 'single' | 'compare'
  
  // Compare mode specific
  compareYearA: null,
  compareTimestampA: null,
  compareYearB: null,
  compareTimestampB: null,
  syncScroll: true,

  // Cache of fetched metadata
  metadataCache: new Map(),
  isLoading: false
};

// --- DOM ELEMENTS ---
const elements = {
  searchForm: document.getElementById('searchForm'),
  urlInput: document.getElementById('urlInput'),
  btnClearUrl: document.getElementById('btnClearUrl'),
  btnSearch: document.getElementById('btnSearch'),
  searchSpinner: document.getElementById('searchSpinner'),
  presetChips: document.querySelectorAll('.preset-chip'),

  viewModeTabs: document.getElementById('viewModeTabs'),
  modeSingleBtn: document.getElementById('modeSingleBtn'),
  modeCompareBtn: document.getElementById('modeCompareBtn'),
  systemStatusBadge: document.getElementById('systemStatusBadge'),
  statusText: document.getElementById('statusText'),

  timelineSection: document.getElementById('timelineSection'),
  currentSiteTag: document.getElementById('currentSiteTag'),
  archiveSpanPill: document.getElementById('archiveSpanPill'),
  totalCapturesPill: document.getElementById('totalCapturesPill'),
  densityBars: document.getElementById('densityBars'),
  yearSlider: document.getElementById('yearSlider'),
  activeYearBubble: document.getElementById('activeYearBubble'),
  yearTicks: document.getElementById('yearTicks'),
  selectedYearLabel: document.getElementById('selectedYearLabel'),
  captureSelect: document.getElementById('captureSelect'),

  btnJumpFirst: document.getElementById('btnJumpFirst'),
  btnJumpMid: document.getElementById('btnJumpMid'),
  btnJumpLatest: document.getElementById('btnJumpLatest'),
  btnJumpRandom: document.getElementById('btnJumpRandom'),

  welcomeState: document.getElementById('welcomeState'),
  loadingState: document.getElementById('loadingState'),
  loadingStatusText: document.getElementById('loadingStatusText'),
  errorState: document.getElementById('errorState'),
  errorTitle: document.getElementById('errorTitle'),
  errorMessage: document.getElementById('errorMessage'),
  btnErrorRetry: document.getElementById('btnErrorRetry'),

  // Single Viewer
  singleViewerContainer: document.getElementById('singleViewerContainer'),
  singleViewerYear: document.getElementById('singleViewerYear'),
  singleViewerTimestamp: document.getElementById('singleViewerTimestamp'),
  singleArchiveLink: document.getElementById('singleArchiveLink'),
  btnReloadSingle: document.getElementById('btnReloadSingle'),
  btnFullscreenSingle: document.getElementById('btnFullscreenSingle'),
  btnSwitchToCompare: document.getElementById('btnSwitchToCompare'),
  singleIframeWrapper: document.getElementById('singleIframeWrapper'),
  singleIframe: document.getElementById('singleIframe'),

  metaHtmlSize: document.getElementById('metaHtmlSize'),
  metaDomNodes: document.getElementById('metaDomNodes'),
  metaImages: document.getElementById('metaImages'),
  metaResources: document.getElementById('metaResources'),
  metaMobileStatus: document.getElementById('metaMobileStatus'),
  metaFrameworkTags: document.getElementById('metaFrameworkTags'),

  // Compare Viewer
  compareViewerContainer: document.getElementById('compareViewerContainer'),
  compareYearSelectA: document.getElementById('compareYearSelectA'),
  compareCaptureSelectA: document.getElementById('compareCaptureSelectA'),
  compareYearSelectB: document.getElementById('compareYearSelectB'),
  compareCaptureSelectB: document.getElementById('compareCaptureSelectB'),
  btnSyncScroll: document.getElementById('btnSyncScroll'),
  btnToggleDiffDrawer: document.getElementById('btnToggleDiffDrawer'),
  btnCloseDiffDrawer: document.getElementById('btnCloseDiffDrawer'),
  diffDrawer: document.getElementById('diffDrawer'),
  diffErasLabel: document.getElementById('diffErasLabel'),
  diffStatsGrid: document.getElementById('diffStatsGrid'),
  paneBannerA: document.getElementById('paneBannerA'),
  paneBannerB: document.getElementById('paneBannerB'),
  compareIframeA: document.getElementById('compareIframeA'),
  compareIframeB: document.getElementById('compareIframeB')
};

// --- INITIALIZATION ---
function init() {
  setupEventListeners();
  // Auto-explore initial default or apple.com
  const initialUrl = elements.urlInput.value.trim();
  if (initialUrl) {
    loadWebsiteHistory(initialUrl);
  }
}

// --- EVENT LISTENERS ---
function setupEventListeners() {
  // Search Form
  elements.searchForm.addEventListener('submit', (e) => {
    e.preventDefault();
    const url = elements.urlInput.value.trim();
    if (url) loadWebsiteHistory(url);
  });

  // Input Clear Button
  elements.urlInput.addEventListener('input', () => {
    elements.btnClearUrl.style.display = elements.urlInput.value ? 'block' : 'none';
  });

  elements.btnClearUrl.addEventListener('click', () => {
    elements.urlInput.value = '';
    elements.btnClearUrl.style.display = 'none';
    elements.urlInput.focus();
  });

  // Preset Chips
  elements.presetChips.forEach(chip => {
    chip.addEventListener('click', () => {
      const url = chip.getAttribute('data-url');
      const targetYear = parseInt(chip.getAttribute('data-year'), 10);
      elements.urlInput.value = url;
      elements.btnClearUrl.style.display = 'block';
      loadWebsiteHistory(url, targetYear);
    });
  });

  // Mode Switcher Tabs
  elements.modeSingleBtn.addEventListener('click', () => switchViewMode('single'));
  elements.modeCompareBtn.addEventListener('click', () => switchViewMode('compare'));
  elements.btnSwitchToCompare.addEventListener('click', () => switchViewMode('compare'));

  // Timeline Slider
  elements.yearSlider.addEventListener('input', (e) => {
    const year = parseInt(e.target.value, 10);
    onYearSelected(year);
  });

  // Sub-timeline capture dropdown
  elements.captureSelect.addEventListener('change', (e) => {
    const ts = e.target.value;
    if (ts) selectTimestamp(ts);
  });

  // Quick Jumps
  elements.btnJumpFirst.addEventListener('click', jumpToFirstYear);
  elements.btnJumpMid.addEventListener('click', jumpToMidYear);
  elements.btnJumpLatest.addEventListener('click', jumpToLatestYear);
  elements.btnJumpRandom.addEventListener('click', jumpToRandomYear);

  // Single Viewer Tools
  elements.btnReloadSingle.addEventListener('click', () => {
    if (elements.singleIframe.src) {
      elements.singleIframe.src = elements.singleIframe.src;
    }
  });

  elements.btnFullscreenSingle.addEventListener('click', () => {
    if (!document.fullscreenElement) {
      elements.singleIframeWrapper.requestFullscreen().catch(err => console.warn(err));
    } else {
      document.exitFullscreen().catch(err => console.warn(err));
    }
  });

  // Compare Era Selectors
  elements.compareYearSelectA.addEventListener('change', (e) => {
    const yr = parseInt(e.target.value, 10);
    state.compareYearA = yr;
    populateCompareCaptures('A', yr);
  });

  elements.compareCaptureSelectA.addEventListener('change', (e) => {
    state.compareTimestampA = e.target.value;
    updateCompareView();
  });

  elements.compareYearSelectB.addEventListener('change', (e) => {
    const yr = parseInt(e.target.value, 10);
    state.compareYearB = yr;
    populateCompareCaptures('B', yr);
  });

  elements.compareCaptureSelectB.addEventListener('change', (e) => {
    state.compareTimestampB = e.target.value;
    updateCompareView();
  });

  // Diff Drawer Controls
  elements.btnToggleDiffDrawer.addEventListener('click', () => {
    elements.diffDrawer.classList.toggle('open');
  });

  elements.btnCloseDiffDrawer.addEventListener('click', () => {
    elements.diffDrawer.classList.remove('open');
  });

  // Sync Scroll Toggle
  elements.btnSyncScroll.addEventListener('click', () => {
    state.syncScroll = !state.syncScroll;
    elements.btnSyncScroll.classList.toggle('active', state.syncScroll);
  });

  // Retry Button
  elements.btnErrorRetry.addEventListener('click', () => {
    elements.urlInput.focus();
    elements.urlInput.select();
  });
}

// --- CORE ACTIONS ---
async function loadWebsiteHistory(url, preferredYear = null) {
  state.currentUrl = url;
  setLoading(true, `Querying Wayback CDX archives for ${url}...`);

  try {
    const data = await fetchSnapshots(url);
    state.snapshotsData = data;
    state.normalizedUrl = data.normalized_url;

    if (!data.snapshots || data.snapshots.length === 0) {
      showError('No Archives Found', `No historical captures were found for "${url}". The site might be unarchived or excluded by robots.txt.`);
      return;
    }

    // Update status badge
    updateStatusBadge(data.cached);

    // Build timeline
    renderTimeline(data, preferredYear);

    // Show appropriate view
    if (state.viewMode === 'single') {
      elements.singleViewerContainer.style.display = 'flex';
      elements.compareViewerContainer.style.display = 'none';
    } else {
      setupCompareModeDefaults();
      elements.singleViewerContainer.style.display = 'none';
      elements.compareViewerContainer.style.display = 'flex';
    }

    elements.welcomeState.style.display = 'none';
    elements.errorState.style.display = 'none';
    elements.timelineSection.style.display = 'block';

  } catch (err) {
    console.error('Error fetching snapshots:', err);
    showError('Archive Query Failed', err.message || 'Unable to connect to the Internet Time Machine backend.');
  } finally {
    setLoading(false);
  }
}

// --- TIMELINE RENDERING ---
function renderTimeline(data, preferredYear = null) {
  const years = data.years;
  if (!years || years.length === 0) return;

  const minYear = years[0].year;
  const maxYear = years[years.length - 1].year;

  // Header info pills
  elements.currentSiteTag.textContent = data.normalized_url;
  elements.archiveSpanPill.textContent = `${minYear} — ${maxYear}`;
  elements.totalCapturesPill.textContent = `${data.total_snapshots.toLocaleString()} snapshots`;

  // Slider bounds
  elements.yearSlider.min = minYear;
  elements.yearSlider.max = maxYear;

  // Pick initial year
  let initialYear = preferredYear || (years.length > 2 ? years[1].year : minYear);
  if (!years.some(y => y.year === initialYear)) {
    initialYear = minYear;
  }
  elements.yearSlider.value = initialYear;
  state.selectedYear = initialYear;

  // Render Density Bars
  const maxCount = Math.max(...years.map(y => y.count), 1);
  elements.densityBars.innerHTML = '';

  // Map of year -> YearDensity
  const yearDensityMap = new Map(years.map(y => [y.year, y]));

  for (let yr = minYear; yr <= maxYear; yr++) {
    const density = yearDensityMap.get(yr);
    const bar = document.createElement('div');
    bar.className = 'density-bar';
    bar.setAttribute('data-year', yr);

    if (density) {
      // Height scaled between 15% and 100%
      const heightPct = Math.max(15, Math.round((density.count / maxCount) * 100));
      bar.style.height = `${heightPct}%`;
      bar.title = `${yr}: ${density.count} captures`;
    } else {
      bar.style.height = '4px';
      bar.style.opacity = '0.2';
      bar.title = `${yr}: 0 captures`;
    }

    if (yr === initialYear) bar.classList.add('active');

    bar.addEventListener('click', () => {
      onYearSelected(yr);
    });

    elements.densityBars.appendChild(bar);
  }

  // Render Year Ticks (every 4-5 years)
  elements.yearTicks.innerHTML = '';
  const step = Math.max(1, Math.round((maxYear - minYear) / 6));
  for (let yr = minYear; yr <= maxYear; yr += step) {
    const tick = document.createElement('span');
    tick.className = 'year-tick';
    tick.textContent = yr;
    tick.addEventListener('click', () => onYearSelected(yr));
    elements.yearTicks.appendChild(tick);
  }
  // Ensure maxYear is shown
  if ((maxYear - minYear) % step !== 0) {
    const lastTick = document.createElement('span');
    lastTick.className = 'year-tick';
    lastTick.textContent = maxYear;
    lastTick.addEventListener('click', () => onYearSelected(maxYear));
    elements.yearTicks.appendChild(lastTick);
  }

  onYearSelected(initialYear);
}

function onYearSelected(year) {
  state.selectedYear = year;
  elements.yearSlider.value = year;
  elements.selectedYearLabel.textContent = year;

  // Update floating year bubble position & text
  if (elements.activeYearBubble) {
    elements.activeYearBubble.textContent = year;
    const min = parseInt(elements.yearSlider.min, 10) || 1996;
    const max = parseInt(elements.yearSlider.max, 10) || 2026;
    const pct = max > min ? ((year - min) / (max - min)) * 100 : 50;
    const thumbOffset = (10 - 20 * (pct / 100));
    elements.activeYearBubble.style.left = `calc(${pct}% + ${thumbOffset}px)`;
  }

  // Update active density bar
  document.querySelectorAll('.density-bar').forEach(b => {
    b.classList.toggle('active', parseInt(b.getAttribute('data-year'), 10) === year);
  });

  // Filter snapshots for this year
  const yearSnapshots = state.snapshotsData.snapshots.filter(s => s.year === year);

  elements.captureSelect.innerHTML = '';
  if (yearSnapshots.length === 0) {
    const opt = document.createElement('option');
    opt.value = '';
    opt.textContent = `No captures in ${year} (scrub to nearby year)`;
    elements.captureSelect.appendChild(opt);
    return;
  }

  yearSnapshots.forEach((snap, idx) => {
    const opt = document.createElement('option');
    opt.value = snap.timestamp;
    opt.textContent = `${snap.date} (${formatBytes(snap.length)})`;
    elements.captureSelect.appendChild(opt);
  });

  // Pick middle or first capture of the year
  const midIdx = Math.floor(yearSnapshots.length / 2);
  const targetSnap = yearSnapshots[midIdx];
  elements.captureSelect.value = targetSnap.timestamp;
  selectTimestamp(targetSnap.timestamp);
}

function selectTimestamp(timestamp) {
  state.selectedTimestamp = timestamp;
  const snap = state.snapshotsData.snapshots.find(s => s.timestamp === timestamp);
  if (!snap) return;

  // Update single viewer
  elements.singleViewerYear.textContent = snap.year;
  elements.singleViewerTimestamp.textContent = snap.date;
  elements.singleArchiveLink.href = snap.playback_url;

  // Load clean playback URL in iframe
  elements.singleIframe.src = snap.clean_playback_url;

  // Load metadata
  loadMetadata(state.normalizedUrl, timestamp);
}

// --- METADATA LOADING ---
async function loadMetadata(url, timestamp) {
  // Clear existing pills to loading placeholder
  elements.metaHtmlSize.textContent = '...';
  elements.metaDomNodes.textContent = '...';
  elements.metaImages.textContent = '...';
  elements.metaResources.textContent = '...';
  elements.metaMobileStatus.textContent = '...';
  elements.metaFrameworkTags.innerHTML = '<span class="meta-tag">Analyzing DOM...</span>';

  try {
    const cacheKey = `${url}:${timestamp}`;
    let meta = state.metadataCache.get(cacheKey);

    if (!meta) {
      meta = await fetchMetadata(url, timestamp);
      state.metadataCache.set(cacheKey, meta);
    }

    elements.metaHtmlSize.textContent = formatBytes(meta.html_size_bytes);
    elements.metaDomNodes.textContent = meta.dom_node_count.toLocaleString();
    elements.metaImages.textContent = meta.image_count.toString();
    elements.metaResources.textContent = meta.external_resource_count.toString();
    
    if (meta.has_mobile_viewport) {
      elements.metaMobileStatus.textContent = '✓ Responsive';
      elements.metaMobileStatus.style.color = 'var(--accent-emerald)';
    } else {
      elements.metaMobileStatus.textContent = '✗ Desktop Only';
      elements.metaMobileStatus.style.color = 'var(--accent-amber)';
    }

    // Framework chips
    elements.metaFrameworkTags.innerHTML = '';
    if (meta.detected_frameworks && meta.detected_frameworks.length > 0) {
      meta.detected_frameworks.forEach(fw => {
        const tag = document.createElement('span');
        tag.className = 'meta-tag highlight';
        tag.textContent = fw;
        elements.metaFrameworkTags.appendChild(tag);
      });
    } else {
      const tag = document.createElement('span');
      tag.className = 'meta-tag';
      tag.textContent = 'Standard Vanilla HTML';
      elements.metaFrameworkTags.appendChild(tag);
    }

  } catch (err) {
    console.warn('Metadata load error:', err);
    elements.metaHtmlSize.textContent = 'N/A';
    elements.metaDomNodes.textContent = 'N/A';
    elements.metaImages.textContent = 'N/A';
    elements.metaResources.textContent = 'N/A';
    elements.metaMobileStatus.textContent = 'N/A';
    elements.metaFrameworkTags.innerHTML = '<span class="meta-tag">Unavailable</span>';
  }
}

// --- QUICK JUMPS ---
function jumpToFirstYear() {
  if (!state.snapshotsData?.years?.length) return;
  const firstYear = state.snapshotsData.years[0].year;
  onYearSelected(firstYear);
}

function jumpToMidYear() {
  if (!state.snapshotsData?.years?.length) return;
  const years = state.snapshotsData.years;
  const midYear = years[Math.floor(years.length / 2)].year;
  onYearSelected(midYear);
}

function jumpToLatestYear() {
  if (!state.snapshotsData?.years?.length) return;
  const years = state.snapshotsData.years;
  const latestYear = years[years.length - 1].year;
  onYearSelected(latestYear);
}

function jumpToRandomYear() {
  if (!state.snapshotsData?.years?.length) return;
  const years = state.snapshotsData.years;
  const randomYear = years[Math.floor(Math.random() * years.length)].year;
  onYearSelected(randomYear);
}

// --- COMPARE MODE ---
function switchViewMode(mode) {
  state.viewMode = mode;
  elements.modeSingleBtn.classList.toggle('active', mode === 'single');
  elements.modeCompareBtn.classList.toggle('active', mode === 'compare');

  if (!state.snapshotsData) return;

  if (mode === 'single') {
    elements.singleViewerContainer.style.display = 'flex';
    elements.compareViewerContainer.style.display = 'none';
    if (state.selectedTimestamp) {
      selectTimestamp(state.selectedTimestamp);
    }
  } else {
    elements.singleViewerContainer.style.display = 'none';
    elements.compareViewerContainer.style.display = 'flex';
    setupCompareModeDefaults();
  }
}

function setupCompareModeDefaults() {
  const years = state.snapshotsData.years;
  if (!years || years.length === 0) return;

  // Populate Year A & B dropdowns
  elements.compareYearSelectA.innerHTML = '';
  elements.compareYearSelectB.innerHTML = '';

  years.forEach(y => {
    const optA = document.createElement('option');
    optA.value = y.year;
    optA.textContent = `${y.year} (${y.count} caps)`;
    elements.compareYearSelectA.appendChild(optA);

    const optB = document.createElement('option');
    optB.value = y.year;
    optB.textContent = `${y.year} (${y.count} caps)`;
    elements.compareYearSelectB.appendChild(optB);
  });

  // Pick distinct default eras: Year A = first archive year, Year B = latest or mid year
  const defaultYearA = years[0].year;
  const defaultYearB = years.length > 1 ? years[years.length - 1].year : years[0].year;

  state.compareYearA = defaultYearA;
  elements.compareYearSelectA.value = defaultYearA;
  populateCompareCaptures('A', defaultYearA);

  state.compareYearB = defaultYearB;
  elements.compareYearSelectB.value = defaultYearB;
  populateCompareCaptures('B', defaultYearB);
}

function populateCompareCaptures(side, year) {
  const select = side === 'A' ? elements.compareCaptureSelectA : elements.compareCaptureSelectB;
  select.innerHTML = '';

  const snaps = state.snapshotsData.snapshots.filter(s => s.year === year);
  if (snaps.length === 0) return;

  snaps.forEach(s => {
    const opt = document.createElement('option');
    opt.value = s.timestamp;
    opt.textContent = s.date;
    select.appendChild(opt);
  });

  const repSnap = snaps[Math.floor(snaps.length / 2)];
  select.value = repSnap.timestamp;

  if (side === 'A') {
    state.compareTimestampA = repSnap.timestamp;
  } else {
    state.compareTimestampB = repSnap.timestamp;
  }

  updateCompareView();
}

async function updateCompareView() {
  const tsA = state.compareTimestampA;
  const tsB = state.compareTimestampB;
  if (!tsA || !tsB) return;

  const snapA = state.snapshotsData.snapshots.find(s => s.timestamp === tsA);
  const snapB = state.snapshotsData.snapshots.find(s => s.timestamp === tsB);

  if (snapA) {
    elements.paneBannerA.textContent = `${snapA.year} Archive (${snapA.date})`;
    elements.compareIframeA.src = snapA.clean_playback_url;
  }

  if (snapB) {
    elements.paneBannerB.textContent = `${snapB.year} Archive (${snapB.date})`;
    elements.compareIframeB.src = snapB.clean_playback_url;
  }

  elements.diffErasLabel.textContent = `${snapA?.year || 'Era A'} vs ${snapB?.year || 'Era B'}`;

  // Fetch structural diff
  try {
    const compData = await fetchComparison(state.normalizedUrl, tsA, tsB);
    renderDiffStats(compData);
  } catch (err) {
    console.warn('Compare diff failed:', err);
  }
}

function renderDiffStats(compData) {
  const diff = compData.diff;
  const snapA = compData.snapshot_a;
  const snapB = compData.snapshot_b;

  const htmlSizeBadge = diff.html_size_delta > 0 
    ? `<span class="delta-badge increase">+${formatBytes(diff.html_size_delta)} (+${diff.html_size_change_pct}%)</span>`
    : `<span class="delta-badge decrease">${formatBytes(diff.html_size_delta)} (${diff.html_size_change_pct}%)</span>`;

  const domBadge = diff.dom_node_delta > 0 
    ? `<span class="delta-badge increase">+${diff.dom_node_delta} nodes</span>`
    : `<span class="delta-badge decrease">${diff.dom_node_delta} nodes</span>`;

  const imgBadge = diff.image_count_delta > 0 
    ? `<span class="delta-badge increase">+${diff.image_count_delta} images</span>`
    : `<span class="delta-badge neutral">${diff.image_count_delta} images</span>`;

  const resBadge = diff.external_resource_delta > 0 
    ? `<span class="delta-badge increase">+${diff.external_resource_delta} resources</span>`
    : `<span class="delta-badge neutral">${diff.external_resource_delta} resources</span>`;

  elements.diffStatsGrid.innerHTML = `
    <div class="diff-stat-card">
      <span class="diff-stat-title">Page Byte Weight</span>
      <div class="diff-stat-values">
        <span class="val-a">${formatBytes(snapA.html_size_bytes)}</span>
        <span class="diff-arrow">→</span>
        <span class="val-b">${formatBytes(snapB.html_size_bytes)}</span>
      </div>
      ${htmlSizeBadge}
    </div>

    <div class="diff-stat-card">
      <span class="diff-stat-title">DOM Node Complexity</span>
      <div class="diff-stat-values">
        <span class="val-a">${snapA.dom_node_count}</span>
        <span class="diff-arrow">→</span>
        <span class="val-b">${snapB.dom_node_count}</span>
      </div>
      ${domBadge}
    </div>

    <div class="diff-stat-card">
      <span class="diff-stat-title">Image Assets</span>
      <div class="diff-stat-values">
        <span class="val-a">${snapA.image_count}</span>
        <span class="diff-arrow">→</span>
        <span class="val-b">${snapB.image_count}</span>
      </div>
      ${imgBadge}
    </div>

    <div class="diff-stat-card">
      <span class="diff-stat-title">External Resources</span>
      <div class="diff-stat-values">
        <span class="val-a">${snapA.external_resource_count}</span>
        <span class="diff-arrow">→</span>
        <span class="val-b">${snapB.external_resource_count}</span>
      </div>
      ${resBadge}
    </div>

    <div class="diff-stat-card">
      <span class="diff-stat-title">Mobile Readiness Transition</span>
      <div class="diff-stat-values">
        <span class="val-b" style="font-size:0.85rem;">${diff.mobile_viewport_transition}</span>
      </div>
    </div>

    <div class="framework-diff-card">
      <span class="diff-stat-title">Web Technology Evolution</span>
      <div class="fw-diff-sections">
        <div class="fw-section">
          <h5>Added Technologies:</h5>
          <div class="fw-pill-list">
            ${diff.frameworks_added.length > 0 
              ? diff.frameworks_added.map(f => `<span class="fw-pill added">+ ${f}</span>`).join('') 
              : '<span class="meta-tag">None detected</span>'}
          </div>
        </div>
        <div class="fw-section">
          <h5>Phased Out Technologies:</h5>
          <div class="fw-pill-list">
            ${diff.frameworks_removed.length > 0 
              ? diff.frameworks_removed.map(f => `<span class="fw-pill removed">- ${f}</span>`).join('') 
              : '<span class="meta-tag">None detected</span>'}
          </div>
        </div>
      </div>
    </div>
  `;
}

// --- UTILITIES & UI STATES ---
function setLoading(loading, message = 'Loading historical archives...') {
  state.isLoading = loading;
  elements.searchSpinner.style.display = loading ? 'inline-block' : 'none';
  elements.btnSearch.disabled = loading;
  elements.loadingStatusText.textContent = message;

  if (loading) {
    elements.loadingState.style.display = 'flex';
    elements.welcomeState.style.display = 'none';
    elements.errorState.style.display = 'none';
  } else {
    elements.loadingState.style.display = 'none';
  }
}

function showError(title, msg) {
  elements.errorTitle.textContent = title;
  elements.errorMessage.textContent = msg;
  elements.errorState.style.display = 'flex';
  elements.welcomeState.style.display = 'none';
  elements.timelineSection.style.display = 'none';
  elements.singleViewerContainer.style.display = 'none';
  elements.compareViewerContainer.style.display = 'none';
}

function updateStatusBadge(cached) {
  elements.systemStatusBadge.classList.toggle('cached', cached);
  elements.statusText.textContent = cached ? 'Cached (SQLite)' : 'Live (CDX API)';
}

function formatBytes(bytes, decimals = 1) {
  if (!bytes || bytes === 0) return '0 B';
  const k = 1024;
  const dm = decimals < 0 ? 0 : decimals;
  const sizes = ['B', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
}

// Run app
document.addEventListener('DOMContentLoaded', init);
