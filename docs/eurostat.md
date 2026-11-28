---
title: Os Açores na Europa
layout: default
permalink: /dados/eurostat/
secao: estatisticas
description: Os Açores ao lado da Madeira, das Canárias e das regiões ultraperiféricas francesas, de Portugal, da União Europeia e de outras ilhas europeias - PIB, rendimento, emprego, educação, pobreza, população e saúde, com os dados regionais do Eurostat.
---
{%- assign e = site.data.eurostat -%}
{% include estatisticas-nav.html %}

# Os Açores na Europa

<p class="lead">Os Açores ao lado das outras regiões ultraperiféricas da
União Europeia (Madeira, Canárias e as cinco regiões francesas do
ultramar), de Portugal, da média da UE e de outras ilhas europeias, com os
dados regionais (NUTS 2) do <a href="https://ec.europa.eu/eurostat/web/regions/database">Eurostat</a>.
São as mesmas séries para todas as regiões, por isso comparam-se umas com as
outras; os números do <a href="/dados/srea/">SREA</a> e do
<a href="/dados/ine/">INE</a> podem diferir nas datas e nas revisões.</p>

{% if e %}
<nav class="indice" aria-label="Nesta página">
  <a href="#rup"><span>1</span> Regiões ultraperiféricas</a>
  <a href="#ilhas"><span>2</span> Outras ilhas</a>
  <a href="#evolucao"><span>3</span> Evolução</a>
  <a href="#notas"><span>4</span> Notas</a>
</nav>

{%- assign rup = "PT20,PT30,ES70,FRY4,FRY1,FRY2,FRY3,FRY5,PT,EU27_2020" | split: "," -%}
{%- assign ilhas = "PT20,ES53,FRM0,ITG2,EL43,MT00,CY00,FI20,IS00,PT,EU27_2020" | split: "," -%}


<h2 id="rup">1. Face às regiões ultraperiféricas</h2>
<p class="nota">O valor mais recente de cada região. Um ano em expoente
quer dizer que o valor não é do mesmo ano que o dos Açores; um asterisco,
que o Eurostat o marca como provisório, estimado ou pouco fiável (passe o
rato ou toque para ver). A posição conta só as regiões ultraperiféricas com
valor nesse ano: 1.ª é a do valor mais alto.</p>
<div class="tabela-scroll">
<table class="sper eurostat">
<thead><tr>
  <th scope="col">Indicador</th>
  <th scope="col" class="n">Ano</th>
  {%- for g in rup -%}{%- for r in e.regioes -%}{%- if r.geo == g %}<th scope="col" class="n{% if g == 'PT20' %} az{% endif %}{% if g == 'PT' %} sep{% endif %}">{{ r.nome }}</th>{% endif -%}{%- endfor -%}{%- endfor %}
  <th scope="col" class="n">Posição dos Açores</th>
</tr></thead>
{%- for t in e.temas %}
<tbody>
<tr class="tema"><th colspan="{{ rup.size | plus: 3 }}" scope="rowgroup">{{ t.tema }}</th></tr>
{%- for l in t.linhas %}
<tr><th scope="row">{{ l.nome }} <small>({{ l.unidade }})</small></th><td class="n">{{ l.ano }}</td>
{%- for g in rup -%}
{%- assign v = l.valores[g] -%}
<td class="n{% if g == 'PT20' %} az{% endif %}{% if g == 'PT' %} sep{% endif %}"{% if v.estado != "" and v %} title="{{ v.estado }}"{% endif %}>{% if v %}{{ v.v }}{% if v.estado != "" %}<span class="est">*</span>{% endif %}{% if v.outro_ano %}<sup>{{ v.ano }}</sup>{% endif %}{% else %}–{% endif %}</td>
{%- endfor -%}
<td class="n">{% if l.posicao %}{{ l.posicao[0] }}.ª de {{ l.posicao[1] }}{% else %}–{% endif %}</td></tr>
{%- endfor %}
</tbody>
{%- endfor %}
</table>
</div>

