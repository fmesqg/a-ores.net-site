---
title: Açores 101
layout: default
permalink: /acores-101/
description: Os Açores explicados a quem chega pela primeira vez aos dados - quem decide, de onde vem e para onde vai o dinheiro, como se vive, com ligação às fontes oficiais.
---
{%- assign r = site.data.resumo -%}
{%- assign f = site.data.fontes -%}
{%- assign pop = r.ine["0012918"] -%}
{%- assign env = r.ine["0012909"] -%}
{%- assign med = r.ine["0012757"] -%}
{%- assign ganho = r.ine["0012656"] -%}
{%- assign rsi = r.ine["0013420"] -%}
{%- assign renda = r.ine["0014698"] -%}
{%- assign dorm = r.ine["0013210"] -%}
{%- assign b = r.beo -%}
{%- assign sr = r.srea -%}

<p class="lead">Nunca olhou para números sobre os Açores? Comece aqui. Em dez
minutos, sem jargão: quem vive cá, quem decide o quê, de onde vem e para onde
vai o dinheiro da Região, e como se vive. Cada número tem ao lado a fonte
oficial, e uma ligação para o explorar a fundo.</p>

<nav class="indice" aria-label="Nesta página">
  <a href="#ilhas"><span>1</span> Nove ilhas, quem cá vive</a>
  <a href="#quem-decide"><span>2</span> Quem decide o quê</a>
  <a href="#dinheiro"><span>3</span> O dinheiro da Região</a>
  <a href="#viver"><span>4</span> Como se vive</a>
  <a href="#palavras"><span>5</span> Seis palavras para ler os números</a>
  <a href="#comecar"><span>6</span> Por onde começar</a>
</nav>

<h2 id="ilhas">1. Nove ilhas, quem cá vive</h2>

{% if pop %}
<p>Os Açores são nove ilhas habitadas no meio do Atlântico, onde vivem
<strong>{{ pop.acores_t }} pessoas</strong> ({{ pop.periodo }}), cerca de
{{ pop.acores | times: 100.0 | divided_by: pop.pt | round: 1 | replace: ".", "," }}%
da população do país. A população está muito concentrada: São Miguel tem
{{ pop.ilhas[0].pct }}% dos habitantes e, com a Terceira, quase oito em cada
dez. No Corvo vivem {{ pop.ilhas.last.valor_t }} pessoas.</p>

<figure class="barras" aria-labelledby="cap-ilhas">
  <figcaption id="cap-ilhas">Habitantes por ilha, {{ pop.periodo }}</figcaption>
  {%- assign maxi = pop.ilhas[0].valor %}
  {%- for i in pop.ilhas %}
  <div class="barra" title="{{ i.ilha }}: {{ i.valor_t }} habitantes ({{ i.pct }}%)">
    <span class="nome">{{ i.ilha }}</span>
    <span class="trilho"><span class="valor" style="width: {{ i.valor | times: 100.0 | divided_by: maxi }}%"></span></span>
    <span class="num">{{ i.valor_t }}</span>
  </div>
  {%- endfor %}
</figure>
<p class="fonte">Fonte: <a href="{{ pop.url }}">INE, população residente</a>
(estimativa anual, soma dos concelhos de cada ilha).
<a href="/dados/ine/#ind=0012918">Ver por concelho e por ano →</a></p>
{% endif %}

<p>O território divide-se em <strong>19 concelhos</strong> (os municípios, cada
um com a sua câmara municipal) e <strong>156 freguesias</strong>.
São Miguel tem seis concelhos; o Corvo, só um.{% if env %} A população é mais
jovem do que a do país: há {{ env.acores_t }} pessoas com 65 ou mais anos por
cada 100 com menos de 15, contra {{ env.pt_t }} no país
(<a href="{{ env.url }}">INE, índice de envelhecimento, {{ env.periodo }}</a>).{% endif %}</p>

{%- assign ph = r.srea.pib_hab %}
{% if ph %}
<h3 id="produz">O que cada ilha produz</h3>

<p>Em {{ ph.ano }}, os Açores produziram cerca de
<strong>{{ ph.total_mm | replace: ".", "," }} mil milhões de euros</strong>: é o
produto interno bruto (PIB), o valor de tudo o que se produz num ano.
Por habitante, dá <strong>{{ ph.acores_t }} €</strong>. São Miguel produz
mais de metade do total, mas por habitante as ilhas ficam mais perto umas das
outras do que a população faria pensar.</p>

