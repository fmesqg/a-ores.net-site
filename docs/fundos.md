---
title: Fundos europeus nos Açores
nav_title: Fundos europeus
layout: default
permalink: /financas/fundos-europeus/
secao: financas
description: Quanto dinheiro europeu chega aos Açores - o PRR por concelho, componente e beneficiário, os pagamentos da PAC e do POSEI por medida, concelho e beneficiário, e os fundos de coesão segundo o Kohesio (em construção), com ligação às fontes.
---
{%- assign f = site.data.fundos -%}
{%- assign prr = f.prr -%}
{%- assign k = f.kohesio -%}
{%- assign pac = f.pac -%}
{% include financas-nav.html %}

# Fundos europeus nos Açores

<p class="lead">O dinheiro europeu que chega aos Açores, projeto a projeto.
Há três fontes: o <strong>PRR</strong>, com os dados abertos da Recuperar
Portugal; a <strong>PAC e o POSEI</strong>, com a lista anual de
beneficiários do IFAP; e os <strong>fundos de coesão</strong> (PO Açores
2020, Açores 2030 e programas nacionais), com o Kohesio, da Comissão
Europeia. A parte do Kohesio <strong>está em construção</strong>.</p>

{% if prr or k or pac %}
<div class="numeros">
{%- if prr %}
<div class="numero">
  <p class="rotulo">PRR aprovado nos Açores</p>
  <p class="grande">{{ prr.aprovado_t }} <small>M€</small></p>
  <p>{{ prr.projetos_t }} projetos e {{ prr.beneficiarios_t }} beneficiários finais.</p>
</div>
<div class="numero">
  <p class="rotulo">PRR pago</p>
  <p class="grande">{{ prr.pago_t }} <small>M€</small></p>
  <p>{{ prr.pct_pago }} % do aprovado. Dados de {{ prr.referencia }}.</p>
</div>
{%- endif %}
{%- if pac %}
<div class="numero">
  <p class="rotulo">PAC paga em {{ pac.ultimo }}</p>
  <p class="grande">{{ pac.total_t }} <small>M€</small></p>
  <p>{{ pac.posei_t }} M€ do POSEI, a {{ pac.beneficiarios_t }} beneficiários com morada nos Açores.</p>
</div>
{%- endif %}
{%- if k %}
<div class="numero construcao">
  <p class="rotulo">Fundos de coesão (UE) <span class="selo">em construção</span></p>
  <p class="grande">{{ k.apoio_ue_t }} <small>M€</small></p>
  <p>{{ k.projetos_t }} projetos desde 2014, sem {{ k.excluidos_t }} projetos de localização duvidosa
  ({{ k.excluidos_ue_t }} M€).</p>
</div>
{%- endif %}
</div>
<p class="fonte">Fontes: <a href="https://dados.gov.pt/datasets/dataset-estrutura-de-missao-prr-projetos-2">Recuperar Portugal (dados.gov.pt)</a>,
<a href="https://www.ifap.pt/portal/transparency">IFAP</a> e
<a href="https://kohesio.ec.europa.eu/">Kohesio</a>. Não se somam sem
cuidado: <a href="#notas">ver notas</a>.</p>

{% if prr %}
<h2 id="prr">PRR: Plano de Recuperação e Resiliência</h2>

<p>Valores dos projetos com uma parte nos Açores, na parte que cabe aos
Açores. Os projetos regionais (código terminado em <code>-RAA</code>) e os
nacionais com beneficiários açorianos entram todos.</p>

<h3 id="prr-concelhos">Por concelho</h3>
<p class="nota">Clique num cabeçalho para ordenar. Os projetos com mais de um
concelho estão em «Vários concelhos».</p>
<div class="tabela-scroll">
<table class="sper ordenavel barras">
<thead><tr>
  <th scope="col">Concelho</th>
  <th scope="col" class="n" data-tipo="n">Projetos</th>
  <th scope="col" class="n" data-tipo="n">Aprovado (M€)</th>
  <th class="barra-col" aria-hidden="true"></th>
  <th scope="col" class="n" data-tipo="n">Pago (M€)</th>
  <th scope="col" class="n" data-tipo="n">% pago</th>
