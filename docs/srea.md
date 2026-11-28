---
title: Indicadores do SREA
layout: default
permalink: /dados/srea/
secao: estatisticas
description: Preços, emprego e salários, atividade económica, habitação, turismo, PIB por ilha, os Açores face ao país e as contas da Região, com os números mais recentes do Serviço Regional de Estatística dos Açores (SREA), explicados.
---
{%- assign s = site.data.resumo.srea -%}
{%- assign f = site.data.fontes -%}
{% include estatisticas-nav.html %}

# Indicadores do SREA

<p class="lead">Como estão os preços, o emprego, a economia e o turismo nos
Açores: os números mais recentes do <a href="{{ f.srea.url }}">Serviço
Regional de Estatística dos Açores (SREA)</a>, a estatística oficial da
Região, explicados sem jargão. Para os números por concelho e freguesia,
veja os <a href="/dados/ine/">indicadores do INE</a>; para quem faz a
economia (setor público e privado), a <a href="/economia/">Economia</a>. A página atualiza-se todas as semanas.</p>

<nav class="indice" aria-label="Nesta página">
  <a href="#precos"><span>1</span> Preços</a>
  <a href="#emprego"><span>2</span> Emprego e salários</a>
  <a href="#atividade"><span>3</span> Atividade e consumo</a>
  <a href="#habitacao"><span>4</span> Habitação</a>
  <a href="#turismo"><span>5</span> Turismo por ilha</a>
  <a href="#ilhas"><span>6</span> O que cada ilha produz</a>
  <a href="#pais"><span>7</span> Os Açores e o país</a>
  <a href="#contas"><span>8</span> Contas da Região</a>
  <a href="#palavras"><span>9</span> Palavras e dados</a>
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

<h2 id="emprego">2. Emprego e salários</h2>
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

{% if s.remuneracoes %}
<p>Quem trabalha por conta de outrem nos Açores recebia em média
<strong>{{ s.remuneracoes.valor_t }} € brutos por mês</strong> de remuneração
regular nos três meses até {{ s.remuneracoes.periodo }}{% if s.remuneracoes.real %}:
descontada a inflação, {% if s.remuneracoes.real < 0 %}menos{% else %}mais{% endif %}
{{ s.remuneracoes.real | abs | replace: ".", "," }}% do que um ano antes{% endif %}.
São cerca de {{ s.remuneracoes.trabalhadores_t }} trabalhadores com descontos
para a Segurança Social ou a Caixa Geral de Aposentações.</p>
{% endif %}
<figure class="grafico" data-g="remuneracoes">
  <figcaption>Remuneração bruta mensal média por trabalhador (€)</figcaption>
  <div class="g-topo"><div class="g-legenda"></div><div class="g-vista" role="group" aria-label="O que mostrar"></div></div>
  <div class="g-area"><svg role="img" tabindex="0"></svg><div class="g-tip" hidden></div></div>
  <details class="g-tabela"><summary>Ver os números</summary><div></div></details>
  <p class="nota">Média dos três meses terminados em cada mês. A remuneração
  base é o salário do contrato; a regular junta-lhe o que se recebe todos os
  meses (subsídio de refeição, diuturnidades…); a total inclui ainda os
  subsídios de férias e de Natal, que a fazem subir em junho, julho e
  dezembro. Só conta quem trabalha por conta de outrem.</p>
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

<figure class="grafico" data-g="pagamentos">
  <figcaption>Pagamentos com cartão: valor por mês (€)</figcaption>
  <div class="g-topo">
    <label class="g-escolha">Concelho <select class="g-concelho"></select></label>
    <div class="g-legenda"></div>
  </div>
  <div class="g-area"><svg role="img" tabindex="0"></svg><div class="g-tip" hidden></div></div>
  <details class="g-tabela"><summary>Ver os números</summary><div></div></details>
  <p class="nota">Compras nos terminais de pagamento (TPA) e levantamentos nas
  caixas automáticas (CA) da rede SIBS, no concelho onde está o terminal.
  As compras com cartões estrangeiros são uma parte das compras em TPA e
  mostram o peso do turismo.</p>
  <p class="fonte"></p>
