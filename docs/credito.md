---
title: Crédito, depósitos e empresas
nav_title: Crédito e depósitos
layout: default
permalink: /dados/credito/
secao: economia
description: Quanto devem e quanto têm depositado as famílias e as empresas dos Açores, quanto crédito está em incumprimento, e como estão as contas das empresas, ao lado da Madeira e do país. Dados do Banco de Portugal.
---
{%- assign d = site.data.credito -%}
{% include economia-nav.html %}

# Crédito, depósitos e empresas

<p class="lead">Quanto devem aos bancos as famílias e as empresas dos Açores,
quanto têm depositado e quanto crédito está em incumprimento, mês a mês. E
como estão as contas das empresas com sede nos Açores, ano a ano. Os números
são do Banco de Portugal (BPstat).</p>

{% if d.cards %}
{%- assign c = d.cards %}
<div class="numeros">
<div class="numero">
  <p class="rotulo">Crédito à habitação, {{ d.ultimo_mes }}</p>
  <p class="grande">{{ c.habitacao_m_t }} <small>M€</small></p>
  <p>Devido por {{ c.devedores_habitacao_mil_t }} mil pessoas com residência
  nos Açores; {{ c.habitacao_cresc_s }} do que um ano antes.</p>
</div>
<div class="numero">
  <p class="rotulo">Empréstimos a empresas, {{ d.ultimo_mes }}</p>
  <p class="grande">{{ c.empresas_m_t }} <small>M€</small></p>
  <p>Sociedades não financeiras com sede nos Açores.</p>
</div>
<div class="numero">
  <p class="rotulo">Depósitos de particulares, {{ d.depositos_mes }}</p>
  <p class="grande">{{ c.dep_particulares_m_t }} <small>M€</small></p>
  <p>Em balcões nos Açores. Os depósitos de emigrantes nesses balcões
  somam {{ c.dep_emigrantes_m_t }} M€.</p>
</div>
<div class="numero">
  <p class="rotulo">Crédito face aos depósitos, {{ d.depositos_mes }}</p>
  <p class="grande">{{ d.credito_depositos.acores_t }} <small>€</small></p>
  <p>emprestados a particulares por cada 100 € que têm depositados (no país,
  {{ d.credito_depositos.pais_t }} €; na Madeira,
  {{ d.credito_depositos.madeira_t }} €).</p>
</div>
</div>
<p class="fonte">Fonte: Banco de Portugal, <a href="https://bpstat.bportugal.pt/">BPstat</a>,
estatísticas regionais (cada tabela abaixo leva às séries). O total do país, os valores por habitante e o crédito face aos
depósitos são cálculos do açores.net (ver <a href="#notas">como ler</a>).</p>

<h2 id="habitante">Por habitante</h2>

<p class="nota">Euros por residente, no fim de {{ d.ultimo_mes }}, com a
população de {{ d.populacao_ano }} (INE). Cada linha leva à série do Banco de
Portugal para os Açores.</p>
<div class="tabela-scroll">
<table class="sper">
<thead><tr><th scope="col"></th><th scope="col" class="n">Açores</th><th scope="col" class="n">Madeira</th><th scope="col" class="n">País</th></tr></thead>
<tbody>
{%- for l in d.por_habitante %}
<tr><th scope="row"><a href="{{ l.url }}">{{ l.nome }}</a></th><td class="n">{{ l.acores_t }}</td><td class="n">{{ l.madeira_t }}</td><td class="n">{{ l.pais_t }}</td></tr>
{%- endfor %}
</tbody>
</table>
</div>

<h2 id="incumprimento">Crédito em incumprimento, {{ d.ultimo_mes }}</h2>

