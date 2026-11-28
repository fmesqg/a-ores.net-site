---
title: Desemprego registado por concelho
layout: default
permalink: /dados/desemprego/
secao: estatisticas
description: Desempregados inscritos nos serviços públicos de emprego dos Açores, mês a mês, em cada concelho e ilha, por mil habitantes e ao lado dos beneficiários do RSI.
---
{%- assign x = site.data.desemprego -%}
{% include estatisticas-nav.html %}

# Desemprego registado por concelho

<p class="lead">As pessoas inscritas como desempregadas nos serviços públicos
de emprego dos Açores, no fim de cada mês, em cada concelho e ilha. Os
Açores têm serviços de emprego próprios, por isso as estatísticas do IEFP
por concelho param no continente; estas vêm dos resumos mensais da
<a href="https://emprego.azores.gov.pt/">Direção Regional de Qualificação
Profissional e Emprego</a>.</p>

{% if x %}
<div class="numeros">
<div class="numero">
  <p class="rotulo">Desempregados inscritos, {{ x.mes }}</p>
  <p class="grande">{{ x.regiao.total_txt }}</p>
  {% if x.regiao.homologa %}<p>{{ x.regiao.homologa }} do que em {{ x.mes_homologo }}{% if x.regiao.mensal %}; {{ x.regiao.mensal }} num mês{% endif %}.</p>{% endif %}
</div>
<div class="numero">
  <p class="rotulo">Por mil habitantes</p>
  <p class="grande">{{ x.regiao.por_mil_txt }}</p>
  <p>Nos Açores, sobre a população residente de {{ x.ano_pop }} (INE). Varia entre concelhos de {{ x.concelhos.last.por_mil_txt }} a {{ x.concelhos.first.por_mil_txt }}.</p>
</div>
<div class="numero">
  <p class="rotulo">Mulheres</p>
  <p class="grande">{{ x.regiao.mulheres }} %</p>
  <p>Dos desempregados inscritos.</p>
</div>
</div>

<nav class="indice" aria-label="Nesta página">
  <a href="#concelhos"><span>1</span> Concelhos</a>
  <a href="#ilhas"><span>2</span> Ilhas</a>
  <a href="#meses"><span>3</span> Mês a mês</a>
  <a href="#medidas"><span>4</span> Medidas e colocações</a>
  <a href="#notas"><span>5</span> Notas</a>
</nav>

<h2 id="concelhos">1. Concelhos ({{ x.mes }})</h2>
<p class="nota">Ordenados pelos desempregados por mil habitantes (cálculo do
açores.net, sobre a população residente do INE em {{ x.ano_pop }}). A variação
homóloga compara com {{ x.mes_homologo }}. Os beneficiários do rendimento
social de inserção são do INE ({{ x.ano_rsi }}), por mil habitantes em idade
ativa.</p>
<div class="tabela-scroll">
<table class="sper desemprego">
<thead><tr>
  <th scope="col">Concelho</th>
  <th scope="col" class="n">Desempregados</th>
  <th scope="col" class="n az">Por mil hab.</th>
  <th scope="col" class="n">Variação homóloga</th>
  <th scope="col" class="n">% mulheres</th>
  <th scope="col" class="n sep">RSI por mil</th>
</tr></thead>
<tbody>
{%- for c in x.concelhos %}
<tr><th scope="row">{{ c.nome }}<small class="conc">{{ c.ilha }}</small></th>
<td class="n">{{ c.total_txt }}</td>
<td class="n az">{{ c.por_mil_txt | default: "–" }}</td>
<td class="n">{{ c.homologa | default: "–" }}</td>
<td class="n">{{ c.mulheres }}</td>
<td class="n sep">{{ c.rsi | default: "–" }}</td></tr>
{%- endfor %}
<tr class="total"><th scope="row">Açores</th>
<td class="n">{{ x.regiao.total_txt }}</td>
<td class="n az">{{ x.regiao.por_mil_txt }}</td>
<td class="n">{{ x.regiao.homologa | default: "–" }}</td>
<td class="n">{{ x.regiao.mulheres }}</td>
<td class="n sep">{{ x.regiao.rsi | default: "–" }}</td></tr>
</tbody>
</table>
</div>

<h2 id="ilhas">2. Ilhas ({{ x.mes }})</h2>
<div class="tabela-scroll">
<table class="sper desemprego">
<thead><tr>
  <th scope="col">Ilha</th>
  <th scope="col" class="n">Desempregados</th>
  <th scope="col" class="n az">Por mil hab.</th>
  <th scope="col" class="n">Variação homóloga</th>
  <th scope="col" class="n">% mulheres</th>
</tr></thead>
<tbody>
{%- for c in x.ilhas %}
<tr><th scope="row">{{ c.nome }}</th>
<td class="n">{{ c.total_txt }}</td>
<td class="n az">{{ c.por_mil_txt | default: "–" }}</td>
<td class="n">{{ c.homologa | default: "–" }}</td>
<td class="n">{{ c.mulheres }}</td></tr>
{%- endfor %}
</tbody>
</table>
</div>

<h2 id="meses">3. Mês a mês</h2>
<p class="nota">Desempregados inscritos nos Açores no fim de cada mês. Os
meses em branco são resumos que o açores.net não encontrou (ver as
notas).</p>
<div class="tabela-scroll">
<table class="sper desemprego meses">
<thead><tr>
  <th scope="col">Ano</th>
  {%- for m in x.meses_nomes %}<th scope="col" class="n">{{ m }}</th>{% endfor %}
