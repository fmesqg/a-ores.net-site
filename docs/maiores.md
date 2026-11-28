---
title: Maiores empresas dos Açores
layout: default
permalink: /dados/maiores-empresas/
secao: economia
description: As 200 maiores empresas com sede nos Açores, por volume de negócios - setor, ilha, trabalhadores, resultados - com as empresas públicas regionais assinaladas. Fonte - 100 Maiores Empresas dos Açores (Açoriano Oriental).
---
{%- assign m = site.data.maiores -%}
{% include economia-nav.html %}

# Maiores empresas dos Açores

<p class="fonte-topo">Fonte: revista <a href="{{ m.url }}"><cite>100 Maiores
Empresas dos Açores {{ m.ano }}</cite></a> (Açoriano Oriental / Açormedia,
com dados da Informa D&B), publicada em dezembro de {{ m.ano | plus: 1 }}.
Todos os números desta página são da revista, exceto a marcação das
empresas públicas.</p>

<p class="lead">As {{ m.n }} empresas com sede nos Açores que mais
faturaram em {{ m.ano }}. Juntas, venderam {{ m.vn_t }} milhões de euros e empregavam
{{ m.trabalhadores_t }} pessoas.</p>

{% if m.n %}
<div class="numeros">
<div class="numero">
  <p class="rotulo">As 10 maiores</p>
  <p class="grande">{{ m.top10_pct }} %</p>
  <p>do volume de negócios das {{ m.n }}.</p>
</div>
<div class="numero">
  <p class="rotulo">Sede em São Miguel</p>
  {%- assign sm = m.ilhas | where: "nome", "São Miguel" | first %}
  <p class="grande">{{ sm.n }} <small>de {{ m.n }}</small></p>
  <p>{{ sm.pct }} % do volume de negócios.</p>
</div>
<div class="numero">
  <p class="rotulo">Empresas públicas regionais</p>
  <p class="grande">{{ m.publicas }}</p>
  <p>{{ m.publicas_pct }} % do volume de negócios.
  <a href="/dados/sper/">Ver todas →</a></p>
</div>
<div class="numero">
  <p class="rotulo">Com prejuízo</p>
  <p class="grande">{{ m.prejuizo }}</p>
  <p>empresas com resultado líquido negativo em {{ m.ano }}.</p>
</div>
</div>

<div class="duas">
<div>
<h2 id="setores">Por setor</h2>
<table class="sper">
  <thead><tr><th scope="col">Setor</th><th scope="col" class="n">Empresas</th><th scope="col" class="n">M€</th><th scope="col" class="n">%</th></tr></thead>
  <tbody>{% for g in m.setores %}<tr><th scope="row">{{ g.nome }}</th><td class="n">{{ g.n }}</td><td class="n">{{ g.vn_t }}</td><td class="n">{{ g.pct }}</td></tr>{% endfor %}</tbody>
</table>
</div>
<div>
<h2 id="ilhas">Por ilha da sede</h2>
<table class="sper">
  <thead><tr><th scope="col">Ilha</th><th scope="col" class="n">Empresas</th><th scope="col" class="n">M€</th><th scope="col" class="n">%</th></tr></thead>
  <tbody>{% for g in m.ilhas %}<tr><th scope="row">{{ g.nome }}</th><td class="n">{{ g.n }}</td><td class="n">{{ g.vn_t }}</td><td class="n">{{ g.pct }}</td></tr>{% endfor %}</tbody>
</table>
<p class="nota">A ilha é a da sede. Uma empresa com sede em São Miguel pode
trabalhar em várias ilhas.</p>
</div>
</div>

<h2 id="lista">As {{ m.n }}</h2>
<form class="filtro" onsubmit="return false" hidden>
  <label>Procurar <input type="search" id="busca" placeholder="nome, setor ou ilha" autocomplete="off"></label>
  <label><input type="checkbox" id="so-publicas"> Só empresas públicas regionais</label>
  <span id="contagem" class="nota" aria-live="polite"></span>
</form>
<p class="nota">Volume de negócios e resultado líquido em milhões de euros.
Clique num cabeçalho para ordenar.</p>
<div class="tabela-scroll">
<table class="sper" id="lista-tabela">
  <thead><tr>
    <th scope="col" class="n" data-tipo="n">#</th>
    <th scope="col">Empresa</th>
    <th scope="col" class="n" data-tipo="n">Trabalhadores</th>
    <th scope="col" class="n" data-tipo="n">Volume de negócios</th>
    <th scope="col" class="n" data-tipo="n">Variação</th>
    <th scope="col" class="n" data-tipo="n">Resultado líquido</th>
  </tr></thead>
  <tbody>
  {%- for e in m.empresas %}
  <tr{% if e.publica != "" %} data-publica="1"{% endif %}>
    <td class="n" data-v="{{ e.posicao }}">{{ e.posicao }}</td>
    <td>{{ e.empresa }}{% if e.publica != "" %} <a class="tag" href="/dados/sper/" title="Empresa pública regional">pública</a>{% endif %}<br><small>{{ e.ilha }} · {{ e.setor }}</small></td>
    <td class="n" data-v="{{ e.trabalhadores }}">{{ e.trabalhadores_t }}</td>
    <td class="n" data-v="{{ e.vn }}">{{ e.vn_t }}</td>
    <td class="n" data-v="{{ e.cresc_vn | default: '' }}">{% if e.cresc_vn_t %}{{ e.cresc_vn_t | replace: "-", "−" }} %{% endif %}</td>
    <td class="n{% if e.rl < 0 %} neg{% endif %}" data-v="{{ e.rl }}">{{ e.rl_t | replace: "-", "−" }}</td>
  </tr>
  {%- endfor %}
  </tbody>
