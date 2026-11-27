---
title: Indicadores do INE
nav_title: Estatísticas
layout: default
permalink: /dados/ine/
secao: estatisticas
---
{% include estatisticas-nav.html %}

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
    <label id="ano-wrap" hidden>Ano <select id="ano"></select></label>
    <label class="ine-grow">Local <input type="search" id="q" placeholder="ex.: Rabo de Peixe, Horta" autocomplete="off"></label>
  </div>
  <label class="ine-check"><input type="checkbox" id="todos"> Mostrar todos os períodos</label>
  <label class="ine-check" id="grupo-wrap" hidden><input type="checkbox" id="grupo" checked> Agrupar as freguesias por concelho</label>
</form>

<p id="estado" role="status" aria-live="polite">A carregar…</p>

<div id="painel" hidden>
  <h2 id="titulo"></h2>
  <p id="sub" class="ine-sub"></p>
  <details id="def" class="ine-def" hidden>
    <summary><strong>O que mede este indicador</strong> <span id="def-resumo"></span></summary>
    <div id="def-corpo"></div>
  </details>
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
  <p id="dist-ajuda" class="ine-sub" hidden>Cada coluna é um limite: 20% dos sujeitos
    passivos têm um rendimento (depois do IRS) abaixo do valor da coluna “20%”, 40% abaixo do da coluna
    “40%”, e assim por diante; a mediana divide-os ao meio. A barra (na tabela e no gráfico) vai do limite dos 20%
    ao dos 80%, com a parte cheia entre os 40% e os 60% e um traço na mediana. As caixas na tabela escolhem os
    locais do gráfico. “80/20” diz quantas vezes o limite dos 80% é
    maior que o dos 20%: quanto maior, mais desigual. Escolha uma categoria para ver a evolução de um quintil.</p>
  <p id="nota" class="ine-sub"></p>
  <p><a id="exportar" href="#" download>Descarregar esta tabela (CSV)</a> ·
     <a href="/dados/ine.csv">todos os indicadores (ine.csv)</a></p>
</div>

<noscript><p>Esta página precisa de JavaScript. O ficheiro <a href="/dados/ine.csv">ine.csv</a> tem os mesmos dados.</p></noscript>

<details id="glossario-sec" class="glossario-todo" hidden>
<summary id="glossario"><strong>Glossário</strong>: todos os conceitos do INE usados nesta página (<span id="g-n"></span>)</summary>
<p class="ine-sub">As definições do INE para os conceitos usados nestes indicadores
(por exemplo, o que é um “sujeito passivo” ou um “agregado fiscal”). O texto é
copiado da metainformação de cada indicador no site do INE, sem alterações;
em cada conceito, “Fonte: INE” liga à página de onde veio.</p>
<input type="search" id="gq" class="g-busca" placeholder="Procurar um conceito" aria-label="Procurar um conceito" autocomplete="off">
<dl id="glossario-lista" class="glossario"></dl>
</details>

## Notas