</tr></thead>
<tbody>
{%- for a in x.grelha %}
<tr><th scope="row">{{ a.ano }}</th>
{%- for v in a.meses %}<td class="n">{{ v }}</td>{% endfor %}</tr>
{%- endfor %}
</tbody>
</table>
</div>

<h2 id="medidas">4. Medidas e colocações</h2>
<p class="nota">Quem está numa medida de emprego (estágio, inserção
socioprofissional, formação) não conta como desempregado inscrito. Pessoas
nas medidas no fim de {{ x.mes }}{% if x.ofertas != "" %}; nesse mês
entraram {{ x.ofertas }} ofertas de emprego{% endif %}.</p>
<div class="tabela-scroll">
<table class="sper desemprego">
<thead><tr><th scope="col">Medida</th><th scope="col" class="n">Pessoas</th></tr></thead>
<tbody>
{%- for m in x.medidas %}
<tr><th scope="row">{{ m.nome }}</th><td class="n">{{ m.total }}</td></tr>
{%- endfor %}
</tbody>
</table>
</div>

<p class="nota">Colocações: ofertas de emprego satisfeitas com candidatos
apresentados pelos serviços de emprego, em {{ x.mes }} e nos
{{ x.meses_coloc }} meses até lá com resumo.</p>
<div class="tabela-scroll">
<table class="sper desemprego">
<thead><tr>
  <th scope="col">Ilha</th>
  <th scope="col" class="n">{{ x.mes }}</th>
  <th scope="col" class="n">{{ x.meses_coloc }} meses</th>
</tr></thead>
<tbody>
{%- for c in x.colocacoes %}
<tr{% if c.nome == "Açores" %} class="total"{% endif %}><th scope="row">{{ c.nome }}</th>
<td class="n">{{ c.mes }}</td><td class="n">{{ c.doze }}</td></tr>
{%- endfor %}
</tbody>
</table>
</div>

<h2 id="notas">5. Notas</h2>
<ul class="notas">
  <li><strong>Desemprego registado não é a taxa de desemprego.</strong> Conta
  quem se inscreveu nos serviços de emprego, não tem emprego e está
  disponível; a taxa de desemprego do
  <a href="/dados/srea/">Inquérito ao Emprego</a> vem de um inquérito às
  famílias e inclui quem não se inscreve. Os dois números não batem e não
  devem ser somados nem divididos um pelo outro.</li>
  <li><strong>Por mil habitantes.</strong> Divide pela população residente
  toda, não pela população ativa (o INE não a publica por concelho todos os
  anos): é um cálculo do açores.net para comparar concelhos de tamanhos
  diferentes, não uma taxa oficial.</li>
  <li><strong>Medidas de emprego.</strong> Estagiários e pessoas em
  programas ocupacionais saem do desemprego registado enquanto lá estão; nos
  Açores são milhares (o quadro da secção 4), quase tantos como os
  inscritos. Uma descida do desemprego registado pode ser uma subida das
  medidas.</li>
  <li><strong>Graciosa e São Jorge desde janeiro de 2026.</strong> Nos
  resumos de 2026 o quadro das ilhas não bate com o dos concelhos destas
  duas ilhas (em março, 153 desempregados na Graciosa, cujo único concelho
  tem 46), embora os dois somem o mesmo total. Aqui os números das ilhas são
  a soma dos seus concelhos, mas nenhum dos quadros segue o de 2025: a
  Calheta passa de cerca de 35 desempregados para cerca de 100 de dezembro
  para janeiro. Use estes números com cuidado até a fonte os corrigir. O
  açores.net verifica que homens e mulheres somam o total e que os concelhos
  somam a região, mas não consegue saber qual dos quadros está certo.</li>
  <li><strong>Meses em falta.</strong> Os sites do Governo Regional só
  deixam descarregar os ficheiros, não as páginas que os listam; os resumos
  foram encontrados pelos motores de busca e os novos são procurados pelo
  nome habitual. Desde {{ x.primeiro }} há {{ x.n_meses }} meses.</li>
  <li><strong>Atualização.</strong> Os resumos saem um a dois meses depois do
  mês a que se referem. São procurados uma vez por semana por
  <a href="https://github.com/fmesqg/a-ores.net-site/blob/main/bot/desemprego.py"><code>bot/desemprego.py</code></a>.
  Os números estão em <a href="/dados/desemprego.csv">desemprego.csv</a> e na
  tabela <code>desemprego</code> de <a href="/dados/sql/">estatisticas.db</a>.</li>
</ul>
{% else %}
<p>Os dados ainda não foram gerados.</p>
{% endif %}

<style>
.lead { font-size: 1.15em; max-width: 40em; }
h2[id] { scroll-margin-top: 1em; margin-top: 1.4em; }
table.desemprego th[scope="row"] { font-weight: normal; }
table.desemprego th[scope="row"] small.conc { display: block; color: var(--s01); font-size: .85em; }
table.desemprego .az { font-weight: bold; background: rgba(37,125,224,.09); }
table.desemprego .sep { border-left: 1px solid var(--s1); }
table.desemprego tr.total th, table.desemprego tr.total td { font-weight: bold; }
table.meses { font-size: .88em; }
</style>
