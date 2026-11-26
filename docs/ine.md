---
title: Indicadores do INE
layout: default
permalink: /dados/ine/
---
# Indicadores do INE

Estatísticas do INE para os Açores, por concelho e, quando o INE as publica,
por freguesia. Escolha um indicador e veja-o em gráfico, em tabela ou nos dois.
A tabela mostra um local por linha e um período por coluna; o gráfico
compara a evolução dos locais que escolher. Em cima, como referência, os valores do INE para os
Açores, a Madeira e Portugal. A última coluna compara o período mais recente
com o mesmo período do ano anterior.
Atualizado todas as semanas. Ver também os [outros dados abertos](/dados/).

<details id="novidades" class="ine-novidades" hidden>
  <summary>Novos dados do INE</summary>
  <ul id="novidades-lista"></ul>
</details>

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
  <div class="ine-vista" role="group" aria-label="Vista">
    <button type="button" data-vista="ambos">Tabela e gráfico</button>
    <button type="button" data-vista="grafico">Gráfico</button>
    <button type="button" data-vista="tabela">Tabela</button>
  </div>
  <div id="grafico" class="ine-grafico">
    <div class="g-topo">
      <div id="g-legenda" class="g-legenda" aria-label="Locais no gráfico"></div>
      <div class="ine-vista g-escala" role="group" aria-label="Escala">
        <button type="button" data-escala="valor">Valores</button>
        <button type="button" data-escala="indice">Índice</button>
      </div>
      <label class="g-juntar"><span class="sr-only">Juntar ao gráfico</span>
        <select id="g-juntar"></select>
      </label>
    </div>
    <p id="g-nota" class="g-nota" hidden></p>
    <div id="g-area" class="g-area">
      <svg id="g-svg" role="img" tabindex="0" aria-describedby="g-ajuda"></svg>
      <div id="g-tip" class="g-tip" hidden></div>
    </div>
    <p id="g-ajuda" class="ine-sub">O gráfico mostra a série completa. Junte locais com a lista acima ou com as caixas na
      tabela (até 8). Passe o rato, toque ou use as setas para ver os valores. Em "Índice", cada local começa em 100, para comparar a evolução.</p>
  </div>
  <div id="tabela-wrap">
  <div class="ine-scroll">
    <table id="tabela">
      <caption class="sr-only" id="legenda"></caption>
      <thead></thead>
      <tbody></tbody>
    </table>
  </div>
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
- Açores (RAA), Madeira (RAM) e Portugal são os valores que o INE publica
  para essas regiões e para o país, não médias das linhas da tabela.