</tr></thead>
<tbody>
{%- assign topo = prr.concelhos | first -%}
{%- for c in prr.concelhos %}
<tr><th scope="row">{{ c.nome }}</th><td class="n" data-v="{{ c.projetos }}">{{ c.projetos_t }}</td><td class="n" data-v="{{ c.aprovado }}">{{ c.aprovado_t }}</td><td class="barra-col" aria-hidden="true"><span class="barra" style="width: {{ c.aprovado | times: 100.0 | divided_by: topo.aprovado }}%"></span></td><td class="n" data-v="{{ c.pago }}">{{ c.pago_t }}</td><td class="n" data-v="{{ c.pct_pago }}">{{ c.pct_pago }} %</td></tr>
{%- endfor %}
</tbody>
</table>
</div>

<h3 id="prr-componentes">Por componente</h3>
<div class="tabela-scroll">
<table class="sper ordenavel barras">
<thead><tr>
  <th scope="col">Componente</th>
  <th scope="col" class="n" data-tipo="n">Projetos</th>
  <th scope="col" class="n" data-tipo="n">Aprovado (M€)</th>
  <th class="barra-col" aria-hidden="true"></th>
  <th scope="col" class="n" data-tipo="n">Pago (M€)</th>
  <th scope="col" class="n" data-tipo="n">% pago</th>
</tr></thead>
<tbody>
{%- assign topo = prr.componentes | first -%}
{%- for c in prr.componentes %}
<tr><th scope="row">{{ c.nome }}</th><td class="n" data-v="{{ c.projetos }}">{{ c.projetos_t }}</td><td class="n" data-v="{{ c.aprovado }}">{{ c.aprovado_t }}</td><td class="barra-col" aria-hidden="true"><span class="barra" style="width: {{ c.aprovado | times: 100.0 | divided_by: topo.aprovado }}%"></span></td><td class="n" data-v="{{ c.pago }}">{{ c.pago_t }}</td><td class="n" data-v="{{ c.pct_pago }}">{{ c.pct_pago }} %</td></tr>
{%- endfor %}
</tbody>
</table>
</div>

<h3 id="prr-beneficiarios">Os 25 maiores beneficiários finais</h3>
<p class="nota">Valor contratado nos projetos com parte nos Açores, na
proporção dessa parte. Com o NIF, cada um pode ser procurado nos contratos
públicos (colunas <code>adjudicante_nif</code> e <code>adjudicatario_nif</code>
da tabela <code>base</code>, em <a href="/dados/sql/">contratos.db</a>).</p>
<div class="tabela-scroll">
<table class="sper ordenavel">
<thead><tr>
  <th scope="col">Beneficiário</th>
  <th scope="col">NIF</th>
  <th scope="col" class="n" data-tipo="n">Projetos</th>
  <th scope="col" class="n" data-tipo="n">Contratado (M€)</th>
</tr></thead>
<tbody>
{%- for b in prr.maiores %}
<tr><th scope="row">{{ b.nome }}</th><td>{{ b.nif }}</td><td class="n" data-v="{{ b.projetos }}">{{ b.projetos_t }}</td><td class="n" data-v="{{ b.valor }}">{{ b.valor_t }}</td></tr>
{%- endfor %}
</tbody>
</table>
</div>
<p>A lista completa, projeto a projeto, está em
<a href="/dados/prr_projetos.csv">prr_projetos.csv</a> e
<a href="/dados/prr_entidades.csv">prr_entidades.csv</a>, e na base
<a href="/dados/sql/">fundos.db</a>.</p>
{% endif %}

{% if k %}
<h2 id="coesao">Fundos de coesão (Kohesio) <span class="selo">em construção</span></h2>