<p class="nota">O <strong>rácio de empréstimos vencidos</strong> é o crédito
vencido a dividir pelo total dos empréstimos; a <strong>percentagem de
devedores</strong> é a parte dos devedores com algum crédito vencido
(definições do Banco de Portugal, <a href="https://www.bportugal.pt/sites/default/files/anexos/documentos-relacionados/nie%2022_2016_crc.pdf">nota
de informação estatística 22/2016</a>).</p>
<div class="tabela-scroll">
<table class="sper">
<thead>
<tr><th scope="col" rowspan="2"></th><th scope="colgroup" colspan="2" class="n">Açores</th><th scope="colgroup" colspan="2" class="n">Madeira</th><th scope="colgroup" colspan="2" class="n">País</th></tr>
<tr><th scope="col" class="n">rácio</th><th scope="col" class="n">devedores</th><th scope="col" class="n">rácio</th><th scope="col" class="n">devedores</th><th scope="col" class="n">rácio</th><th scope="col" class="n">devedores</th></tr>
</thead>
<tbody>
{%- for l in d.incumprimento %}
<tr><th scope="row"><a href="{{ l.url }}">{{ l.nome }}</a></th><td class="n">{{ l.acores_racio_s }}</td><td class="n">{{ l.acores_devedores_s }}</td><td class="n">{{ l.madeira_racio_s }}</td><td class="n">{{ l.madeira_devedores_s }}</td><td class="n">{{ l.pais_racio_s }}</td><td class="n">{{ l.pais_devedores_s }}</td></tr>
{%- endfor %}
</tbody>
</table>
</div>
<p class="fonte">Para o país, o Banco de Portugal não dá estes rácios nas
estatísticas regionais: são cálculos do açores.net com a soma das regiões
(o rácio exato; a percentagem de devedores, aproximada, a partir de valores
arredondados).</p>

<h2 id="serie">Ano a ano, Açores</h2>

<p class="nota">Saldo no fim de cada ano (e do último mês), em milhões de
euros. Os empréstimos a particulares só se dividem entre habitação e consumo
desde 2009; os depósitos por região começam em dezembro de 2018.</p>
<div class="tabela-scroll">
<table class="sper">
<thead><tr>
  <th scope="col"></th>
  <th scope="col" class="n">Crédito à habitação</th>
  <th scope="col" class="n">Consumo e outros fins</th>
  <th scope="col" class="n">Empréstimos a empresas</th>
  <th scope="col" class="n">Vencidos, particulares</th>
  <th scope="col" class="n">Vencidos, empresas</th>
  <th scope="col" class="n">Depósitos de particulares</th>
  <th scope="col" class="n">Depósitos de empresas</th>
  <th scope="col" class="n">Depósitos de emigrantes</th>
</tr></thead>
<tbody>
{%- for s in d.serie %}
<tr><th scope="row">{{ s.periodo }}</th><td class="n">{{ s.habitacao_t }}</td><td class="n">{{ s.consumo_t }}</td><td class="n">{{ s.empresas_t }}</td><td class="n">{{ s.vencidos_particulares_s }}</td><td class="n">{{ s.vencidos_empresas_s }}</td><td class="n">{{ s.dep_particulares_t }}</td><td class="n">{{ s.dep_empresas_t }}</td><td class="n">{{ s.dep_emigrantes_t }}</td></tr>
{%- endfor %}
</tbody>
</table>
</div>
<p class="fonte">«Vencidos» é o rácio de empréstimos vencidos. Os depósitos
de emigrantes são uma série à parte, que o Banco de Portugal descreve como um
«detalhe» das estatísticas regionais de depósitos.</p>

{%- assign e = d.empresas %}
{% if e.ano %}
<h2 id="empresas">As contas das empresas, {{ e.ano }}</h2>

<p class="nota">Sociedades não financeiras com sede em cada região (todas as
atividades exceto as das sedes sociais, como o Banco de Portugal as agrega), a partir das contas anuais que entregam na
Informação Empresarial Simplificada (IES). Cada linha leva à série do Banco de
Portugal para os Açores, com a definição.</p>
<div class="tabela-scroll">
<table class="sper">
<thead><tr><th scope="col"></th><th scope="col" class="n">Açores</th><th scope="col" class="n">Madeira</th><th scope="col" class="n">País</th></tr></thead>
<tbody>
{%- for l in e.comparar %}
<tr><th scope="row"><a href="{{ l.url }}">{{ l.nome }}</a></th><td class="n">{{ l.acores_s }}</td><td class="n">{{ l.madeira_s }}</td><td class="n">{{ l.pais_s }}</td></tr>
{%- endfor %}
</tbody>
</table>
</div>

