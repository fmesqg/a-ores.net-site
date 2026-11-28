---
title: IRS por escalão
nav_title: IRS por escalão
layout: default
permalink: /dados/irs/
secao: financas
description: Quantos agregados há em cada escalão de IRS nos Açores, quanto rendimento declaram e quanto imposto pagam, ano a ano desde 2016, com a Madeira e o continente ao lado. Dados da Autoridade Tributária.
---
{%- assign d = site.data.irs -%}
{% include financas-nav.html %}

# IRS por escalão

<p class="lead">Quantos agregados há em cada escalão de IRS nos Açores, quanto
rendimento declaram e quanto imposto pagam. Os números são da Autoridade
Tributária (AT), que publica todos os anos as estatísticas das declarações de
IRS por região.</p>

{% if d.escaloes %}
<div class="numeros">
<div class="numero">
  <p class="rotulo">Agregados que entregaram IRS, {{ d.ano }}</p>
  <p class="grande">{{ d.agregados_t }}</p>
  <p>Declararam {{ d.rendimento_m_t }} M€ de rendimento englobado e pagaram
  {{ d.irs_m_t }} M€ de IRS: {{ d.taxa_media_t }} % do rendimento.</p>
</div>
<div class="numero">
  <p class="rotulo">Último escalão, {{ d.ano }}</p>
  <p class="grande">{{ d.topo.agregados_t }}</p>
  <p>{{ d.topo.agregados_pct_t }} % dos agregados, que pagaram
  {{ d.topo.irs_pct_t }} % do IRS, à taxa de {{ d.topo.taxa_s }} (no
  continente, {{ d.topo.taxa_continente_s }}).</p>
</div>
<div class="numero">
  <p class="rotulo">Primeiro escalão, {{ d.ano }}</p>
  {%- assign um = d.escaloes | first %}
  <p class="grande">{{ um.agregados_t }}</p>
  <p>{{ um.agregados_pct_t }} % dos agregados, que pagaram {{ um.irs_pct_t }} %
  do IRS.</p>
</div>
</div>
<p class="fonte">Fonte: AT, <a href="{{ d.url }}">Dossier Estatístico do IRS
{{ d.dossie | replace: "-", "–" }}</a> (mapas «Taxas de Tributação por
Circunscrições Administrativas»). As percentagens e o IRS por agregado são
cálculos do açores.net com esses números (a AT dá a mesma taxa média, que
chama «taxa efetiva», nas notas prévias).</p>

<h2 id="escaloes">Por escalão, {{ d.ano }}</h2>

<p class="nota">Nos Açores, as taxas são mais baixas do que no continente (30 %
abaixo em todos os escalões desde 2022). O escalão é a taxa que a AT aplicou a
cada agregado.</p>
<div class="tabela-scroll">
<table class="sper">
<thead><tr>
  <th scope="col">Escalão</th>
  <th scope="col" class="n">Taxa nos Açores</th>
  <th scope="col" class="n">Taxa no continente</th>
  <th scope="col" class="n">Agregados</th>
  <th scope="col" class="n">% dos agregados</th>
  <th scope="col" class="n">Rendimento englobado (M€)</th>
  <th scope="col" class="n">IRS liquidado (M€)</th>
  <th scope="col" class="n">% do IRS</th>
  <th scope="col" class="n">IRS por agregado (€)</th>
</tr></thead>
<tbody>
{%- for e in d.escaloes %}
<tr><th scope="row">{{ e.ordem }}.º</th><td class="n">{{ e.taxa_s }}</td><td class="n">{{ e.taxa_continente_s }}</td><td class="n">{{ e.agregados_t }}</td><td class="n">{{ e.agregados_pct_t }}</td><td class="n">{{ e.rendimento_m_t }}</td><td class="n">{{ e.irs_m_t }}</td><td class="n">{{ e.irs_pct_t }}</td><td class="n">{{ e.irs_medio_t }}</td></tr>
{%- endfor %}
</tbody>
<tfoot><tr><th scope="row">Total</th><td></td><td></td><td class="n">{{ d.agregados_t }}</td><td class="n">100</td><td class="n">{{ d.rendimento_m_t }}</td><td class="n">{{ d.irs_m_t }}</td><td class="n">100</td><td></td></tr></tfoot>
</table>
</div>