<div class="aviso">
<p><strong>Em construção.</strong> Estes números vêm do Kohesio, a base de
projetos da Comissão Europeia, e ainda não foram conferidos com a lista de
operações de cada programa. O que já se sabe:</p>
<ul>
  <li>O Kohesio localiza alguns projetos pelo nome do sítio e engana-se:
  põe nos Açores projetos do Porto (em Vila do Porto), da Maia (na Maia, em
  São Miguel) e da Calheta da Madeira (na Calheta de São Jorge). Esses
  projetos, os de programas de outras regiões e os do Interreg (que vêm pelo
  valor do projeto inteiro) estão fora dos totais: {{ k.excluidos_t }}
  projetos, {{ k.excluidos_ue_t }} M€. Ainda pode haver outros.</li>
  <li>Ainda não se lê o beneficiário de cada projeto. A lista de
  beneficiários abaixo é a do Kohesio para a região, e inclui os projetos
  mal localizados.</li>
  <li>O Kohesio não tem NIF, por isso não se pode cruzar com os contratos
  públicos a não ser pelo nome.</li>
</ul>
</div>

<h3 id="coesao-periodos">Por período de programação</h3>
<div class="tabela-scroll">
<table class="sper">
<thead><tr>
  <th scope="col">Período</th>
  <th scope="col" class="n">Projetos</th>
  <th scope="col" class="n">Apoio da UE (M€)</th>
</tr></thead>
<tbody>
{%- for x in k.periodos %}
<tr><th scope="row">{{ x.nome }}</th><td class="n">{{ x.projetos_t }}</td><td class="n">{{ x.apoio_ue_t }}</td></tr>
{%- endfor %}
</tbody>
</table>
</div>
<p class="nota">Os projetos de 2021-2027 são os já aprovados e carregados no
Kohesio; o período ainda está a meio.</p>

<h3 id="coesao-programas">Por programa</h3>
<p class="nota">Todos os projetos que o Kohesio situa nos Açores, incluindo
os que ficam fora dos totais (com nota).</p>
<div class="tabela-scroll">
<table class="sper ordenavel">
<thead><tr>
  <th scope="col">Programa</th>
  <th scope="col">Período</th>
  <th scope="col" class="n" data-tipo="n">Projetos</th>
  <th scope="col" class="n" data-tipo="n">Apoio da UE (M€)</th>
  <th scope="col">Nota</th>
</tr></thead>
<tbody>
{%- for x in k.programas %}
<tr{% if x.nota != "" %} class="fora"{% endif %}><th scope="row">{{ x.nome }}</th><td>{{ x.periodo }}</td><td class="n" data-v="{{ x.projetos }}">{{ x.projetos_t }}</td><td class="n" data-v="{{ x.apoio_ue }}">{{ x.apoio_ue_t }}</td><td>{{ x.nota }}</td></tr>
{%- endfor %}
</tbody>
</table>
</div>

<h3 id="coesao-beneficiarios">Os 25 maiores beneficiários, segundo o Kohesio</h3>
<p class="nota">Totais do Kohesio para a região, sem correção: incluem
projetos mal localizados e projetos nacionais pelo valor inteiro (é o caso
do IEFP e da Direção-Geral do Ensino Superior).</p>
<div class="tabela-scroll">
<table class="sper ordenavel">
<thead><tr>
  <th scope="col">Beneficiário</th>
  <th scope="col" class="n" data-tipo="n">Projetos</th>
  <th scope="col" class="n" data-tipo="n">Apoio da UE (M€)</th>
