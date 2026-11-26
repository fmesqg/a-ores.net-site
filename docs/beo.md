---
title: Execução orçamental
nav_title: Contas da Região
layout: default
permalink: /dados/beo/
---
# Execução orçamental

Receita e despesa do Governo Regional dos Açores, mês a mês, a partir do
[Boletim de Execução Orçamental](https://portal.azores.gov.pt/web/drot/beo-boletim-de-execu%C3%A7%C3%A3o-or%C3%A7amental)
que a Direção Regional do Orçamento e Tesouro publica todos os meses. Escolha
um quadro do boletim e veja-o em gráfico, em tabela ou nos dois. Os valores
publicados são acumulados desde janeiro; em "Mensal" vê o que entrou ou saiu
em cada mês. A última coluna compara com o mesmo mês do ano anterior.
Atualizado todas as semanas. Ver também os [indicadores do INE](/dados/ine/)
e os [outros dados abertos](/dados/).

<p id="ultimo" class="ine-sub" hidden></p>

<form id="beo-form" class="ine-form" onsubmit="return false">
  <div class="ine-row">
    <label class="ine-grow">Quadro
      <select id="quadro"></select>
    </label>
    <label id="linhas-wrap" hidden>Linhas <select id="linhas"></select></label>
    <label id="filtro-wrap" hidden><span id="filtro-nome">Subsetor</span> <select id="filtro"></select></label>
    <label id="med-wrap" hidden>Medida <select id="med"></select></label>
  </div>
  <div class="ine-row">
    <div id="modo-wrap" class="ine-vista" role="group" aria-label="Valores">
      <button type="button" data-modo="acum">Acumulado no ano</button>
      <button type="button" data-modo="mensal">Mensal</button>
    </div>
    <label class="ine-grow">Procurar <input type="search" id="busca" placeholder="ex.: IRS, pessoal, saúde" autocomplete="off"></label>
  </div>
  <label class="ine-check"><input type="checkbox" id="todos"> Mostrar todos os meses</label>
</form>

<p id="estado" role="status" aria-live="polite">A carregar…</p>

<div id="painel" hidden>
  <h2 id="titulo"></h2>
  <p id="sub" class="ine-sub"></p>
  <details id="def" class="ine-def" hidden>
    <summary><strong>Termos usados neste quadro</strong> <span id="def-resumo"></span></summary>
    <dl id="def-corpo"></dl>
  </details>
  <div class="ine-vista" role="group" aria-label="Vista">
    <button type="button" data-vista="ambos">Tabela e gráfico</button>
    <button type="button" data-vista="grafico">Gráfico</button>
    <button type="button" data-vista="tabela">Tabela</button>
  </div>
  <div id="grafico" class="ine-grafico">
    <div class="g-topo">
      <div id="g-legenda" class="g-legenda" aria-label="Séries no gráfico"></div>
      <div class="ine-vista g-escala" role="group" aria-label="Gráfico">
        <button type="button" data-graf="tempo">Ao longo do tempo</button>
        <button type="button" data-graf="anos">Ano a ano</button>
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
    <p id="g-ajuda" class="ine-sub">Junte linhas com a lista acima ou com as caixas na tabela (até 8). Em "Ano a ano",
      cada linha é um ano, de janeiro a dezembro, para a primeira série escolhida. Passe o rato, toque ou use as setas para ver os valores.</p>
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
     <a href="/dados/beo.csv">todos os quadros (beo.csv)</a></p>
</div>

<noscript><p>Esta página precisa de JavaScript. O ficheiro <a href="/dados/beo.csv">beo.csv</a> tem os mesmos dados.</p></noscript>

<h2 id="glossario">Glossário</h2>

<p class="ine-sub">Os termos do boletim em linguagem corrente. <strong>Estas
explicações são do açores.net, não são texto oficial.</strong> Em cada termo
está a ligação para onde está a definição oficial: a lei ou o próprio boletim.
Se encontrar um erro, diga-nos no
<a href="https://github.com/fmesqg/a-ores.net-site/issues">GitHub</a>.</p>

<dl class="glossario">
{%- for g in site.data.glossario_beo %}
  <dt id="g-{{ g.termo | slugify }}">{{ g.termo }}</dt>
  <dd>{{ g.def }}</dd>
  <dd class="fonte">Definição oficial:
  {%- for k in g.fontes %}{% assign f = site.data.fontes[k] %}{% if f.url == "beo_ultimo" %}{% assign u = site.data.beo_ultimo.url %}{% else %}{% assign u = f.url %}{% endif %}
    <a href="{{ u }}">{{ f.nome }}</a>{% unless forloop.last %};{% endunless %}
  {%- endfor %}</dd>
{%- endfor %}
</dl>

## Notas

- Os valores vêm dos PDF do boletim, lidos por
  [`bot/beo.py`](https://github.com/fmesqg/a-ores.net-site/blob/main/bot/beo.py).
  Cada valor no ficheiro tem o endereço do boletim de onde saiu, que é o que
  se deve citar. O título de cada tabela liga ao último boletim.
- Os boletins dão valores acumulados desde janeiro. "Mensal" é a diferença
  entre um mês e o anterior; em janeiro é o próprio valor.
- O que quer dizer cada termo (receita efetiva, saldo primário, GRA, SFA,
  EPR…) está no [glossário](#glossario), mais abaixo.
- Os valores de 2023 vêm da coluna do ano anterior dos boletins de 2024, e só
  existem para a receita fiscal, a receita não fiscal e a despesa do GRA.
- Os departamentos mudaram com o Governo que tomou posse em 2024. Os antigos
  só aparecem em "Mostrar todos os meses". Quando o boletim deixa uma
  célula em branco, a tabela mostra "–".
- Todos os quadros num só ficheiro: [beo.csv](/dados/beo.csv), um valor por
  linha. Também está na base de dados SQLite (tabela `beo`), descrita em
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
.ine-def dl, .glossario { margin: .5em 0 0; max-width: 52em; }
.ine-def dt, .glossario dt { font-weight: bold; margin-top: .5em; }
.ine-def dd, .glossario dd { margin: 0 0 .2em; }
.glossario dd.fonte, .ine-def dd.fonte { font-size: .85em; color: #586e75; margin-bottom: .5em; }
.ine-sub { color: #586e75; font-size: .9em; }
.ine-scroll { overflow-x: auto; }
#tabela { font-size: .9em; border-collapse: collapse; width: auto; min-width: 100%; }
#tabela th, #tabela td { padding: .35em .6em; white-space: nowrap; }
#tabela td.num, #tabela th.num { text-align: right; font-variant-numeric: tabular-nums; }
#tabela td.lugar { white-space: normal; min-width: 12em; }
#tabela td.lugar.n1 { padding-left: 1.6em; }
#tabela td.lugar.n2 { padding-left: 2.8em; }
#tabela tr.n0 td { font-weight: bold; }
#tabela th:first-child, #tabela td:first-child { position: sticky; left: 0; background: #fdf6e3; z-index: 1; }
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
.ine-vista button:disabled { opacity: .45; cursor: not-allowed; }
.ine-vista button:focus-visible, .g-legenda button:focus-visible, #g-svg:focus-visible { outline: 3px solid #268bd2; outline-offset: 1px; }
.ine-row .ine-vista { margin: 0; align-self: flex-end; }
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
  var BUILD = "{{ site.time | date: '%s' }}";
  var RECENT = 6, EUR = "Montante (€)";
  var $ = function (id) { return document.getElementById(id); };
  var fmtM = new Intl.NumberFormat("pt-PT", { minimumFractionDigits: 1, maximumFractionDigits: 1, useGrouping: "always" });
  var fmtAxis = new Intl.NumberFormat("pt-PT", { maximumFractionDigits: 1, useGrouping: "always" });
  var pct = new Intl.NumberFormat("pt-PT", { maximumFractionDigits: 1, signDisplay: "exceptZero" });
  var fold = function (s) { return (s || "").normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase(); };
  var slug = function (s) { return fold(s).replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, ""); };
  var Q = {}, QORDER = [];
  // docs/_data/glossario_beo.yml: plain-language terms, matched to rubricas.
  var GLOSS = {{ site.data.glossario_beo | jsonify }};
  var FONTES = {{ site.data.fontes | jsonify }};
  FONTES.boletim.url = {{ site.data.beo_ultimo.url | jsonify }};
  var st = { q: "", linhas: "rubrica", filtro: "", med: EUR, modo: "acum", graf: "tempo", busca: "", todos: false,
    ord: null, dir: 1, vista: "ambos", sel: null };
  // Categorical colours in fixed order, the same as the INE page (validated
  // against this background). A series keeps its colour while selected.
  var COLORS = ["#257de0", "#f47230", "#00b894", "#f2a600", "#ee7fac", "#008a17", "#6a4ce2", "#ec4647"];
  var MAXSEL = COLORS.length, slot = {};
  var SVGNS = "http://www.w3.org/2000/svg";
  var MES = ["jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez"];
  var MESL = ["janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho", "agosto", "setembro", "outubro", "novembro", "dezembro"];
  var DIM = { "Síntese global": ["Subsetor", "Subsetores", "Consolidado"],
    "Despesa do GRA por departamento": ["Departamento", "Departamentos", "Total"] };
  var DEFAULTS = { "Síntese global": ["Receita efetiva", "Despesa efetiva", "Saldo global"],
    "Receita fiscal do GRA": ["Receita fiscal", "Impostos diretos", "Impostos indiretos"],
    "Receita não fiscal do GRA": ["Receita não fiscal", "Correntes", "Capital"],
    "Despesa do GRA": ["Despesa efetiva", "Despesa corrente", "Despesas de capital"] };
  var table = null;

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

  function label(d) { return MES[+d.slice(5, 7) - 1] + " " + d.slice(0, 4); }
  function longLabel(d) { return MESL[+d.slice(5, 7) - 1] + " de " + d.slice(0, 4); }

  function index(rows) {
    rows.forEach(function (r) {
      var x = Q[r.quadro];
      if (!x) { x = Q[r.quadro] = { nome: r.quadro, rows: [], dims: {}, meds: {}, rub: {}, last: "", url: "" }; QORDER.push(r.quadro); }
      r.v = parseFloat(r.valor);
      x.rows.push(r); x.meds[r.medida] = 1;
      if (r.dimensao) x.dims[r.dimensao] = 1;
      if (!x.rub[r.caminho]) x.rub[r.caminho] = { caminho: r.caminho, rubrica: r.rubrica, nivel: +r.nivel, ordem: +r.ordem };
      if (r.data > x.last) { x.last = r.data; x.url = r.boletim; }
    });
  }

  function fillQuadros() {
    var sel = $("quadro");
    QORDER.forEach(function (q) { var o = document.createElement("option"); o.value = slug(q); o.textContent = q; sel.appendChild(o); });
    var latest = Q["Síntese global"];
    if (latest) {
      var p = $("ultimo"), a = document.createElement("a");
      a.href = latest.url; a.textContent = "boletim de " + longLabel(latest.last);
      p.append("Último boletim: ", a, ".");
      p.hidden = false;
    }
  }

  function opt(sel, items, keep, fallback) {
    sel.replaceChildren();
    items.forEach(function (it) {
      var o = document.createElement("option"); o.value = it[0]; o.textContent = it[1]; sel.appendChild(o);
    });
    var vals = items.map(function (it) { return it[0]; });
    sel.value = vals.indexOf(keep) >= 0 ? keep : vals.indexOf(fallback) >= 0 ? fallback : vals[0] || "";
    return sel.value;
  }

  // "Definição oficial: <law>; <law>" for a glossary entry.
  function sources(keys) {
    var dd = document.createElement("dd");
    dd.className = "fonte";
    dd.appendChild(document.createTextNode("Definição oficial: "));
    (keys || []).forEach(function (k, i) {
      var f = FONTES[k], a = document.createElement("a");
      if (!f) return;
      if (i) dd.appendChild(document.createTextNode("; "));
      a.href = f.url; a.textContent = f.nome;
      dd.appendChild(a);
    });
    return dd;
  }

  // The glossary entries that explain something in the table on screen.
  function fillTerms(names, euros) {
    var seen = {};
    names.forEach(function (n) { if (n) seen[fold(n)] = 1; });
    var hits = GLOSS.filter(function (g) {
      if (g.medida) return !euros;
      return (g.aplica || []).some(function (a) { return seen[fold(a)]; });
    });
    var dl = $("def-corpo"), frag = document.createDocumentFragment();
    hits.forEach(function (g) {
      var dt = document.createElement("dt"), dd = document.createElement("dd");
      dt.textContent = g.termo; dd.textContent = g.def;
      frag.appendChild(dt); frag.appendChild(dd);
      frag.appendChild(sources(g.fontes));
    });
    var note = document.createElement("dd");
    note.className = "fonte";
    note.innerHTML = 'Explicações do açores.net, não são texto oficial. <a href="#glossario">Glossário completo</a>.';
    if (hits.length) frag.appendChild(note);
    dl.replaceChildren(frag);
    $("def-resumo").textContent = hits.length ? "— " + hits.map(function (g) { return g.termo.toLowerCase(); }).slice(0, 4).join(", ") + (hits.length > 4 ? "…" : "") : "";
    $("def").hidden = !hits.length;
  }

  function rubricas(x) {
    return Object.keys(x.rub).map(function (k) { return x.rub[k]; }).sort(function (a, b) { return a.ordem - b.ordem; });
  }

  function prevMonth(d) {
    var y = +d.slice(0, 4), m = +d.slice(5, 7);
    return m === 1 ? null : y + "-" + String(m - 1).padStart(2, "0") + "-01";
  }

  function build() {
    var x = Q[st.q], dimInfo = DIM[st.q], dims = Object.keys(x.dims);
    // Controls for this quadro
    $("linhas-wrap").hidden = !dims.length;
    if (dims.length) st.linhas = opt($("linhas"), [["rubrica", "Rubricas"], ["dimensao", dimInfo[1]]], st.linhas, "rubrica");
    else st.linhas = "rubrica";
    $("filtro-wrap").hidden = !dims.length;
    var byDim = st.linhas === "dimensao";
    if (dims.length) {
      $("filtro-nome").textContent = byDim ? "Rubrica" : dimInfo[0];
      if (byDim) {
        var rs = rubricas(x), top = rs.filter(function (r) { return r.nivel === 0; });
        st.filtro = opt($("filtro"), rs.map(function (r) { return [r.caminho, "   ".repeat(r.nivel) + r.rubrica]; }),
          st.filtro, (top.filter(function (r) { return /^Despesa efetiva$/i.test(r.rubrica); })[0] || top[0] || {}).caminho);
      } else {
        var order = ["Governo Regional (GRA)", "Serviços e fundos autónomos (SFA)", "Entidades públicas reclassificadas (EPR)", "Consolidado"];
        dims.sort(function (a, b) {
          var ia = order.indexOf(a), ib = order.indexOf(b);
          if (ia >= 0 || ib >= 0) return (ia < 0 ? 99 : ia) - (ib < 0 ? 99 : ib);
          return a === "Total" ? -1 : b === "Total" ? 1 : a.localeCompare(b, "pt");
        });
        st.filtro = opt($("filtro"), dims.map(function (d) { return [d, d]; }), st.filtro, dimInfo[2]);
      }
    } else st.filtro = "";
    var meds = Object.keys(x.meds).sort(function (a) { return a === EUR ? -1 : 1; });
    $("med-wrap").hidden = meds.length < 2;
    st.med = opt($("med"), meds.map(function (m) { return [m, m]; }), st.med, EUR);
    var euros = st.med === EUR;
    if (!euros) st.modo = "acum";
    document.querySelector('[data-modo="mensal"]').disabled = !euros;

    // Pivot: one row per rubrica (or per subsetor/department), one column per month.
    var rows = {}, periods = {};
    x.rows.forEach(function (r) {
      if (r.medida !== st.med) return;
      if (dims.length && (byDim ? r.caminho !== st.filtro : r.dimensao !== st.filtro)) return;
      var k = byDim ? r.dimensao : r.caminho;
      var p = rows[k] || (rows[k] = byDim ? { key: k, nome: k, nivel: 0, ordem: 0, v: {} }
        : { key: k, nome: r.rubrica, nivel: x.rub[k].nivel, ordem: x.rub[k].ordem, caminho: k, v: {} });
      p.v[r.data] = r.v; periods[r.data] = 1;
    });
    var list = Object.keys(rows).map(function (k) { return rows[k]; });
    if (st.modo === "mensal") {
      list.forEach(function (p) {
        var m = {};
        Object.keys(p.v).forEach(function (d) {
          var pd = prevMonth(d);
          m[d] = pd === null ? p.v[d] : (p.v[pd] === undefined ? NaN : p.v[d] - p.v[pd]);
        });
        p.v = m;
      });
    }
    var keys = Object.keys(periods).sort();
    var shown = st.todos ? keys : keys.slice(-RECENT);
    // Hide rows without a value in the months shown (old departments).
    list = list.filter(function (p) { return shown.some(function (d) { return ok(p.v[d]); }); });
    var last = keys[keys.length - 1] || "", yearAgo = last ? (+last.slice(0, 4) - 1) + last.slice(4) : "";
    table = { all: keys, periods: shown, last: last, prev: periods[yearAgo] ? yearAgo : "", rows: list, byDim: byDim, euros: euros };
    $("todos").parentNode.hidden = keys.length <= RECENT;
    if (!st.sel) st.sel = defaultSel(x, list, byDim);
    st.sel = st.sel.filter(function (k) { return rows[k]; });
    if (!st.sel.length) st.sel = defaultSel(x, list, byDim);
    assignSlots();
    render();
  }

  function ok(v) { return v !== undefined && !isNaN(v); }

  function defaultSel(x, list, byDim) {
    var names = !byDim && DEFAULTS[x.nome];
    if (names) {
      var found = names.map(function (n) {
        return list.filter(function (p) { return fold(p.nome) === fold(n); }).sort(function (a, b) { return a.nivel - b.nivel; })[0];
      }).filter(Boolean).map(function (p) { return p.key; });
      if (found.length) return found;
    }
    var last = table.last, minLvl = Math.min.apply(null, list.map(function (p) { return p.nivel; }).concat([9]));
    return list.filter(function (p) { return p.nome !== "Total" && p.nivel <= minLvl + 1; })
      .sort(function (a, b) { return (ok(b.v[last]) ? b.v[last] : -Infinity) - (ok(a.v[last]) ? a.v[last] : -Infinity); })
      .slice(0, 3).map(function (p) { return p.key; });
  }

  function show(v) { return !ok(v) ? "–" : table.euros ? fmtM.format(v / 1e6) : fmtM.format(v) + "%"; }

  function change(p) {
    var a = p.v[table.prev], b = p.v[table.last];
    if (!table.prev || !ok(a) || !ok(b)) return NaN;
    if (!table.euros) return b - a;
    return a > 0 && b >= 0 ? (b / a - 1) * 100 : NaN; // not meaningful across signs
  }

  function render() {
    var x = Q[st.q], t = table;
    var terms = fold(st.busca).split(/\s+/).filter(Boolean);
    var rows = t.rows.filter(function (p) {
      var s = fold(p.nome + " " + (p.caminho || ""));
      return terms.every(function (w) { return s.indexOf(w) >= 0; });
    });
    var key = st.ord || (t.byDim ? t.last : "ordem"), dir = st.ord ? st.dir : (t.byDim ? -1 : 1);
    var get = function (p) {
      if (key === "ordem") return p.ordem;
      if (key === "nome") return p.nome;
      if (key === "var") return change(p);
      return p.v[key];
    };
    rows.sort(function (a, b) {
      var x1 = get(a), y1 = get(b);
      if (key === "nome") return x1.localeCompare(y1, "pt") * dir;
      var na = !ok(x1), nb = !ok(y1);
      if (na || nb) return na - nb;
      return (x1 - y1) * dir;
    });
    var tree = key === "ordem" && !terms.length;

    var first = t.byDim ? DIM[st.q][0] : "Rubrica";
    var cols = [["nome", first, ""]];
    t.periods.forEach(function (d) { cols.push([d, label(d), "num"]); });
    if (t.prev) cols.push(["var", "Var. face a " + label(t.prev) + (t.euros ? "" : " (pontos)"), "num"]);
    var tr = document.createElement("tr");
    cols.forEach(function (c) {
      var th = document.createElement("th"); th.scope = "col"; th.className = c[2];
      var b = document.createElement("button"); b.type = "button"; b.textContent = c[1];
      if (key === c[0] || (c[0] === "nome" && key === "ordem")) th.setAttribute("aria-sort", key === "ordem" ? "none" : dir > 0 ? "ascending" : "descending");
      b.addEventListener("click", function () {
        if (c[0] === "nome" && !t.byDim) { // rubrica column: boletim order, then A-Z, then Z-A
          if (key === "ordem") { st.ord = "nome"; st.dir = 1; } else if (key === "nome" && dir > 0) { st.dir = -1; } else { st.ord = null; }
        } else if (key === c[0]) { st.ord = c[0]; st.dir = -dir; } else { st.ord = c[0]; st.dir = c[0] === "nome" ? 1 : -1; }
        render(); writeHash();
      });
      th.appendChild(b); tr.appendChild(th);
    });
    $("tabela").tHead.replaceChildren(tr);

    var max = 0;
    rows.forEach(function (p) { var v = p.v[t.last]; if (ok(v) && Math.abs(v) > max) max = Math.abs(v); });
    var frag = document.createDocumentFragment();
    rows.forEach(function (p) {
      var r = document.createElement("tr"); if (tree && !t.byDim) r.className = "n" + p.nivel;
      var td = function (text, cls) { var c = document.createElement("td"); c.textContent = text; if (cls) c.className = cls; r.appendChild(c); return c; };
      var lc = td("", "lugar" + (tree && !t.byDim ? " n" + p.nivel : "")), lab = document.createElement("label"), cb = document.createElement("input");
      cb.type = "checkbox"; cb.checked = st.sel.indexOf(p.key) >= 0;
      cb.disabled = !cb.checked && st.sel.length >= MAXSEL;
      cb.setAttribute("aria-label", "Mostrar " + p.nome + " no gráfico");
      if (cb.checked) lc.style.setProperty("--c", colorOf(p.key));
      cb.addEventListener("change", function () { toggleSel(p.key); });
      lab.appendChild(cb); lab.appendChild(document.createTextNode(tree || t.byDim ? p.nome : (p.caminho || p.nome))); lc.appendChild(lab);
      t.periods.forEach(function (d) {
        var v = p.v[d], c = td(show(v), "num");
        if (!ok(v)) c.className += " falta";
        if (d === t.last && max && ok(v)) { c.className += " ult"; c.style.setProperty("--w", (Math.abs(v) / max * 100).toFixed(1) + "%"); }
      });
      if (t.prev) {
        var ch = change(p), c = td(isNaN(ch) ? "–" : pct.format(ch) + (t.euros ? "%" : ""), "num");
        c.className += isNaN(ch) ? " falta" : ch > 0 ? " sobe" : ch < 0 ? " desce" : "";
      }
      frag.appendChild(r);
    });
    $("tabela").tBodies[0].replaceChildren(frag);

    var a = document.createElement("a"); a.href = x.url; a.textContent = x.nome;
    $("titulo").replaceChildren(a);
    var what = t.euros ? "Milhões de euros, " + (st.modo === "mensal" ? "por mês" : "acumulado desde janeiro") : st.med + ", acumulada desde janeiro";
    $("sub").textContent = [what, DIM[st.q] ? (t.byDim ? Q[st.q].rub[st.filtro].rubrica : st.filtro) : "",
      t.all.length ? "de " + label(t.all[0]) + " a " + label(t.last) : "", "Boletim de Execução Orçamental"].filter(Boolean).join(" · ");
    $("nota").textContent = t.prev ? "A variação compara " + longLabel(t.last) + " com " + longLabel(t.prev) +
      (t.euros ? " (só quando os dois valores são positivos)." : ", em pontos percentuais.") : "";
    $("legenda").textContent = x.nome + (st.filtro ? ", " + st.filtro : "");
    fillTerms(rows.map(function (p) { return p.nome; }).concat([st.filtro, x.nome]), t.euros);
    $("estado").textContent = rows.length + (t.byDim ? " " + DIM[st.q][1].toLowerCase() : " rubricas") + ".";
    $("painel").hidden = false;
    document.querySelectorAll("#modo-wrap button").forEach(function (b) {
      b.setAttribute("aria-pressed", b.getAttribute("data-modo") === st.modo ? "true" : "false");
    });
    table.view = { cols: cols, rows: rows };
    applyVista();
    drawChart();
  }

  // ---- chart -------------------------------------------------------------
  function colorOf(k) { return COLORS[slot[k]] || "#586e75"; }

  function assignSlots() {
    Object.keys(slot).forEach(function (g) { if (st.sel.indexOf(g) < 0) delete slot[g]; });
    st.sel.forEach(function (g) {
      if (slot[g] !== undefined) return;
      var used = {}; Object.keys(slot).forEach(function (k) { used[slot[k]] = 1; });
      for (var i = 0; i < COLORS.length; i++) if (!used[i]) { slot[g] = i; break; }
    });
  }

  function toggleSel(k) {
    var i = st.sel.indexOf(k);
    if (i >= 0) st.sel.splice(i, 1); else if (st.sel.length < MAXSEL) st.sel.push(k);
    assignSlots(); render(); writeHash();
  }

  function applyVista() {
    $("grafico").hidden = st.vista === "tabela";
    $("tabela-wrap").hidden = st.vista === "grafico";
    document.querySelectorAll("[data-vista]").forEach(function (b) {
      b.setAttribute("aria-pressed", b.getAttribute("data-vista") === st.vista ? "true" : "false");
    });
    document.querySelectorAll("[data-graf]").forEach(function (b) {
      b.setAttribute("aria-pressed", b.getAttribute("data-graf") === st.graf ? "true" : "false");
    });
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

  var chart = null;

  // The series to draw: the selected rows over time, or, "ano a ano", one
  // line per year of the first selected row, January to December.
  function chartData() {
    var t = table, byKey = {};
    t.rows.forEach(function (p) { byKey[p.key] = p; });
    var sel = st.sel.filter(function (k) { return byKey[k]; });
    if (st.graf === "anos" && sel.length) {
      var p = byKey[sel[0]], years = {};
      Object.keys(p.v).forEach(function (d) { if (ok(p.v[d])) years[d.slice(0, 4)] = 1; });
      var ys = Object.keys(years).sort(), months = MES.map(function (_, i) { return String(i + 1).padStart(2, "0"); });
      return { keys: months, lab: function (m) { return MES[+m - 1]; }, longLab: function (m) { return MESL[+m - 1]; },
        title: p.nome, series: ys.map(function (y) {
          var v = {}; months.forEach(function (m) { v[m] = p.v[y + "-" + m + "-01"]; });
          return { key: y, nome: y, c: COLORS[(+y - 2023) % COLORS.length], v: v, fixed: true };
        }) };
    }
    return { keys: t.all, lab: label, longLab: longLabel, title: Q[st.q].nome,
      series: sel.map(function (k) { return { key: k, nome: byKey[k].nome, c: colorOf(k), v: byKey[k].v }; }) };
  }

  function drawChart() {
    if (st.vista === "tabela" || !table) return;
    var t = table, cd = chartData(), series = cd.series, keys = cd.keys;
    fillJuntar();
    drawLegend(series);
    var anos = st.graf === "anos";
    $("g-nota").hidden = !anos;
    $("g-nota").textContent = anos && series.length ? cd.title + ": cada linha é um ano." : "";
    var svg = $("g-svg"); svg.replaceChildren();
    var W = $("g-area").clientWidth || 600, narrow = W < 560;
    var H = narrow ? 240 : 320, direct = series.length <= 4 && !narrow;
    var m = { l: 8, r: direct ? 150 : 12, t: 10, b: 26 };
    var scale = t.euros ? 1e6 : 1, vals = [];
    series.forEach(function (s) { keys.forEach(function (k) { if (ok(s.v[k])) vals.push(s.v[k] / scale); }); });
    svg.setAttribute("viewBox", "0 0 " + W + " " + H); svg.setAttribute("height", H);
    svg.setAttribute("aria-label", cd.title + ": " + series.map(function (s) { return s.nome; }).join(", "));
    if (!vals.length || !keys.length) {
      var tx = el("text", { x: W / 2, y: H / 2, "text-anchor": "middle" }, svg);
      tx.textContent = series.length ? "Sem valores para as linhas escolhidas." : "Escolha pelo menos uma linha na tabela.";
      chart = null; return;
    }
    var lo = Math.min.apply(null, vals), hi = Math.max.apply(null, vals);
    if (lo >= 0 && lo < hi * 0.35) lo = 0; else { var pad = (hi - lo) * 0.08 || Math.abs(hi) * 0.05 || 1; lo -= pad; hi += pad; }
    if (lo < 0 && hi < 0) hi = 0;
    var ticks = niceTicks(lo, hi, narrow ? 4 : 5); lo = ticks[0]; hi = ticks[ticks.length - 1];
    var probe = el("text", {}, svg), wmax = 0;
    ticks.forEach(function (v) { probe.textContent = fmtAxis.format(v); wmax = Math.max(wmax, probe.getComputedTextLength()); });
    svg.removeChild(probe); m.l = Math.ceil(wmax) + 10;
    var iw = W - m.l - m.r, ih = H - m.t - m.b;
    var X = function (i) { return m.l + (keys.length === 1 ? iw / 2 : i * iw / (keys.length - 1)); };
    var Y = function (v) { return m.t + ih - (v / scale - lo) / (hi - lo) * ih; };
    ticks.forEach(function (v) {
      var y = m.t + ih - (v - lo) / (hi - lo) * ih;
      el("line", { x1: m.l, x2: m.l + iw, y1: y, y2: y, "class": v === 0 ? "eixo" : "grade" }, svg);
      var tx = el("text", { x: m.l - 6, y: y + 4, "text-anchor": "end" }, svg); tx.textContent = fmtAxis.format(v);
    });
    var every = Math.max(1, Math.ceil(keys.length / Math.max(2, Math.floor(iw / (narrow ? 56 : 72)))));
    keys.forEach(function (k, i) {
      if ((keys.length - 1 - i) % every) return;
      var tx = el("text", { x: X(i), y: H - 6, "text-anchor": "middle" }, svg); tx.textContent = cd.lab(k);
    });
    // Year-to-date values restart in January: over time, each year is its
    // own segment instead of a drop to zero.
    var restart = !anos && st.modo === "acum" && t.euros;
    series.forEach(function (s) {
      var d = "", prevOk = false;
      keys.forEach(function (k, i) {
        var v = s.v[k], good = ok(v);
        if (restart && k.slice(5, 7) === "01") prevOk = false;
        if (good) d += (prevOk ? "L" : "M") + X(i).toFixed(1) + " " + Y(v).toFixed(1);
        if (good && !prevOk && !ok(s.v[keys[i + 1]])) el("circle", { cx: X(i), cy: Y(v), r: 3.5, fill: s.c }, svg);
        prevOk = good;
      });
      if (d) el("path", { d: d, fill: "none", stroke: s.c, "stroke-width": 2, "stroke-linejoin": "round", "stroke-linecap": "round" }, svg);
    });
    var ends = [];
    series.forEach(function (s) {
      for (var i = keys.length - 1; i >= 0; i--) if (ok(s.v[keys[i]])) { ends.push({ s: s, i: i, y: Y(s.v[keys[i]]) }); break; }
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
        tx.textContent = e.s.nome.length > 19 ? e.s.nome.slice(0, 18) + "…" : e.s.nome;
      });
    }
    var g = el("g", {}, svg);
    var cross = el("line", { y1: m.t, y2: m.t + ih, "class": "cruz", visibility: "hidden" }, g);
    chart = { cd: cd, keys: keys, series: series, X: X, Y: Y, m: m, iw: iw, g: g, cross: cross, idx: -1, dots: [] };
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
    var hd = document.createElement("div"); hd.className = "p"; hd.textContent = c.cd.longLab(k); tip.appendChild(hd);
    c.series.slice().sort(function (a, b) { return (ok(b.v[k]) ? b.v[k] : -Infinity) - (ok(a.v[k]) ? a.v[k] : -Infinity); })
      .forEach(function (s) {
        var v = s.v[k];
        if (ok(v)) c.dots.push(el("circle", { cx: x, cy: c.Y(v), r: 4.5, fill: s.c, stroke: "#fdf6e3", "stroke-width": 2 }, c.g));
        var row = document.createElement("div"); row.className = "l";
        var key = document.createElement("i"); key.style.setProperty("--c", s.c);
        var b = document.createElement("b"); b.textContent = show(v) + (ok(v) && table.euros ? " M€" : "");
        var n = document.createElement("span"); n.textContent = s.nome;
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
      it.appendChild(key); it.appendChild(document.createTextNode(s.nome));
      if (!s.fixed) {
        var b = document.createElement("button"); b.type = "button"; b.textContent = "×";
        b.setAttribute("aria-label", "Tirar " + s.nome + " do gráfico");
        b.addEventListener("click", function () { toggleSel(s.key); });
        it.appendChild(b);
      }
      box.appendChild(it);
    });
  }

  function fillJuntar() {
    var sel = $("g-juntar"); sel.replaceChildren();
    var o0 = document.createElement("option"); o0.value = "";
    o0.textContent = st.graf === "anos" ? "Mudar de série…" : st.sel.length >= MAXSEL ? "Máximo de 8 linhas" : "Juntar ao gráfico…";
    sel.appendChild(o0);
    sel.disabled = st.graf !== "anos" && st.sel.length >= MAXSEL;
    table.rows.slice().sort(function (a, b) { return a.ordem - b.ordem || a.nome.localeCompare(b.nome, "pt"); }).forEach(function (p) {
      if (st.graf !== "anos" && st.sel.indexOf(p.key) >= 0) return;
      var o = document.createElement("option"); o.value = p.key;
      o.textContent = "  ".repeat(table.byDim ? 0 : p.nivel) + p.nome; sel.appendChild(o);
    });
  }

  function exportCSV(e) {
    var esc = function (s) { s = String(s); return /[",\n]/.test(s) ? '"' + s.replace(/"/g, '""') + '"' : s; };
    var head = [table.byDim ? DIM[st.q][0].toLowerCase() : "rubrica"].concat(table.periods);
    var body = table.view.rows.map(function (p) {
      return [p.caminho || p.nome].concat(table.periods.map(function (d) { return ok(p.v[d]) ? +p.v[d].toFixed(2) : ""; }));
    });
    var text = "﻿" + [head].concat(body).map(function (r) { return r.map(esc).join(","); }).join("\n");
    var url = URL.createObjectURL(new Blob([text], { type: "text/csv;charset=utf-8" }));
    e.currentTarget.href = url;
    e.currentTarget.download = "beo-" + slug(st.q) + (st.filtro ? "-" + slug(table.byDim ? Q[st.q].rub[st.filtro].rubrica : st.filtro) : "") +
      (st.modo === "mensal" ? "-mensal" : "") + ".csv";
    setTimeout(function () { URL.revokeObjectURL(url); }, 10000);
  }

  function readHash() {
    var p = new URLSearchParams(location.hash.slice(1)), qs = p.get("quadro");
    st.q = QORDER.filter(function (q) { return slug(q) === qs; })[0] || QORDER[0];
    st.linhas = p.get("linhas") === "dimensao" ? "dimensao" : "rubrica";
    st.filtro = p.get("filtro") || ""; st.med = p.get("medida") || EUR;
    st.modo = p.get("modo") === "mensal" ? "mensal" : "acum";
    st.graf = p.get("grafico") === "anos" ? "anos" : "tempo";
    st.busca = p.get("q") || ""; st.todos = p.get("todos") === "1";
    st.ord = p.get("ord") || null; st.dir = p.get("dir") === "desc" ? -1 : 1;
    st.vista = ["ambos", "grafico", "tabela"].indexOf(p.get("vista")) >= 0 ? p.get("vista") : "ambos";
    st.sel = p.get("sel") ? p.get("sel").split("|").filter(Boolean).slice(0, MAXSEL) : null;
    slot = {};
    $("quadro").value = slug(st.q); $("busca").value = st.busca; $("todos").checked = st.todos;
  }

  function writeHash() {
    var p = new URLSearchParams();
    [["quadro", slug(st.q)], ["linhas", st.linhas === "dimensao" ? "dimensao" : ""], ["filtro", st.filtro],
     ["medida", st.med === EUR ? "" : st.med], ["modo", st.modo === "mensal" ? "mensal" : ""], ["grafico", st.graf === "anos" ? "anos" : ""],
     ["q", st.busca], ["todos", st.todos ? "1" : ""], ["ord", st.ord || ""], ["dir", st.ord ? (st.dir > 0 ? "asc" : "desc") : ""],
     ["vista", st.vista === "ambos" ? "" : st.vista], ["sel", (st.sel || []).join("|")]]
      .forEach(function (kv) { if (kv[1]) p.set(kv[0], kv[1]); });
    history.replaceState(null, "", "#" + p.toString());
  }

  function on(id, ev, fn) { $(id).addEventListener(ev, function () { fn(); writeHash(); }); }
  on("quadro", "change", function () {
    st.q = QORDER.filter(function (q) { return slug(q) === $("quadro").value; })[0];
    st.linhas = "rubrica"; st.filtro = ""; st.med = EUR; st.ord = null; st.sel = null; st.busca = ""; $("busca").value = ""; slot = {}; build();
  });
  on("linhas", "change", function () { st.linhas = $("linhas").value; st.filtro = ""; st.ord = null; st.sel = null; slot = {}; build(); });
  on("filtro", "change", function () { st.filtro = $("filtro").value; build(); });
  on("med", "change", function () { st.med = $("med").value; build(); });
  on("todos", "change", function () { st.todos = $("todos").checked; build(); });
  document.querySelectorAll("#modo-wrap button").forEach(function (b) {
    b.addEventListener("click", function () { if (b.disabled) return; st.modo = b.getAttribute("data-modo"); build(); writeHash(); });
  });
  var timer;
  $("busca").addEventListener("input", function () { clearTimeout(timer); timer = setTimeout(function () { st.busca = $("busca").value.trim(); render(); writeHash(); }, 150); });
  $("exportar").addEventListener("click", exportCSV);
  document.querySelectorAll("[data-vista]").forEach(function (b) {
    b.addEventListener("click", function () { st.vista = b.getAttribute("data-vista"); applyVista(); drawChart(); writeHash(); });
  });
  document.querySelectorAll("[data-graf]").forEach(function (b) {
    b.addEventListener("click", function () { st.graf = b.getAttribute("data-graf"); applyVista(); drawChart(); writeHash(); });
  });
  $("g-juntar").addEventListener("change", function () {
    var k = $("g-juntar").value; if (!k) return;
    if (st.graf === "anos") { st.sel = [k].concat(st.sel.filter(function (x) { return x !== k; })).slice(0, MAXSEL); assignSlots(); render(); writeHash(); }
    else toggleSel(k);
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

  fetch("/dados/beo.csv?v=" + BUILD)
    .then(function (r) { if (!r.ok) throw new Error(r.status); return r.text(); })
    .then(function (text) {
      index(parseCSV(text)); fillQuadros(); readHash(); build(); writeHash();
      window.addEventListener("hashchange", function () { readHash(); build(); });
    })
    .catch(function (err) { $("estado").textContent = "Não foi possível carregar os dados (" + err.message + "). Use o ficheiro beo.csv."; });
})();
</script>