<p class="nota">Por setor de atividade, Açores, {{ e.ano }}:</p>
<div class="tabela-scroll">
<table class="sper">
<thead><tr>
  <th scope="col">Setor</th>
  <th scope="col" class="n">Empresas</th>
  <th scope="col" class="n">Pessoas ao serviço</th>
  <th scope="col" class="n">Vendas</th>
  <th scope="col" class="n">Autonomia financeira</th>
  <th scope="col" class="n">Rendibilidade do ativo</th>
  <th scope="col" class="n">Com prejuízo</th>
  <th scope="col" class="n">Prazo médio de pagamentos</th>
</tr></thead>
<tbody>
{%- for l in e.setores %}
<tr><th scope="row">{{ l.nome }}</th><td class="n">{{ l.empresas_t }}</td><td class="n">{{ l.pessoas_s }}</td><td class="n">{{ l.vendas_s }}</td><td class="n">{{ l.autonomia_s }}</td><td class="n">{{ l.rendibilidade_s }}</td><td class="n">{{ l.negativo_s }}</td><td class="n">{{ l.pagamentos_s }}</td></tr>
{%- endfor %}
</tbody>
</table>
</div>
<p class="fonte">«Com prejuízo»: empresas com resultado líquido negativo, em
percentagem das empresas do setor. Autonomia financeira: capital próprio em
percentagem do ativo.</p>

<p class="nota">Ano a ano, todas as empresas dos Açores:</p>
<div class="tabela-scroll">
<table class="sper">
<thead><tr><th scope="col">Ano</th><th scope="col" class="n">Empresas</th><th scope="col" class="n">Pessoas ao serviço</th><th scope="col" class="n">Vendas</th><th scope="col" class="n">Autonomia financeira</th><th scope="col" class="n">Rendibilidade do ativo</th><th scope="col" class="n">Com prejuízo</th></tr></thead>
<tbody>
{%- for l in e.evolucao %}
<tr><th scope="row">{{ l.ano }}</th><td class="n">{{ l.empresas_s }}</td><td class="n">{{ l.pessoas_s }}</td><td class="n">{{ l.vendas_s }}</td><td class="n">{{ l.autonomia_s }}</td><td class="n">{{ l.rendibilidade_s }}</td><td class="n">{{ l.negativo_s }}</td></tr>
{%- endfor %}
</tbody>
</table>
</div>
<p class="fonte">Para comparar com outras fontes: a AT conta as
<a href="/dados/irc/">declarações de IRC</a> de todas as empresas com sede nos
Açores, incluindo as que não são sociedades não financeiras; a revista
<a href="/dados/maiores-empresas/">100 Maiores</a> lista as maiores, uma a
uma.</p>
{% endif %}

{% if d.ide.size > 0 %}
<h2 id="ide">Investimento direto do exterior</h2>

<p class="nota">Posição no fim de cada ano, em milhões de euros: o capital
que investidores de fora de Portugal têm em empresas com sede nos Açores
(«sedes») e em estabelecimentos situados nos Açores, mesmo de empresas com
sede noutra região («estabelecimentos»).</p>
<div class="tabela-scroll">
<table class="sper">
<thead><tr><th scope="col">Ano</th><th scope="col" class="n">Sedes nos Açores</th><th scope="col" class="n">% do país</th><th scope="col" class="n">Estabelecimentos nos Açores</th><th scope="col" class="n">% do país</th></tr></thead>
<tbody>
{%- for l in d.ide %}
<tr><th scope="row">{{ l.ano }}</th><td class="n">{{ l.sedes_t }}</td><td class="n">{{ l.sedes_pct_t }}</td><td class="n">{{ l.estab_t }}</td><td class="n">{{ l.estab_pct_t }}</td></tr>
{%- endfor %}
</tbody>
</table>
</div>
<p class="fonte">Fonte: Banco de Portugal, <a href="{{ d.ide_url }}">investimento
direto do exterior em Portugal por região</a>. As percentagens são cálculos do
açores.net.</p>
{% endif %}