</figure>
<h2 id="habitacao">4. Habitação</h2>
<div class="cartoes">
{% if s.avaliacao %}
<section class="cartao">
  <h3>Avaliação das casas</h3>
  <p class="grande">{{ s.avaliacao.valor_t }} €/m²<small> em {{ s.avaliacao.periodo }}</small></p>
  <p>Valor mediano por metro quadrado das casas avaliadas pelos bancos para
  crédito à habitação{% if s.avaliacao.var %}, {% if s.avaliacao.var < 0 %}menos{% else %}mais{% endif %}
  {{ s.avaliacao.var | abs | replace: ".", "," }}% do que um ano antes{% endif %}.</p>
</section>
{% endif %}
{% if s.transacoes %}
<section class="cartao">
  <h3>Casas vendidas</h3>
  <p class="grande">{{ s.transacoes.valor_t }}<small> no {{ s.transacoes.periodo }}</small></p>
  <p>Alojamentos familiares vendidos nos Açores{% if s.transacoes.var %},
  {% if s.transacoes.var < 0 %}menos{% else %}mais{% endif %}
  {{ s.transacoes.var | abs | replace: ".", "," }}% do que no mesmo trimestre do ano anterior{% endif %}.</p>
</section>
{% endif %}
{% if s.emprestimos %}
<section class="cartao">
  <h3>Crédito à habitação</h3>
  <p class="grande">{{ s.emprestimos.valor_t }} M€<small> em {{ s.emprestimos.periodo }}</small></p>
  <p>O que as famílias dos Açores devem aos bancos por compra de casa{% if s.emprestimos.var %},
  {% if s.emprestimos.var < 0 %}menos{% else %}mais{% endif %}
  {{ s.emprestimos.var | abs | replace: ".", "," }}% do que um ano antes{% endif %}.</p>
</section>
{% endif %}
</div>
<figure class="grafico" data-g="avaliacao">
  <figcaption>Valor mediano da avaliação bancária da habitação (€ por m²)</figcaption>
  <div class="g-topo">
    <label class="g-escolha">Concelho <select class="g-concelho"></select></label>
    <div class="g-legenda"></div>
  </div>
  <div class="g-area"><svg role="img" tabindex="0"></svg><div class="g-tip" hidden></div></div>
  <details class="g-tabela"><summary>Ver os números</summary><div></div></details>
  <p class="nota">Só as casas avaliadas para um pedido de crédito, não todas as
  vendas. Nos concelhos com poucas avaliações o INE não publica o valor: só
  aparecem os que têm meses com dados.</p>
  <p class="fonte"></p>
</figure>
<figure class="grafico" data-g="transacoes">
  <figcaption>Casas vendidas nos Açores, por trimestre</figcaption>
  <div class="g-topo"><div class="g-legenda"></div><div class="g-vista" role="group" aria-label="O que mostrar"></div></div>
  <div class="g-area"><svg role="img" tabindex="0"></svg><div class="g-tip" hidden></div></div>
  <details class="g-tabela"><summary>Ver os números</summary><div></div></details>
  <p class="nota">Alojamentos familiares (casas e apartamentos) vendidos, novos
  ou já usados, e o valor das vendas (INE).</p>
  <p class="fonte"></p>
</figure>
<figure class="grafico" data-g="emprestimos">
  <figcaption>Empréstimos dos bancos a famílias e empresas dos Açores (M€, no fim de cada mês)</figcaption>
  <div class="g-topo"><div class="g-legenda"></div><div class="g-vista" role="group" aria-label="O que mostrar"></div></div>
  <div class="g-area"><svg role="img" tabindex="0"></svg><div class="g-tip" hidden></div></div>
  <details class="g-tabela"><summary>Ver os números</summary><div></div></details>
  <p class="nota">O que está por pagar, não o que se pediu nesse mês (Banco de
  Portugal). Os empréstimos vencidos são as prestações em atraso, em % do
  total emprestado.</p>
  <p class="fonte"></p>
</figure>
<p class="ir">Rendas, concelho a concelho:
<a href="/dados/ine/#ind=0014698">valor mediano das rendas (INE) →</a></p>

<h2 id="turismo">5. Turismo por ilha</h2>
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

<h2 id="ilhas">6. O que cada ilha produz</h2>
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

<h2 id="pais">7. Os Açores e o país</h2>
{% if s.creg %}
<div class="cartoes">
{% if s.creg.ppc %}<section class="cartao">
  <h3>Face à União Europeia</h3>
  <p class="grande">{{ s.creg.ppc_t }}<small> (UE = 100), {{ s.creg.ppc_ano }}</small></p>
  <p>PIB por habitante dos Açores, descontadas as diferenças de preços entre
  países (paridades de poder de compra). É o número que decide os fundos
  europeus: abaixo de 75, a Região conta como “menos desenvolvida”.</p>