<h2 id="ilhas">2. Face a outras ilhas europeias</h2>
<p class="nota">Ilhas e arquipélagos que são regiões NUTS 2 (ou países) com
séries no Eurostat. A Islândia está fora das contas regionais da UE, por
isso aparece só onde há dados.</p>
<div class="tabela-scroll">
<table class="sper eurostat">
<thead><tr>
  <th scope="col">Indicador</th>
  {%- for g in ilhas -%}{%- for r in e.regioes -%}{%- if r.geo == g %}<th scope="col" class="n{% if g == 'PT20' %} az{% endif %}{% if g == 'PT' %} sep{% endif %}">{{ r.nome }}</th>{% endif -%}{%- endfor -%}{%- endfor %}
</tr></thead>
{%- for t in e.temas %}
<tbody>
<tr class="tema"><th colspan="{{ ilhas.size | plus: 1 }}" scope="rowgroup">{{ t.tema }}</th></tr>
{%- for l in t.linhas %}
<tr><th scope="row">{{ l.nome }} <small>({{ l.unidade }})</small></th>
{%- for g in ilhas -%}
{%- assign v = l.valores[g] -%}
<td class="n{% if g == 'PT20' %} az{% endif %}{% if g == 'PT' %} sep{% endif %}"{% if v.estado != "" and v %} title="{{ v.estado }}"{% endif %}>{% if v %}{{ v.v }}{% if v.estado != "" %}<span class="est">*</span>{% endif %}{% if v.outro_ano or g == "PT20" %}<sup>{{ v.ano }}</sup>{% endif %}{% else %}–{% endif %}</td>
{%- endfor -%}
</tr>
{%- endfor %}
</tbody>
{%- endfor %}
</table>
</div>

<h2 id="evolucao">3. Evolução</h2>
<noscript><p>O gráfico precisa de JavaScript. As séries completas estão em
<a href="/dados/eurostat.csv">eurostat.csv</a>.</p></noscript>
<figure class="grafico" id="g-eurostat">
  <div class="g-escolha">
    <label>Indicador <select class="g-indicador"></select></label>
    <label>Comparar com <select class="g-grupo">
      <option value="rup">regiões ultraperiféricas</option>
      <option value="ilha">outras ilhas</option>
    </select></label>
  </div>
  <figcaption></figcaption>
  <div class="g-legenda"></div>
  <div class="g-area"><svg role="img" tabindex="0"></svg><div class="g-tip" hidden></div></div>
  <p class="fonte"></p>
  <details class="g-tabela"><summary>Ver os números</summary><div></div></details>
</figure>

<h2 id="notas">4. Notas</h2>
<ul class="notas">
  <li><strong>Paridade de poder de compra (PPC).</strong> O PIB e o
  rendimento em PPC descontam as diferenças de preços entre países (não
  entre regiões do mesmo país): os Açores e Lisboa usam o mesmo deflator.</li>
  <li><strong>Amostras pequenas.</strong> O desemprego, o abandono escolar,
  os jovens que não trabalham nem estudam e a pobreza vêm de inquéritos
  (Inquérito ao Emprego, EU-SILC). Nas regiões pequenas o Eurostat marca
  muitos valores como pouco fiáveis e omite outros; o desemprego jovem dos
  Açores não é publicado desde 2014.</li>
  <li><strong>Média da UE.</strong> As tabelas regionais de pobreza e de
  demografia não trazem a média da UE (só países e regiões); fica «–».</li>
  <li><strong>Atualização.</strong> As tabelas são relidas uma vez por
  semana por
  <a href="https://github.com/fmesqg/a-ores.net-site/blob/main/bot/eurostat.py"><code>bot/eurostat.py</code></a>.
  Última atualização do Eurostat: {{ e.atualizado }}. Todos os valores, com a
  marca do Eurostat, estão em <a href="/dados/eurostat.csv">eurostat.csv</a> e na
  tabela <code>eurostat</code> de <a href="/dados/sql/">estatisticas.db</a>.</li>
</ul>
{% else %}
<p>Os dados ainda não foram gerados.</p>
{% endif %}