</tr></thead>
<tbody>
{%- for b in k.maiores %}
<tr><th scope="row"><a href="{{ b.ligacao }}">{{ b.nome }}</a></th><td class="n" data-v="{{ b.projetos }}">{{ b.projetos_t }}</td><td class="n" data-v="{{ b.apoio_ue }}">{{ b.apoio_ue_t }}</td></tr>
{%- endfor %}
</tbody>
</table>
</div>
<p>Projeto a projeto: <a href="/dados/kohesio_projetos.csv">kohesio_projetos.csv</a>
(com a coluna <code>nota</code>) e
<a href="/dados/kohesio_beneficiarios.csv">kohesio_beneficiarios.csv</a>.</p>
{% endif %}

{% if pac %}
<h2 id="pac">PAC e POSEI: pagamentos aos agricultores</h2>

<p>Pagamentos do FEAGA e do FEADER (com o cofinanciamento nacional e
regional) a beneficiários com morada fiscal nos Açores, por exercício
financeiro (o exercício de {{ pac.ultimo }} vai de 16 de outubro do ano
anterior a 15 de outubro). O POSEI é o regime agrícola próprio das regiões
ultraperiféricas e é a maior parte do dinheiro.</p>

<h3 id="pac-anos">Por ano e programa (M€)</h3>
<div class="tabela-scroll">
<table class="sper">
<thead><tr>
  <th scope="col">Exercício</th>
  <th scope="col" class="n">POSEI</th>
  <th scope="col" class="n">Desenvolvimento rural</th>
  <th scope="col" class="n">Mercados</th>
  <th scope="col" class="n">Pagamentos diretos</th>
  <th scope="col" class="n">Total</th>
  <th scope="col" class="n">dos quais UE</th>
</tr></thead>
<tbody>
{%- for a in pac.anos reversed %}
<tr><th scope="row">{{ a.ano }}</th><td class="n">{{ a.posei_t }}</td><td class="n">{{ a.rural_t }}</td><td class="n">{{ a.mercados_t }}</td><td class="n">{{ a.diretos_t }}</td><td class="n"><strong>{{ a.total_t }}</strong></td><td class="n">{{ a.ue_t }}</td></tr>
{%- endfor %}
</tbody>
</table>
</div>
<p class="nota">O IFAP só tem online os dois últimos exercícios; os totais
dos anos anteriores ficam aqui à medida que o site os lê (desde 2024).</p>

<h3 id="pac-medidas">Por medida, {{ pac.ultimo }}</h3>
<div class="tabela-scroll">
<table class="sper ordenavel barras">
<thead><tr>
  <th scope="col">Medida</th>
  <th scope="col">Programa</th>
  <th scope="col" class="n" data-tipo="n">M€</th>
  <th class="barra-col" aria-hidden="true"></th>
  <th scope="col" class="n" data-tipo="n">%</th>
</tr></thead>
<tbody>
{%- assign topo = pac.medidas | first -%}
{%- for m in pac.medidas %}
<tr><th scope="row"><code>{{ m.codigo }}</code> {{ m.nome }}</th><td>{{ m.programa }}</td><td class="n" data-v="{{ m.valor }}">{{ m.valor_t }}</td><td class="barra-col" aria-hidden="true">{% if m.valor > 0 %}<span class="barra" style="width: {{ m.valor | times: 100.0 | divided_by: topo.valor }}%"></span>{% endif %}</td><td class="n" data-v="{{ m.pct }}">{{ m.pct }} %</td></tr>
{%- endfor %}
</tbody>
</table>
</div>
<p class="nota">Medidas acima de 50 mil €. As que começam por V são do
PEPAC (2023-2027) e as que começam por VI do PRORURAL+ (2014-2022), ainda a
pagar compromissos.</p>

<h3 id="pac-concelhos">Por concelho, {{ pac.ultimo }}</h3>
<p class="nota">Pela morada do beneficiário, que pode não ser onde fica a
exploração. Por habitante: população do INE.</p>
<div class="tabela-scroll">
<table class="sper ordenavel barras">
<thead><tr>
  <th scope="col">Concelho</th>
  <th scope="col">Ilha</th>
  <th scope="col" class="n" data-tipo="n">Total (M€)</th>
  <th class="barra-col" aria-hidden="true"></th>
  <th scope="col" class="n" data-tipo="n">POSEI (M€)</th>
  <th scope="col" class="n" data-tipo="n">€ por habitante</th>
