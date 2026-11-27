---
title: Indicadores da economia
layout: default
permalink: /dados/srea/
secao: economia
description: Preços, emprego, atividade económica, turismo e PIB por ilha nos Açores, com os números mais recentes do Serviço Regional de Estatística dos Açores (SREA), explicados.
---
{%- assign s = site.data.resumo.srea -%}
{%- assign f = site.data.fontes -%}
{% include economia-nav.html %}

# Indicadores da economia

<p class="lead">Como estão os preços, o emprego, a economia e o turismo nos
Açores: os números mais recentes do <a href="{{ f.srea.url }}">Serviço
Regional de Estatística dos Açores (SREA)</a>, a estatística oficial da
Região, explicados sem jargão. A página atualiza-se todas as semanas.</p>

<nav class="indice" aria-label="Nesta página">
  <a href="#precos"><span>1</span> Preços</a>
  <a href="#emprego"><span>2</span> Emprego</a>
  <a href="#atividade"><span>3</span> Atividade e consumo</a>
  <a href="#turismo"><span>4</span> Turismo por ilha</a>
  <a href="#ilhas"><span>5</span> O que cada ilha produz</a>
  <a href="#palavras"><span>6</span> Palavras e dados</a>
</nav>

<noscript><p>Os gráficos precisam de JavaScript. Os números estão em
<a href="/dados/srea.csv">srea.csv</a>.</p></noscript>

<h2 id="precos">1. Preços</h2>
{% if s.ipc %}
<p class="grande">{{ s.ipc.valor_t }}%<small> em um ano</small></p>
<p>Entre {{ s.ipc.antes }} e {{ s.ipc.periodo }} os preços nos Açores
subiram {{ s.ipc.valor_t }}%: o que custava 100 € custa agora, em média,
cerca de {{ s.ipc.cem | round: 2 | replace: ".", "," }} €. É a inflação
medida pelo índice de preços no consumidor (IPC) dos Açores.
{%- if s.ipc.media12 %} Em média, nos últimos doze meses, a subida foi de
{{ s.ipc.media12_t }}%.{% endif %}</p>
<div class="duas">
<div>
<p><strong>O que mais subiu</strong></p>
<ul>{% for c in s.ipc.mais %}<li>{{ c.nome | escape }}: {{ c.valor_t }}%</li>{% endfor %}</ul>
</div>
<div>
<p><strong>O que menos subiu ou desceu</strong></p>
<ul>{% for c in s.ipc.menos %}<li>{{ c.nome | escape }}: {{ c.valor_t }}%</li>{% endfor %}</ul>
</div>
</div>
{% endif %}
<figure class="grafico" data-g="ipc">
  <figcaption>Inflação nos Açores: variação dos preços face ao mesmo mês do ano anterior (%)</figcaption>
  <div class="g-topo"><div class="g-legenda"></div><div class="g-vista" role="group" aria-label="Período"></div></div>
  <div class="g-area"><svg role="img" tabindex="0"></svg><div class="g-tip" hidden></div></div>
  <details class="g-tabela"><summary>Ver os números</summary><div></div></details>
  <p class="fonte"></p>
</figure>

<h2 id="emprego">2. Emprego</h2>
{% if s.desemprego %}
<p class="grande">{{ s.desemprego.valor_t }}%<small> de desemprego</small></p>
<p>No {{ s.desemprego.periodo }}, {{ s.desemprego.valor_t }} em cada 100
pessoas ativas (as que trabalham ou procuram trabalho) estavam
desempregadas{% if s.desemprego.antes %}; um ano antes, no
{{ s.desemprego.periodo_antes }}, eram {{ s.desemprego.antes_t }}%{% endif %}.</p>
<p class="aviso">O número vem de um inquérito a uma amostra de famílias, e o
SREA marca-o como <em>dado com fiabilidade reduzida</em>: uma diferença de
poucas décimas de um trimestre para o outro pode não querer dizer nada.
Olhe para a tendência de vários trimestres.</p>
{% endif %}
<figure class="grafico" data-g="desemprego">
  <figcaption>Taxa de desemprego nos Açores, por trimestre (%)</figcaption>
  <div class="g-topo"><div class="g-legenda"></div></div>
  <div class="g-area"><svg role="img" tabindex="0"></svg><div class="g-tip" hidden></div></div>
  <details class="g-tabela"><summary>Ver os números</summary><div></div></details>
  <p class="fonte"></p>