<figure class="barras" aria-labelledby="cap-pib">
  <figcaption id="cap-pib">PIB por habitante, por ilha, {{ ph.ano }}{% if ph.provisorio %} (provisório){% endif %}</figcaption>
  {%- for i in ph.por_ilha %}
  <div class="barra" title="{{ i.ilha }}: {{ i.valor_t }} € por habitante">
    <span class="nome">{{ i.ilha }}</span>
    <span class="trilho"><span class="valor" style="width: {{ i.pct }}%"></span></span>
    <span class="num">{{ i.valor_t }} €</span>
  </div>
  {%- endfor %}
</figure>
<p>O PIB por habitante não é o que cada pessoa ganha: conta também os lucros
das empresas e o que se produz para fora, e uma ilha pequena com um aeroporto
ou um porto grande produz muito por habitante. Para o rendimento das
famílias, veja <a href="#viver">Como se vive</a>.</p>
<p class="fonte">Fonte: <a href="{{ ph.url }}">SREA, PIB por ilha</a>, dividido
pela população residente estimada pelo SREA no mesmo ano (conta do açores.net).
<a href="/dados/srea/#ilhas">Mais sobre a economia de cada ilha →</a></p>
{% endif %}

<h2 id="quem-decide">2. Quem decide o quê</h2>

<p>Os Açores são uma <strong>região autónoma</strong>: desde 1976 têm
parlamento e governo próprios, que decidem sobre a maior parte do que se passa
nas ilhas, da saúde e da escola aos transportes e à economia. As regras estão
no <a href="{{ f.estatuto.url }}">Estatuto Político-Administrativo</a>.</p>

<div class="cartoes">
<section class="cartao">
  <h3>Assembleia Legislativa</h3>
  <p>O parlamento regional, na Horta (Faial). São <strong>57 deputados</strong>,
  eleitos de quatro em quatro anos: cada ilha elege os seus e mais cinco saem
  de um círculo regional de compensação. Aprova as leis regionais e o
  orçamento da Região e fiscaliza o Governo, por exemplo com perguntas
  escritas.</p>
  <p class="ir"><a href="/dados/#fonte=alra&tipo=Requerimentos">Ver as perguntas dos deputados →</a></p>
  <p class="fonte">Fontes: <a href="{{ f.lei_eleitoral.url }}">lei eleitoral</a>,
  <a href="{{ f.alra.url }}">alra.pt</a></p>
</section>
<section class="cartao">
  <h3>Governo Regional</h3>
  <p>O presidente do Governo é nomeado a partir dos resultados das eleições
  para a Assembleia. Com as secretarias regionais, executa o orçamento: paga
  os salários de médicos, enfermeiros e professores da Região, estradas,
  transportes, apoios a empresas e famílias. As suas decisões saem no
  <em>Jornal Oficial</em>.</p>
  <p class="ir"><a href="/dados/beo/">Ver as contas, mês a mês →</a></p>
  <p class="fonte">Fontes: <a href="{{ f.estatuto.url }}">Estatuto</a>,
  <a href="{{ f.governo.url }}">portal do Governo</a></p>
</section>
<section class="cartao">
  <h3>Representante da República</h3>
  <p>Nomeado pelo Presidente da República. Assina, ou veta, os diplomas
  aprovados na Região e nomeia o presidente do Governo Regional.</p>
  <p class="fonte">Fonte: <a href="{{ f.estatuto.url }}">Estatuto</a></p>
</section>
<section class="cartao">
  <h3>Câmaras e juntas de freguesia</h3>
  <p>As 19 câmaras municipais e as 156 juntas tratam do que está mais perto:
  água, recolha do lixo, ruas, licenças de obras, apoios locais. Têm
  orçamento próprio, separado do da Região.</p>
  <p class="ir"><a href="/dados/ine/#ind=0013899">Quanto recebe cada câmara por habitante →</a></p>
</section>
<section class="cartao">
  <h3>O Estado</h3>
  <p>A República fica com a justiça, a defesa, as polícias e as relações
  externas, e transfere todos os anos uma parte do dinheiro do orçamento
  regional (ver o ponto 3).</p>
  <p class="fonte">Fonte: <a href="{{ f.lfra.url }}">Lei das Finanças das Regiões Autónomas</a></p>
