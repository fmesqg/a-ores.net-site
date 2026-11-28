---
title: IRC das empresas
nav_title: IRC das empresas
layout: default
permalink: /dados/irc/
secao: financas
description: Quantas empresas com sede nos Açores entregam a declaração de IRC, quanto lucro declaram e quanto imposto pagam, ano a ano desde 2011, ao lado da Madeira e do país. Dados da Autoridade Tributária.
---
{%- assign d = site.data.irc -%}
{% include financas-nav.html %}

# IRC das empresas

<p class="lead">Quantas empresas com sede nos Açores entregam a declaração de
IRC (Modelo 22), quanto lucro declaram e quanto imposto pagam. Os números são
da Autoridade Tributária (AT), que publica todos os anos as estatísticas das
declarações por distrito, e os Açores contam como um distrito.</p>

{% if d.serie %}
{%- assign u = d.ultimo %}
<div class="numeros">
<div class="numero">
  <p class="rotulo">Declarações de empresas dos Açores, {{ d.ano }}</p>
  <p class="grande">{{ u.declaracoes_t }}</p>
  <p>{{ u.decl_pct_t }} % das declarações do país.</p>
</div>
<div class="numero">
  <p class="rotulo">IRC liquidado, {{ d.ano }}</p>
  <p class="grande">{{ u.irc_m_t }} <small>M€</small></p>
  <p>{{ u.irc_pct_t }} % do IRC liquidado no país, sobre
  {{ u.lucro_m_t }} M€ de lucro tributável.</p>
</div>
<div class="numero">
  <p class="rotulo">Taxa média efetiva, {{ d.ano }}</p>
  <p class="grande">{{ u.taxa_s }}</p>
  <p>No país, {{ u.taxa_pais_s }}; na Madeira, {{ u.taxa_madeira_s }}. A
  taxa normal de IRC nos Açores é 30 % mais baixa do que no continente.</p>
</div>
<div class="numero">
  <p class="rotulo">Imposto à taxa da Região, {{ d.ano }}</p>
  <p class="grande">{{ u.regional_m_t }} <small>M€</small></p>
  <p>Declarado em {{ d.regional_n_t }} declarações, de empresas com sede
  nos Açores ou fora (ver <a href="#notas">como ler</a>).</p>
</div>
</div>
<p class="fonte">Fonte: AT, <a href="{{ d.url }}">Dossier Estatístico do IRC
{{ d.dossie | replace: "-", "–" }}</a> (mapas «por distrito», «Cálculo do
imposto» e «Derrama estadual por escalões»). As percentagens do país são
cálculos do açores.net com esses números (a AT dá as mesmas nas notas
prévias).</p>

<h2 id="serie">Ano a ano</h2>

<p class="nota">Empresas com sede (ou estabelecimento estável) nos Açores. Até
2019, a AT divide os Açores pelos antigos distritos de Angra do Heroísmo, Horta
e Ponta Delgada: aqui estão somados.</p>
<div class="tabela-scroll">
<table class="sper">
<thead><tr>
  <th scope="col">Ano</th>
  <th scope="col" class="n">Declarações</th>
  <th scope="col" class="n">% do país</th>
  <th scope="col" class="n">Lucro tributável (M€)</th>
  <th scope="col" class="n">Prejuízo fiscal (M€)</th>
  <th scope="col" class="n">IRC liquidado (M€)</th>
  <th scope="col" class="n">% do IRC do país</th>
  <th scope="col" class="n">Imposto à taxa da Região (M€)</th>
</tr></thead>
<tbody>
{%- for s in d.serie reversed %}
<tr><th scope="row">{{ s.ano }}</th><td class="n">{{ s.declaracoes_t }}</td><td class="n">{{ s.decl_pct_t }}</td><td class="n">{{ s.lucro_m_t }}</td><td class="n">{{ s.prejuizo_m_t }}</td><td class="n">{{ s.irc_m_t }}</td><td class="n">{{ s.irc_pct_t }}</td><td class="n">{{ s.regional_m_t }}</td></tr>
{%- endfor %}
</tbody>
</table>
</div>

<h2 id="taxa">Taxa média efetiva</h2>

<p class="nota">O imposto pago a dividir pela matéria coletável, como a AT a
calcula (fórmula em <a href="#notas">como ler</a>). Até 2019 a AT só a dá
para cada um dos três antigos distritos dos Açores, que não se podem somar:
esses anos ficam em branco (estão em
<a href="/dados/at_distritos.csv">at_distritos.csv</a>).</p>
<div class="tabela-scroll">
<table class="sper">
<thead><tr><th scope="col">Ano</th><th scope="col" class="n">Açores</th><th scope="col" class="n">Madeira</th><th scope="col" class="n">País</th></tr></thead>
<tbody>
{%- for s in d.serie reversed %}
<tr><th scope="row">{{ s.ano }}</th><td class="n">{{ s.taxa_s }}</td><td class="n">{{ s.taxa_madeira_s }}</td><td class="n">{{ s.taxa_pais_s }}</td></tr>
{%- endfor %}
</tbody>
</table>
</div>

<h2 id="taxas">Taxas nominais, {{ d.ano }}</h2>