<h2 id="topo">O último escalão, ano a ano</h2>

<p class="nota">Agregados no último escalão, nos Açores e na Madeira. A
comparação por mil agregados desconta o tamanho de cada região. O número de
escalões e o rendimento a partir do qual se entra no último mudam com o
Orçamento do Estado (5 escalões até 2017, 7 até 2021 e 9 desde 2022): ver as
<a href="#gerais">taxas gerais</a>.</p>
<div class="tabela-scroll">
<table class="sper">
<thead><tr>
  <th scope="col">Ano</th>
  <th scope="col" class="n">Açores: agregados</th>
  <th scope="col" class="n">por mil agregados</th>
  <th scope="col" class="n">% do IRS</th>
  <th scope="col" class="n">taxa</th>
  <th scope="col" class="n">Madeira: agregados</th>
  <th scope="col" class="n">por mil agregados</th>
  <th scope="col" class="n">% do IRS</th>
  <th scope="col" class="n">taxa</th>
</tr></thead>
<tbody>
{%- for s in d.serie %}
<tr><th scope="row">{{ s.ano }}</th><td class="n">{{ s.acores_t }}</td><td class="n">{{ s.acores_por_mil_t }}</td><td class="n">{{ s.acores_irs_pct_t }}</td><td class="n">{{ s.acores_taxa_s }}</td><td class="n">{{ s.madeira_t }}</td><td class="n">{{ s.madeira_por_mil_t }}</td><td class="n">{{ s.madeira_irs_pct_t }}</td><td class="n">{{ s.madeira_taxa_s }}</td></tr>
{%- endfor %}
</tbody>
</table>
</div>

{% if d.gerais.escaloes %}
<h2 id="gerais">Taxas gerais, {{ d.gerais.ano }}</h2>

<div class="tabela-scroll">
<table class="sper">
<thead><tr><th scope="col">Rendimento coletável</th><th scope="col" class="n">Continente</th><th scope="col" class="n">Açores</th><th scope="col" class="n">Madeira</th></tr></thead>
<tbody>
{%- for e in d.gerais.escaloes %}
<tr><th scope="row">{{ e.escalao }}</th><td class="n">{{ e.continente_s }}</td><td class="n">{{ e.acores_s }}</td><td class="n">{{ e.madeira_s }}</td></tr>
{%- endfor %}
</tbody>
</table>
</div>
<p class="fonte">Fonte: AT, mapa «Taxas Gerais de IRS» do dossiê. As taxas
dos anos desde 2017 estão em <a href="/dados/at_irs.csv">at_irs.csv</a>.</p>
{% endif %}

{% if d.pais %}
<h2 id="pais">Os Açores no país</h2>

<p class="nota">Agregados e IRS liquidado por região, nos mapas «por distrito»
da AT. Estes mapas contam mais agregados e mais imposto do que os mapas por
escalão acima (em {{ d.ano }}, {{ d.pais.last.acores_agregados_t }} agregados e
{{ d.pais.last.acores_irs_m_t }} M€ nos Açores, contra {{ d.agregados_t }} e
{{ d.irs_m_t }} M€). As notas prévias da AT não explicam a diferença; use
cada série com a sua tabela. O IRS por agregado é um cálculo do
açores.net.</p>
<div class="tabela-scroll">
<table class="sper">
<thead><tr>
  <th scope="col">Ano</th>
  <th scope="col" class="n">Açores: agregados</th>
  <th scope="col" class="n">% do país</th>
  <th scope="col" class="n">IRS (M€)</th>
  <th scope="col" class="n">% do país</th>
  <th scope="col" class="n">IRS por agregado (€)</th>
  <th scope="col" class="n">Madeira: IRS por agregado (€)</th>
  <th scope="col" class="n">País: IRS por agregado (€)</th>