</figure>

<h2 id="atividade">3. Atividade e consumo</h2>
<div class="cartoes">
{% if s.iae %}
<section class="cartao">
  <h3>Atividade económica</h3>
  <p class="grande">{{ s.iae.valor | round: 1 | replace: ".", "," }}%<small> em {{ s.iae.periodo }}</small></p>
  <p>Acima de zero, a economia dos Açores está a produzir mais do que
  um ano antes; abaixo de zero, menos. Junta num só número vários
  indicadores que saem todos os meses.</p>
  <p class="fonte">Fonte: <a href="{{ s.iae.url }}">SREA, Indicador de Atividade Económica (IAE-Açores)</a></p>
</section>
{% endif %}
{% if s.icp %}
<section class="cartao">
  <h3>Consumo das famílias</h3>
  <p class="grande">{{ s.icp.valor | round: 1 | replace: ".", "," }}%<small> em {{ s.icp.periodo }}</small></p>
  <p>Quanto as famílias compram, descontada a subida dos preços, face ao
  ano anterior. Acima de zero, compram mais; abaixo, menos.</p>
  <p class="fonte">Fonte: <a href="{{ s.icp.url }}">SREA, Indicador do Consumo Privado (ICP-Açores)</a></p>
</section>
{% endif %}
</div>
<figure class="grafico" data-g="atividade">
  <figcaption>Atividade económica e consumo das famílias: variação face ao ano anterior (%)</figcaption>
  <div class="g-topo"><div class="g-legenda"></div><div class="g-vista" role="group" aria-label="Período"></div></div>
  <div class="g-area"><svg role="img" tabindex="0"></svg><div class="g-tip" hidden></div></div>
  <details class="g-tabela"><summary>Ver os números</summary><div></div></details>
  <p class="fonte"></p>
</figure>

<h2 id="turismo">4. Turismo por ilha</h2>
{% if s.dormidas %}
<p class="grande">{{ s.dormidas.valor | divided_by: 10000 | divided_by: 100.0 | round: 2 | replace: ".", "," }} milhões<small> de dormidas</small></p>
<p>De {{ s.dormidas.periodo }}, hotéis e alojamento local dos Açores
contaram {{ s.dormidas.valor_t }} dormidas (cada noite de cada hóspede
conta uma){% if s.dormidas.var %}, {% if s.dormidas.var < 0 %}menos{% else %}mais{% endif %}
{{ s.dormidas.var | abs | replace: ".", "," }}% do que nos mesmos meses do ano anterior{% endif %}.</p>
<figure class="barras">
  <figcaption>Dormidas por ilha, {{ s.dormidas.periodo }}, e variação face ao ano anterior</figcaption>
  {%- assign top = s.dormidas.ilhas.first.valor %}
  {%- for i in s.dormidas.ilhas %}
  <div class="barra"><span>{{ i.ilha }}</span>
    <span class="trilho"><span class="valor" style="width: {{ i.valor | times: 100.0 | divided_by: top | round: 1 }}%"></span></span>
    <span class="num">{{ i.valor_t }}{% if i.var %}<small>{% if i.var > 0 %}+{% endif %}{{ i.var_t }}%</small>{% endif %}</span></div>
  {%- endfor %}
</figure>
{% endif %}
<figure class="grafico" data-g="turismo">
  <figcaption>Dormidas mês a mês: este ano e o anterior</figcaption>
  <div class="g-topo">
    <label class="g-escolha">Ilha <select class="g-ilha"></select></label>
    <label class="g-escolha">Alojamento <select class="g-tipo">
      <option value="">Hotéis e alojamento local</option>
      <option value="Hotelaria">Só hotelaria</option>
      <option value="Alojamento local">Só alojamento local</option>
    </select></label>
    <div class="g-legenda"></div>
  </div>
  <div class="g-area"><svg role="img" tabindex="0"></svg><div class="g-tip" hidden></div></div>
  <details class="g-tabela"><summary>Ver os números</summary><div></div></details>
  <p class="fonte"></p>
</figure>
<p class="ir">Mais sobre turismo, concelho a concelho:
<a href="/dados/ine/#ind=0013210">dormidas por 100 habitantes (INE) →</a></p>