</section>{% endif %}
{% if s.creg.pib_pt %}<section class="cartao">
  <h3>PIB face ao país</h3>
  <p class="grande">{{ s.creg.pib_pt_t }}<small> (Portugal = 100), {{ s.creg.pib_pt_ano }}</small></p>
  <p>O que se produz por habitante nos Açores, em % da média nacional.</p>
</section>{% endif %}
{% if s.creg.rdb_pt %}<section class="cartao">
  <h3>Rendimento das famílias</h3>
  <p class="grande">{{ s.creg.rdb_pt_t }}<small> (Portugal = 100), {{ s.creg.rdb_pt_ano }}</small></p>
  <p>O rendimento disponível das famílias por habitante (salários, lucros,
  pensões e apoios, depois de impostos), em % da média nacional. Fica mais
  perto da média nacional do que o PIB por habitante.</p>
</section>{% endif %}
</div>
{% endif %}
<figure class="grafico" data-g="creg">
  <figcaption>Contas regionais: os Açores, a Madeira e o país, desde 1995</figcaption>
  <div class="g-topo">
    <label class="g-escolha">Indicador <select class="g-indicador"></select></label>
    <div class="g-legenda"></div>
  </div>
  <div class="g-area"><svg role="img" tabindex="0"></svg><div class="g-tip" hidden></div></div>
  <details class="g-tabela"><summary>Ver os números</summary><div></div></details>
  <p class="nota">Contas regionais do INE (base 2021). Os rendimentos das
  famílias por região só existem desde 2021. O último ano é provisório. Os
  valores em milhões de euros e em milhares de pessoas mostram só os Açores;
  as outras regiões estão em <a href="/dados/srea.csv">srea.csv</a>.</p>
  <p class="fonte"></p>
</figure>

<h2 id="contas">8. Contas da Região</h2>
{% if s.apr %}
<p>Em {{ s.apr.ano }}{% if s.apr.provisorio %} (valores provisórios){% endif %}, as
administrações públicas da Região (Governo Regional, institutos, hospitais e
empresas públicas que contam como Estado) gastaram mais
{{ s.apr.saldo | abs }} milhões de euros do que receberam, e deviam
{{ s.apr.divida_t }} milhões. São as contas nacionais (SEC 2010), as que
Bruxelas usa para o défice e a dívida: não coincidem com a execução
orçamental, que conta só o que entra e sai de caixa.
<a href="/financas/">Execução orçamental e Tribunal de Contas →</a></p>
{% endif %}
<figure class="grafico" data-g="apr">
  <figcaption>Receitas e despesas das administrações públicas regionais (M€)</figcaption>
  <div class="g-apr tabela-scroll"></div>
  <p class="fonte"></p>
</figure>

<h2 id="palavras">9. Palavras e dados</h2>
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
  <dt>Paridades de poder de compra (PPC)</dt>
  <dd>Uma conversão que desconta as diferenças de preços entre países, para
  que 100 € comprem o mesmo em todo o lado.</dd>
  <dt>Rendimento disponível das famílias</dt>
  <dd>O que as famílias recebem (salários, rendimentos de empresas e
  propriedades, pensões e apoios sociais) depois de pagar impostos e
  contribuições.</dd>
  <dt>Valor mediano</dt>
  <dd>O valor do meio: metade das casas avaliadas vale menos, metade vale
  mais. Não é puxado por umas poucas casas muito caras, como a média.</dd>
</dl>

<p><strong>Descarregar:</strong> todas as séries num só ficheiro,
<a href="/dados/srea.csv">srea.csv</a> (um valor por linha, com a ligação
para o ficheiro do SREA de onde veio). As séries vêm das páginas do SREA de
<a href="{{ f.srea_precos.url }}">preços</a>,
<a href="{{ f.srea_conjuntura.url }}">conjuntura</a>,
<a href="{{ f.srea_emprego.url }}">mercado de trabalho</a>,
<a href="{{ f.srea_turismo.url }}">turismo</a>,
<a href="{{ f.srea_habitacao.url }}">construção e habitação</a>,
<a href="{{ f.srea_financeira.url }}">atividade financeira</a>,
<a href="{{ f.srea_contas.url }}">contas regionais</a> e
<a href="{{ f.srea_populacao.url }}">população</a>, recolhidas todas as
semanas.</p>