</tr></thead>
<tbody>
{%- for s in d.pais reversed %}
<tr><th scope="row">{{ s.ano }}</th><td class="n">{{ s.acores_agregados_t }}</td><td class="n">{{ s.acores_agregados_pct_t }}</td><td class="n">{{ s.acores_irs_m_t }}</td><td class="n">{{ s.acores_irs_pct_t }}</td><td class="n">{{ s.acores_por_agregado_t }}</td><td class="n">{{ s.madeira_por_agregado_t }}</td><td class="n">{{ s.pais_por_agregado_t }}</td></tr>
{%- endfor %}
</tbody>
</table>
</div>
<p class="fonte">Fonte: AT, mapas «por distrito» dos dossiês (até 2019 os
Açores aparecem também divididos pelos antigos distritos de Angra do Heroísmo,
Horta e Ponta Delgada). Todos os distritos, a taxa efetiva e o rendimento
estão em <a href="/dados/at_distritos.csv">at_distritos.csv</a>.</p>
{% endif %}

<h2 id="adicional">Taxa adicional de solidariedade</h2>

<p class="nota">No continente paga-se 2,5 % sobre a parte do rendimento
coletável entre 80 mil € e 250 mil €, e 5 % acima de 250 mil €
(<a href="https://info.portaldasfinancas.gov.pt/pt/informacao_fiscal/codigos_tributarios/cirs_rep/Pages/irs68a.aspx">artigo
68.º-A do Código do IRS</a>). Nos Açores estas taxas também têm desconto.
Agregados e imposto nos Açores:</p>
<div class="tabela-scroll">
<table class="sper">
<thead><tr><th scope="col">Ano</th><th scope="col" class="n">Agregados</th><th scope="col" class="n">IRS liquidado (M€)</th></tr></thead>
<tbody>
{%- for a in d.adicional %}
<tr><th scope="row">{{ a.ano }}</th><td class="n">{{ a.agregados_t }}</td><td class="n">{{ a.irs_m_t }}</td></tr>
{%- endfor %}
</tbody>
</table>
</div>
<p class="fonte">Fonte: AT, mapas «Taxa Adicional de Solidariedade» dos dossiês
estatísticos. Os valores somam as duas linhas da AT (80 a 250 mil € e acima
de 250 mil €); estão separadas em <a href="/dados/at_irs.csv">at_irs.csv</a>.</p>

<h2 id="notas">Como ler</h2>

<ul class="notas">
  <li><strong>Agregado</strong>: uma declaração de IRS (uma pessoa, ou um casal
  que entrega em conjunto). A AT conta-o na região onde reside.</li>
  <li><strong>Rendimento englobado</strong>: o rendimento sujeito às taxas
  gerais (trabalho, pensões, rendimentos empresariais…). Ficam de fora os
  rendimentos tributados a taxas especiais (juros, dividendos, mais-valias,
  quando não englobados).</li>
  <li><strong>IRS liquidado</strong>: o imposto apurado na liquidação, depois
  das deduções, para o ano de rendimentos. Não é a receita de caixa do ano, que
  está nos <a href="/dados/beo/">boletins de execução orçamental</a>.</li>
  <li>Cada dossiê traz três anos e a AT revê os anteriores: aqui fica sempre o
  valor da edição mais recente. Leia as
  <a href="https://info.portaldasfinancas.gov.pt/pt/dgci/divulgacao/estatisticas/estatisticas_ir/Pages/estatisticas_irs.aspx">notas
  prévias</a> de cada dossiê antes de usar os números.</li>
  <li>Os dados completos (também casados e não casados, e o continente) estão em
  <a href="/dados/at_irs.csv">at_irs.csv</a> e na tabela <code>at_irs</code> da
  <a href="/dados/sql/">base de dados</a>. São atualizados quando
  a AT publica um dossiê novo (entre o fim de março e meados de abril), por
  <a href="https://github.com/fmesqg/a-ores.net-site/blob/main/bot/at_ir.py"><code>bot/at_ir.py</code></a>.</li>
</ul>
{% else %}
<p>Os dados ainda não foram gerados.</p>
{% endif %}

<style>
.lead { font-size: 1.15em; max-width: 40em; }
.numeros { display: grid; grid-template-columns: repeat(auto-fit, minmax(min(12em, 100%), 1fr)); gap: .9em; margin: 1em 0 .4em; }
h2[id] { scroll-margin-top: 1em; margin-top: 1.4em; }
table.sper th[scope="row"] { font-weight: normal; white-space: nowrap; }
.fonte { font-size: .85em; color: var(--s01); }
@media (prefers-color-scheme: dark) {
  .fonte { color: var(--s01); }
}
</style>