<h2 id="ilhas">5. O que cada ilha produz</h2>
{% if s.pib_hab %}
<p>O produto interno bruto (PIB) é o valor de tudo o que se produz num ano.
Dividido pelos residentes, dá o <strong>PIB por habitante</strong>: nos
Açores, {{ s.pib_hab.acores_t }} € em {{ s.pib_hab.ano }}{% if s.pib_hab.provisorio %}
(valores provisórios){% endif %}. Não é o que cada pessoa ganha: inclui os
lucros das empresas e o que se produz para fora, e uma ilha com um
aeroporto ou um porto grande produz muito por habitante.
<a href="/dados/ine/#ind=0012757&nivel=Concelho">O rendimento das famílias, concelho a concelho →</a></p>
<figure class="barras">
  <figcaption>PIB por habitante, por ilha, {{ s.pib_hab.ano }} (€)</figcaption>
  {%- for i in s.pib_hab.por_ilha %}
  <div class="barra"><span>{{ i.ilha }}</span>
    <span class="trilho"><span class="valor" style="width: {{ i.pct }}%"></span></span>
    <span class="num">{{ i.valor_t }} €</span></div>
  {%- endfor %}
</figure>
<p class="fonte">Fonte: <a href="{{ s.pib_hab.url }}">SREA, PIB por ilha</a>,
dividido pela <a href="{{ f.srea_populacao.url }}">população residente estimada pelo SREA</a>
no mesmo ano (conta do açores.net).</p>
{% endif %}

<h2 id="palavras">6. Palavras e dados</h2>
<p class="fonte">Explicações do açores.net, não são texto oficial. As
definições oficiais estão na <a href="{{ f.srea_meta.url }}">metainformação
do SREA</a> e nas fichas de cada ficheiro.</p>
<dl class="palavras">
  <dt>Variação homóloga</dt>
  <dd>A comparação com o mesmo mês (ou trimestre) do ano anterior. Evita
  confundir subidas reais com as do calendário: o turismo sobe sempre no
  verão, os preços da roupa descem sempre nos saldos.</dd>
  <dt>Inflação e IPC</dt>
  <dd>O índice de preços no consumidor segue os preços de um cabaz do que as
  famílias compram (comida, casa, transportes…). A inflação é quanto esse
  cabaz ficou mais caro.</dd>
  <dt>Taxa de desemprego</dt>
  <dd>Desempregados em cada 100 pessoas ativas. Ativos são os que trabalham
  e os que procuram trabalho e estão disponíveis; reformados e estudantes
  não contam.</dd>
  <dt>Indicadores coincidentes (IAE e ICP)</dt>
  <dd>Juntam dados que saem todos os meses para mostrar, cerca de 45 dias
  depois, para onde vai a economia, sem esperar pelas contas anuais. O ICP é,
  nas palavras do SREA, “uma média móvel ponderada e centrada de 7 meses das
  taxas de variação homóloga do indicador do consumo, calculado em volume”:
  alisa os altos e baixos de cada mês.</dd>
  <dt>Dormidas</dt>
  <dd>Cada noite passada por cada hóspede: um casal que fica três noites
  conta seis dormidas.</dd>
  <dt>PIB</dt>
  <dd>O valor de tudo o que se produz num ano, descontado o que foi gasto
  para o produzir.</dd>
</dl>

<p><strong>Descarregar:</strong> todas as séries num só ficheiro,
<a href="/dados/srea.csv">srea.csv</a> (um valor por linha, com a ligação
para o ficheiro do SREA de onde veio). As séries vêm das páginas do SREA de
<a href="{{ f.srea_precos.url }}">preços</a>,
<a href="{{ f.srea_conjuntura.url }}">conjuntura</a>,
<a href="{{ f.srea_emprego.url }}">mercado de trabalho</a>,
<a href="{{ f.srea_turismo.url }}">turismo</a>,
<a href="{{ f.srea_contas.url }}">contas regionais</a> e
<a href="{{ f.srea_populacao.url }}">população</a>, recolhidas todas as
semanas.</p>

