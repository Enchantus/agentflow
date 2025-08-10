/* globals LiteGraph, LGraph, LGraphCanvas */

const $ = (s) => document.querySelector(s);

let graph, canvas, nodeDefs = {}, idToNode = {}, model = null;

// ---------- Canvas boot ----------
function initCanvas() {
  graph = new LGraph();
  canvas = new LGraphCanvas("#canvas", graph);

  // dark theme
  canvas.clear_background = true;
  canvas.background_image = "";
  canvas.ds.clear_color = "#111216";

  // snap-to-grid
  canvas.grid = 24;
  canvas.align_to_grid = true;

  // draw custom grid + style via hook (muted orange)
  canvas.onDrawBackground = function(ctx) {
    const step = this.grid || 24;
    const w = this.canvas.width, h = this.canvas.height;
    const off = this.ds.offset;
    const scale = this.ds.scale;
    ctx.save();
    ctx.fillStyle = "#111216";
    ctx.fillRect(0, 0, w, h);
    ctx.strokeStyle = "rgba(245,158,11,0.12)";
    ctx.lineWidth = 1;
    ctx.beginPath();
    const ox = -((off[0] / scale) % step), oy = -((off[1] / scale) % step);
    for (let x = ox; x < w; x += step) { ctx.moveTo(x, 0); ctx.lineTo(x, h); }
    for (let y = oy; y < h; y += step) { ctx.moveTo(0, y); ctx.lineTo(w, y); }
    ctx.stroke();
    ctx.restore();
  };

  // square-beveled links (orthogonal with small rounding)
  const R = 8;
  const drawOrthLink = function(ctx, start, end) {
    const midX = (start[0] + end[0]) / 2;
    ctx.beginPath();
    ctx.moveTo(start[0], start[1]);

    // horizontal to midX with small bevel
    let x1 = start[0], y1 = start[1], x2 = midX, y2 = start[1];
    if (Math.abs(y2 - end[1]) > R) {
      ctx.lineTo(x2 - R, y2);
      ctx.quadraticCurveTo(x2, y2, x2, y2 + Math.sign(end[1] - y2) * R);
    } else {
      ctx.lineTo(x2, y2);
    }

    // vertical toward end.y with bevel
    let vx = midX, vy = start[1], ty = end[1];
    if (Math.abs(ty - vy) > R) {
      ctx.lineTo(vx, ty - Math.sign(ty - vy) * R);
      ctx.quadraticCurveTo(vx, ty, vx + R, ty);
    } else {
      ctx.lineTo(vx, ty);
    }

    // horizontal to end
    ctx.lineTo(end[0], end[1]);
    ctx.stroke();
  };

  // monkey-patch connection rendering
  const _drawLink = canvas.drawLink;
  canvas.drawLink = function(ctx, a, b, link, color, selected, width) {
    ctx.save();
    ctx.strokeStyle = color || "#8892a6";
    ctx.lineWidth = width || 2;
    if (link && link.data && link.data.__exec) ctx.setLineDash([6, 5]); // exec edges dotted

    // call our orthogonal beveled drawer
    drawOrthLink(ctx, a, b);
    ctx.restore();
  };
}

// ---------- Node class factory ----------
function registerNodeTypes(defs) {
  defs.forEach(def => {
    nodeDefs[def.type] = def;

    function AFNode() { this.title = def.type; this.color = "#1b2130"; this.bgcolor = "#0f1320"; }
    AFNode.title = def.type;
    AFNode.prototype.onConfigure = function(o) { this.properties = (o && o.params) || {}; };
    AFNode.prototype.onDrawForeground = function(ctx) {
      if (this.__state === "running") {
        ctx.strokeStyle = getComputedStyle(document.body).getPropertyValue("--running").trim();
        ctx.lineWidth = 2.5; ctx.strokeRect(1,1,this.size[0]-2,this.size[1]-2);
      } else if (this.__state === "done") {
        ctx.strokeStyle = getComputedStyle(document.body).getPropertyValue("--active").trim();
        ctx.lineWidth = 2; ctx.strokeRect(1,1,this.size[0]-2,this.size[1]-2);
      }
    };
    AFNode.prototype.onAdded = function() {
      // inputs
      const inputs = def.inputs || {};
      if (inputs) for (const name of Object.keys(inputs)) this.addInput(name, inputs[name] || "*");
      // outputs
      const outputs = def.outputs || {};
      if (outputs) for (const name of Object.keys(outputs)) this.addOutput(name, outputs[name] || "*");
      // exec ports (visual only)
      this.addInput("exec", "exec");
      this.addOutput("out", "exec");
      this.size = this.computeSize();
    };

    LiteGraph.registerNodeType(def.type, AFNode);
  });
}

// ---------- Graph <-> Canvas sync ----------
function loadModelIntoCanvas(m) {
  model = m;
  graph.clear();
  idToNode = {};

  // add nodes
  for (const n of m.nodes) {
    const klass = LiteGraph.registered_node_types[n.type] ? n.type : null;
    const node = klass ? LiteGraph.createNode(klass) : new LiteGraph.LGraphNode(n.type);
    if (!node) continue;
    node.pos = n.position ? [n.position[0], n.position[1]] : [80, 60];
    node.properties = n.params || {};
    graph.add(node);
    idToNode[n.id] = node;
  }

  // data edges
  for (const e of m.edges.data) {
    const [sid, sport] = e.src, [did, dport] = e.dst;
    const sn = idToNode[sid], dn = idToNode[did];
    if (!sn || !dn) continue;

    const so = sn.findOutputSlot ? sn.findOutputSlot(sport) : 0;
    const di = dn.findInputSlot ? dn.findInputSlot(dport) : 0;
    if (so !== -1 && di !== -1) sn.connect(so, dn, di);
  }

  // exec edges (visual only, dotted)
  for (const e of m.edges.exec) {
    const sn = idToNode[e.src], dn = idToNode[e.dst];
    if (!sn || !dn) continue;
    const so = sn.findOutputSlot ? sn.findOutputSlot("out") : 0;
    const di = dn.findInputSlot ? dn.findInputSlot("exec") : 0;
    if (so !== -1 && di !== -1) {
      const link = sn.connect(so, dn, di);
      if (link) link.data = Object.assign({}, link.data || {}, { __exec: true });
    }
  }

  graph.start(); // enables animations / time callbacks if any
  canvas.draw(true, true);
}