<h2 id="notas">Como ler</h2>

<ul class="notas">
  <li><strong>Empréstimos</strong>: o que os bancos («outras instituições
  financeiras monetárias», na classificação do Banco de Portugal) emprestaram e
  ainda está por pagar no fim do mês, arrumado pela região de residência de
  quem deve. Os
  <strong>particulares</strong> incluem as instituições sem fim lucrativo ao
  serviço das famílias; as <strong>empresas</strong> são as sociedades não
  financeiras.</li>
  <li><strong>Depósitos</strong>: arrumados pela localização do balcão onde
  está o depósito, não pela residência do depositante. Os depósitos que não
  estão ligados a um balcão físico ficam numa linha à parte («Concelho não
  alocado») e não contam em nenhuma região.</li>
  <li><strong>Total do país</strong>: para empréstimos e depósitos, o Banco de
  Portugal dá as regiões mas não o total. Aqui é a soma das nove regiões NUTS
  II (e, nos depósitos, dos que não estão ligados a um balcão): um cálculo do
  açores.net.</li>
  <li><strong>Por habitante</strong> e <strong>crédito face aos
  depósitos</strong>: cálculos do açores.net, com a população residente do
  INE. O crédito face aos depósitos compara os empréstimos a particulares
  residentes nos Açores com os depósitos de particulares em balcões nos
  Açores: as duas bases não são iguais, por isso é uma aproximação.</li>
  <li>Os valores do último ano podem ser revistos pelo Banco de Portugal; aqui
  fica sempre a versão mais recente.</li>
  <li>Os dados completos (as nove regiões NUTS II, todos os setores de
  atividade e indicadores das empresas) estão em
  <a href="/dados/bportugal.csv">bportugal.csv</a> e na tabela
  <code>bportugal</code> da <a href="/dados/sql/">base de
  dados</a>. São atualizados todas as semanas por
  <a href="https://github.com/fmesqg/a-ores.net-site/blob/main/bot/bportugal.py"><code>bot/bportugal.py</code></a>,
  a partir da <a href="https://bpstat.bportugal.pt/api/media/files/scripts/menu/api.html">API
  do BPstat</a>.</li>
</ul>
{% else %}
<p>Os dados ainda não foram gerados.</p>
{% endif %}

<style>
.lead { font-size: 1.15em; max-width: 40em; }
.numeros { display: grid; grid-template-columns: repeat(auto-fit, minmax(min(12em, 100%), 1fr)); gap: .9em; margin: 1em 0 .4em; }
.numero { border: 1px solid rgba(147,161,161,.6); border-radius: 8px; padding: .8em 1em .3em; background: rgba(147,161,161,.08); }
.numero p { margin-bottom: .4em; font-size: .95em; }
.numero .rotulo { font-weight: bold; margin-bottom: .2em; }
.numero .grande { font-size: 1.8em; font-weight: bold; line-height: 1.15; margin-bottom: .3em; }
.numero .grande small { font-size: .5em; font-weight: normal; }
h2[id] { scroll-margin-top: 1em; margin-top: 1.4em; }
.nota, .notas { font-size: .9em; }
.notas li { margin-bottom: .35em; }
.tabela-scroll { overflow-x: auto; margin-bottom: 1em; }
table.sper { border-collapse: collapse; font-size: .9em; min-width: 100%; }
table.sper th, table.sper td { padding: .3em .5em; border-bottom: 1px solid rgba(147,161,161,.35); text-align: left; vertical-align: top; }
table.sper thead th { font-size: .9em; vertical-align: bottom; }
table.sper th[scope="row"] { font-weight: normal; }
table.sper .n { text-align: right; white-space: nowrap; font-variant-numeric: tabular-nums; }
table.sper thead .n { white-space: normal; }
.fonte { font-size: .85em; color: #586e75; }
@media (prefers-color-scheme: dark) {
  .fonte { color: #93a1a1; }
}
</style>