<style>
.lead { font-size: 1.15em; max-width: 40em; }
.indice { display: grid; grid-template-columns: repeat(auto-fit, minmax(min(12em, 100%), 1fr)); gap: .4em; margin: 1em 0 1.5em; }
h2[id] { scroll-margin-top: 1em; margin-top: 1.4em; }
p.grande { font-size: 1.9em; font-weight: bold; line-height: 1.15; margin-bottom: .3em; }
.grande small { font-size: .5em; font-weight: normal; }
.aviso { border-left: 4px solid #b58900; padding: .2em 0 .2em .8em; font-size: .95em; max-width: 42em; }
.duas { display: grid; grid-template-columns: repeat(auto-fit, minmax(min(18em, 100%), 1fr)); gap: 0 2em; }
.cartoes { display: grid; grid-template-columns: repeat(auto-fit, minmax(min(16em, 100%), 1fr)); gap: .9em; margin: 1em 0 1.2em; }
.cartao h3 { font-size: 1.05em; margin: 0 0 .4em; }
.cartao .grande { font-size: 1.7em; font-weight: bold; line-height: 1.15; margin-bottom: .3em; }
.fonte { font-size: .85em; color: var(--s01); }
.ir { font-size: .95em; }
.barras { margin: 1em 0 .6em; max-width: 42em; }
.barras figcaption, .grafico figcaption { font-weight: bold; margin-bottom: .5em; }
.barra { display: grid; grid-template-columns: minmax(7em, 10em) 1fr auto; align-items: center; gap: .6em; margin: .3em 0; font-size: .95em; }
.barra .trilho { height: .8em; background: rgba(147,161,161,.15); border-radius: 4px; overflow: hidden; }
.barra .valor { display: block; height: 100%; background: #268bd2; border-radius: 0 4px 4px 0; min-width: 2px; }
.barra .num { font-variant-numeric: tabular-nums; text-align: right; white-space: nowrap; min-width: 9em; }
.barra .num small { color: var(--s01); margin-left: .4em; display: inline-block; min-width: 3.2em; }
.grafico { margin: 1em 0 1.4em; max-width: 46em; }
.g-legenda { display: flex; flex-wrap: wrap; gap: .3em .9em; font-size: .85em; color: var(--s01); flex: 1 1 12em; }
.g-legenda span { display: inline-flex; align-items: center; gap: .35em; }
.g-legenda i, .g-tip i { display: inline-block; width: 14px; border-top: 2px solid var(--c); border-radius: 2px; }
.g-escolha { font-size: .9em; }
.g-escolha select { font: inherit; padding: .15em .3em; max-width: 14em; }
.g-escolha .g-indicador { max-width: min(30em, 100%); }
.g-vista { display: inline-flex; border: 1px solid var(--s1); border-radius: 6px; overflow: hidden; }
.g-vista:empty { display: none; }
.g-vista button { font: inherit; font-size: .85em; padding: .25em .7em; border: 0; background: transparent; color: var(--s01); cursor: pointer; }
.g-vista button + button { border-left: 1px solid var(--s1); }
.g-vista button[aria-pressed="true"] { background: var(--s01); color: var(--sobre-acento); }
.grafico svg { display: block; width: 100%; overflow: visible; touch-action: pan-y; }
.grafico svg:focus-visible, .g-vista button:focus-visible { outline: 3px solid #268bd2; outline-offset: 1px; }
.grafico svg text { font-size: 12px; fill: var(--s01); font-variant-numeric: tabular-nums; }
.grafico svg .grade { stroke: var(--s2); stroke-width: 1; }
.grafico svg .eixo { stroke: var(--s1); stroke-width: 1; }
.grafico svg .cruz { stroke: var(--s1); stroke-width: 1; }
.grafico svg .rotulo { fill: var(--s02); }
.g-tip { position: absolute; pointer-events: none; background: #fffdf5; border: 1px solid var(--s1); border-radius: 6px; padding: .4em .6em; font-size: .85em; box-shadow: 0 2px 6px rgba(0,0,0,.12); min-width: 9em; z-index: 3; }
.g-tabela { margin-top: .4em; font-size: .9em; }
.g-tabela summary { cursor: pointer; color: var(--s01); }
.g-tabela div { max-height: 22em; overflow: auto; }
.g-tabela table { border-collapse: collapse; font-variant-numeric: tabular-nums; }
.g-apr { font-size: .9em; margin-bottom: .4em; }
.g-apr td { text-align: right; font-variant-numeric: tabular-nums; }
.g-apr tbody th { text-align: left; font-weight: normal; white-space: nowrap; }
.g-apr tr.forte th, .g-apr tr.forte td { font-weight: bold; }
.grafico .nota { font-size: .85em; max-width: 44em; }
.g-tabela th, .g-tabela td { padding: .15em .6em; text-align: right; border-bottom: 1px solid rgba(147,161,161,.3); }
.g-tabela th:first-child, .g-tabela td:first-child { text-align: left; }
.palavras dt { font-weight: bold; margin-top: .7em; }
.palavras dd { margin: .15em 0 0 0; max-width: 42em; }
@media (max-width: 30em) { .barra { grid-template-columns: 1fr auto; } .barra .trilho { grid-column: 1 / -1; grid-row: 2; } }
@media (prefers-color-scheme: dark) {
  .fonte, .barra .num small, .g-legenda, .g-tabela summary { color: var(--s01); }
  .grafico svg text { fill: var(--s01); }
  .grafico svg .rotulo { fill: var(--s02); }
  .grafico svg .grade { stroke: rgba(147,161,161,.22); }
  .g-tip { background: var(--s2); }
  .g-tip b { color: var(--s02); }
  .g-tip .p, .g-tip span { color: var(--s01); }
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
      var a = h("a", "SREA, " + decodeURIComponent(s.ficheiro.replace(/\/$/, "").split("/").pop()), p); a.href = s.ficheiro;
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

  function pagamentos() {
    var fig = document.querySelector('[data-g="pagamentos"]');
    var rows = find({ serie: "pagamentos", indicador: "Valor" });
    if (!rows.length) return;
    var sel = fig.querySelector(".g-concelho");
    var locais = ["Açores"].concat(rows.map(function (s) { return s.local; }).filter(function (x, i, a) { return x !== "Açores" && a.indexOf(x) === i; }).sort(function (x, y) { return x.localeCompare(y, "pt"); }));
    locais.forEach(function (l) { var o = h("option", l, sel); o.value = l; });
    var NOMES = [["Compras em TPA", "Compras em TPA", C1], ["Compras em TPA com cartões estrangeiros", "Das quais, com cartões estrangeiros", C2], ["Levantamentos em CA", "Levantamentos em CA", "#859900"]];
    var redraw = function () {
      var keys = {}, series = [];
      NOMES.forEach(function (n) {
        var s = rows.filter(function (r) { return r.local === sel.value && r.rubrica === n[0]; })[0];
        if (!s) return;
        s.p.forEach(function (p) { keys[p[0]] = 1; });
        series.push({ nome: n[1], c: n[2], v: asMap(s) });
      });
      draw(fig, Object.keys(keys).sort(), series, { big: true, zero: true });
    };
    sel.onchange = redraw;
    redraw(); source(fig, rows.filter(function (s) { return s.local === "Açores"; }).slice(0, 1));
    return redraw;
  }
  function series(q, nome, c) { var s = one(q); return s ? { nome: nome, c: c, v: asMap(s), s: s } : null; }
  function keysOf(list) {
    var k = {}; list.forEach(function (x) { x.s.p.forEach(function (p) { k[p[0]] = 1; }); });
    return Object.keys(k).sort();
  }
  // a chart whose series are chosen with buttons: views = [[label, function () -> {series, opt}]]
  function withViews(fig, views) {
    var cur = 0, redraw = function (i) {
      if (i != null) cur = i;
      var v = views[cur][1](), list = v.series.filter(Boolean);
      if (!list.length) return;
      draw(fig, v.keys || keysOf(list), list, v.opt);
      source(fig, list.map(function (x) { return x.s; }).slice(0, 1));
    };
    if (views.length > 1) rangeButtons(fig, views.map(function (v, i) { return [i, v[0]]; }), 0, redraw);
    redraw();
    return function () { redraw(); };
  }
  function remuneracoes() {
    var fig = document.querySelector('[data-g="remuneracoes"]'), R = "remuneracoes";
    if (!one({ serie: R })) return;
    return withViews(fig, [
      ["Salário", function () { return { series: [
        series({ serie: R, indicador: "Remuneração bruta regular média" }, "Regular", C1),
        series({ serie: R, indicador: "Remuneração bruta base média" }, "Base", C2),
        series({ serie: R, indicador: "Remuneração bruta total média" }, "Total", "#859900")], opt: { unit: " €" } }; }],
      ["Acima da inflação", function () { return { series: [
        series({ serie: R, indicador: "Remuneração bruta regular média: variação homóloga real" }, "Regular", C1),
        series({ serie: R, indicador: "Remuneração bruta base média: variação homóloga real" }, "Base", C2)], opt: { unit: "%" } }; }],
      ["Trabalhadores", function () { return { series: [
        series({ serie: R, indicador: "Número de trabalhadores" }, "Trabalhadores (milhares)", C1)], opt: { unit: " mil" } }; }]
    ]);
  }
  function avaliacao() {
    var fig = document.querySelector('[data-g="avaliacao"]');
    var rows = find({ serie: "avaliacao" });
    if (!rows.length) return;
    var sel = fig.querySelector(".g-concelho");
    var locais = ["Açores"].concat(rows.map(function (s) { return s.local; }).filter(function (x, i, a) { return x !== "Açores" && a.indexOf(x) === i; }).sort(function (x, y) { return x.localeCompare(y, "pt"); }));
    locais.forEach(function (l) { var o = h("option", l, sel); o.value = l; });
    var redraw = function () {
      var l = sel.value, list = [
        series({ serie: "avaliacao", rubrica: "Habitação", local: l }, l === "Açores" ? "Todas as casas" : l, C1)];
      if (l === "Açores") list.push(series({ serie: "avaliacao", rubrica: "Apartamentos", local: l }, "Apartamentos", C2), series({ serie: "avaliacao", rubrica: "Moradias", local: l }, "Moradias", "#859900"));
      else list.push(series({ serie: "avaliacao", rubrica: "Habitação", local: "Açores" }, "Açores", C2));
      list = list.filter(Boolean);
      draw(fig, keysOf(list), list, { unit: " €/m²" });
    };
    sel.onchange = redraw;
    redraw(); source(fig, rows.slice(0, 1));
    return redraw;
  }
  function transacoes() {
    var fig = document.querySelector('[data-g="transacoes"]'), T = "transacoes";
    if (!one({ serie: T })) return;
    function three(ind) { return [
      series({ serie: T, indicador: ind, rubrica: "Total" }, "Todas", C1),
      series({ serie: T, indicador: ind, rubrica: "Existentes" }, "Usadas", C2),
      series({ serie: T, indicador: ind, rubrica: "Novos" }, "Novas", "#859900")]; }
    return withViews(fig, [
      ["Número", function () { return { series: three("Número"), opt: { zero: true } }; }],
      ["Valor (€)", function () { return { series: three("Valor"), opt: { zero: true, big: true, unit: " €" } }; }]
    ]);
  }
  function emprestimos() {
    var fig = document.querySelector('[data-g="emprestimos"]'), E = "emprestimos";
    if (!one({ serie: E })) return;
    function three(ind) { return [
      series({ serie: E, indicador: ind, rubrica: "Particulares - Habitação" }, "Famílias: habitação", C1),
      series({ serie: E, indicador: ind, rubrica: "Particulares - Consumo e outros" }, "Famílias: consumo e outros", C2),
      series({ serie: E, indicador: ind, rubrica: "Empresas não financeiras" }, "Empresas", "#859900")]; }
    return withViews(fig, [
      ["Valor em dívida", function () { return { series: three("Valor em fim do período"), opt: { zero: true, unit: " M€" } }; }],
      ["Em atraso (%)", function () { return { series: three("Rácio de empréstimos vencidos"), opt: { zero: true, unit: "%" } }; }]
    ]);
  }
  var CREG = [
    ["PIBpc PPC (UE27=100)", "PIB por habitante em paridades de poder de compra (UE = 100)", ""],
    ["Produto interno bruto por habitante (PT=100)", "PIB por habitante (Portugal = 100)", ""],
    ["Rendimento disponível bruto das famílias por habitante (PT=100)", "Rendimento disponível das famílias por habitante (Portugal = 100)", ""],
    ["Rendimento disponível bruto das famílias por habitante", "Rendimento disponível das famílias por habitante (€)", " €"],
    ["Produto interno bruto por habitante", "PIB por habitante (€)", " €"],
    ["Evolução real PIBVol", "Crescimento real do PIB (%)", "%"],
    ["Produtividade aparente do trabalho (PT=100)", "Produtividade do trabalho (Portugal = 100)", ""],
    ["Emprego - indivíduos totais", "Pessoas empregadas nos Açores (milhares)", " mil", 1],
    ["Produto interno bruto - preços correntes", "PIB dos Açores (milhões de euros)", " M€", 1],
    ["Remunerações dos empregados", "Salários pagos nos Açores (milhões de euros)", " M€", 1],
    ["Formação bruta de capital fixo", "Investimento nos Açores (milhões de euros)", " M€", 1]
  ];
  function creg() {
    var fig = document.querySelector('[data-g="creg"]');
    if (!one({ serie: "creg" })) return;
    var sel = fig.querySelector(".g-indicador");
    CREG.forEach(function (c, i) { if (one({ serie: "creg", indicador: c[0] })) { var o = h("option", c[1], sel); o.value = i; } });
    var redraw = function () {
      var c = CREG[+sel.value], q = function (l) { return { serie: "creg", indicador: c[0], local: l }; };
      var list = [series(q("Açores"), "Açores", C1)];
      if (!c[3]) list.push(series(q("Madeira"), "Madeira", C2), series(q("Portugal"), "Portugal", "#859900"));
      list = list.filter(Boolean);
      var nota = {}; list[0].s.p.forEach(function (p) { if (p[2]) nota[p[0]] = p[2]; }); list[0].nota = nota;
      draw(fig, keysOf(list), list, { unit: c[2], dots: keysOf(list).length < 8 });
      source(fig, [list[0].s]);
    };
    sel.onchange = redraw;
    redraw();
    return redraw;
  }
  var APR = [["Receitas totais", 0], ["Receita corrente", 1], ["Impostos sobre o rendimento e património", 2], ["Impostos sobre a produção e importação", 2], ["Contribuições sociais", 2], ["Vendas", 2], ["Outras receitas correntes", 2], ["Receitas de capital", 1],
    ["Despesas totais", 0], ["Despesa corrente", 1], ["Prestações sociais", 2], ["Despesas com pessoal", 2], ["Juros", 2], ["Consumo intermédio", 2], ["Subsídios", 2], ["Outra despesa corrente", 2], ["Despesa de capital", 1], ["Investimento", 2], ["Outra despesa de capital", 2],
    ["Saldo total", 0], ["Dívida bruta consolidada", 0]];
  function apr() {
    var fig = document.querySelector('[data-g="apr"]'), rows = find({ serie: "apr" });
    if (!rows.length) return;
    var anos = {}, prov = {};
    rows.forEach(function (s) { s.p.forEach(function (p) { anos[p[0]] = 1; if (p[2]) prov[p[0]] = 1; }); });
    anos = Object.keys(anos).sort().reverse();
    var t = h("table", null, fig.querySelector(".g-apr")); t.className = "sper";
    var tr = h("tr", null, h("thead", null, t)); h("th", "", tr);
    anos.forEach(function (a) { h("th", a + (prov[a] ? "*" : ""), tr); });
    var body = h("tbody", null, t);
    APR.forEach(function (r) {
      var s = rows.filter(function (x) { return x.rubrica === r[0]; })[0]; if (!s) return;
      var v = asMap(s), row = h("tr", null, body), th = h("th", r[0], row);
      th.style.paddingLeft = (0.3 + r[1] * 1.1) + "em"; if (!r[1]) row.className = "forte";
      anos.forEach(function (a) { h("td", v[a] == null ? "–" : n1.format(v[a]).replace("-", "−"), row); });
    });
    if (Object.keys(prov).length) h("p", "* Provisório.", fig.querySelector(".g-apr")).className = "nota";
    source(fig, rows.slice(0, 1));
  }

  fetch("/dados/srea.json?v=" + BUILD).then(function (r) { return r.json(); }).then(function (d) {
    DATA = d;
    apr();
    var redraws = [ipc(), desemprego(), remuneracoes(), atividade(), pagamentos(), avaliacao(), transacoes(), emprestimos(), turismo(), creg()].filter(Boolean);
    var w = 0;
    window.addEventListener("resize", function () {
      clearTimeout(w); w = setTimeout(function () { redraws.forEach(function (f) { f(); }); }, 200);
    });
  }).catch(function () {
    document.querySelectorAll(".grafico .fonte").forEach(function (p) { p.textContent = "Não foi possível carregar os dados. Estão em srea.csv."; });
  });
})();
</script>