- A variação compara o período mais recente com o mesmo período do ano
  anterior (ou com o período anterior, nas séries que não são anuais). Nos
  indicadores em % ou ‰ é a diferença em pontos.
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
.ine-novidades { margin-bottom: 1em; }
.ine-novidades summary { cursor: pointer; font-weight: bold; }
.ine-novidades ul { margin-top: .4em; }
.ine-scroll { overflow-x: auto; }
#tabela { font-size: .9em; border-collapse: collapse; width: auto; min-width: 100%; }
#tabela th, #tabela td { padding: .35em .6em; white-space: nowrap; }
#tabela td.num, #tabela th.num { text-align: right; font-variant-numeric: tabular-nums; }
#tabela td.lugar { white-space: normal; min-width: 9em; }
#tabela th:first-child, #tabela td:first-child { position: sticky; left: 0; background: #fdf6e3; z-index: 1; }
#tabela tr.ref td { font-weight: bold; }
#tabela tr.ref + tr:not(.ref) td { border-top: 2px solid #93a1a1; }
#tabela td.ult { background-image: linear-gradient(to left, rgba(38,139,210,.18) var(--w, 0%), transparent var(--w, 0%)); }
#tabela td.falta { color: #93a1a1; }
#tabela td.sobe { color: #2d7a2d; }
#tabela td.desce { color: #b03a2e; }
th button { all: unset; cursor: pointer; font-weight: bold; }
th[aria-sort="ascending"] button::after { content: " ▲"; }
th[aria-sort="descending"] button::after { content: " ▼"; }
.ine-vista { display: inline-flex; border: 1px solid #93a1a1; border-radius: 6px; overflow: hidden; margin: .25em 0 .75em; }
.ine-vista button { font: inherit; font-size: .9em; padding: .3em .8em; border: 0; background: transparent; color: #586e75; cursor: pointer; }
.ine-vista button + button { border-left: 1px solid #93a1a1; }
.ine-vista button[aria-pressed="true"] { background: #586e75; color: #fdf6e3; }
.ine-vista button:focus-visible, .g-legenda button:focus-visible, #g-svg:focus-visible { outline: 3px solid #268bd2; outline-offset: 1px; }
.ine-grafico { margin-bottom: 1em; }
.g-escala { margin: 0; }
.g-nota { font-size: .85em; color: #586e75; margin: 0 0 .3em; }
.g-topo { display: flex; flex-wrap: wrap; gap: .5em 1em; align-items: center; margin-bottom: .4em; }
.g-legenda { display: flex; flex-wrap: wrap; gap: .3em .9em; font-size: .85em; color: #586e75; flex: 1 1 20em; }
.g-legenda span.item { display: inline-flex; align-items: center; gap: .35em; }
.g-legenda i { display: inline-block; width: 16px; height: 0; border-top: 2px solid var(--c); border-radius: 2px; }
.g-legenda button { all: unset; cursor: pointer; color: #93a1a1; padding: 0 .2em; }
.g-legenda button:hover { color: #b03a2e; }
.g-juntar select { font: inherit; font-size: .85em; padding: .2em .3em; max-width: 16em; }
.g-area { position: relative; }
#g-svg { display: block; width: 100%; overflow: visible; touch-action: pan-y; }
#g-svg text { font-size: 12px; fill: #586e75; font-variant-numeric: tabular-nums; }
#g-svg .grade { stroke: #eee8d5; stroke-width: 1; }
#g-svg .eixo { stroke: #93a1a1; stroke-width: 1; }
#g-svg .cruz { stroke: #93a1a1; stroke-width: 1; }
#g-svg .rotulo { font-size: 12px; fill: #073642; }
.g-tip { position: absolute; pointer-events: none; background: #fffdf5; border: 1px solid #93a1a1; border-radius: 6px; padding: .4em .6em; font-size: .85em; box-shadow: 0 2px 6px rgba(0,0,0,.12); min-width: 10em; z-index: 3; }
.g-tip .p { color: #586e75; margin-bottom: .2em; }
.g-tip div.l { display: flex; align-items: center; gap: .4em; white-space: nowrap; }
.g-tip i { display: inline-block; width: 12px; border-top: 2px solid var(--c); }
.g-tip b { font-variant-numeric: tabular-nums; color: #073642; }
.g-tip span { color: #586e75; }
#tabela td.lugar label { display: inline-flex; gap: .4em; align-items: baseline; cursor: pointer; }
#tabela td.lugar input { accent-color: var(--c, #586e75); }
[hidden] { display: none !important; }
.sr-only { position: absolute; width: 1px; height: 1px; overflow: hidden; clip: rect(0 0 0 0); }
</style>

<script>
(function () {
  "use strict";
  // Build time: the data files change with every deploy, so ask for this
  // build's copy and never mix a new page with cached old data.
  var BUILD = "{{ site.time | date: '%s' }}";
  var RECENT = 6;
  var $ = function (id) { return document.getElementById(id); };
  var fmt = new Intl.NumberFormat("pt-PT", { maximumFractionDigits: 2 });
  var pct = new Intl.NumberFormat("pt-PT", { maximumFractionDigits: 1, signDisplay: "exceptZero" });
  var fold = function (s) { return (s || "").normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase(); };
  var IND = {}, ORDER = [], st = { ind: "", nivel: "", ilha: "", cat: "", q: "", todos: false, ord: null, dir: -1,
    vista: "ambos", sel: [], escala: "" }; // escala "" = automatic
  // Categorical colours in fixed order (validated against this page's
  // background: adjacent CVD ΔE >= 11.8). A place keeps its colour while it
  // stays selected; colour follows the place, never its rank.
  var COLORS = ["#257de0", "#f47230", "#00b894", "#f2a600", "#ee7fac", "#008a17", "#6a4ce2", "#ec4647"];
  var DEFAULT_SEL = ["20", "30", "PT"], MAXSEL = COLORS.length, slot = {};
  var SVGNS = "http://www.w3.org/2000/svg";
  var table = null; // { periods, refs, rows, view } of the current view
  var REF = { "20": "Açores (RAA)", "30": "Madeira (RAM)", "PT": "Portugal" };

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

  // Most recently updated indicators, newest first (INE's update date).
  function fillNews() {
    var news = ORDER.map(function (v) {
      var x = IND[v], last = "";
      x.rows.forEach(function (r) { if (r.geocod === "20" && r.data > last) { last = r.data; x.ultimo = r.periodo; } });
      return x;
    }).sort(function (a, b) { return b.atualizado.localeCompare(a.atualizado); }).slice(0, 8);
    var ul = $("novidades-lista");
    news.forEach(function (x) {
      var li = document.createElement("li"), a = document.createElement("a");
      a.href = "#ind=" + x.varcd; a.textContent = x.nome;
      li.appendChild(document.createTextNode(x.atualizado + ": ")); li.appendChild(a);
      if (x.ultimo) li.appendChild(document.createTextNode(", até " + x.ultimo));
      ul.appendChild(li);
    });
    $("novidades").hidden = !news.length;
    $("novidades").open = true;
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
    // Reference rows are INE's own values for the region and the country,
    // not averages of the rows below. Columns come from Azores data only.
    var periods = {}, places = {}, refs = {};
    x.rows.forEach(function (r) {
      if (r.categoria !== st.cat) return;
      if (REF[r.geocod]) {
        var q = refs[r.geocod] || (refs[r.geocod] = { geo: r.geocod, local: REF[r.geocod], concelho: "", ilha: "", v: {} });
        q.v[r.data] = parseFloat(r.valor);
        if (r.geocod !== "20") return;
      } else if (r.nivel === st.nivel) {
        var p = places[r.geocod] || (places[r.geocod] = { geo: r.geocod, local: r.local, concelho: r.concelho, ilha: r.ilha, v: {} });
        p.v[r.data] = parseFloat(r.valor);
      } else return;
      periods[r.data] = r.periodo;
    });
    var keys = Object.keys(periods).sort();
    var shown = st.todos ? keys : keys.slice(-RECENT);
    // Change: latest period against the same period a year before (or the
    // period before it, for series that are not yearly or have gaps).
    var last = keys[keys.length - 1], prev = "";
    if (last) {
      var yearAgo = (parseInt(last.slice(0, 4), 10) - 1) + last.slice(4);
      prev = periods[yearAgo] ? yearAgo : keys[keys.length - 2] || "";
    }
    table = { all: keys, periods: shown, labels: periods, last: last, prev: prev,
      refs: Object.keys(REF).filter(function (g) { return refs[g]; }).map(function (g) { return refs[g]; }),
      rows: Object.keys(places).map(function (k) { return places[k]; }) };
    $("todos").parentNode.hidden = keys.length <= RECENT;
    render();
  }

  function change(p, first, last, rate) {
    var a = p.v[first], b = p.v[last];
    if (!first || first === last || a === undefined || b === undefined || isNaN(a) || isNaN(b)) return NaN;
    if (rate) return b - a;
    return a ? (b / a - 1) * 100 : NaN;
  }

  function render() {
    var x = IND[st.ind], t = table, rate = isRate(x.unidade);
    var first = t.prev, last = t.last;
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
    if (t.prev) cols.push(["var", "Var. face a " + t.labels[t.prev] + (rate ? " (pontos)" : ""), "num"]);
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
      var lc = td("", "lugar"), lab = document.createElement("label"), cb = document.createElement("input");
      cb.type = "checkbox"; cb.checked = st.sel.indexOf(p.geo) >= 0;
      cb.disabled = !cb.checked && st.sel.length >= MAXSEL;
      cb.setAttribute("aria-label", "Mostrar " + p.local + " no gráfico");
      if (cb.checked) lc.style.setProperty("--c", colorOf(p.geo));
      cb.addEventListener("change", function () { toggleSel(p.geo); });
      lab.appendChild(cb); lab.appendChild(document.createTextNode(p.local)); lc.appendChild(lab);
      if (freg) td(p.concelho);
      if (!st.ilha) td(p.ilha);
      t.periods.forEach(function (d) {
        var v = p.v[d], c = td(v === undefined || isNaN(v) ? "–" : fmt.format(v), "num");
        if (v === undefined || isNaN(v)) c.className += " falta";
        if (d === last && !isRef && max && !isNaN(v)) { c.className += " ult"; c.style.setProperty("--w", (Math.abs(v) / max * 100).toFixed(1) + "%"); }
      });
      if (t.prev) {
        var ch = change(p, first, last, rate);
        var c = td(isNaN(ch) ? "–" : pct.format(ch) + (rate ? "" : "%"), "num");
        c.className += isNaN(ch) ? " falta" : ch > 0 ? " sobe" : ch < 0 ? " desce" : "";
      }
      frag.appendChild(r);
    };
    t.refs.forEach(function (r) { line(r, true); });
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
    table.view = { cols: cols, rows: t.refs.concat(rows), first: first, last: last, rate: rate };
    applyVista();
    drawChart();
  }

  // ---- chart -------------------------------------------------------------
  function colorOf(geo) { return COLORS[slot[geo]] || "#586e75"; }

  function assignSlots() {
    Object.keys(slot).forEach(function (g) { if (st.sel.indexOf(g) < 0) delete slot[g]; });
    st.sel.forEach(function (g) {
      if (slot[g] !== undefined) return;
      var used = {}; Object.keys(slot).forEach(function (k) { used[slot[k]] = 1; });
      for (var i = 0; i < COLORS.length; i++) if (!used[i]) { slot[g] = i; break; }
    });
  }

  function toggleSel(geo) {
    var i = st.sel.indexOf(geo);
    if (i >= 0) st.sel.splice(i, 1); else if (st.sel.length < MAXSEL) st.sel.push(geo);
    assignSlots(); render(); writeHash();
  }

  function applyVista() {
    $("grafico").hidden = st.vista === "tabela";
    $("tabela-wrap").hidden = st.vista === "grafico";
    document.querySelectorAll(".ine-vista button").forEach(function (b) {
      b.setAttribute("aria-pressed", b.getAttribute("data-vista") === st.vista ? "true" : "false");
    });
  }

  var MESES = { janeiro: "jan", fevereiro: "fev", "março": "mar", abril: "abr", maio: "mai", junho: "jun", julho: "jul",
    agosto: "ago", setembro: "set", outubro: "out", novembro: "nov", dezembro: "dez" };
  function shortLabel(s) {
    var m = /^(\S+) de (\d{4})$/.exec(s);
    if (m && MESES[m[1].toLowerCase()]) return MESES[m[1].toLowerCase()] + " " + m[2];
    m = /^(\d)\.º (Trimestre|Semestre) de (\d{4})$/.exec(s);
    if (m) return (m[2] === "Trimestre" ? "T" : "S") + m[1] + " " + m[3];
    return s;
  }

  function niceTicks(lo, hi, n) {
    var span = hi - lo || Math.abs(hi) || 1, step = Math.pow(10, Math.floor(Math.log10(span / n))), err = span / n / step;
    step *= err >= 7.5 ? 10 : err >= 3.5 ? 5 : err >= 1.5 ? 2 : 1;
    var t = [], v = Math.floor(lo / step) * step;
    for (; v <= hi + step * 1e-9; v += step) t.push(+v.toFixed(10));
    if (t[t.length - 1] < hi) t.push(t[t.length - 1] + step);
    return t;
  }

  function el(name, attrs, parent) {
    var e = document.createElementNS(SVGNS, name);
    Object.keys(attrs || {}).forEach(function (k) { e.setAttribute(k, attrs[k]); });
    if (parent) parent.appendChild(e);
    return e;
  }

  var chart = null; // { xs, keys, series, x(), y() } for the hover layer

  function drawChart() {
    if (st.vista === "tabela" || !table) return;
    var t = table, x = IND[st.ind];
    var all = {}; t.refs.concat(t.rows).forEach(function (p) { all[p.geo] = p; });
    var series = st.sel.filter(function (g) { return all[g]; }).map(function (g) { return { geo: g, p: all[g], c: colorOf(g) }; });
    fillJuntar(all);
    drawLegend(series);
    var svg = $("g-svg"); svg.replaceChildren();
    var keys = t.all, W = $("g-area").clientWidth || 600, narrow = W < 560;
    // Index (base = 100) when the places differ too much in size to share
    // one axis (Portugal vs a concelho), or when asked for.
    var ok = function (v) { return v !== undefined && !isNaN(v); };
    var lastVals = series.map(function (s) { for (var i = keys.length - 1; i >= 0; i--) if (ok(s.p.v[keys[i]])) return Math.abs(s.p.v[keys[i]]); return NaN; })
      .filter(function (v) { return !isNaN(v) && v > 0; });
    var spread = lastVals.length > 1 ? Math.max.apply(null, lastVals) / Math.min.apply(null, lastVals) : 1;
    var indice = st.escala ? st.escala === "indice" : spread > 15;
    var base = null;
    if (indice) {
      base = keys.filter(function (k) { return series.every(function (s) { return ok(s.p.v[k]) && s.p.v[k] !== 0; }); })[0] || null;
      series.forEach(function (s) {
        var b = base || keys.filter(function (k) { return ok(s.p.v[k]) && s.p.v[k] !== 0; })[0];
        s.raw = s.p.v; s.p = Object.assign({}, s.p, { v: {} });
        keys.forEach(function (k) { if (b && ok(s.raw[k])) s.p.v[k] = s.raw[k] / s.raw[b] * 100; });
      });
    }
    document.querySelectorAll(".g-escala button").forEach(function (b) {
      b.setAttribute("aria-pressed", (b.getAttribute("data-escala") === "indice") === indice ? "true" : "false");
    });
    $("g-nota").hidden = !indice;
    $("g-nota").textContent = indice ? "Índice: " + (base ? t.labels[base] : "primeiro valor de cada local") + " = 100" +
      (!st.escala ? " (os locais têm dimensões muito diferentes; escolha \"Valores\" para ver os valores)." : ".") : "";
    var H = narrow ? 240 : 320, direct = series.length <= 4 && !narrow;
    var m = { l: 8, r: direct ? 130 : 12, t: 10, b: 26 };
    var vals = [];
    series.forEach(function (s) { keys.forEach(function (k) { var v = s.p.v[k]; if (v !== undefined && !isNaN(v)) vals.push(v); }); });
    svg.setAttribute("viewBox", "0 0 " + W + " " + H); svg.setAttribute("height", H);
    svg.setAttribute("aria-label", x.nome + ": " + series.map(function (s) { return s.p.local; }).join(", "));
    if (!vals.length || !keys.length) {
      var tx = el("text", { x: W / 2, y: H / 2, "text-anchor": "middle" }, svg);
      tx.textContent = series.length ? "Sem valores para os locais escolhidos." : "Escolha pelo menos um local.";
      chart = null; return;
    }
    var lo = Math.min.apply(null, vals), hi = Math.max.apply(null, vals);
    if (lo >= 0 && lo < hi * 0.35) lo = 0; else { var pad = (hi - lo) * 0.08 || Math.abs(hi) * 0.05 || 1; lo -= pad; hi += pad; }
    var ticks = niceTicks(lo, hi, narrow ? 4 : 5); lo = ticks[0]; hi = ticks[ticks.length - 1];
    // left margin from the widest tick label
    var probe = el("text", {}, svg), wmax = 0;
    ticks.forEach(function (v) { probe.textContent = fmt.format(v); wmax = Math.max(wmax, probe.getComputedTextLength()); });
    svg.removeChild(probe); m.l = Math.ceil(wmax) + 10;
    var iw = W - m.l - m.r, ih = H - m.t - m.b;
    var X = function (i) { return m.l + (keys.length === 1 ? iw / 2 : i * iw / (keys.length - 1)); };
    var Y = function (v) { return m.t + ih - (v - lo) / (hi - lo) * ih; };
    // grid + y labels
    ticks.forEach(function (v) {
      el("line", { x1: m.l, x2: m.l + iw, y1: Y(v), y2: Y(v), "class": v === 0 ? "eixo" : "grade" }, svg);
      var tx = el("text", { x: m.l - 6, y: Y(v) + 4, "text-anchor": "end" }, svg); tx.textContent = fmt.format(v);
    });
    // x labels, thinned to fit
    var every = Math.max(1, Math.ceil(keys.length / Math.max(2, Math.floor(iw / (narrow ? 56 : 72)))));
    keys.forEach(function (k, i) {
      if ((keys.length - 1 - i) % every) return; // always label the latest period
      var tx = el("text", { x: X(i), y: H - 6, "text-anchor": "middle" }, svg); tx.textContent = shortLabel(t.labels[k]);
    });
    // lines (broken where INE has no value), isolated points as dots
    series.forEach(function (s) {
      var d = "", prevOk = false;
      keys.forEach(function (k, i) {
        var v = s.p.v[k], ok = v !== undefined && !isNaN(v);
        if (ok) d += (prevOk ? "L" : "M") + X(i).toFixed(1) + " " + Y(v).toFixed(1);
        var nextV = s.p.v[keys[i + 1]], nextOk = nextV !== undefined && !isNaN(nextV);
        if (ok && !prevOk && !nextOk) el("circle", { cx: X(i), cy: Y(v), r: 3.5, fill: s.c }, svg);
        prevOk = ok;
      });
      if (d) el("path", { d: d, fill: "none", stroke: s.c, "stroke-width": 2, "stroke-linejoin": "round", "stroke-linecap": "round" }, svg);
    });
    // end dots + direct labels (nudged apart)
    var ends = [];
    series.forEach(function (s) {
      for (var i = keys.length - 1; i >= 0; i--) {
        var v = s.p.v[keys[i]];
        if (v !== undefined && !isNaN(v)) { ends.push({ s: s, i: i, y: Y(v) }); break; }
      }
    });
    ends.forEach(function (e) { el("circle", { cx: X(e.i), cy: e.y, r: 4, fill: e.s.c, stroke: "#fdf6e3", "stroke-width": 2 }, svg); });
    if (direct) {
      ends.sort(function (a, b) { return a.y - b.y; });
      var ly = ends.map(function (e) { return e.y; });
      for (var j = 1; j < ly.length; j++) if (ly[j] - ly[j - 1] < 15) ly[j] = ly[j - 1] + 15;
      var over = ly.length ? ly[ly.length - 1] - (m.t + ih) : 0;
      if (over > 0) ly = ly.map(function (v) { return v - over; });
      ends.forEach(function (e, j) {
        var lx = m.l + iw + 10;
        el("line", { x1: lx, x2: lx + 10, y1: ly[j], y2: ly[j], stroke: e.s.c, "stroke-width": 2, "stroke-linecap": "round" }, svg);
        var tx = el("text", { x: lx + 14, y: ly[j] + 4, "class": "rotulo" }, svg);
        var name = e.s.p.local; tx.textContent = name.length > 16 ? name.slice(0, 15) + "…" : name;
      });
    }
    // hover layer
    var g = el("g", {}, svg);
    var cross = el("line", { y1: m.t, y2: m.t + ih, "class": "cruz", visibility: "hidden" }, g);
    chart = { keys: keys, series: series, X: X, Y: Y, m: m, iw: iw, g: g, cross: cross, idx: -1, dots: [] };
    var hit = el("rect", { x: m.l, y: m.t, width: iw, height: ih, fill: "transparent" }, svg);
    hit.addEventListener("pointermove", function (e) {
      var r = svg.getBoundingClientRect(), px = (e.clientX - r.left) * (W / r.width);
      showAt(Math.round((px - m.l) / (keys.length > 1 ? iw / (keys.length - 1) : 1)));
    });
    hit.addEventListener("pointerdown", function (e) { hit.dispatchEvent(new PointerEvent("pointermove", e)); });
    hit.addEventListener("pointerleave", hideTip);
  }

  function showAt(i) {
    var c = chart; if (!c) return;
    i = Math.max(0, Math.min(c.keys.length - 1, i)); c.idx = i;
    var k = c.keys[i], x = c.X(i);
    c.cross.setAttribute("x1", x); c.cross.setAttribute("x2", x); c.cross.setAttribute("visibility", "visible");
    c.dots.forEach(function (d) { d.remove(); }); c.dots = [];
    var tip = $("g-tip"); tip.replaceChildren();
    var hd = document.createElement("div"); hd.className = "p"; hd.textContent = table.labels[k]; tip.appendChild(hd);
    c.series.slice().sort(function (a, b) {
      var va = a.p.v[k], vb = b.p.v[k];
      return (isNaN(vb) || vb === undefined ? -Infinity : vb) - (isNaN(va) || va === undefined ? -Infinity : va);
    }).forEach(function (s) {
      var v = s.p.v[k], ok = v !== undefined && !isNaN(v);
      if (ok) c.dots.push(el("circle", { cx: x, cy: c.Y(v), r: 4.5, fill: s.c, stroke: "#fdf6e3", "stroke-width": 2 }, c.g));
      var row = document.createElement("div"); row.className = "l";
      var key = document.createElement("i"); key.style.setProperty("--c", s.c);
      var b = document.createElement("b"); b.textContent = ok ? fmt.format(v) : "–";
      var n = document.createElement("span");
      n.textContent = s.p.local + (s.raw && ok ? " · " + fmt.format(s.raw[k]) : "");
      row.appendChild(key); row.appendChild(b); row.appendChild(n); tip.appendChild(row);
    });
    tip.hidden = false;
    var area = $("g-area"), sx = area.clientWidth / (parseFloat($("g-svg").getAttribute("viewBox").split(" ")[2]) || 1);
    var left = x * sx + 14; if (left + tip.offsetWidth > area.clientWidth) left = x * sx - tip.offsetWidth - 14;
    tip.style.left = Math.max(0, left) + "px"; tip.style.top = (c.m.t + 4) + "px";
  }

  function hideTip() {
    if (!chart) return;
    chart.cross.setAttribute("visibility", "hidden");
    chart.dots.forEach(function (d) { d.remove(); }); chart.dots = []; chart.idx = -1;
    $("g-tip").hidden = true;
  }

  function drawLegend(series) {
    var box = $("g-legenda"); box.replaceChildren();
    series.forEach(function (s) {
      var it = document.createElement("span"); it.className = "item";
      var key = document.createElement("i"); key.style.setProperty("--c", s.c);
      var b = document.createElement("button"); b.type = "button"; b.textContent = "×";
      b.setAttribute("aria-label", "Tirar " + s.p.local + " do gráfico");
      b.addEventListener("click", function () { toggleSel(s.geo); });
      it.appendChild(key); it.appendChild(document.createTextNode(s.p.local)); it.appendChild(b);
      box.appendChild(it);
    });
  }

  function fillJuntar(all) {
    var sel = $("g-juntar"); sel.replaceChildren();
    var o0 = document.createElement("option"); o0.value = "";
    o0.textContent = st.sel.length >= MAXSEL ? "Máximo de 8 locais" : "Juntar ao gráfico…"; sel.appendChild(o0);
    sel.disabled = st.sel.length >= MAXSEL;
    var places = table.refs.concat(table.rows.filter(function (p) { return !st.ilha || p.ilha === st.ilha; })
      .sort(function (a, b) { return a.local.localeCompare(b.local, "pt"); }));
    places.forEach(function (p) {
      if (st.sel.indexOf(p.geo) >= 0) return;
      var o = document.createElement("option"); o.value = p.geo;
      o.textContent = p.local + (p.concelho ? " (" + p.concelho + ")" : ""); sel.appendChild(o);
    });
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
    st.escala = ["valor", "indice"].indexOf(p.get("escala")) >= 0 ? p.get("escala") : "";
    st.vista = ["ambos", "grafico", "tabela"].indexOf(p.get("vista")) >= 0 ? p.get("vista") : "ambos";
    st.sel = p.get("sel") !== null ? p.get("sel").split(",").filter(Boolean).slice(0, MAXSEL) : DEFAULT_SEL.slice();
    slot = {}; assignSlots();
    $("ind").value = st.ind; $("q").value = st.q; $("todos").checked = st.todos;
  }

  function writeHash() {
    var p = new URLSearchParams();
    [["ind", st.ind], ["nivel", st.nivel], ["ilha", st.ilha], ["cat", st.cat], ["q", st.q],
     ["todos", st.todos ? "1" : ""], ["ord", st.ord || ""], ["dir", st.ord ? (st.dir > 0 ? "asc" : "desc") : ""],
     ["vista", st.vista === "ambos" ? "" : st.vista], ["escala", st.escala], ["sel", st.sel.join(",") === DEFAULT_SEL.join(",") ? "" : st.sel.join(",")]]
      .forEach(function (kv) { if (kv[1]) p.set(kv[0], kv[1]); });
    if (!st.sel.length) p.set("sel", "");
    history.replaceState(null, "", "#" + p.toString());
  }

  function on(id, ev, fn) { $(id).addEventListener(ev, function () { fn(); writeHash(); }); }
  on("ind", "change", function () { st.ind = $("ind").value; st.cat = ""; st.ord = null; st.escala = ""; build(); });
  on("nivel", "change", function () { st.nivel = $("nivel").value; st.ord = null; build(); });
  on("ilha", "change", function () { st.ilha = $("ilha").value; render(); });
  on("cat", "change", function () { st.cat = $("cat").value; build(); });
  on("todos", "change", function () { st.todos = $("todos").checked; st.ord = null; build(); });
  var timer;
  $("q").addEventListener("input", function () { clearTimeout(timer); timer = setTimeout(function () { st.q = $("q").value.trim(); render(); writeHash(); }, 150); });
  $("exportar").addEventListener("click", exportCSV);
  document.querySelectorAll(".ine-vista button").forEach(function (b) {
    b.addEventListener("click", function () { st.vista = b.getAttribute("data-vista"); applyVista(); drawChart(); writeHash(); });
  });
  document.querySelectorAll(".g-escala button").forEach(function (b) {
    b.addEventListener("click", function () { st.escala = b.getAttribute("data-escala"); drawChart(); writeHash(); });
  });
  $("g-juntar").addEventListener("change", function () { var g = $("g-juntar").value; if (g) toggleSel(g); });
  $("g-svg").addEventListener("keydown", function (e) {
    if (!chart) return;
    if (e.key === "ArrowLeft" || e.key === "ArrowRight") {
      e.preventDefault();
      showAt(chart.idx < 0 ? chart.keys.length - 1 : chart.idx + (e.key === "ArrowRight" ? 1 : -1));
    } else if (e.key === "Escape") hideTip();
  });
  $("g-svg").addEventListener("blur", hideTip);
  var rt; window.addEventListener("resize", function () { clearTimeout(rt); rt = setTimeout(drawChart, 150); });

  fetch("/dados/ine.csv?v=" + BUILD)
    .then(function (r) { if (!r.ok) throw new Error(r.status); return r.text(); })
    .then(function (text) {
      index(parseCSV(text)); fillIndicators(); fillNews(); readHash(); build(); writeHash();
      // a shared link opened on this page (writeHash uses replaceState, which does not fire this)
      window.addEventListener("hashchange", function () { readHash(); build(); });
    })
    .catch(function (err) { $("estado").textContent = "Não foi possível carregar os dados (" + err.message + "). Use o ficheiro ine.csv."; });
})();
</script>