<style>
.lead { font-size: 1.15em; max-width: 40em; }
h2[id] { scroll-margin-top: 1em; margin-top: 1.4em; }
table.eurostat { font-size: .9em; }
table.eurostat th[scope="row"] { font-weight: normal; min-width: 14em; }
table.eurostat th[scope="row"] small { color: var(--s01); }
table.eurostat tr.tema th { text-align: left; font-weight: bold; padding-top: .9em; }
table.eurostat .az { font-weight: bold; background: rgba(37,125,224,.09); }
table.eurostat .sep { border-left: 1px solid var(--s1); }
table.eurostat sup { color: var(--s01); font-size: .72em; margin-left: .15em; }
table.eurostat .est { color: var(--s01); }
table.eurostat td[title] { cursor: help; }
.grafico { margin: 1em 0 1.4em; max-width: 46em; }
.grafico figcaption { font-weight: bold; margin: .6em 0 .4em; }
.g-escolha { display: flex; flex-wrap: wrap; gap: .4em 1em; font-size: .9em; }
.g-escolha select { font: inherit; padding: .15em .3em; max-width: min(30em, 100%); }
.g-legenda { display: flex; flex-wrap: wrap; gap: .3em .9em; font-size: .85em; color: var(--s01); margin-bottom: .3em; }
.g-legenda span { display: inline-flex; align-items: center; gap: .35em; }
.g-legenda i, .g-tip i { display: inline-block; width: 14px; border-top: 2px solid var(--c); border-radius: 2px; }
.g-legenda i.tracejado, .g-tip i.tracejado { border-top-style: dashed; }
.g-area { position: relative; }
.grafico svg { display: block; width: 100%; overflow: visible; touch-action: pan-y; }
.grafico svg:focus-visible { outline: 3px solid #268bd2; outline-offset: 1px; }
.grafico svg text { font-size: 12px; fill: var(--s01); font-variant-numeric: tabular-nums; }
.grafico svg .grade { stroke: var(--s2); stroke-width: 1; }
.grafico svg .eixo { stroke: var(--s1); stroke-width: 1; }
.grafico svg .cruz { stroke: var(--s1); stroke-width: 1; }
.grafico svg .rotulo { fill: var(--s02); }
.g-tip { position: absolute; pointer-events: none; background: #fffdf5; border: 1px solid var(--s1); border-radius: 6px; padding: .4em .6em; font-size: .85em; box-shadow: 0 2px 6px rgba(0,0,0,.12); min-width: 10em; z-index: 3; }
.g-tip .p { font-weight: bold; margin-bottom: .2em; }
.g-tip .l { display: flex; align-items: center; gap: .4em; white-space: nowrap; }
.g-tip .l b { margin-left: auto; font-variant-numeric: tabular-nums; }
.g-tip .l.az { font-weight: bold; }
.g-tabela { margin-top: .4em; font-size: .9em; }
.g-tabela summary { cursor: pointer; color: var(--s01); }
.g-tabela div { max-height: 22em; overflow: auto; }
.g-tabela table { border-collapse: collapse; font-variant-numeric: tabular-nums; }
.g-tabela th, .g-tabela td { padding: .15em .6em; text-align: right; border-bottom: 1px solid rgba(147,161,161,.3); white-space: nowrap; }
.g-tabela th:first-child, .g-tabela td:first-child { text-align: left; }
.fonte { font-size: .85em; color: var(--s01); }
@media (prefers-color-scheme: dark) {
  table.eurostat .az { background: rgba(37,125,224,.18); }
  .grafico svg .grade { stroke: rgba(147,161,161,.22); }
  .g-tip { background: var(--s2); }
}
</style>

<script>
(function () {
  "use strict";
  var fig = document.getElementById("g-eurostat");
  if (!fig) return;
  var BUILD = "{{ site.time | date: '%s' }}";
  // the site's categorical order (INE, BEO, SREA pages): Azores first,
  // Portugal second; the other regions are grey context
  var C_AZ = "#257de0", C_PT = "#f47230", C_UE = "#6c71c4";
  var SVGNS = "http://www.w3.org/2000/svg";
  var n2 = new Intl.NumberFormat("pt-PT", { maximumFractionDigits: 2, useGrouping: "always" });
  var nBig = new Intl.NumberFormat("pt-PT", { maximumFractionDigits: 0, useGrouping: "always" });
  var DATA, sel = fig.querySelector(".g-indicador"), grp = fig.querySelector(".g-grupo");

  function el(name, attrs, parent) {
    var e = document.createElementNS(SVGNS, name);
    Object.keys(attrs || {}).forEach(function (k) { e.setAttribute(k, attrs[k]); });
    if (parent) parent.appendChild(e);
    return e;
  }
  function h(tag, text, parent) {
    var e = document.createElement(tag);
    if (text != null) e.textContent = text;
    if (parent) parent.appendChild(e);
    return e;
  }
  function niceTicks(lo, hi, n) {
    var step = Math.pow(10, Math.floor(Math.log10((hi - lo) / n)));
    var err = (hi - lo) / n / step;
    step *= err >= 7.5 ? 10 : err >= 3.5 ? 5 : err >= 1.5 ? 2 : 1;
    var out = [];
    for (var v = Math.floor(lo / step) * step; v <= hi + step / 2; v += step) out.push(+v.toFixed(10));
    if (out[out.length - 1] < hi) out.push(out[out.length - 1] + step);
    return out;
  }

  function series(ind, grupo) {
    var nomes = {}; DATA.regioes.forEach(function (r) { nomes[r.geo] = r; });
    var out = [];
    Object.keys(ind.s).forEach(function (g) {
      var r = nomes[g]; if (!r) return;
      var keep = g === "PT20" || g === "PT" || g === "EU27_2020" || r.grupo === grupo;
      if (!keep) return;
      var v = {}, est = {};
      ind.s[g].forEach(function (p) { v[p[0]] = p[1]; if (p[2]) est[p[0]] = p[2]; });
      out.push({
        geo: g, nome: r.nome, v: v, est: est,
        c: g === "PT20" ? C_AZ : g === "PT" ? C_PT : g === "EU27_2020" ? C_UE : "var(--s1)",
        w: g === "PT20" ? 2.5 : g === "PT" || g === "EU27_2020" ? 2 : 1.25,
        dash: g === "EU27_2020" ? "5 4" : null,
        fundo: !(g === "PT20" || g === "PT" || g === "EU27_2020")
      });
    });
    // context first (drawn underneath), then UE, Portugal, Azores on top
    var ordem = { EU27_2020: 1, PT: 2, PT20: 3 };
    out.sort(function (a, b) { return (ordem[a.geo] || 0) - (ordem[b.geo] || 0); });
    return out;
  }

  function draw() {
    var ind = DATA.indicadores[+sel.value], grupo = grp.value;
    var ss = series(ind, grupo);
    var big = /pessoas|€|PPC|hab\./.test(ind.unidade);
    var fmt = function (v) { return big ? nBig.format(v) : n2.format(v); };
    var anos = {};
    ss.forEach(function (s) { Object.keys(s.v).forEach(function (k) { anos[k] = 1; }); });
    var keys = Object.keys(anos).map(Number).sort(function (a, b) { return a - b; });
    // from the first year the Azores have a value
    var az = ss.filter(function (s) { return s.geo === "PT20"; })[0];
    if (az) { var y0 = Math.min.apply(null, Object.keys(az.v).map(Number)); keys = keys.filter(function (k) { return k >= y0; }); }
    fig.querySelector("figcaption").textContent = ind.nome + " (" + ind.unidade + ")";
    var leg = fig.querySelector(".g-legenda"); leg.replaceChildren();
    [["Açores", C_AZ], ["Portugal", C_PT], ["União Europeia", C_UE, true],
     [grupo === "rup" ? "Outras regiões ultraperiféricas" : "Outras ilhas", "var(--s1)"]].forEach(function (x) {
      var it = h("span", null, leg), i = h("i", null, it); i.style.setProperty("--c", x[1]);
      if (x[2]) i.className = "tracejado";
      it.appendChild(document.createTextNode(x[0]));
    });
    var svg = fig.querySelector("svg"), tip = fig.querySelector(".g-tip"), area = fig.querySelector(".g-area");
    svg.replaceChildren();
    var W = area.clientWidth || 600, narrow = W < 520, H = narrow ? 240 : 300;
    var m = { l: 8, r: narrow ? 14 : 110, t: 10, b: 26 };
    var vals = [];
    ss.forEach(function (s) { keys.forEach(function (k) { if (s.v[k] != null) vals.push(s.v[k]); }); });
    svg.setAttribute("viewBox", "0 0 " + W + " " + H); svg.setAttribute("height", H);
    svg.setAttribute("aria-label", fig.querySelector("figcaption").textContent);
    if (!vals.length) { el("text", { x: W / 2, y: H / 2, "text-anchor": "middle" }, svg).textContent = "Sem dados."; return; }
    var lo = Math.min.apply(null, vals), hi = Math.max.apply(null, vals);
    if (lo > 0 && lo < hi * 0.35) lo = 0;
    if (lo === hi) { lo -= 1; hi += 1; }
    var ticks = niceTicks(lo, hi, narrow ? 4 : 5); lo = ticks[0]; hi = ticks[ticks.length - 1];
    var tfmt = function (v) { return Math.abs(hi) >= 1e6 ? n2.format(v / 1e6) + " M" : Math.abs(hi) >= 1e4 ? n2.format(v / 1e3) + " mil" : n2.format(v); };
    var probe = el("text", {}, svg), wmax = 0;
    ticks.forEach(function (v) { probe.textContent = tfmt(v); wmax = Math.max(wmax, probe.getComputedTextLength()); });
    svg.removeChild(probe); m.l = Math.ceil(wmax) + 10;
    var iw = W - m.l - m.r, ih = H - m.t - m.b;
    var X = function (i) { return m.l + (keys.length === 1 ? iw / 2 : i * iw / (keys.length - 1)); };
    var Y = function (v) { return m.t + ih - (v - lo) / (hi - lo) * ih; };
    ticks.forEach(function (v) {
      el("line", { x1: m.l, x2: m.l + iw, y1: Y(v), y2: Y(v), "class": v === 0 ? "eixo" : "grade" }, svg);
      el("text", { x: m.l - 6, y: Y(v) + 4, "text-anchor": "end" }, svg).textContent = tfmt(v);
    });
    var every = Math.max(1, Math.ceil(keys.length / Math.max(2, Math.floor(iw / (narrow ? 44 : 56)))));
    keys.forEach(function (k, i) {
      if ((keys.length - 1 - i) % every) return;
      el("text", { x: X(i), y: H - 6, "text-anchor": "middle" }, svg).textContent = k;
    });
    var ends = [];
    ss.forEach(function (s) {
      var d = "", prev = false, last = -1;
      keys.forEach(function (k, i) {
        var v = s.v[k];
        if (v != null) { d += (prev ? "L" : "M") + X(i).toFixed(1) + " " + Y(v).toFixed(1); last = i; }
        if (v != null && !prev && s.v[keys[i + 1]] == null) el("circle", { cx: X(i), cy: Y(v), r: s.fundo ? 2.5 : 3.5, fill: s.c }, svg);
        prev = v != null;
      });
      var attrs = { d: d, fill: "none", stroke: s.c, "stroke-width": s.w, "stroke-linejoin": "round", "stroke-linecap": "round" };
      if (s.dash) attrs["stroke-dasharray"] = s.dash;
      if (s.fundo) attrs["stroke-opacity"] = 0.8;
      if (d) el("path", attrs, svg);
      if (last >= 0 && !s.fundo) ends.push({ s: s, i: last, y: Y(s.v[keys[last]]) });
    });
    ends.forEach(function (e) { el("circle", { cx: X(e.i), cy: e.y, r: 4, fill: e.s.c, stroke: "#fdf6e3", "stroke-width": 2 }, svg); });
    if (!narrow) {
      ends.sort(function (a, b) { return a.y - b.y; });
      var ly = ends.map(function (e) { return e.y; });
      for (var j = 1; j < ly.length; j++) if (ly[j] - ly[j - 1] < 15) ly[j] = ly[j - 1] + 15;
      ends.forEach(function (e, j) {
        el("text", { x: X(e.i) + 10, y: ly[j] + 4, "class": "rotulo" }, svg).textContent = e.s.nome;
      });
    }
    var g = el("g", {}, svg), cross = el("line", { y1: m.t, y2: m.t + ih, "class": "cruz", visibility: "hidden" }, g), dots = [];
    function show(i) {
      i = Math.max(0, Math.min(keys.length - 1, i));
      var k = keys[i], x = X(i);
      cross.setAttribute("x1", x); cross.setAttribute("x2", x); cross.setAttribute("visibility", "visible");
      dots.forEach(function (d) { d.remove(); }); dots = [];
      tip.replaceChildren(); h("div", String(k), tip).className = "p";
      ss.filter(function (s) { return s.v[k] != null; })
        .sort(function (a, b) { return b.v[k] - a.v[k]; })
        .forEach(function (s) {
          if (!s.fundo) dots.push(el("circle", { cx: x, cy: Y(s.v[k]), r: 4.5, fill: s.c, stroke: "#fdf6e3", "stroke-width": 2 }, g));
          var row = h("div", null, tip); row.className = "l" + (s.geo === "PT20" ? " az" : "");
          var key = h("i", null, row); key.style.setProperty("--c", s.c); if (s.dash) key.className = "tracejado";
          h("span", s.nome, row);
          h("b", fmt(s.v[k]) + (s.est[k] ? "*" : ""), row);
        });
      tip.hidden = false;
      var sx = area.clientWidth / W, left = x * sx + 14;
      if (left + tip.offsetWidth > area.clientWidth) left = x * sx - tip.offsetWidth - 14;
      tip.style.left = Math.max(0, left) + "px"; tip.style.top = (m.t + 4) + "px";
    }
    function hide() { cross.setAttribute("visibility", "hidden"); dots.forEach(function (d) { d.remove(); }); dots = []; tip.hidden = true; }
    var hit = el("rect", { x: m.l, y: m.t, width: iw, height: ih, fill: "transparent" }, svg), cur = keys.length - 1;
    hit.addEventListener("pointermove", function (e) {
      var r = svg.getBoundingClientRect(), px = (e.clientX - r.left) * (W / r.width);
      cur = Math.round((px - m.l) / (keys.length > 1 ? iw / (keys.length - 1) : 1)); show(cur);
    });
    hit.addEventListener("pointerdown", function (e) { hit.dispatchEvent(new PointerEvent("pointermove", e)); });
    hit.addEventListener("pointerleave", hide);
    svg.onkeydown = function (e) {
      if (e.key === "ArrowLeft" || e.key === "ArrowRight") { cur = Math.max(0, Math.min(keys.length - 1, cur + (e.key === "ArrowLeft" ? -1 : 1))); show(cur); e.preventDefault(); }
      if (e.key === "Escape") hide();
    };
    svg.onblur = hide;
    var p = fig.querySelector(".fonte"); p.replaceChildren();
    p.appendChild(document.createTextNode("Fonte: Eurostat, tabela "));
    var a = h("a", ind.tabela, p); a.href = "https://ec.europa.eu/eurostat/databrowser/view/" + ind.tabela + "/default/table";
    p.appendChild(document.createTextNode(", atualizada a " + ind.atualizado + ". * provisório, estimado ou pouco fiável."));
    // the same numbers as a table, newest first, Azores first
    var box = fig.querySelector(".g-tabela div"); box.replaceChildren();
    var cols = ss.slice().reverse();
    var tb = h("table", null, box), tr = h("tr", null, h("thead", null, tb));
    h("th", "Ano", tr); cols.forEach(function (s) { h("th", s.nome, tr); });
    var body = h("tbody", null, tb);
    keys.slice().reverse().forEach(function (k) {
      var r = h("tr", null, body); h("td", String(k), r);
      cols.forEach(function (s) { var v = s.v[k]; h("td", v == null ? "–" : fmt(v) + (s.est[k] ? "*" : ""), r); });
    });
  }

  fetch("/dados/eurostat.json?v=" + BUILD).then(function (r) { return r.json(); }).then(function (d) {
    DATA = d;
    var tema = "";
    var og;
    d.indicadores.forEach(function (ind, i) {
      if (ind.tema !== tema) { og = h("optgroup", null, sel); og.label = tema = ind.tema; }
      var o = h("option", ind.nome, og); o.value = i;
    });
    var hash = new URLSearchParams(location.hash.slice(1));
    var want = hash.get("indicador");
    d.indicadores.forEach(function (ind, i) { if (ind.id === want) sel.value = i; });
    if (hash.get("comparar") === "ilha") grp.value = "ilha";
    function update() {
      history.replaceState(null, "", "#indicador=" + d.indicadores[+sel.value].id + (grp.value === "ilha" ? "&comparar=ilha" : ""));
      draw();
    }
    sel.addEventListener("change", update); grp.addEventListener("change", update);
    draw();
    var t; window.addEventListener("resize", function () { clearTimeout(t); t = setTimeout(draw, 150); });
  }).catch(function () {
    fig.querySelector("figcaption").textContent = "Não foi possível carregar os dados.";
  });
})();
</script>