</tr></thead>
<tbody>
{%- assign topo = pac.concelhos | first -%}
{%- for c in pac.concelhos %}
<tr><th scope="row">{{ c.nome }}</th><td>{{ c.ilha }}</td><td class="n" data-v="{{ c.valor }}">{{ c.valor_t }}</td><td class="barra-col" aria-hidden="true"><span class="barra" style="width: {{ c.valor | times: 100.0 | divided_by: topo.valor }}%"></span></td><td class="n" data-v="{{ c.posei }}">{{ c.posei_t }}</td><td class="n" data-v="{{ c.por_hab }}">{{ c.por_hab_t | default: "–" }}</td></tr>
{%- endfor %}
</tbody>
</table>
</div>

<h3 id="pac-beneficiarios">Os 25 maiores beneficiários, {{ pac.ultimo }}</h3>
<p class="nota">{{ pac.beneficiarios_t }} beneficiários; os 10 % que mais
receberam ficaram com {{ pac.pct_top10 }} % do total. Os nomes são os que o
IFAP publica por obrigação europeia (Regulamento (UE) 2021/2116, art. 98.º),
e só durante dois anos: o site segue a mesma regra e guarda dos anos mais
antigos apenas os totais por concelho e medida.</p>
<div class="tabela-scroll">
<table class="sper ordenavel">
<thead><tr>
  <th scope="col">Beneficiário</th>
  <th scope="col">Concelho</th>
  <th scope="col" class="n" data-tipo="n">Total (€)</th>
  <th scope="col" class="n" data-tipo="n">dos quais POSEI (€)</th>
</tr></thead>
<tbody>
{%- for b in pac.maiores %}
<tr><th scope="row">{{ b.nome }}</th><td>{{ b.concelho }}</td><td class="n" data-v="{{ b.valor }}">{{ b.valor_t }}</td><td class="n" data-v="{{ b.posei }}">{{ b.posei_t }}</td></tr>
{%- endfor %}
</tbody>
</table>
</div>
<p>Beneficiário a beneficiário e medida a medida:
<a href="/dados/ifap_pagamentos.csv">ifap_pagamentos.csv</a> (exercícios
{{ pac.anos_nomes | join: " e " }}); totais por concelho e medida:
<a href="/dados/ifap_resumo.csv">ifap_resumo.csv</a>; as duas tabelas, com
pesquisa por nome, em <a href="/dados/sql/">fundos.db</a>. A pesquisa
oficial é a do <a href="https://apj13.ifap.pt/idigital.consultarFundos/">IFAP</a>.</p>
{% endif %}

<h2 id="notas">Notas</h2>
<ul class="notas">
  <li><strong>PRR, parte dos Açores.</strong> O ficheiro de localizações da
  Recuperar Portugal dá, para cada projeto, os concelhos e a percentagem do
  valor aprovado em cada um. A parte dos Açores é a soma dos concelhos dos
  Açores, e aplica-se também ao valor pago (as percentagens do pago somam
  mais de 100 % em alguns projetos, por isso não se usam).</li>
  <li><strong>Aprovado e pago.</strong> O aprovado é o apoio do PRR ao
  projeto (subvenções e empréstimos); o pago é o que já foi transferido.
  Valores nominais.</li>
  <li><strong>Beneficiários finais e intermediários.</strong> Muitos
  projetos têm um beneficiário intermediário (uma direção regional, o IAPMEI,
  o Fundo Ambiental) que passa o dinheiro ao beneficiário final. Os 25
  maiores são só beneficiários finais. As entidades todas estão em
  <code>prr_entidades.csv</code>.</li>
  <li><strong>PAC e POSEI: o que não está.</strong> A lista do IFAP
  arruma cada beneficiário pela morada fiscal. Ajudas do POSEI pagas a
  operadores com sede fora dos Açores (parte do regime específico de
  abastecimento) não contam como açorianas, e um agricultor com morada
  noutro concelho conta nesse concelho. Os valores negativos são
  recuperações de pagamentos indevidos.</li>
  <li><strong>PRR e fundos de coesão não se somam diretamente.</strong> Os
  valores do PRR são o apoio aprovado; os do Kohesio são o apoio da UE
  (cofinanciamento) a projetos aprovados, de 2014 em diante.</li>
  <li><strong>Atualização.</strong> O PRR e o Kohesio são relidos uma vez
  por semana por
  <a href="https://github.com/fmesqg/a-ores.net-site/blob/main/bot/fundos.py"><code>bot/fundos.py</code></a>;
  a lista do IFAP, também semanalmente, por
  <a href="https://github.com/fmesqg/a-ores.net-site/blob/main/bot/ifap.py"><code>bot/ifap.py</code></a>
  (o IFAP publica cada exercício uma vez por ano, por volta de maio).</li>