</table>
</div>
{% endif %}

<h2 id="fontes">Fonte e notas</h2>
<ul>
  <li>{{ m.fonte }} <a href="{{ m.url }}">Notícia do lançamento</a>.
  Volume de negócios é o total dos proveitos correntes de {{ m.ano }}; o
  ranking inclui só empresas com sede nos Açores. Os valores são os que as
  empresas prestaram, sem ajustamentos (metodologia da revista).</li>
  <li>A revista foi publicada em dezembro de {{ m.ano | plus: 1 }}. Os
  números foram passados do PDF para esta tabela pelo açores.net e
  verificados pela coerência interna (ativo = capital próprio + passivo,
  crescimento e rentabilidades recalculados).</li>
  <li>Empresas públicas regionais: as do <a href="/dados/sper/">setor
  público empresarial regional</a>, segundo o Conselho das Finanças
  Públicas. Os hospitais não entram no ranking.</li>
  <li>Dados abertos: <a href="/dados/maiores.csv">maiores.csv</a>, com
  todas as colunas da tabela da revista <cite>100 Maiores Empresas dos
  Açores {{ m.ano }}</cite> (VAB, ativo, capital próprio, passivo,
  rentabilidades, em milhares de euros); cada linha cita a revista na coluna
  <code>fonte</code>.</li>
</ul>

<style>
.lead { font-size: 1.15em; max-width: 40em; }
.numeros { display: grid; grid-template-columns: repeat(auto-fit, minmax(min(9.5em, 100%), 1fr)); gap: .9em; margin: 1.2em 0 1.5em; }
.duas { display: grid; grid-template-columns: repeat(auto-fit, minmax(min(20em, 100%), 1fr)); gap: 1.5em; }
table.sper th[scope="row"] { font-weight: normal; }
table.sper thead th, table.sper thead th.n, table.sper .n small { white-space: normal; }
table.sper .neg { color: #b5442c; }
#lista-tabela thead th { cursor: pointer; }
#lista-tabela td small { color: var(--s0); }
#lista-tabela thead th[aria-sort]::after { content: " ↓"; }
#lista-tabela thead th[aria-sort="ascending"]::after { content: " ↑"; }
.tag { font-size: .75em; border: 1px solid var(--s1); border-radius: 4px; padding: 0 .3em; text-decoration: none; white-space: nowrap; }
.fonte-topo { font-size: .9em; border-left: 4px solid #268bd2; padding: .3em .8em; background: rgba(38,139,210,.08); }
.filtro { display: flex; flex-wrap: wrap; gap: .5em 1.2em; align-items: center; margin-bottom: .5em; }
.nota { font-size: .85em; color: var(--s01); }
@media (prefers-color-scheme: dark) { .nota { color: var(--s01); } table.sper .neg { color: #e0805f; } }
</style>

<script>
(function () {
  var tabela = document.getElementById("lista-tabela");
  if (!tabela) return;
  var form = document.querySelector(".filtro");
  var busca = document.getElementById("busca");
  var publicas = document.getElementById("so-publicas");
  var contagem = document.getElementById("contagem");
  var corpo = tabela.tBodies[0];
  var linhas = Array.prototype.slice.call(corpo.rows);
  form.hidden = false;
  function norm(s) { return s.normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase(); }
  linhas.forEach(function (tr) { tr._texto = norm(tr.textContent); });
  function filtrar() {
    var q = norm(busca.value.trim()), n = 0;
    linhas.forEach(function (tr) {
      var ok = (!q || tr._texto.indexOf(q) !== -1) && (!publicas.checked || tr.dataset.publica);
      tr.hidden = !ok;
      if (ok) n++;
    });
    contagem.textContent = n === linhas.length ? "" : n + " de " + linhas.length;
  }
  busca.addEventListener("input", filtrar);
  publicas.addEventListener("change", filtrar);
  var ths = tabela.tHead.rows[0].cells;
  Array.prototype.forEach.call(ths, function (th, i) {
    th.tabIndex = 0;
    function ordenar() {
      var asc = th.getAttribute("aria-sort") === "descending";
      Array.prototype.forEach.call(ths, function (o) { o.removeAttribute("aria-sort"); });
      th.setAttribute("aria-sort", asc ? "ascending" : "descending");
      var num = th.dataset.tipo === "n";
      linhas.sort(function (a, b) {
        var x = a.cells[i], y = b.cells[i], r;
        if (num) {
          var vx = parseFloat(x.dataset.v), vy = parseFloat(y.dataset.v);
          if (isNaN(vx)) vx = -Infinity;
          if (isNaN(vy)) vy = -Infinity;
          r = vx - vy;
        } else {
          r = x.textContent.localeCompare(y.textContent, "pt");
        }
        return asc ? r : -r;
      });
      linhas.forEach(function (tr) { corpo.appendChild(tr); });
    }
    th.addEventListener("click", ordenar);
    th.addEventListener("keydown", function (e) { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); ordenar(); } });
  });
})();
</script>
