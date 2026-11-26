---
title: Indicadores do INE
layout: default
permalink: /dados/ine/
---
# Indicadores do INE

Estatísticas do INE para os Açores, por concelho e, quando o INE as publica,
por freguesia. Escolha um indicador. A tabela mostra um local por linha e um
período por coluna, com o total dos Açores em cima como referência.
Atualizado todas as semanas. Ver também os [outros dados abertos](/dados/).

<form id="ine-form" class="ine-form" onsubmit="return false">
  <div class="ine-row">
    <label class="ine-grow">Indicador
      <select id="ind"></select>
    </label>
  </div>
  <div class="ine-row">
    <label>Nível <select id="nivel"></select></label>
    <label>Ilha <select id="ilha"><option value="">todas</option></select></label>
    <label id="cat-wrap" hidden>Categoria <select id="cat"></select></label>
    <label class="ine-grow">Local <input type="search" id="q" placeholder="ex.: Rabo de Peixe, Horta" autocomplete="off"></label>
  </div>
  <label class="ine-check"><input type="checkbox" id="todos"> Mostrar todos os períodos</label>
</form>

<p id="estado" role="status" aria-live="polite">A carregar…</p>

<div id="painel" hidden>
  <h2 id="titulo"></h2>
  <p id="sub" class="ine-sub"></p>
  <div class="ine-scroll">
    <table id="tabela">
      <caption class="sr-only" id="legenda"></caption>
      <thead></thead>
      <tbody></tbody>
    </table>
  </div>
  <p id="nota" class="ine-sub"></p>
  <p><a id="exportar" href="#" download>Descarregar esta tabela (CSV)</a> ·
     <a href="/dados/ine.csv">todos os indicadores (ine.csv)</a></p>
</div>

<noscript><p>Esta página precisa de JavaScript. O ficheiro <a href="/dados/ine.csv">ine.csv</a> tem os mesmos dados.</p></noscript>

## Notas