</ul>
{% else %}
<p>Os dados ainda não foram gerados.</p>
{% endif %}

<style>
.lead { font-size: 1.15em; max-width: 40em; }
.numeros { display: grid; grid-template-columns: repeat(auto-fit, minmax(min(12em, 100%), 1fr)); gap: .9em; margin: 1em 0 .4em; }
.numero.construcao { border-style: dashed; }
.selo { display: inline-block; font-size: .7em; font-weight: bold; vertical-align: middle; padding: .1em .5em; border-radius: 999px; background: #b58900; color: var(--sobre-acento); }
.aviso { border-left: 4px solid #b58900; padding: .4em .8em; background: rgba(181,137,0,.08); margin-bottom: 1em; }
.aviso ul { margin-bottom: .4em; }
h2[id], h3[id] { scroll-margin-top: 1em; margin-top: 1.4em; }
table.sper th[scope="row"] { font-weight: normal; }
table.sper tr.fora th, table.sper tr.fora td { color: var(--s0); }
table.ordenavel thead th[data-tipo] { cursor: pointer; }
table.ordenavel thead th[aria-sort="descending"]::after { content: " ▼"; }
table.ordenavel thead th[aria-sort="ascending"]::after { content: " ▲"; }
.barra-col { width: 18%; min-width: 4em; }
.barra { display: block; height: .8em; margin-top: .25em; background: #268bd2; border-radius: 0 4px 4px 0; }
.fonte { font-size: .85em; color: var(--s01); }
@media (prefers-color-scheme: dark) {
  .fonte { color: var(--s01); }
}
</style>

<script>
(function () {
  document.querySelectorAll("table.ordenavel").forEach(function (tabela) {
    var corpo = tabela.tBodies[tabela.tBodies.length - 1];
    var ths = tabela.tHead.rows[0].cells;
    Array.prototype.forEach.call(ths, function (th, i) {
      if (!th.dataset.tipo) return;
      th.tabIndex = 0;
      function ordenar(e) {
        if (e.target.closest("a")) return;
        var desc = th.getAttribute("aria-sort") !== "descending";
        Array.prototype.forEach.call(ths, function (o) { o.removeAttribute("aria-sort"); });
        th.setAttribute("aria-sort", desc ? "descending" : "ascending");
        var linhas = Array.prototype.slice.call(corpo.rows);
        linhas.sort(function (a, b) {
          var x = parseFloat(a.cells[i].dataset.v), y = parseFloat(b.cells[i].dataset.v);
          if (isNaN(x)) x = -Infinity;
          if (isNaN(y)) y = -Infinity;
          return desc ? y - x : x - y;
        });
        linhas.forEach(function (tr) { corpo.appendChild(tr); });
      }
      th.addEventListener("click", ordenar);
      th.addEventListener("keydown", function (e) { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); ordenar(e); } });
    });
  });
})();
</script>