</section>
</div>

<h2 id="dinheiro">3. O dinheiro da Região</h2>

{% if b.ano %}
<p>Em {{ b.ano }}, o Governo Regional e as entidades que dependem dele
(serviços e fundos autónomos, hospitais e outras) receberam
<strong>{{ b.receita_t }} milhões de euros</strong> e gastaram
<strong>{{ b.despesa_t }} milhões</strong>{% if b.despesa_hab_t %}, cerca de
{{ b.despesa_hab_t }} € por habitante{% endif %}.
{% if b.saldo < 0 %}A diferença, {{ b.saldo_abs_t }} milhões, é
<strong>défice</strong>: foi paga com dívida nova.{% else %}Sobraram
{{ b.saldo_abs_t }} milhões: houve <strong>excedente</strong>.{% endif %}</p>

<div class="duas">
<figure class="barras" aria-labelledby="cap-rec">
  <figcaption id="cap-rec">De onde veio o dinheiro, {{ b.ano }} (milhões de €)</figcaption>
  {%- assign maxi = b.receitas | map: "valor" | sort | last %}
  {%- for i in b.receitas %}
  <div class="barra" title="{{ i.nome }}: {{ i.valor_t }} M€ ({{ i.pct }}% da receita)">
    <span class="nome">{{ i.nome }}</span>
    <span class="trilho"><span class="valor" style="width: {{ i.valor | times: 100.0 | divided_by: maxi }}%"></span></span>
    <span class="num">{{ i.valor_t }} <small>{{ i.pct }}%</small></span>
  </div>
  {%- endfor %}
</figure>
<figure class="barras" aria-labelledby="cap-desp">
  <figcaption id="cap-desp">Em que foi gasto, {{ b.ano }} (milhões de €)</figcaption>
  {%- assign maxi = b.despesas | map: "valor" | sort | last %}
  {%- for i in b.despesas %}
  <div class="barra" title="{{ i.nome }}: {{ i.valor_t }} M€ ({{ i.pct }}% da despesa)">
    <span class="nome">{{ i.nome }}</span>
    <span class="trilho"><span class="valor" style="width: {{ i.valor | times: 100.0 | divided_by: maxi }}%"></span></span>
    <span class="num">{{ i.valor_t }} <small>{{ i.pct }}%</small></span>
  </div>
  {%- endfor %}
</figure>
</div>

<p>Mais de metade da receita são <strong>impostos pagos nos Açores</strong>
(IVA, IRS, IRC, combustíveis, tabaco…): ficam na Região, que pode baixar as
taxas até certo limite; é por isso que o IVA cá é mais baixo do que no
continente. O resto vem sobretudo do Orçamento do Estado e de fundos
europeus. Do lado da despesa, a maior fatia são os salários de quem trabalha
para a Região.</p>

{% if b.funcoes %}
<figure class="barras" aria-labelledby="cap-func">
  <figcaption id="cap-func">Para que serviu a despesa do Governo Regional, {{ b.ano }} (milhões de €)</figcaption>
  {%- assign maxi = b.funcoes[0].valor %}
  {%- for i in b.funcoes %}
  <div class="barra" title="{{ i.nome }}: {{ i.valor_t }} M€ ({{ i.pct }}%)">
    <span class="nome">{{ i.nome }}</span>
    <span class="trilho"><span class="valor" style="width: {{ i.valor | times: 100.0 | divided_by: maxi }}%"></span></span>
    <span class="num">{{ i.valor_t }} <small>{{ i.pct }}%</small></span>
  </div>
  {%- endfor %}
</figure>
<p>A saúde, sozinha, leva cerca de um terço; com a educação, mais de metade.
(Este quadro é só do Governo Regional, por isso o total,
{{ b.funcoes_total_t }} milhões, é um pouco diferente do de cima.)</p>
{% endif %}

<p class="fonte">Fonte: <a href="{{ b.boletim }}">Boletim de execução
orçamental de dezembro de {{ b.ano }}</a> (Governo dos Açores), valores
pagos e cobrados no ano. Classificação das receitas e despesas:
<a href="{{ f.classificador.url }}">Decreto-Lei n.º 26/2002</a>; impostos da
Região: <a href="{{ f.lfra.url }}">Lei das Finanças das Regiões Autónomas</a>.
<a href="/dados/beo/">Ver o ano corrente, mês a mês →</a></p>
{% endif %}