<style>
.lead { font-size: 1.15em; max-width: 40em; }
.indice { display: grid; grid-template-columns: repeat(auto-fit, minmax(min(12em, 100%), 1fr)); gap: .4em; margin: 1em 0 1.5em; }
.indice a { display: block; padding: .45em .7em; border: 1px solid rgba(147,161,161,.6); border-radius: 6px; background: rgba(147,161,161,.08); text-decoration: none; }
.indice a:hover { background: rgba(38,139,210,.12); }
.indice span { display: inline-block; min-width: 1.4em; font-weight: bold; color: #268bd2; }
h2[id] { scroll-margin-top: 1em; margin-top: 1.4em; }
p.grande { font-size: 1.9em; font-weight: bold; line-height: 1.15; margin-bottom: .3em; }
.grande small { font-size: .5em; font-weight: normal; }
.aviso { border-left: 4px solid #b58900; padding: .2em 0 .2em .8em; font-size: .95em; max-width: 42em; }
.duas { display: grid; grid-template-columns: repeat(auto-fit, minmax(min(18em, 100%), 1fr)); gap: 0 2em; }
.cartoes { display: grid; grid-template-columns: repeat(auto-fit, minmax(min(16em, 100%), 1fr)); gap: .9em; margin: 1em 0 1.2em; }
.cartao { border: 1px solid rgba(147,161,161,.6); border-radius: 8px; padding: .8em 1em .3em; background: rgba(147,161,161,.08); }
.cartao h3 { font-size: 1.05em; margin: 0 0 .4em; }
.cartao p { font-size: .95em; margin-bottom: .5em; }
.cartao .grande { font-size: 1.7em; font-weight: bold; line-height: 1.15; margin-bottom: .3em; }
.fonte { font-size: .85em; color: #586e75; }
.ir { font-size: .95em; }
.barras { margin: 1em 0 .6em; max-width: 42em; }
.barras figcaption, .grafico figcaption { font-weight: bold; margin-bottom: .5em; }
.barra { display: grid; grid-template-columns: minmax(7em, 10em) 1fr auto; align-items: center; gap: .6em; margin: .3em 0; font-size: .95em; }
.barra .trilho { height: .8em; background: rgba(147,161,161,.15); border-radius: 4px; overflow: hidden; }
.barra .valor { display: block; height: 100%; background: #268bd2; border-radius: 0 4px 4px 0; min-width: 2px; }
.barra .num { font-variant-numeric: tabular-nums; text-align: right; white-space: nowrap; min-width: 9em; }
.barra .num small { color: #586e75; margin-left: .4em; display: inline-block; min-width: 3.2em; }
.grafico { margin: 1em 0 1.4em; max-width: 46em; }
.g-topo { display: flex; flex-wrap: wrap; gap: .5em 1em; align-items: center; margin-bottom: .4em; }
.g-legenda { display: flex; flex-wrap: wrap; gap: .3em .9em; font-size: .85em; color: #586e75; flex: 1 1 12em; }
.g-legenda span { display: inline-flex; align-items: center; gap: .35em; }
.g-legenda i, .g-tip i { display: inline-block; width: 14px; border-top: 2px solid var(--c); border-radius: 2px; }
.g-escolha { font-size: .9em; }
.g-escolha select { font: inherit; padding: .15em .3em; max-width: 14em; }
.g-vista { display: inline-flex; border: 1px solid #93a1a1; border-radius: 6px; overflow: hidden; }
.g-vista:empty { display: none; }
.g-vista button { font: inherit; font-size: .85em; padding: .25em .7em; border: 0; background: transparent; color: #586e75; cursor: pointer; }
.g-vista button + button { border-left: 1px solid #93a1a1; }
.g-vista button[aria-pressed="true"] { background: #586e75; color: #fdf6e3; }
.g-area { position: relative; }
.grafico svg { display: block; width: 100%; overflow: visible; touch-action: pan-y; }
.grafico svg:focus-visible, .g-vista button:focus-visible { outline: 3px solid #268bd2; outline-offset: 1px; }
.grafico svg text { font-size: 12px; fill: #586e75; font-variant-numeric: tabular-nums; }
.grafico svg .grade { stroke: #eee8d5; stroke-width: 1; }
.grafico svg .eixo { stroke: #93a1a1; stroke-width: 1; }
.grafico svg .cruz { stroke: #93a1a1; stroke-width: 1; }
.grafico svg .rotulo { fill: #073642; }
.g-tip { position: absolute; pointer-events: none; background: #fffdf5; border: 1px solid #93a1a1; border-radius: 6px; padding: .4em .6em; font-size: .85em; box-shadow: 0 2px 6px rgba(0,0,0,.12); min-width: 9em; z-index: 3; }
.g-tip .p { color: #586e75; margin-bottom: .2em; }
.g-tip div.l { display: flex; align-items: center; gap: .4em; white-space: nowrap; }
.g-tip b { font-variant-numeric: tabular-nums; color: #073642; }
.g-tip span { color: #586e75; }
.g-tabela { margin-top: .4em; font-size: .9em; }
.g-tabela summary { cursor: pointer; color: #586e75; }
.g-tabela div { max-height: 22em; overflow: auto; }
.g-tabela table { border-collapse: collapse; font-variant-numeric: tabular-nums; }
.g-tabela th, .g-tabela td { padding: .15em .6em; text-align: right; border-bottom: 1px solid rgba(147,161,161,.3); }
.g-tabela th:first-child, .g-tabela td:first-child { text-align: left; }
.palavras dt { font-weight: bold; margin-top: .7em; }
.palavras dd { margin: .15em 0 0 0; max-width: 42em; }
[hidden] { display: none !important; }
@media (max-width: 30em) { .barra { grid-template-columns: 1fr auto; } .barra .trilho { grid-column: 1 / -1; grid-row: 2; } }
@media (prefers-color-scheme: dark) {
  .fonte, .barra .num small, .g-legenda, .g-tabela summary { color: #93a1a1; }
  .grafico svg text { fill: #93a1a1; }
  .grafico svg .rotulo { fill: #eee8d5; }
  .grafico svg .grade { stroke: rgba(147,161,161,.22); }
  .g-tip { background: #073642; }
  .g-tip b { color: #eee8d5; }
  .g-tip .p, .g-tip span { color: #93a1a1; }
}
</style>

<script>
(function () {
  "use strict";
  var BUILD = "{{ site.time | date: '%s' }}";
  // Categorical colours in fixed order, the same as the INE and BEO pages.
  var C1 = "#257de0", C2 = "#f47230";
  var SVGNS = "http://www.w3.org/2000/svg";
  var MESES = ["jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez"];
  var MESES_L = ["janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho", "agosto", "setembro", "outubro", "novembro", "dezembro"];
  var n1 = new Intl.NumberFormat("pt-PT", { maximumFractionDigits: 1, useGrouping: "always" });
  var n2 = new Intl.NumberFormat("pt-PT", { maximumFractionDigits: 2, useGrouping: "always" });
  var DATA = [];

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
    var span = hi - lo || Math.abs(hi) || 1, step = Math.pow(10, Math.floor(Math.log10(span / n))), err = span / n / step;
    step *= err >= 7.5 ? 10 : err >= 3.5 ? 5 : err >= 1.5 ? 2 : 1;
    var t = [], v = Math.floor(lo / step) * step;
    for (; v <= hi + step * 1e-9; v += step) t.push(+v.toFixed(10));
    if (t[t.length - 1] < hi) t.push(t[t.length - 1] + step);
    return t;
  }
  function find(q) {
    return DATA.filter(function (s) {
      return Object.keys(q).every(function (k) { return s[k] === q[k]; });
    });
  }
  function one(q) { return find(q)[0]; }
  function asMap(s) { var m = {}; (s ? s.p : []).forEach(function (p) { m[p[0]] = p[1]; }); return m; }
  function perLabel(k) {
    if (/^\d{4}-T\d$/.test(k)) return k.slice(6) + ".º trim. " + k.slice(0, 4);
    if (/^\d{4}-\d{2}$/.test(k)) return MESES_L[+k.slice(5) - 1] + " de " + k.slice(0, 4);
    return k;
  }
  function axisLabel(k, span) {
    if (/^\d{4}-T\d$/.test(k)) return k.slice(6) + "T " + k.slice(2, 4);
    if (/^\d{4}-\d{2}$/.test(k)) return span > 30 ? k.slice(0, 4) : MESES[+k.slice(5) - 1] + " " + k.slice(2, 4);
    return k;
  }
  function source(fig, list) {
    var p = fig.querySelector(".fonte"); p.replaceChildren();
    p.appendChild(document.createTextNode("Fonte: "));
    var seen = {};
    list.filter(Boolean).forEach(function (s, i) {
      if (seen[s.ficheiro]) return; seen[s.ficheiro] = 1;
      if (Object.keys(seen).length > 1) p.appendChild(document.createTextNode(" · "));
      var a = h("a", "SREA, " + decodeURIComponent(s.ficheiro.split("/").pop()), p); a.href = s.ficheiro;
    });
    var pg = list.filter(Boolean)[0];
    if (pg) { p.appendChild(document.createTextNode(" (")); var b = h("a", "página do SREA", p); b.href = pg.pagina; p.appendChild(document.createTextNode(")")); }
  }

  // A line chart: keys = x categories in order; series = [{nome, c, v: {key: value}}].
  function draw(fig, keys, series, opt) {
    opt = opt || {};
    var svg = fig.querySelector("svg"), tip = fig.querySelector(".g-tip"), area = fig.querySelector(".g-area");
    svg.replaceChildren();
    var leg = fig.querySelector(".g-legenda"); leg.replaceChildren();
    if (series.length > 1) series.forEach(function (s) {
      var it = h("span", null, leg), i = h("i", null, it); i.style.setProperty("--c", s.c);
      it.appendChild(document.createTextNode(s.nome));
    });
    var W = area.clientWidth || 600, narrow = W < 520, H = narrow ? 220 : 280;
    var direct = series.length > 1 && series.length <= 4 && !narrow;
    var m = { l: 8, r: direct ? 120 : 14, t: 10, b: 26 };
    var vals = [];
    series.forEach(function (s) { keys.forEach(function (k) { if (s.v[k] != null) vals.push(s.v[k]); }); });
    svg.setAttribute("viewBox", "0 0 " + W + " " + H); svg.setAttribute("height", H);
    svg.setAttribute("aria-label", fig.querySelector("figcaption").textContent);
    if (!vals.length) { var t0 = el("text", { x: W / 2, y: H / 2, "text-anchor": "middle" }, svg); t0.textContent = "Sem dados."; return; }
    var lo = Math.min.apply(null, vals), hi = Math.max.apply(null, vals);
    if (opt.zero && lo > 0) lo = 0;
    if (lo === hi) { lo -= 1; hi += 1; }
    var ticks = niceTicks(lo, hi, narrow ? 4 : 5); lo = ticks[0]; hi = ticks[ticks.length - 1];
    var fmt = opt.big ? function (v) { return Math.abs(hi) >= 1e6 ? n1.format(v / 1e6) + " M" : Math.abs(hi) >= 1e4 ? n1.format(v / 1e3) + " mil" : n1.format(v); } : n1.format;
    var probe = el("text", {}, svg), wmax = 0;
    ticks.forEach(function (v) { probe.textContent = fmt(v); wmax = Math.max(wmax, probe.getComputedTextLength()); });
    svg.removeChild(probe); m.l = Math.ceil(wmax) + 10;
    var iw = W - m.l - m.r, ih = H - m.t - m.b;
    var X = function (i) { return m.l + (keys.length === 1 ? iw / 2 : i * iw / (keys.length - 1)); };
    var Y = function (v) { return m.t + ih - (v - lo) / (hi - lo) * ih; };
    ticks.forEach(function (v) {
      el("line", { x1: m.l, x2: m.l + iw, y1: Y(v), y2: Y(v), "class": v === 0 ? "eixo" : "grade" }, svg);
      var tx = el("text", { x: m.l - 6, y: Y(v) + 4, "text-anchor": "end" }, svg); tx.textContent = fmt(v);
    });
    var span = keys.length, lab = opt.lab || function (k) { return axisLabel(k, span); };
    var every = Math.max(1, Math.ceil(keys.length / Math.max(2, Math.floor(iw / (narrow ? 52 : 64)))));
    if (span > 30 && /^\d{4}-\d{2}$/.test(keys[0])) {
      // monthly over years: one label per year (every few years if crowded)
      var years = keys.filter(function (k) { return k.slice(5) === "01"; });
      var ystep = Math.max(1, Math.ceil(years.length / Math.max(2, Math.floor(iw / 46))));
      years.forEach(function (k, j) {
        if ((years.length - 1 - j) % ystep) return;
        var tx = el("text", { x: X(keys.indexOf(k)), y: H - 6, "text-anchor": "middle" }, svg); tx.textContent = k.slice(0, 4);
      });
    } else keys.forEach(function (k, i) {
      if ((keys.length - 1 - i) % every) return;
      var tx = el("text", { x: X(i), y: H - 6, "text-anchor": "middle" }, svg); tx.textContent = lab(k);
    });
    var ends = [];
    series.forEach(function (s) {
      var d = "", prev = false, last = -1;
      keys.forEach(function (k, i) {
        var v = s.v[k];
        if (v != null) { d += (prev ? "L" : "M") + X(i).toFixed(1) + " " + Y(v).toFixed(1); last = i; }
        if (v != null && (opt.dots || (!prev && s.v[keys[i + 1]] == null))) el("circle", { cx: X(i), cy: Y(v), r: opt.dots ? 3.5 : 3, fill: s.c }, svg);
        prev = v != null;
      });
      if (d) el("path", { d: d, fill: "none", stroke: s.c, "stroke-width": 2, "stroke-linejoin": "round", "stroke-linecap": "round" }, svg);
      if (last >= 0) ends.push({ s: s, i: last, y: Y(s.v[keys[last]]) });
    });
    ends.forEach(function (e) { el("circle", { cx: X(e.i), cy: e.y, r: 4, fill: e.s.c, stroke: "#fdf6e3", "stroke-width": 2 }, svg); });
    if (direct) {
      ends.sort(function (a, b) { return a.y - b.y; });
      var ly = ends.map(function (e) { return e.y; });
      for (var j = 1; j < ly.length; j++) if (ly[j] - ly[j - 1] < 15) ly[j] = ly[j - 1] + 15;
      ends.forEach(function (e, j) {
        var tx = el("text", { x: m.l + iw + 10, y: ly[j] + 4, "class": "rotulo" }, svg); tx.textContent = e.s.nome;
      });
    }
    var g = el("g", {}, svg), cross = el("line", { y1: m.t, y2: m.t + ih, "class": "cruz", visibility: "hidden" }, g), dots = [];
    var unit = opt.unit || "";
    function show(i) {
      i = Math.max(0, Math.min(keys.length - 1, i));
      var k = keys[i], x = X(i);
      cross.setAttribute("x1", x); cross.setAttribute("x2", x); cross.setAttribute("visibility", "visible");
      dots.forEach(function (d) { d.remove(); }); dots = [];
      tip.replaceChildren(); h("div", (opt.tipLab || perLabel)(k), tip).className = "p";
      series.forEach(function (s) {
        var v = s.v[k];
        if (v != null) dots.push(el("circle", { cx: x, cy: Y(v), r: 4.5, fill: s.c, stroke: "#fdf6e3", "stroke-width": 2 }, g));
        var row = h("div", null, tip); row.className = "l";
        var key = h("i", null, row); key.style.setProperty("--c", s.c);
        h("b", v == null ? "–" : (opt.big ? n1.format(v) : n2.format(v)) + unit, row);
        if (series.length > 1) h("span", s.nome, row);
        var nt = s.nota && s.nota[k]; if (nt) h("span", "(" + nt + ")", row);
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
    // the same numbers as a table, newest first
    var box = fig.querySelector(".g-tabela div"); box.replaceChildren();
    var tb = h("table", null, box), tr = h("tr", null, h("thead", null, tb));
    h("th", "Período", tr); series.forEach(function (s) { h("th", s.nome + (unit ? " (" + unit.trim() + ")" : ""), tr); });
    var body = h("tbody", null, tb);
    keys.slice().reverse().forEach(function (k) {
      var r = h("tr", null, body); h("td", (opt.tipLab || perLabel)(k), r);
      series.forEach(function (s) { var v = s.v[k]; h("td", v == null ? "–" : (opt.big ? n1.format(v) : n2.format(v)), r); });
    });
  }

  function rangeButtons(fig, choices, def, redraw) {
    var box = fig.querySelector(".g-vista"); if (!box) return def;
    box.replaceChildren();
    choices.forEach(function (c) {
      var b = h("button", c[1], box); b.type = "button"; b.setAttribute("aria-pressed", c[0] === def);
      b.addEventListener("click", function () {
        box.querySelectorAll("button").forEach(function (x) { x.setAttribute("aria-pressed", x === b); });
        redraw(c[0]);
      });
    });
    return def;
  }
  function lastYears(keys, n) {
    if (!n || !keys.length) return keys;
    var from = (+keys[keys.length - 1].slice(0, 4) - n + 1) + "-01";
    return keys.filter(function (k) { return k >= from; });
  }
  function ipc() {
    var fig = document.querySelector('[data-g="ipc"]'), s = one({ serie: "ipc", indicador: "Variação homóloga", rubrica: "Total" });
    if (!s) return;
    var all = s.p.map(function (p) { return p[0]; }), v = asMap(s);
    var cur = 10, redraw = function (n) { if (n != null) cur = n; draw(fig, lastYears(all, cur), [{ nome: "Inflação", c: C1, v: v }], { unit: "%" }); };
    redraw(rangeButtons(fig, [[5, "5 anos"], [10, "10 anos"], [0, "Desde 1992"]], 10, redraw));
    source(fig, [s]);
    return function () { redraw(); };
  }
  function desemprego() {
    var fig = document.querySelector('[data-g="desemprego"]'), s = one({ serie: "desemprego", rubrica: "Total" });
    if (!s) return;
    var nota = {}; s.p.forEach(function (p) { if (p[2]) nota[p[0]] = p[2]; });
    var redraw = function () { draw(fig, s.p.map(function (p) { return p[0]; }), [{ nome: "Taxa de desemprego", c: C1, v: asMap(s), nota: nota }], { unit: "%", dots: true }); };
    redraw(); source(fig, [s]);
    return redraw;
  }
  function atividade() {
    var fig = document.querySelector('[data-g="atividade"]');
    var a = one({ serie: "iae" }), b = one({ serie: "icp" });
    if (!a && !b) return;
    var keys = {}; [a, b].forEach(function (s) { if (s) s.p.forEach(function (p) { keys[p[0]] = 1; }); });
    var all = Object.keys(keys).sort();
    var series = [];
    if (a) series.push({ nome: "Atividade económica", c: C1, v: asMap(a) });
    if (b) series.push({ nome: "Consumo das famílias", c: C2, v: asMap(b) });
    var cur = 10, redraw = function (n) { if (n != null) cur = n; draw(fig, lastYears(all, cur), series, { unit: "%" }); };
    redraw(rangeButtons(fig, [[5, "5 anos"], [10, "10 anos"], [0, "Desde 1996"]], 10, redraw));
    source(fig, [a, b]);
    return function () { redraw(); };
  }
  function turismo() {
    var fig = document.querySelector('[data-g="turismo"]');
    var rows = find({ serie: "dormidas" });
    if (!rows.length) return;
    var selI = fig.querySelector(".g-ilha"), selT = fig.querySelector(".g-tipo");
    var ilhas = ["Açores"].concat(rows.map(function (s) { return s.local; }).filter(function (x, i, a) { return x !== "Açores" && a.indexOf(x) === i; }).sort(function (x, y) { return x.localeCompare(y, "pt"); }));
    ilhas.forEach(function (i) { var o = h("option", i === "Açores" ? "Todas (Açores)" : i, selI); o.value = i; });
    var redraw = function () {
      var tipo = selT.value, local = selI.value, tot = {};
      rows.forEach(function (s) {
        if (s.local !== local || (tipo && s.rubrica !== tipo)) return;
        s.p.forEach(function (p) { tot[p[0]] = (tot[p[0]] || 0) + p[1]; });
      });
      // a month counts only when every kind chosen has published it
      var kinds = tipo ? 1 : 2, cnt = {};
      rows.forEach(function (s) { if (s.local === local && (!tipo || s.rubrica === tipo)) s.p.forEach(function (p) { cnt[p[0]] = (cnt[p[0]] || 0) + 1; }); });
      var years = Object.keys(tot).map(function (k) { return k.slice(0, 4); }).filter(function (x, i, a) { return a.indexOf(x) === i; }).sort().slice(-2);
      var series = years.map(function (y, j) {
        var v = {}; MESES.forEach(function (m, i) { var k = y + "-" + (i < 9 ? "0" : "") + (i + 1); if (cnt[k] === kinds) v[m] = tot[k]; });
        return { nome: y, c: j === years.length - 1 ? C1 : C2, v: v };
      });
      draw(fig, MESES, series, { big: true, zero: true, lab: function (k) { return k; }, tipLab: function (k) { return MESES_L[MESES.indexOf(k)]; } });
    };
    selI.onchange = selT.onchange = redraw;
    redraw(); source(fig, rows.filter(function (s) { return s.local === "Açores"; }));
    return redraw;
  }

  fetch("/dados/srea.json?v=" + BUILD).then(function (r) { return r.json(); }).then(function (d) {
    DATA = d;
    var redraws = [ipc(), desemprego(), atividade(), turismo()].filter(Boolean);
    var w = 0;
    window.addEventListener("resize", function () {
      clearTimeout(w); w = setTimeout(function () { redraws.forEach(function (f) { f(); }); }, 200);
    });
  }).catch(function () {
    document.querySelectorAll(".grafico .fonte").forEach(function (p) { p.textContent = "Não foi possível carregar os dados. Estão em srea.csv."; });
  });
})();
</script>