- É uma seleção de indicadores, não a base de dados toda do INE. A lista está
  em [`bot/ine.py`](https://github.com/fmesqg/a-ores.net-site/blob/main/bot/ine.py).
  Os valores são os do INE no dia da recolha. O título de cada tabela liga ao
  indicador no site do INE, com a metainformação. É esse que se deve citar.
- "–" quer dizer que o INE não publica o valor. O INE não divulga valores com
  poucas observações. Por isso as medianas, o Gini e os rácios P80/P20 e
  P90/P10 só existem para as freguesias maiores, e as rendas e vendas de
  casas só para alguns concelhos. Os totais e as médias (sujeitos passivos,
  rendimento por sujeito passivo, fogos licenciados) cobrem todas as
  freguesias.
- As séries por concelho de população, turismo e câmaras começam em 2021,
  ano em que o INE passou a usar as NUTS 2024.
- Nos indicadores em % ou ‰, a variação é a diferença em pontos.
- Todos os indicadores num só ficheiro: [ine.csv](/dados/ine.csv), um valor
  por linha. Também está na base de dados SQLite (tabela `ine`), descrita em
  [Dados abertos](/dados/#consultar-em-sql).

<style>
.wrapper { max-width: min(1200px, 100%); }
.ine-row { display: flex; flex-wrap: wrap; gap: .5em 1em; align-items: flex-end; margin-bottom: .75em; }
.ine-row label { display: flex; flex-direction: column; margin: 0; min-width: 0; max-width: 100%; }
.ine-grow { flex: 1 1 16em; }
.ine-form select, .ine-form input { font: inherit; padding: .3em .4em; max-width: 100%; }
.ine-check { display: inline-flex; gap: .4em; align-items: center; margin-bottom: .5em; }
.ine-form select:focus-visible, .ine-form input:focus-visible, th button:focus-visible { outline: 3px solid #268bd2; outline-offset: 1px; }
#titulo { margin-bottom: .25em; font-size: 1.3em; }
.ine-sub { color: #586e75; font-size: .9em; }
.ine-scroll { overflow-x: auto; }
#tabela { font-size: .9em; border-collapse: collapse; width: auto; min-width: 100%; }
#tabela th, #tabela td { padding: .35em .6em; white-space: nowrap; }
#tabela td.num, #tabela th.num { text-align: right; font-variant-numeric: tabular-nums; }
#tabela td.lugar { white-space: normal; min-width: 9em; }
#tabela th:first-child, #tabela td:first-child { position: sticky; left: 0; background: #fdf6e3; z-index: 1; }
#tabela tr.ref td { font-weight: bold; border-bottom: 2px solid #93a1a1; }
#tabela td.ult { background-image: linear-gradient(to left, rgba(38,139,210,.18) var(--w, 0%), transparent var(--w, 0%)); }
#tabela td.falta { color: #93a1a1; }
#tabela td.sobe { color: #2d7a2d; }
#tabela td.desce { color: #b03a2e; }
th button { all: unset; cursor: pointer; font-weight: bold; }
th[aria-sort="ascending"] button::after { content: " ▲"; }
th[aria-sort="descending"] button::after { content: " ▼"; }
[hidden] { display: none !important; }
.sr-only { position: absolute; width: 1px; height: 1px; overflow: hidden; clip: rect(0 0 0 0); }
</style>

<script>
(function () {
  "use strict";
  var RECENT = 6;
  var $ = function (id) { return document.getElementById(id); };
  var fmt = new Intl.NumberFormat("pt-PT", { maximumFractionDigits: 2 });
  var pct = new Intl.NumberFormat("pt-PT", { maximumFractionDigits: 1, signDisplay: "exceptZero" });
  var fold = function (s) { return (s || "").normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase(); };
  var IND = {}, ORDER = [], st = { ind: "", nivel: "", ilha: "", cat: "", q: "", todos: false, ord: null, dir: -1 };
  var table = null; // { periods, ref, rows, cols } of the current view

  function parseCSV(text) {
    var rows = [], row = [], f = "", q = false, i = 0, c;
    if (text.charCodeAt(0) === 0xfeff) i = 1;
    for (; i < text.length; i++) {
      c = text[i];
      if (q) {
        if (c === '"') { if (text[i + 1] === '"') { f += '"'; i++; } else q = false; }
        else f += c;
      } else if (c === '"') q = true;
      else if (c === ",") { row.push(f); f = ""; }
      else if (c === "\n") { row.push(f); rows.push(row); row = []; f = ""; }
      else if (c !== "\r") f += c;
    }
    if (f || row.length) { row.push(f); rows.push(row); }
    var cols = rows.shift();
    return rows.map(function (r) { var o = {}; cols.forEach(function (k, j) { o[k] = r[j] || ""; }); return o; });
  }

  function index(rows) {
    rows.forEach(function (r) {
      var x = IND[r.varcd];
      if (!x) {
        x = IND[r.varcd] = { varcd: r.varcd, tema: r.tema, nome: r.indicador, unidade: r.unidade,
          atualizado: r.atualizado, url: r.url, rows: [], niveis: {}, cats: {} };
        ORDER.push(r.varcd);
      }
      x.rows.push(r); x.niveis[r.nivel] = 1; x.cats[r.categoria] = 1;
    });
  }

  function fillIndicators() {
    var sel = $("ind"), groups = {};
    ORDER.forEach(function (v) {
      var x = IND[v], g = groups[x.tema];
      if (!g) { g = groups[x.tema] = document.createElement("optgroup"); g.label = x.tema || "Outros"; sel.appendChild(g); }
      var o = document.createElement("option"); o.value = v; o.textContent = x.nome; g.appendChild(o);
    });
  }

  function fillSelect(sel, values, keep, first) {
    sel.innerHTML = "";
    if (first) { var o0 = document.createElement("option"); o0.value = ""; o0.textContent = first; sel.appendChild(o0); }
    values.forEach(function (v) { var o = document.createElement("option"); o.value = v; o.textContent = v; sel.appendChild(o); });
    sel.value = values.indexOf(keep) >= 0 ? keep : (first ? "" : values[0] || "");
    return sel.value;
  }

  function isRate(u) { return /%|‰/.test(u || ""); }

  function build() {
    var x = IND[st.ind];
    var niveis = ["Concelho", "Freguesia"].filter(function (n) { return x.niveis[n]; });
    st.nivel = fillSelect($("nivel"), niveis, st.nivel || "Concelho");
    var cats = Object.keys(x.cats).filter(Boolean).sort(function (a, b) { return a.localeCompare(b, "pt", { numeric: true }); });
    $("cat-wrap").hidden = !cats.length;
    st.cat = cats.length ? fillSelect($("cat"), cats, st.cat) : "";
    var ilhas = {};
    x.rows.forEach(function (r) { if (r.nivel === st.nivel && r.ilha) ilhas[r.ilha] = 1; });
    var ilhaOrder = ["Santa Maria", "São Miguel", "Terceira", "Graciosa", "São Jorge", "Pico", "Faial", "Flores", "Corvo"];
    st.ilha = fillSelect($("ilha"), ilhaOrder.filter(function (i) { return ilhas[i]; }), st.ilha, "todas");

    // Pivot: one row per place, one column per period.
    var periods = {}, places = {}, ref = null;
    x.rows.forEach(function (r) {
      if (r.categoria !== st.cat) return;
      if (r.nivel === "Região") { ref = ref || { local: "Açores", concelho: "", ilha: "", v: {} }; ref.v[r.data] = parseFloat(r.valor); }
      else if (r.nivel === st.nivel) {
        var p = places[r.geocod] || (places[r.geocod] = { local: r.local, concelho: r.concelho, ilha: r.ilha, v: {} });
        p.v[r.data] = parseFloat(r.valor);
      } else return;
      periods[r.data] = r.periodo;
    });
    var keys = Object.keys(periods).sort();
    var shown = st.todos ? keys : keys.slice(-RECENT);
    table = { all: keys, periods: shown, labels: periods, ref: ref, rows: Object.keys(places).map(function (k) { return places[k]; }) };
    $("todos").parentNode.hidden = keys.length <= RECENT;
    render();
  }

  function change(p, first, last, rate) {
    var a = p.v[first], b = p.v[last];
    if (first === last || isNaN(a) || isNaN(b)) return NaN;
    if (rate) return b - a;
    return a ? (b / a - 1) * 100 : NaN;
  }

  function render() {
    var x = IND[st.ind], t = table, rate = isRate(x.unidade);
    var first = t.periods[0], last = t.periods[t.periods.length - 1];
    var freg = st.nivel === "Freguesia";
    var terms = fold(st.q).split(/\s+/).filter(Boolean);
    var rows = t.rows.filter(function (p) {
      if (st.ilha && p.ilha !== st.ilha) return false;
      var s = fold(p.local + " " + p.concelho + " " + p.ilha);
      return terms.every(function (w) { return s.indexOf(w) >= 0; });
    });
    var key = st.ord || last, dir = st.ord ? st.dir : -1;
    var get = function (p) {
      if (key === "local") return p.local;
      if (key === "var") return change(p, first, last, rate);
      return p.v[key];
    };
    rows.sort(function (a, b) {
      var x1 = get(a), y1 = get(b);
      if (key === "local") return x1.localeCompare(y1, "pt") * dir;
      var na = x1 === undefined || isNaN(x1), nb = y1 === undefined || isNaN(y1);
      if (na || nb) return na - nb; // missing values last
      return (x1 - y1) * dir;
    });

    // Header
    var cols = [["local", freg ? "Freguesia" : "Concelho", ""]];
    if (freg) cols.push([null, "Concelho", ""]);
    if (!st.ilha) cols.push([null, "Ilha", ""]);
    t.periods.forEach(function (d) { cols.push([d, t.labels[d], "num"]); });
    if (t.periods.length > 1) cols.push(["var", rate ? "Variação (pontos)" : "Variação", "num"]);
    var tr = document.createElement("tr");
    cols.forEach(function (c) {
      var th = document.createElement("th"); th.scope = "col"; th.className = c[2];
      if (!c[0]) { th.textContent = c[1]; tr.appendChild(th); return; }
      var b = document.createElement("button"); b.type = "button"; b.textContent = c[1];
      if (key === c[0]) th.setAttribute("aria-sort", dir > 0 ? "ascending" : "descending");
      b.addEventListener("click", function () {
        if (key === c[0]) { st.ord = c[0]; st.dir = -dir; } else { st.ord = c[0]; st.dir = c[0] === "local" ? 1 : -1; }
        render(); writeHash();
      });
      th.appendChild(b); tr.appendChild(th);
    });
    $("tabela").tHead.replaceChildren(tr);

    // Body
    var max = 0;
    rows.forEach(function (p) { var v = p.v[last]; if (!isNaN(v) && Math.abs(v) > max) max = Math.abs(v); });
    var frag = document.createDocumentFragment();
    var line = function (p, isRef) {
      var r = document.createElement("tr"); if (isRef) r.className = "ref";
      var td = function (text, cls) { var c = document.createElement("td"); c.textContent = text; if (cls) c.className = cls; r.appendChild(c); return c; };
      td(p.local, "lugar");
      if (freg) td(p.concelho);
      if (!st.ilha) td(p.ilha);
      t.periods.forEach(function (d) {
        var v = p.v[d], c = td(v === undefined || isNaN(v) ? "–" : fmt.format(v), "num");
        if (v === undefined || isNaN(v)) c.className += " falta";
        if (d === last && !isRef && max && !isNaN(v)) { c.className += " ult"; c.style.setProperty("--w", (Math.abs(v) / max * 100).toFixed(1) + "%"); }
      });
      if (t.periods.length > 1) {
        var ch = change(p, first, last, rate);
        var c = td(isNaN(ch) ? "–" : pct.format(ch) + (rate ? "" : "%"), "num");
        c.className += isNaN(ch) ? " falta" : ch > 0 ? " sobe" : ch < 0 ? " desce" : "";
      }
      frag.appendChild(r);
    };
    if (t.ref && !st.q && !st.ilha) line(t.ref, true);
    rows.forEach(function (p) { line(p, false); });
    $("tabela").tBodies[0].replaceChildren(frag);

    // Text around the table
    var a = document.createElement("a"); a.href = x.url; a.textContent = x.nome;
    $("titulo").replaceChildren(a);
    $("sub").textContent = [x.unidade, st.cat, t.all.length ? "dados de " + t.labels[t.all[0]] + " a " + t.labels[t.all[t.all.length - 1]] : "",
      "INE, atualizado em " + x.atualizado].filter(Boolean).join(" · ");
    var total = freg ? 156 : 19; // freguesias and concelhos of the Azores
    var withLast = t.rows.filter(function (p) { return !isNaN(p.v[last]); }).length;
    $("nota").textContent = withLast < total
      ? "Em " + t.labels[last] + ", o INE publica valores para " + withLast + " de " + total + " " +
        (freg ? "freguesias" : "concelhos") + ". Os outros não aparecem ou têm “–”."
      : "";
    $("legenda").textContent = x.nome + ", por " + (freg ? "freguesia" : "concelho");
    $("estado").textContent = rows.length + (freg ? " freguesias" : " concelhos") + (st.ilha ? " (" + st.ilha + ")" : "") + ".";
    $("painel").hidden = false;
    table.view = { cols: cols, rows: (t.ref && !st.q && !st.ilha ? [t.ref] : []).concat(rows), first: first, last: last, rate: rate };
  }

  function exportCSV(e) {
    var v = table.view, esc = function (s) { s = String(s); return /[",\n]/.test(s) ? '"' + s.replace(/"/g, '""') + '"' : s; };
    var freg = st.nivel === "Freguesia";
    var head = ["local"].concat(freg ? ["concelho"] : [], ["ilha"], table.periods.map(function (d) { return table.labels[d]; }));
    var body = v.rows.map(function (p) {
      return [p.local].concat(freg ? [p.concelho] : [], [p.ilha], table.periods.map(function (d) { var x = p.v[d]; return x === undefined || isNaN(x) ? "" : x; }));
    });
    var text = "﻿" + [head].concat(body).map(function (r) { return r.map(esc).join(","); }).join("\n");
    var url = URL.createObjectURL(new Blob([text], { type: "text/csv;charset=utf-8" }));
    e.currentTarget.href = url; e.currentTarget.download = "ine-" + st.ind + "-" + fold(st.nivel) + ".csv";
    setTimeout(function () { URL.revokeObjectURL(url); }, 10000);
  }

  function readHash() {
    var p = new URLSearchParams(location.hash.slice(1));
    st.ind = IND[p.get("ind")] ? p.get("ind") : ORDER[0];
    st.nivel = p.get("nivel") || ""; st.ilha = p.get("ilha") || ""; st.cat = p.get("cat") || "";
    st.q = p.get("q") || ""; st.todos = p.get("todos") === "1";
    st.ord = p.get("ord") || null; st.dir = p.get("dir") === "asc" ? 1 : -1;
    $("ind").value = st.ind; $("q").value = st.q; $("todos").checked = st.todos;
  }

  function writeHash() {
    var p = new URLSearchParams();
    [["ind", st.ind], ["nivel", st.nivel], ["ilha", st.ilha], ["cat", st.cat], ["q", st.q],
     ["todos", st.todos ? "1" : ""], ["ord", st.ord || ""], ["dir", st.ord ? (st.dir > 0 ? "asc" : "desc") : ""]]
      .forEach(function (kv) { if (kv[1]) p.set(kv[0], kv[1]); });
    history.replaceState(null, "", "#" + p.toString());
  }

  function on(id, ev, fn) { $(id).addEventListener(ev, function () { fn(); writeHash(); }); }
  on("ind", "change", function () { st.ind = $("ind").value; st.cat = ""; st.ord = null; build(); });
  on("nivel", "change", function () { st.nivel = $("nivel").value; st.ord = null; build(); });
  on("ilha", "change", function () { st.ilha = $("ilha").value; render(); });
  on("cat", "change", function () { st.cat = $("cat").value; build(); });
  on("todos", "change", function () { st.todos = $("todos").checked; st.ord = null; build(); });
  var timer;
  $("q").addEventListener("input", function () { clearTimeout(timer); timer = setTimeout(function () { st.q = $("q").value.trim(); render(); writeHash(); }, 150); });
  $("exportar").addEventListener("click", exportCSV);

  fetch("/dados/ine.csv")
    .then(function (r) { if (!r.ok) throw new Error(r.status); return r.text(); })
    .then(function (text) {
      index(parseCSV(text)); fillIndicators(); readHash(); build(); writeHash();
      // a shared link opened on this page (writeHash uses replaceState, which does not fire this)
      window.addEventListener("hashchange", function () { readHash(); build(); });
    })
    .catch(function (err) { $("estado").textContent = "Não foi possível carregar os dados (" + err.message + "). Use o ficheiro ine.csv."; });
})();
</script>