<div class="tabela-scroll">
<table class="sper">
<thead><tr><th scope="col"></th><th scope="col" class="n">Continente</th><th scope="col" class="n">Açores</th><th scope="col" class="n">Madeira</th></tr></thead>
<tbody>
{%- for t in d.nominais %}
<tr><th scope="row">{{ t.designacao }}</th><td class="n">{{ t.continente_s }}</td><td class="n">{{ t.acores_s }}</td><td class="n">{{ t.madeira_s }}</td></tr>
{%- endfor %}
</tbody>
</table>
</div>
<p class="fonte">Fonte: AT, quadro «Evolução das taxas nominais em IRC» do
dossiê. A taxa reduzida aplica-se às pequenas e médias empresas, na parte da
matéria coletável até ao limite indicado. As taxas de anos anteriores estão em
<a href="/dados/at_irc.csv">at_irc.csv</a>.</p>

<h2 id="derrama">Derrama estadual</h2>

<p class="nota">Uma taxa adicional sobre o lucro tributável acima de 1,5
milhões de euros
(<a href="https://info.portaldasfinancas.gov.pt/pt/informacao_fiscal/codigos_tributarios/circ_rep/Pages/irc87a.aspx">artigo
87.º-A do Código do IRC</a>). Empresas dos Açores que a pagaram e quanto:</p>
<div class="tabela-scroll">
<table class="sper">
<thead><tr><th scope="col">Ano</th><th scope="col" class="n">Declarações</th><th scope="col" class="n">Derrama (M€)</th></tr></thead>
<tbody>
{%- for s in d.serie reversed %}{% if s.derrama_m != "" %}
<tr><th scope="row">{{ s.ano }}</th><td class="n">{{ s.derrama_n_t }}</td><td class="n">{{ s.derrama_m_t }}</td></tr>
{%- endif %}{% endfor %}
</tbody>
</table>
</div>
<p class="nota">Por escalão de lucro tributável, {{ d.ano }}:</p>
<div class="tabela-scroll">
<table class="sper">
<thead><tr><th scope="col">Lucro tributável (€)</th><th scope="col" class="n">Declarações</th><th scope="col" class="n">Derrama (M€)</th></tr></thead>
<tbody>
{%- for e in d.derrama_escaloes %}
<tr><th scope="row">{{ e.escalao }}</th><td class="n">{{ e.declaracoes_t }}</td><td class="n">{{ e.valor_m_t }}</td></tr>
{%- endfor %}
</tbody>
</table>
</div>
<p class="fonte">Fonte: AT, mapas «Derrama estadual por escalões» (desde 2017).
A AT conta aqui as declarações individuais das empresas de um grupo, por isso
o número pode passar o dos outros mapas.</p>

<h2 id="notas">Como ler</h2>

<ul class="notas">
  <li><strong>Distrito</strong>: a AT arruma cada declaração pelo distrito
  da sede ou do estabelecimento estável. Uma empresa com sede em Lisboa e lojas
  nos Açores conta em Lisboa.</li>
  <li><strong>Imposto à taxa da Região</strong>: a parte do imposto que as
  empresas calculam à taxa dos Açores no quadro 10 da declaração Modelo 22
  (mapa «Cálculo do imposto»). É maior do que o IRC liquidado das empresas com
  sede nos Açores; a nossa leitura é que inclui empresas de fora com atividade
  nos Açores, que pagam essa parte à taxa regional, mas as notas da AT não o
  explicam.</li>
  <li><strong>Taxa média efetiva</strong> (definição da AT): IRC liquidado
  corrigido, reposição de benefícios fiscais, tributações autónomas, resultado
  da liquidação, derrama estadual e IRC de anos anteriores, a dividir pela
  matéria coletável mais os benefícios deduzidos ao rendimento. Por causa das
  tributações autónomas pode passar a taxa nominal.</li>
  <li>Os valores são do ano a que respeitam os lucros, declarados no ano
  seguinte. Não são a receita de caixa do ano, que está nos
  <a href="/dados/beo/">boletins de execução orçamental</a>.</li>
  <li>Cada dossiê traz três anos e a AT revê os anteriores: aqui fica sempre o
  valor da edição mais recente. Leia as
  <a href="https://info.portaldasfinancas.gov.pt/pt/dgci/divulgacao/estatisticas/estatisticas_ir/Pages/estatisticas_irc.aspx">notas
  prévias</a> de cada dossiê antes de usar os números.</li>
  <li>Os dados completos (todos os distritos, também o resultado líquido e a
  matéria coletável) estão em <a href="/dados/at_distritos.csv">at_distritos.csv</a>
  e <a href="/dados/at_irc.csv">at_irc.csv</a>, e nas tabelas com o mesmo nome
  da <a href="/dados/sql/">base de dados</a>. São atualizados
  quando a AT publica um dossiê novo (entre o fim de março e meados de abril),
  por <a href="https://github.com/fmesqg/a-ores.net-site/blob/main/bot/at_ir.py"><code>bot/at_ir.py</code></a>.</li>
</ul>
{% else %}
<p>Os dados ainda não foram gerados.</p>
{% endif %}

<style>
.lead { font-size: 1.15em; max-width: 40em; }
.numeros { display: grid; grid-template-columns: repeat(auto-fit, minmax(min(12em, 100%), 1fr)); gap: .9em; margin: 1em 0 .4em; }
h2[id] { scroll-margin-top: 1em; margin-top: 1.4em; }
table.sper th[scope="row"] { font-weight: normal; }
.fonte { font-size: .85em; color: var(--s01); }
@media (prefers-color-scheme: dark) {
  .fonte { color: var(--s01); }
}
</style>