- Cada indicador tem, em “O que mede este indicador”, a fórmula, as
  definições dos conceitos, a nota e a fonte, tal como o INE as publica
  (também em [ine_meta.json](/dados/ine_meta.json)).
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
.ine-def { margin: .25em 0 .9em; padding: .5em .8em; border-left: 3px solid #268bd2; background: rgba(38,139,210,.06); font-size: .95em; max-width: 52em; }
.ine-def summary { cursor: pointer; }
.ine-def summary span { color: #586e75; font-size: .9em; }
.ine-def dl, .glossario { margin: .5em 0 0; }
.ine-def dt, .glossario dt { font-weight: bold; margin-top: .5em; }
.ine-def dd, .glossario dd { margin: 0 0 .2em; }
.glossario-todo { margin: 1.5em 0; max-width: 52em; }
.glossario-todo > summary { cursor: pointer; font-size: 1.1em; }
.ine-def p.fonte { font-size: .85em; color: #586e75; }
.ine-def p { margin: .5em 0 0; }
.glossario dd.usado { font-size: .85em; color: #586e75; }
.g-busca { font: inherit; padding: .3em .4em; width: min(24em, 100%); margin: .3em 0; }
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
#tabela tr.conc td { font-weight: bold; border-top: 2px solid #93a1a1; }
#tabela tr.sub td.lugar { padding-left: 1.4em; }
#tabela td.med { font-weight: bold; }
#tabela td.dist { padding-top: 0; padding-bottom: 0; vertical-align: middle; }
.strip { display: block; }
.strip .s-banda { stroke: #268bd2; stroke-opacity: .45; stroke-width: 2; stroke-linecap: round; }
.strip .s-meio { fill: #268bd2; }
.strip .s-med, #g-svg .d-med { stroke: #073642; stroke-width: 2; }
@media (prefers-color-scheme: dark) { .strip .s-med, #g-svg .d-med { stroke: #eee8d5; } #g-svg .rotulo { fill: #eee8d5; } #g-svg .grade { stroke: rgba(147,161,161,.22); } }
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
    vista: "ambos", sel: [], escala: "", ano: "", grupo: true }; // escala "" = automatic
  // Categorical colours in fixed order (validated against this page's
  // background: adjacent CVD ΔE >= 11.8). A place keeps its colour while it
  // stays selected; colour follows the place, never its rank.
  var COLORS = ["#257de0", "#f47230", "#00b894", "#f2a600", "#ee7fac", "#008a17", "#6a4ce2", "#ec4647"];
  var DEFAULT_SEL = ["20", "30", "PT"], MAXSEL = COLORS.length, slot = {};
  var SVGNS = "http://www.w3.org/2000/svg";
  var table = null; // { periods, refs, rows, view } of the current view
  var REF = { "20": "Açores (RAA)", "30": "Madeira (RAM)", "PT": "Portugal" };
  var DEF = {}; // varcd -> definitions from ine_meta.json (may stay empty)
  var MEDIANA = "0012757"; // median after IRS per sujeito passivo, shown with the quintiles
  // Clearer names than INE's for indicators whose INE name hides what they are.
  var NOMES = { "0012759": "Quintis do rendimento após IRS por sujeito passivo (como se distribui o rendimento)" };

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
        x = IND[r.varcd] = { varcd: r.varcd, tema: r.tema, nome: NOMES[r.varcd] || r.indicador, inome: r.indicador, unidade: r.unidade,
          atualizado: r.atualizado, url: r.url, rows: [], niveis: {}, cats: {} };
        ORDER.push(r.varcd);
      }
      x.rows.push(r); x.niveis[r.nivel] = 1; x.cats[r.categoria] = 1;
    });
    // The quintiles right after the median, at the top of the income list.
    var i = ORDER.indexOf("0012759"), j;
    if (i >= 0 && ORDER.indexOf(MEDIANA) >= 0) { ORDER.splice(i, 1); j = ORDER.indexOf(MEDIANA); ORDER.splice(j + 1, 0, "0012759"); }
  }

  // ---- definitions (ine_meta.json) -------------------------------------
  function hel(tag, text, cls) {
    var e = document.createElement(tag);
    if (text) e.textContent = text;
    if (cls) e.className = cls;
    return e;
  }

  function fillDefinition(varcd) {
    var d = DEF[varcd], box = $("def"), body = $("def-corpo");
    if (!d) { box.hidden = true; return; }
    var parts = [], src = hel("p", "", "fonte"), sl = hel("a", "metainformação do indicador " + varcd);
    sl.href = d.metainfo || x_url(varcd);
    src.appendChild(document.createTextNode("Texto do INE, copiado da "));
    src.appendChild(sl);
    src.appendChild(document.createTextNode(" no site do INE (atualizado todas as semanas)."));
    parts.push(src);
    if (d.formula) {
      var p = hel("p"); p.appendChild(hel("strong", "Fórmula: ")); p.appendChild(document.createTextNode(d.formula)); parts.push(p);
    }
    var cs = d.conceitos || [];
    if (cs.length) {
      var dl = hel("dl");
      cs.forEach(function (c) { dl.appendChild(hel("dt", c[0])); dl.appendChild(hel("dd", c[1])); });
      parts.push(dl);
    }
    [["Nota do INE: ", d.nota], ["Observações: ", d.observacoes], ["Fonte: ", d.fonte]].forEach(function (f) {
      if (!f[1]) return;
      var p = hel("p"); p.appendChild(hel("strong", f[0])); p.appendChild(document.createTextNode(f[1])); parts.push(p);
    });
    var fim = hel("p", d.periodicidade ? "Série " + d.periodicidade.toLowerCase() + (d.primeiro ? ", desde " + d.primeiro : "") + ". " : "", "fonte");
    var gl = hel("a", "Todos os conceitos no glossário"); gl.href = "#glossario"; gl.className = "abre-gloss";
    fim.appendChild(gl); parts.push(fim);
    body.replaceChildren.apply(body, parts);
    var names = cs.map(function (c) { return c[0].toLowerCase(); });
    $("def-resumo").textContent = names.length
      ? "— " + (names.length > 3 ? names.slice(0, 3).join(", ") + "…" : names.join(", "))
      : d.formula ? "— fórmula e fonte" : "— fonte e notas";
    box.hidden = false;
  }
  function x_url(varcd) { return "https://www.ine.pt/xurl/metax/" + varcd; }

  // All concepts, alphabetically, with the indicators that use them.
  function fillGlossary() {
    var terms = {};
    ORDER.forEach(function (v) {
      ((DEF[v] || {}).conceitos || []).forEach(function (c) {
        var k = fold(c[0]), t = terms[k];
        if (!t) t = terms[k] = { nome: c[0], def: c[1], ind: [] };
        if (t.ind.indexOf(v) < 0) t.ind.push(v);
      });
    });
    var keys = Object.keys(terms).sort(function (a, b) { return a.localeCompare(b, "pt"); });
    if (!keys.length) return;
    var dl = $("glossario-lista"), frag = document.createDocumentFragment();
    keys.forEach(function (k) {
      var t = terms[k], dt = hel("dt", t.nome), dd = hel("dd", t.def), used = hel("dd", "Usado em: ", "usado"),
        src = hel("a", "INE"), first = DEF[t.ind[0]] || {};
      src.href = first.metainfo || x_url(t.ind[0]);
      src.title = "Metainformação do indicador " + t.ind[0] + " no site do INE";
      dt.setAttribute("data-k", k + " " + fold(t.def));
      t.ind.forEach(function (v, i) {
        if (i) used.appendChild(document.createTextNode("; "));
        var a = hel("a", IND[v].nome); a.href = "#ind=" + v;
        a.addEventListener("click", function () { window.scrollTo(0, 0); });
        used.appendChild(a);
      });
      used.appendChild(document.createTextNode(" · Fonte: "));
      used.appendChild(src);
      frag.appendChild(dt); frag.appendChild(dd); frag.appendChild(used);
    });
    dl.replaceChildren(frag);
    $("glossario-sec").hidden = false;
    $("g-n").textContent = keys.length;
    $("gq").addEventListener("input", function () {
      var q = fold(this.value).split(/\s+/).filter(Boolean);
      dl.querySelectorAll("dt").forEach(function (dt) {
        var show = q.every(function (w) { return dt.getAttribute("data-k").indexOf(w) >= 0; });
        dt.hidden = !show; dt.nextSibling.hidden = !show; dt.nextSibling.nextSibling.hidden = !show;
      });
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

  // Quintile indicators are shown as a distribution: for one year, the four
  // quintile limits side by side (plus INE's median, which sits between the
  // 2nd and 3rd), instead of one quintile at a time.
  function isDist(x) {
    var c = Object.keys(x.cats).filter(Boolean);
    return c.length > 1 && c.every(function (k) { return /quintil/i.test(k); });
  }
  var DIST_COLS = [["1º quintil", "20%"], ["2º quintil", "40%"], ["med", "Mediana"], ["3º quintil", "60%"], ["4º quintil", "80%"]];

  function build() {
    var x = IND[st.ind];
    var niveis = ["Concelho", "Freguesia"].filter(function (n) { return x.niveis[n]; });
    st.nivel = fillSelect($("nivel"), niveis, st.nivel || "Concelho");
    var freg = st.nivel === "Freguesia";
    var cats = Object.keys(x.cats).filter(Boolean).sort(function (a, b) { return a.localeCompare(b, "pt", { numeric: true }); });
    var distOK = isDist(x);
    $("cat-wrap").hidden = !cats.length;
    st.cat = cats.length ? fillSelect($("cat"), cats, st.cat, distOK ? "todos (distribuição)" : null) : "";
    var dist = distOK && !st.cat;
    var ilhas = {};
    x.rows.forEach(function (r) { if (r.nivel === st.nivel && r.ilha) ilhas[r.ilha] = 1; });
    var ilhaOrder = ["Santa Maria", "São Miguel", "Terceira", "Graciosa", "São Jorge", "Pico", "Faial", "Flores", "Corvo"];
    st.ilha = fillSelect($("ilha"), ilhaOrder.filter(function (i) { return ilhas[i]; }), st.ilha, "todas");
    $("grupo-wrap").hidden = !freg;
    $("grupo").checked = st.grupo;

    // Years, for the distribution view.
    var years = {};
    if (dist) x.rows.forEach(function (r) { years[r.data] = r.periodo; });
    var ykeys = Object.keys(years).sort();
    $("ano-wrap").hidden = !dist;
    if (dist) {
      var as = $("ano"); as.replaceChildren();
      ykeys.slice().reverse().forEach(function (k) { var o = document.createElement("option"); o.value = k; o.textContent = years[k]; as.appendChild(o); });
      if (ykeys.indexOf(st.ano) < 0) st.ano = ykeys[ykeys.length - 1] || "";
      as.value = st.ano;
    }

    // Pivot: one row per place, one column per period (or per quintile).
    // Reference rows are INE's own values for the region and the country,
    // not averages of the rows below. Columns come from Azores data only.
    // At freguesia level the concelhos come along too, to head their groups.
    var periods = {}, places = {}, refs = {}, conc = {}, byGeo = {};
    var add = function (r, key) {
      var p, counts = true;
      if (REF[r.geocod]) {
        p = refs[r.geocod] || (refs[r.geocod] = { geo: r.geocod, local: REF[r.geocod], concelho: "", ilha: "", v: {} });
        counts = r.geocod === "20";
      } else if (r.nivel === st.nivel) {
        p = places[r.geocod] || (places[r.geocod] = { geo: r.geocod, local: r.local, concelho: r.concelho, ilha: r.ilha, v: {} });
      } else if (freg && r.nivel === "Concelho") {
        p = conc[r.local] || (conc[r.local] = { geo: r.geocod, local: "Concelho de " + r.local, nome: r.local,
          concelho: r.local, ilha: r.ilha, v: {}, conc: true });
        counts = false;
      } else return;
      p.v[key] = parseFloat(r.valor);
      byGeo[r.geocod] = p;
      if (counts && !dist) periods[r.data] = r.periodo;
    };
    var keys, shown, last = "", prev = "", labels, sortDefault;
    if (dist) {
      x.rows.forEach(function (r) { if (r.data === st.ano) add(r, r.categoria); });
      var med = IND[MEDIANA];
      if (med) med.rows.forEach(function (r) {
        if (r.data === st.ano && !r.categoria && byGeo[r.geocod]) byGeo[r.geocod].v.med = parseFloat(r.valor);
      });
      var hasMed = Object.keys(byGeo).some(function (g) { return byGeo[g].v.med !== undefined; });
      var cols = DIST_COLS.filter(function (c) { return c[0] !== "med" || hasMed; });
      keys = shown = cols.map(function (c) { return c[0]; });
      labels = {}; cols.forEach(function (c) { labels[c[0]] = c[1]; });
      last = "1º quintil"; sortDefault = hasMed ? "med" : "3º quintil";
    } else {
      x.rows.forEach(function (r) { if (r.categoria === st.cat) add(r, r.data); });
      keys = Object.keys(periods).sort();
      shown = st.todos ? keys : keys.slice(-RECENT);
      labels = periods;
      // Change: latest period against the same period a year before (or the
      // period before it, for series that are not yearly or have gaps).
      last = keys[keys.length - 1];
      if (last) {
        var yearAgo = (parseInt(last.slice(0, 4), 10) - 1) + last.slice(4);
        prev = periods[yearAgo] ? yearAgo : keys[keys.length - 2] || "";
      }
      sortDefault = last;
    }
    table = { dist: dist, ano: dist ? years[st.ano] : "", all: dist ? [] : keys, periods: shown, labels: labels,
      last: last, prev: prev, sortDefault: sortDefault,
      refs: Object.keys(REF).filter(function (g) { return refs[g]; }).map(function (g) { return refs[g]; }),
      rows: Object.keys(places).map(function (k) { return places[k]; }),
      conc: Object.keys(conc).map(function (k) { return conc[k]; }) };
    $("todos").parentNode.hidden = dist || keys.length <= RECENT;
    render();
  }

  function change(p, first, last, rate) {
    var a = p.v[first], b = p.v[last];
    if (!first || first === last || a === undefined || b === undefined || isNaN(a) || isNaN(b)) return NaN;
    if (rate) return b - a;
    return a ? (b / a - 1) * 100 : NaN;
  }
  function ratio(p) { var a = p.v["1º quintil"], b = p.v["4º quintil"]; return a > 0 && b > 0 ? b / a : NaN; }
  function ok(v) { return v !== undefined && !isNaN(v); }

  // One row's distribution: thin band from the 20% to the 80% limit, solid
  // between 40% and 60%, a tick at the median. Shared scale for the table.
  function strip(p, lo, hi) {
    var W = 150, H = 16, q = p.v, s = el("svg", { width: W, height: H, viewBox: "0 0 " + W + " " + H, "class": "strip" });
    var a = q["1º quintil"], b = q["2º quintil"], c = q["3º quintil"], d = q["4º quintil"];
    if (!ok(a) || !ok(d) || !(hi > lo)) return s;
    var X = function (v) { return 4 + (v - lo) / (hi - lo) * (W - 8); };
    el("line", { x1: X(a), x2: X(d), y1: H / 2, y2: H / 2, "class": "s-banda" }, s);
    if (ok(b) && ok(c)) el("rect", { x: X(b), y: 3, width: Math.max(2, X(c) - X(b)), height: H - 6, rx: 2, "class": "s-meio" }, s);
    if (ok(q.med)) el("line", { x1: X(q.med), x2: X(q.med), y1: 1, y2: H - 1, "class": "s-med" }, s);
    var t = el("title", {}, s);
    t.textContent = p.local + ": 20% abaixo de " + fmt.format(a) + " €, 20% acima de " + fmt.format(d) + " €" +
      (ok(q.med) ? "; mediana " + fmt.format(q.med) + " €" : "");
    return s;
  }

  function render() {
    var x = IND[st.ind], t = table, rate = isRate(x.unidade), dist = t.dist;
    var first = t.prev, last = t.last;
    var freg = st.nivel === "Freguesia", grouped = freg && st.grupo;
    var terms = fold(st.q).split(/\s+/).filter(Boolean);
    var match = function (p) {
      if (st.ilha && p.ilha !== st.ilha) return false;
      var s = fold(p.local + " " + p.concelho + " " + p.ilha);
      return terms.every(function (w) { return s.indexOf(w) >= 0; });
    };
    var rows = t.rows.filter(match);
    var key = st.ord || t.sortDefault, dir = st.ord ? st.dir : -1;
    var get = function (p) {
      if (key === "local") return p.nome || p.local;
      if (key === "var") return change(p, first, last, rate);
      if (key === "razao") return ratio(p);
      return p.v[key];
    };
    var cmp = function (a, b) {
      var x1 = get(a), y1 = get(b);
      if (key === "local") return x1.localeCompare(y1, "pt") * dir;
      var na = !ok(x1), nb = !ok(y1);
      if (na || nb) return na - nb; // missing values last
      return (x1 - y1) * dir;
    };
    rows.sort(cmp);
    var heads = [];
    if (grouped) {
      // Each concelho, then its freguesias; concelhos and freguesias each in
      // the chosen order.
      var by = {};
      rows.forEach(function (p) { (by[p.concelho] || (by[p.concelho] = [])).push(p); });
      heads = t.conc.filter(function (c) { return by[c.nome] || match(c); }).sort(cmp);
      var out = [];
      heads.forEach(function (c) { out.push(c); (by[c.nome] || []).forEach(function (p) { out.push(p); }); delete by[c.nome]; });
      Object.keys(by).forEach(function (k) { by[k].forEach(function (p) { out.push(p); }); });
      rows = out;
    }
    var nFreg = rows.filter(function (p) { return !p.conc; }).length;

    // Header
    var cols = [["local", freg ? (grouped ? "Concelho e freguesias" : "Freguesia") : "Concelho", ""]];
    if (freg && !grouped) cols.push([null, "Concelho", ""]);
    if (!st.ilha) cols.push([null, "Ilha", ""]);
    t.periods.forEach(function (d) { cols.push([d, t.labels[d], "num"]); });
    if (!dist && t.prev) cols.push(["var", "Var. face a " + t.labels[t.prev] + (rate ? " (pontos)" : ""), "num"]);
    if (dist) { cols.push(["razao", "80/20", "num"]); cols.push([null, "Distribuição", "dist"]); }
    var tr = document.createElement("tr");
    cols.forEach(function (c) {
      var th = document.createElement("th"); th.scope = "col"; th.className = c[2];
      if (c[0] === "razao") th.title = "Quantas vezes o limite dos 80% é maior que o dos 20%";
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
    var max = 0, lo = Infinity, hi = -Infinity;
    rows.forEach(function (p) { var v = p.v[last]; if (!p.conc && ok(v) && Math.abs(v) > max) max = Math.abs(v); });
    if (dist) t.refs.concat(rows).forEach(function (p) {
      if (ok(p.v["1º quintil"])) lo = Math.min(lo, p.v["1º quintil"]);
      if (ok(p.v["4º quintil"])) hi = Math.max(hi, p.v["4º quintil"]);
    });
    var frag = document.createDocumentFragment();
    var line = function (p, isRef) {
      var r = document.createElement("tr");
      r.className = isRef ? "ref" : p.conc ? "conc" : grouped ? "sub" : "";
      var td = function (text, cls) { var c = document.createElement("td"); c.textContent = text; if (cls) c.className = cls; r.appendChild(c); return c; };
      var lc = td("", "lugar"), lab = document.createElement("label");
      {
        var cb = document.createElement("input");
        cb.type = "checkbox"; cb.checked = st.sel.indexOf(p.geo) >= 0;
        cb.disabled = !cb.checked && st.sel.length >= MAXSEL;
        cb.setAttribute("aria-label", "Mostrar " + p.local + " no gráfico");
        if (cb.checked) lc.style.setProperty("--c", colorOf(p.geo));
        cb.addEventListener("change", function () { toggleSel(p.geo); });
        lab.appendChild(cb);
      }
      lab.appendChild(document.createTextNode(p.local)); lc.appendChild(lab);
      if (freg && !grouped) td(p.concelho);
      if (!st.ilha) td(p.ilha);
      t.periods.forEach(function (d) {
        var v = p.v[d], c = td(ok(v) ? fmt.format(v) : "–", "num");
        if (!ok(v)) c.className += " falta";
        if (!dist && d === last && !isRef && !p.conc && max && ok(v)) { c.className += " ult"; c.style.setProperty("--w", (Math.abs(v) / max * 100).toFixed(1) + "%"); }
        if (dist && d === "med") c.className += " med";
      });
      if (!dist && t.prev) {
        var ch = change(p, first, last, rate);
        var c = td(isNaN(ch) ? "–" : pct.format(ch) + (rate ? "" : "%"), "num");
        c.className += isNaN(ch) ? " falta" : ch > 0 ? " sobe" : ch < 0 ? " desce" : "";
      }
      if (dist) {
        var rz = ratio(p);
        td(ok(rz) ? fmt.format(Math.round(rz * 100) / 100) : "–", "num" + (ok(rz) ? "" : " falta"));
        td("", "dist").appendChild(strip(p, lo, hi));
      }
      frag.appendChild(r);
    };
    t.refs.forEach(function (r) { line(r, true); });
    rows.forEach(function (p) { line(p, false); });
    $("tabela").tBodies[0].replaceChildren(frag);

    // Text around the table
    var a = document.createElement("a"); a.href = x.url; a.textContent = x.nome;
    if (x.nome !== x.inome) a.title = "No INE: " + x.inome;
    $("titulo").replaceChildren(a);
    fillDefinition(st.ind);
    $("sub").textContent = (dist
      ? [x.unidade, "distribuição em " + t.ano]
      : [x.unidade, st.cat, t.all.length ? "dados de " + t.labels[t.all[0]] + " a " + t.labels[t.all[t.all.length - 1]] : ""])
      .concat(["INE, atualizado em " + x.atualizado]).filter(Boolean).join(" · ");
    $("dist-ajuda").hidden = !dist;
    var total = freg ? 156 : 19; // freguesias and concelhos of the Azores
    var withLast = t.rows.filter(function (p) { return ok(p.v[last]); }).length;
    var when = dist ? t.ano : t.labels[last];
    $("nota").textContent = withLast < total
      ? "Em " + when + ", o INE publica valores para " + withLast + " de " + total + " " +
        (freg ? "freguesias" : "concelhos") + ". Os outros não aparecem ou têm “–”." +
        (dist && freg ? " Nas freguesias pequenas, o INE não divulga os quintis." : "")
      : "";
    $("legenda").textContent = x.nome + ", por " + (freg ? "freguesia" : "concelho");
    var pl = function (n, one, many) { return n + " " + (n === 1 ? one : many); };
    $("estado").textContent = (freg ? pl(nFreg, "freguesia", "freguesias") : pl(nFreg, "concelho", "concelhos")) +
      (grouped ? " em " + pl(heads.length, "concelho", "concelhos") : "") + (st.ilha ? " (" + st.ilha + ")" : "") + ".";
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

  // Quintiles: one row per chosen place, on one euro axis. Thin band from
  // the 20% to the 80% limit, solid from 40% to 60%, a tick at the median.
  // Colour follows the place, as in the table and the other charts.
  function drawDist(all) {
    var t = table, x = IND[st.ind];
    var series = st.sel.filter(function (g) { return all[g]; }).map(function (g) { return { geo: g, p: all[g], c: colorOf(g) }; });
    fillJuntar(all);
    drawLegend(series);
    var svg = $("g-svg"); svg.replaceChildren();
    var W = $("g-area").clientWidth || 600, narrow = W < 560, RH = 34;
    var Q = ["1º quintil", "2º quintil", "3º quintil", "4º quintil"];
    var vals = [];
    series.forEach(function (s) { Q.concat(["med"]).forEach(function (k) { if (ok(s.p.v[k])) vals.push(s.p.v[k]); }); });
    var m = { l: 8, r: 16, t: 6, b: 26 }, H = m.t + Math.max(1, series.length) * RH + m.b;
    svg.setAttribute("viewBox", "0 0 " + W + " " + H); svg.setAttribute("height", H);
    svg.setAttribute("aria-label", x.nome + ", " + t.ano + ": " + series.map(function (s) { return s.p.local; }).join(", "));
    $("g-nota").hidden = false;
    $("g-nota").textContent = t.ano + ". Barra fina: dos 20% aos 80%. Parte cheia: dos 40% aos 60%. Traço: mediana.";
    if (!vals.length) {
      var tx = el("text", { x: W / 2, y: H / 2, "text-anchor": "middle" }, svg);
      tx.textContent = series.length ? "Sem valores para os locais escolhidos." : "Escolha pelo menos um local na tabela ou na lista.";
      chart = null; return;
    }
    var lo = Math.min.apply(null, vals), hi = Math.max.apply(null, vals), pad = (hi - lo) * 0.05 || hi * 0.05;
    var ticks = niceTicks(lo - pad, hi + pad, narrow ? 4 : 6); lo = ticks[0]; hi = ticks[ticks.length - 1];
    // left margin from the longest place name (capped)
    var probe = el("text", { "class": "rotulo" }, svg), wmax = 0, cap = narrow ? 120 : 220;
    series.forEach(function (s) { probe.textContent = s.p.local; wmax = Math.max(wmax, probe.getComputedTextLength()); });
    svg.removeChild(probe); m.l = Math.min(cap, Math.ceil(wmax)) + 22;
    var iw = W - m.l - m.r;
    var X = function (v) { return m.l + (v - lo) / (hi - lo) * iw; };
    ticks.forEach(function (v) {
      el("line", { x1: X(v), x2: X(v), y1: m.t, y2: H - m.b, "class": "grade" }, svg);
      var tx = el("text", { x: X(v), y: H - 6, "text-anchor": "middle" }, svg); tx.textContent = fmt.format(v);
    });
    var tip = $("g-tip");
    series.forEach(function (s, i) {
      var q = s.p.v, y = m.t + i * RH + RH / 2, g = el("g", {}, svg);
      el("circle", { cx: 8, cy: y, r: 5, fill: s.c }, g);
      var name = el("text", { x: 18, y: y + 4, "class": "rotulo" }, g), nm = s.p.local;
      name.textContent = nm;
      while (name.getComputedTextLength() > m.l - 24 && nm.length > 4) { nm = nm.slice(0, -2); name.textContent = nm + "…"; }
      if (ok(q[Q[0]]) && ok(q[Q[3]])) el("line", { x1: X(q[Q[0]]), x2: X(q[Q[3]]), y1: y, y2: y, stroke: s.c, "stroke-opacity": .5, "stroke-width": 3, "stroke-linecap": "round" }, g);
      if (ok(q[Q[1]]) && ok(q[Q[2]])) el("rect", { x: X(q[Q[1]]), y: y - 7, width: Math.max(2, X(q[Q[2]]) - X(q[Q[1]])), height: 14, rx: 3, fill: s.c }, g);
      if (ok(q.med)) el("line", { x1: X(q.med), x2: X(q.med), y1: y - 10, y2: y + 10, "class": "d-med" }, g);
      var hit = el("rect", { x: 0, y: y - RH / 2, width: W, height: RH, fill: "transparent" }, g);
      var showTip = function () {
        tip.replaceChildren();
        var hd = document.createElement("div"); hd.className = "p"; hd.textContent = s.p.local + ", " + t.ano; tip.appendChild(hd);
        [["20%", Q[0]], ["40%", Q[1]], ["Mediana", "med"], ["60%", Q[2]], ["80%", Q[3]]].forEach(function (c) {
          if (!ok(q[c[1]])) return;
          var row = document.createElement("div"); row.className = "l";
          var b = document.createElement("b"); b.textContent = fmt.format(q[c[1]]) + " €";
          var n = document.createElement("span"); n.textContent = c[0];
          row.appendChild(b); row.appendChild(n); tip.appendChild(row);
        });
        tip.hidden = false;
        var area = $("g-area"), sx = area.clientWidth / W, left = X(ok(q[Q[3]]) ? q[Q[3]] : hi) * sx + 12;
        if (left + tip.offsetWidth > area.clientWidth) left = Math.max(0, X(ok(q[Q[0]]) ? q[Q[0]] : lo) * sx - tip.offsetWidth - 12);
        tip.style.left = left + "px"; tip.style.top = Math.max(0, (y - RH / 2) * sx) + "px";
      };
      hit.addEventListener("pointermove", showTip);
      hit.addEventListener("pointerdown", showTip);
      hit.addEventListener("pointerleave", function () { tip.hidden = true; });
    });
    chart = null;
  }

  function drawChart() {
    if (st.vista === "tabela" || !table) return;
    var t = table, x = IND[st.ind];
    var all = {}; t.refs.concat(t.conc, t.rows).forEach(function (p) { all[p.geo] = p; });
    document.querySelector(".g-escala").hidden = t.dist;
    var aj = $("g-ajuda"); if (!aj.dataset.txt) aj.dataset.txt = aj.textContent;
    aj.textContent = t.dist ? "Escolha os locais com as caixas na tabela ou com a lista acima (até 8). Passe o rato ou toque numa linha para ver os valores." : aj.dataset.txt;
    if (t.dist) { drawDist(all); return; }
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
    var places = table.refs.concat(table.conc.concat(table.rows).filter(function (p) { return !st.ilha || p.ilha === st.ilha; })
      .sort(function (a, b) { return a.local.localeCompare(b.local, "pt"); }));
    places.forEach(function (p) {
      if (st.sel.indexOf(p.geo) >= 0) return;
      var o = document.createElement("option"); o.value = p.geo;
      o.textContent = p.local + (p.concelho && !p.conc ? " (" + p.concelho + ")" : ""); sel.appendChild(o);
    });
  }

  function exportCSV(e) {
    var v = table.view, esc = function (s) { s = String(s); return /[",\n]/.test(s) ? '"' + s.replace(/"/g, '""') + '"' : s; };
    var freg = st.nivel === "Freguesia";
    var head = ["local"].concat(freg ? ["nivel", "concelho"] : [], ["ilha"], table.periods.map(function (d) { return table.labels[d]; }));
    var body = v.rows.map(function (p) {
      return [p.nome || p.local].concat(freg ? [p.conc ? "Concelho" : REF[p.geo] ? "" : "Freguesia", p.concelho] : [], [p.ilha],
        table.periods.map(function (d) { var x = p.v[d]; return x === undefined || isNaN(x) ? "" : x; }));
    });
    var text = "﻿" + [head].concat(body).map(function (r) { return r.map(esc).join(","); }).join("\n");
    var url = URL.createObjectURL(new Blob([text], { type: "text/csv;charset=utf-8" }));
    e.currentTarget.href = url; e.currentTarget.download = "ine-" + st.ind + "-" + fold(st.nivel) + (table.dist ? "-" + table.ano : "") + ".csv";
    setTimeout(function () { URL.revokeObjectURL(url); }, 10000);
  }

  function readHash() {
    var p = new URLSearchParams(location.hash.slice(1));
    st.ind = IND[p.get("ind")] ? p.get("ind") : ORDER[0];
    st.nivel = p.get("nivel") || ""; st.ilha = p.get("ilha") || ""; st.cat = p.get("cat") || "";
    st.q = p.get("q") || ""; st.todos = p.get("todos") === "1";
    st.ano = p.get("ano") || ""; st.grupo = p.get("grupo") !== "0";
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
     ["todos", st.todos ? "1" : ""], ["ano", table && table.dist ? st.ano : ""], ["grupo", st.grupo ? "" : "0"], ["ord", st.ord || ""], ["dir", st.ord ? (st.dir > 0 ? "asc" : "desc") : ""],
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
  on("ano", "change", function () { st.ano = $("ano").value; build(); });
  on("grupo", "change", function () { st.grupo = $("grupo").checked; render(); });
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
  // The hash holds the page state: open the glossary without touching it.
  document.addEventListener("click", function (e) {
    var a = e.target.closest && e.target.closest('a[href="#glossario"]');
    if (!a) return;
    e.preventDefault();
    $("glossario-sec").open = true;
    $("glossario-sec").scrollIntoView({ behavior: "smooth", block: "start" });
  });
  $("g-svg").addEventListener("keydown", function (e) {
    if (!chart) return;
    if (e.key === "ArrowLeft" || e.key === "ArrowRight") {
      e.preventDefault();
      showAt(chart.idx < 0 ? chart.keys.length - 1 : chart.idx + (e.key === "ArrowRight" ? 1 : -1));
    } else if (e.key === "Escape") hideTip();
  });
  $("g-svg").addEventListener("blur", hideTip);
  var rt; window.addEventListener("resize", function () { clearTimeout(rt); rt = setTimeout(drawChart, 150); });

  // Definitions are optional: the page works without them.
  var defs = fetch("/dados/ine_meta.json?v=" + BUILD)
    .then(function (r) { return r.ok ? r.json() : {}; })
    .catch(function () { return {}; });
  Promise.all([fetch("/dados/ine.csv?v=" + BUILD)
    .then(function (r) { if (!r.ok) throw new Error(r.status); return r.text(); }), defs])
    .then(function (res) {
      var text = res[0]; DEF = res[1] || {};
      index(parseCSV(text)); fillIndicators(); fillNews(); readHash(); build(); writeHash(); fillGlossary();
      // a shared link opened on this page (writeHash uses replaceState, which does not fire this)
      window.addEventListener("hashchange", function () { readHash(); build(); });
    })
    .catch(function (err) { $("estado").textContent = "Não foi possível carregar os dados (" + err.message + "). Use o ficheiro ine.csv."; });
})();
</script>