<h2 id="viver">4. Como se vive</h2>

<p>Alguns números para começar. São valores da
Região inteira: entre concelhos e freguesias as diferenças são grandes, e
as ligações abrem cada indicador lugar a lugar.</p>

<div class="cartoes">
{% if med %}
<section class="cartao num">
  <h3>Rendimento, depois do IRS</h3>
  <p class="grande">{{ med.acores_t }} €<small> por ano</small></p>
  <p>Metade de quem entrega IRS nos Açores declara menos do que isto, já
  descontado o imposto; a outra metade, mais. No país: {{ med.pt_t }} €.</p>
  <p class="ir"><a href="/dados/ine/#ind=0012757&nivel=Freguesia">Por freguesia →</a>
  · <a href="/dados/ine/#ind=0012759">Como se distribui (quintis) →</a></p>
  <p class="fonte">Fonte: <a href="{{ med.url }}">INE, {{ med.periodo }}</a></p>
</section>
{% endif %}
{% if ganho %}
<section class="cartao num">
  <h3>Salário médio</h3>
  <p class="grande">{{ ganho.acores_t }} €<small> por mês</small></p>
  <p>O ganho bruto médio de quem trabalha por conta de outrem a tempo
  completo, antes de impostos. No país: {{ ganho.pt_t }} €.</p>
  <p class="ir"><a href="/dados/ine/#ind=0012656">Por concelho →</a></p>
  <p class="fonte">Fonte: <a href="{{ ganho.url }}">INE, {{ ganho.periodo }}</a></p>
</section>
{% endif %}
{% if rsi %}
<section class="cartao num">
  <h3>Rendimento social de inserção</h3>
  <p class="grande">{{ rsi.acores_t }}<small> em cada mil pessoas</small></p>
  <p>Recebem o RSI, o apoio para quem está em pobreza extrema:
  {{ rsi.acores | divided_by: rsi.pt | round: 1 | replace: ".", "," }} vezes
  a proporção do país ({{ rsi.pt_t }} em cada mil).</p>
  <p class="ir"><a href="/dados/ine/#ind=0013420">Por concelho →</a></p>
  <p class="fonte">Fonte: <a href="{{ rsi.url }}">INE, {{ rsi.periodo }}</a></p>
</section>
{% endif %}
{% if renda %}
<section class="cartao num">
  <h3>Arrendar casa</h3>
  <p class="grande">{{ renda.acores_t }} €<small> por m² por mês</small></p>
  <p>Valor do meio das rendas dos contratos novos: uma casa de 80 m² ficaria
  por cerca de {{ renda.acores | times: 80 | round }} € por mês (conta do
  açores.net). No país: {{ renda.pt_t }} €/m².</p>
  <p class="ir"><a href="/dados/ine/#ind=0014698">Por concelho →</a></p>
  <p class="fonte">Fonte: <a href="{{ renda.url }}">INE, {{ renda.periodo }}</a></p>
</section>
{% endif %}
{% if dorm %}
<section class="cartao num">
  <h3>Turismo</h3>
  <p class="grande">{{ dorm.acores_t }}<small> dormidas por 100 habitantes</small></p>
  <p>Noites passadas em hotéis e alojamentos turísticos ao longo do ano.
  No país: {{ dorm.pt_t }}; na Madeira: {{ dorm.madeira_t }}.</p>
  <p class="ir"><a href="/dados/ine/#ind=0013210">Por concelho →</a></p>
  <p class="fonte">Fonte: <a href="{{ dorm.url }}">INE, {{ dorm.periodo }}</a></p>
</section>
{% endif %}
{% if sr.ipc %}
<section class="cartao num">
  <h3>Preços</h3>
  <p class="grande">{{ sr.ipc.valor_t }}%<small> em um ano</small></p>
  <p>Quanto subiram os preços nos Açores entre {{ sr.ipc.antes }} e
  {{ sr.ipc.periodo }}: o que custava 100 € custa agora cerca de
  {{ sr.ipc.cem | round: 2 | replace: ".", "," }} €.</p>
  <p class="ir"><a href="/dados/srea/#precos">O que mais subiu →</a></p>
  <p class="fonte">Fonte: <a href="{{ sr.ipc.url }}">SREA, IPC, {{ sr.ipc.periodo }}</a></p>