async function fetchNodes() {
  const res = await fetch("/api/nodes");
  const json = await res.json();
  registerNodeTypes(json.nodes || []);
  renderPalette(json.nodes || []);
}

function renderPalette(defs) {
  const host = $("#palette");
  host.innerHTML = "";
  defs.forEach(def => {
    const span = document.createElement("span");
    span.className = "node-chip";
    span.textContent = def.type;
    span.draggable = true;
    span.addEventListener("dragstart", (ev) => {
      ev.dataTransfer.setData("text/plain", def.type);
    });
    host.appendChild(span);
  });

  const canvasEl = $("#canvas");
  canvasEl.addEventListener("dragover", (ev) => ev.preventDefault());
  canvasEl.addEventListener("drop", (ev) => {
    ev.preventDefault();
    const type = ev.dataTransfer.getData("text/plain");
    const node = LiteGraph.createNode(type);
    const rect = canvasEl.getBoundingClientRect();
    const x = (ev.clientX - rect.left) / canvas.ds.scale - canvas.ds.offset[0];
    const y = (ev.clientY - rect.top) / canvas.ds.scale - canvas.ds.offset[1];
    node.pos = [Math.round(x / canvas.grid) * canvas.grid, Math.round(y / canvas.grid) * canvas.grid];
    graph.add(node);
  });
}

async function fetchGraph() {
  const res = await fetch("/api/graph");
  const json = await res.json();
  loadModelIntoCanvas(json);
}

async function saveGraph() {
  // serialize back: positions + params only; edges from current links
  const nodes = graph._nodes.map((n, i) => {
    const id = Object.keys(idToNode).find(k => idToNode[k] === n) || `n${i}`;
    return {
      id, type: n.title, params: n.properties || {}, inputs: {},
      position: [Math.round(n.pos[0]), Math.round(n.pos[1])]
    };
  });

  const dataEdges = [];
  const execEdges = [];
  for (const l of graph.links) {
    if (!l) continue;
    const start = graph.getNodeById(l.origin_id);
    const end = graph.getNodeById(l.target_id);
    const sid = Object.keys(idToNode).find(k => idToNode[k] === start);
    const did = Object.keys(idToNode).find(k => idToNode[k] === end);
    if (!sid || !did) continue;
    const srcPort = start.outputs[l.origin_slot]?.name || "out";
    const dstPort = end.inputs[l.target_slot]?.name || "in";
    if (l.data && l.data.__exec) execEdges.push({ src: sid, dst: did });
    else dataEdges.push({ src: [sid, srcPort], dst: [did, dstPort] });
  }

  const payload = {
    version: model?.version || "0.2.0",
    meta: model?.meta || {},
    nodes, edges: { data: dataEdges, exec: execEdges }
  };
  await fetch("/api/graph", { method: "PUT", headers: { "Content-Type": "application/json" }, body: JSON.stringify(payload) });
}

async function runGraph() {
  const res = await fetch("/api/run", { method: "POST", headers: { "Content-Type": "application/json" }, body: "{}" });
  const json = await res.json();
  console.log("run result", json);
}

// ---------- WS step-debug highlighting ----------
function connectWS() {
  const ws = new WebSocket(`ws://${location.host}/ws/events`);
  ws.onopen = () => $("#status").textContent = "ws: connected";
  ws.onclose = () => $("#status").textContent = "ws: disconnected";
  ws.onmessage = (ev) => {
    const evt = JSON.parse(ev.data);
    if (evt.type === "NodeStarted") {
      const nid = evt.payload.node_id;
      const node = idToNode[nid];
      if (node) { node.__state = "running"; canvas.draw(true, true); }
    } else if (evt.type === "NodeFinished") {
      const nid = evt.payload.node_id;
      const node = idToNode[nid];
      if (node) {
        node.__state = "done";
        setTimeout(() => { node.__state = undefined; canvas.draw(true, true); }, 800);
        canvas.draw(true, true);
      }
    }
  };
}

// ---------- Toolbar ----------
function initToolbar() {
  $("#btn-import").onclick = () => $("#file").click();
  $("#file").onchange = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    const text = await file.text();
    const json = JSON.parse(text);
    await fetch("/api/graph", { method: "PUT", headers: {"Content-Type":"application/json"}, body: JSON.stringify(json) });
    await fetchGraph();
  };
  $("#btn-export").onclick = () => {
    const blob = new Blob([JSON.stringify(model, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url; a.download = (model?.meta?.id || "agentflow") + ".json"; a.click();
    URL.revokeObjectURL(url);
  };
  $("#btn-save").onclick = saveGraph;
  $("#btn-run").onclick = runGraph;
}

// ---------- boot ----------
initCanvas();
initToolbar();
connectWS();
fetchNodes().then(fetchGraph);