</section>
{% endif %}
{% if sr.desemprego %}
<section class="cartao num">
  <h3>Desemprego</h3>
  <p class="grande">{{ sr.desemprego.valor_t }}%<small> da população ativa</small></p>
  <p>Desempregados em cada 100 pessoas que trabalham ou procuram trabalho,
  no {{ sr.desemprego.periodo }}{% if sr.desemprego.antes %} (um ano antes:
  {{ sr.desemprego.antes_t }}%){% endif %}. É uma estimativa por amostragem.</p>
  <p class="ir"><a href="/dados/srea/#emprego">Trimestre a trimestre →</a></p>
  <p class="fonte">Fonte: <a href="{{ sr.desemprego.url }}">SREA, Inquérito ao Emprego</a></p>
</section>
{% endif %}
</div>
<p class="ir">Preços, emprego, economia e turismo ilha a ilha, todos os meses:
<a href="/dados/srea/">Economia →</a></p>

<h2 id="palavras">5. Seis palavras para ler os números</h2>

<dl class="palavras">
  <dt>Mediana</dt>
  <dd>O valor do meio: metade está abaixo, metade acima. Ao contrário da
  média, não sobe só porque meia dúzia de pessoas ganha muito, por isso
  diz melhor como vive a maioria.</dd>
  <dt>Quintis</dt>
  <dd>Pôr todos em fila, do menor para o maior rendimento, e partir a fila em
  cinco grupos iguais. Comparar o limite dos 20% de cima com o dos 20% de
  baixo mostra a distância entre ricos e pobres.
  <a href="/dados/ine/#ind=0012759">Ver os quintis →</a></dd>
  <dt>Por habitante, por mil habitantes</dt>
  <dd>Dividir pela população, para comparar lugares de tamanhos diferentes:
  São Miguel tem sempre mais de tudo do que o Corvo, mas por habitante a
  comparação já é justa.</dd>
  <dt>Sujeito passivo e agregado fiscal</dt>
  <dd>Quem entrega a declaração de IRS. Um casal que declara em conjunto
  conta como um agregado; quem não entrega IRS (muitas pessoas com
  rendimentos baixos) fica de fora destas estatísticas.</dd>
  <dt>Mês a mês e acumulado</dt>
  <dd>Os boletins das contas da Região somam desde janeiro: o valor de
  setembro é o total de janeiro a setembro. No açores.net pode ver cada mês
  em separado ou o acumulado.</dd>
  <dt>Défice e dívida</dt>
  <dd>O défice é o que falta num ano (gastou-se mais do que se recebeu); a
  dívida é o que se deve ao fim de todos os anos. Cada défice aumenta a
  dívida.</dd>
</dl>
<p class="fonte">Explicações do açores.net, não são texto oficial. As
definições oficiais estão junto de cada indicador do INE e no glossário
das <a href="/dados/beo/">contas da Região</a>, com ligação aos textos legais.</p>

<h2 id="comecar">6. Por onde começar</h2>

<ul class="perguntas">
  <li><a href="/dados/ine/#ind=0012757&nivel=Freguesia">Quanto se ganha na minha freguesia?</a></li>
  <li><a href="/dados/ine/#ind=0012918">A população do meu concelho está a crescer ou a diminuir?</a></li>
  <li><a href="/dados/ine/#ind=0014698">Quanto custa arrendar casa no meu concelho?</a></li>
  <li><a href="/dados/srea/#turismo">Quantos turistas vão à minha ilha, mês a mês?</a></li>
  <li><a href="/dados/beo/#quadro=despesa-do-gra-por-funcao">Quanto gasta a Região em saúde, este ano?</a></li>
  <li><a href="/dados/beo/#quadro=receita-fiscal-do-gra&grafico=anos">Quanto rende o IVA, mês a mês?</a></li>
  <li><a href="/dados/#fonte=base">Que contratos fez a minha câmara, e com quem?</a></li>
  <li><a href="/dados/#fonte=alra&tipo=Requerimentos">O que perguntaram os deputados ao Governo?</a></li>
  <li><a href="/atualizacoes/">O que saiu hoje no Jornal Oficial e na Assembleia?</a></li>
</ul>

{%- assign antigas = site.posts | where_exp: "p", "p.op != true" | sort: "date" | reverse %}
{% if antigas.size > 0 %}
<details class="antigas">
<summary>Para ir mais fundo: análises anteriores</summary>
<p>Textos e gráficos publicados no açores.net em anos anteriores, sobre
pobreza, desigualdade, dívida e orçamento. Usam os dados que havia quando
foram escritos: para valores recentes, use as ferramentas acima.</p>
<ul>
{%- for p in antigas %}
  <li><a href="{% if p.link %}{{ p.page }}{% else %}{{ p.url }}{% endif %}">{{ p.title | xml_escape }}</a> <span class="meta">({{ p.date | date: "%Y" }})</span></li>
{%- endfor %}
  <li><a href="/assets/pdf/RetratoAçores2023.pdf">Retrato dos Açores 2023</a> (PORDATA, <a href="https://www.pordata.pt/retratos/2023/retrato+dos+acores-91">site</a>) <span class="meta">(2023)</span></li>
</ul>
</details>
{% endif %}

<style>
.lead { font-size: 1.15em; max-width: 40em; }
.indice { display: grid; grid-template-columns: repeat(auto-fit, minmax(min(15em, 100%), 1fr)); gap: .4em; margin: 1em 0 1.5em; }
.indice a { display: block; padding: .45em .7em; border: 1px solid rgba(147,161,161,.6); border-radius: 6px; background: rgba(147,161,161,.08); text-decoration: none; }
.indice a:hover { background: rgba(38,139,210,.12); }
.indice span { display: inline-block; min-width: 1.4em; font-weight: bold; color: #268bd2; }
h2[id] { scroll-margin-top: 1em; margin-top: 1.4em; }
.cartoes { display: grid; grid-template-columns: repeat(auto-fit, minmax(min(16em, 100%), 1fr)); gap: .9em; margin: 1em 0 1.2em; }
.cartao { border: 1px solid rgba(147,161,161,.6); border-radius: 8px; padding: .8em 1em .3em; background: rgba(147,161,161,.08); }
.cartao h3 { font-size: 1.05em; margin: 0 0 .4em; }
.cartao p { font-size: .95em; margin-bottom: .5em; }
.cartao .grande { font-size: 1.7em; font-weight: bold; line-height: 1.15; margin-bottom: .3em; }
.cartao .grande small { font-size: .5em; font-weight: normal; }
.cartao .ir { font-size: .9em; }
.fonte { font-size: .85em; color: #586e75; }
.cartao .fonte { margin-top: .2em; }
.barras { margin: 1em 0 .6em; max-width: 42em; }
.barras figcaption { font-weight: bold; margin-bottom: .5em; }
.barra { display: grid; grid-template-columns: minmax(7em, 13em) 1fr auto; align-items: center; gap: .6em; margin: .3em 0; font-size: .95em; }
.barra .trilho { height: .8em; background: rgba(147,161,161,.15); border-radius: 4px; overflow: hidden; }
.barra .valor { display: block; height: 100%; background: #268bd2; border-radius: 0 4px 4px 0; min-width: 2px; }
.barra .num { font-variant-numeric: tabular-nums; text-align: right; white-space: nowrap; min-width: 4.5em; }
.barra .num small { color: #586e75; margin-left: .3em; }
.duas { display: grid; grid-template-columns: repeat(auto-fit, minmax(min(22em, 100%), 1fr)); gap: 0 2em; }
.palavras dt { font-weight: bold; margin-top: .7em; }
.palavras dd { margin: .15em 0 0 0; max-width: 42em; }
.perguntas { columns: 2 18em; }
.perguntas li { break-inside: avoid; margin-bottom: .3em; }
.antigas { margin-top: 2em; border-top: 1px solid rgba(147,161,161,.4); padding-top: .8em; }
.antigas summary { cursor: pointer; font-weight: bold; }
.meta { color: #586e75; font-size: .85em; }
@media (max-width: 30em) { .barra { grid-template-columns: 1fr auto; } .barra .trilho { grid-column: 1 / -1; grid-row: 2; } }
@media (prefers-color-scheme: dark) {
  .fonte, .meta, .barra .num small { color: #93a1a1; }
}
</style>
