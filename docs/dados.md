---
title: Dados
nav_title: Pesquisar
layout: default
permalink: /dados/
---
# Dados abertos

Uma tabela por fonte: contratos públicos (BASE) desde 2012, e atividade da
Assembleia Legislativa (ALRA) e atos com montantes do Jornal Oficial (JORAA)
desde agosto de 2024. Pesquise aqui ou descarregue os CSV. Cada linha tem a
ligação para o documento original (ver o [guia](/tutorial/)).

**Estatísticas do INE por concelho e freguesia** (rendimentos e IRS, rendas,
construção, população, turismo, câmaras): ver [Indicadores do INE](/dados/ine/).

**Receita e despesa do Governo Regional, mês a mês** (boletins de execução
orçamental): ver [Execução orçamental](/dados/beo/).

**O que o Tribunal de Contas diz sobre a Conta da Região** (juízo, reservas,
recomendações e números): ver [Tribunal de Contas](/dados/tdc/).

**Quantos agregados há em cada escalão de IRS e quanto pagam** (Autoridade
Tributária, desde 2016, com a Madeira e o continente): ver
[IRS por escalão](/dados/irs/).

<form id="dados-form" class="dados-form" role="search" onsubmit="return false">
  <fieldset>
    <legend>Fonte</legend>
    <label><input type="radio" name="fonte" value="base" checked> Contratos (BASE)</label>
    <label><input type="radio" name="fonte" value="alra"> Assembleia (ALRA)</label>
    <label><input type="radio" name="fonte" value="joraa"> Jornal Oficial (JORAA)</label>
  </fieldset>
  <div class="dados-row">
    <label class="dados-grow">Pesquisa
      <input type="search" id="q" placeholder="ex.: bencom, combustível, Flores" autocomplete="off">
    </label>
    <label><span id="tipo-label">Tipo</span>
      <select id="tipo"><option value="">todos</option></select>
    </label>
  </div>
  <div class="dados-row">
    <label>De <input type="date" id="de"></label>
    <label>Até <input type="date" id="ate"></label>
    <label id="min-wrap">Valor mínimo (€) <input type="number" id="min" min="0" step="1000" inputmode="numeric"></label>
    <button type="button" id="limpar">Limpar</button>
  </div>
</form>

<p id="estado" role="status" aria-live="polite">A carregar…</p>
<p><a id="exportar" href="#" download>Descarregar estes resultados (CSV)</a></p>

<div class="dados-scroll">
  <table id="tabela">
    <caption class="sr-only">Resultados</caption>
    <thead></thead>
    <tbody></tbody>
  </table>
</div>
<p><button type="button" id="mais" hidden>Mostrar mais</button></p>

## O que é cada fonte

<dl class="glossario">
  <dt>Contratos públicos (BASE)</dt>
  <dd>O portal <a href="https://www.base.gov.pt/">base.gov.pt</a>, onde as
  entidades públicas são obrigadas a publicar os contratos que assinam. Aqui
  estão os contratos executados nos Açores (Governo Regional, câmaras,
  hospitais, empresas públicas, serviços do Estado na Região): desde agosto de
  2024, os que o açores.net viu aparecer dia a dia; antes disso, e para
  completar, os
  <a href="https://dados.gov.pt/datasets/contratos-publicos-portal-base-impic-contratos-de-2012-a-2026">dados
  abertos do IMPIC</a>, que gere o portal.</dd>
  <dt>Assembleia Legislativa (ALRA)</dt>
  <dd>O parlamento regional, em <a href="https://www.alra.pt/">alra.pt</a>:
  requerimentos, iniciativas legislativas, votos, petições, audições,
  diários das sessões e notas de imprensa.</dd>
  <dt>Jornal Oficial (JORAA)</dt>
  <dd>O <a href="https://jo.azores.gov.pt/">Jornal Oficial da Região</a>,
  onde saem os atos do Governo Regional. Só entram os atos com montantes
  (apoios, subsídios, contratos-programa, autorizações de despesa).</dd>
</dl>

<details class="termos">
<summary><strong>O que quer dizer…</strong> adjudicante, ajuste direto, requerimento e outros termos</summary>
<p class="fonte">Explicações do açores.net em linguagem corrente, não são texto
oficial. Em cada termo está a ligação para a lei ou a fonte com a definição oficial.</p>
<dl class="glossario">
  <dt>Adjudicante</dt>
  <dd>A entidade pública que contrata e paga (uma secretaria regional, uma câmara, um hospital).</dd>
  <dd class="fonte">Definição oficial: <a href="{{ site.data.fontes.ccp.url }}">{{ site.data.fontes.ccp.nome }}</a></dd>
  <dt>Adjudicatário</dt>
  <dd>A empresa ou pessoa contratada.</dd>
  <dd class="fonte">Definição oficial: <a href="{{ site.data.fontes.ccp.url }}">{{ site.data.fontes.ccp.nome }}</a></dd>
  <dt>Preço contratual</dt>
  <dd>O valor do contrato, sem IVA, tal como publicado no BASE. O valor
  efetivamente pago pode ser diferente (por exemplo, com trabalhos a mais).</dd>
  <dd class="fonte">Definição oficial: <a href="{{ site.data.fontes.ccp.url }}">{{ site.data.fontes.ccp.nome }}</a>; <a href="{{ site.data.fontes.base.url }}">{{ site.data.fontes.base.nome }}</a></dd>
  <dt>Ajuste direto</dt>
  <dd>A entidade convida uma única empresa, sem concorrência. Só é permitido
  abaixo de certos valores ou em casos previstos no Código dos Contratos
  Públicos (urgência, um só fornecedor possível…).</dd>
  <dd class="fonte">Definição oficial: <a href="{{ site.data.fontes.ccp.url }}">{{ site.data.fontes.ccp.nome }}</a></dd>
  <dt>Consulta prévia</dt>
  <dd>A entidade convida pelo menos três empresas à sua escolha.</dd>
  <dd class="fonte">Definição oficial: <a href="{{ site.data.fontes.ccp.url }}">{{ site.data.fontes.ccp.nome }}</a></dd>
  <dt>Concurso público</dt>
  <dd>Aberto a qualquer empresa, anunciado em Diário da República.</dd>
  <dd class="fonte">Definição oficial: <a href="{{ site.data.fontes.ccp.url }}">{{ site.data.fontes.ccp.nome }}</a></dd>
  <dt>Acordo-quadro</dt>
  <dd>Um contrato que fixa condições (preços, fornecedores) para compras
  futuras; as compras feitas ao abrigo dele aparecem como contratos próprios.</dd>
  <dd class="fonte">Definição oficial: <a href="{{ site.data.fontes.ccp.url }}">{{ site.data.fontes.ccp.nome }}</a></dd>
  <dt>Requerimento</dt>
  <dd>Uma pergunta escrita de um ou mais deputados ao Governo Regional. O
  Governo tem um prazo para responder; o estado mostra se está “no prazo”,
  “fora de prazo” ou respondido.</dd>
  <dd class="fonte">Definição oficial: <a href="{{ site.data.fontes.estatuto.url }}">{{ site.data.fontes.estatuto.nome }}</a>; <a href="{{ site.data.fontes.alra.url }}">{{ site.data.fontes.alra.nome }}</a></dd>
  <dt>Proposta e projeto (de decreto legislativo regional, de resolução)</dt>
  <dd>Iniciativas legislativas: a proposta vem do Governo, o projeto vem dos
  deputados. Um decreto legislativo regional é uma lei regional; uma
  resolução é uma recomendação ou decisão da Assembleia.</dd>
  <dd class="fonte">Definição oficial: <a href="{{ site.data.fontes.estatuto.url }}">{{ site.data.fontes.estatuto.nome }}</a>; <a href="{{ site.data.fontes.alra.url }}">{{ site.data.fontes.alra.nome }}</a></dd>
  <dt>Voto</dt>
  <dd>Uma moção de pesar, congratulação, saudação ou protesto, votada em plenário.</dd>
  <dd class="fonte">Definição oficial: <a href="{{ site.data.fontes.alra.url }}">{{ site.data.fontes.alra.nome }}</a></dd>
  <dt>Portaria, despacho e resolução do Conselho de Governo</dt>
  <dd>Atos do Governo Regional publicados no Jornal Oficial. A resolução é
  decidida em Conselho de Governo; a portaria e o despacho são de um ou mais
  membros do Governo.</dd>
  <dd class="fonte">Definição oficial: <a href="{{ site.data.fontes.estatuto.url }}">{{ site.data.fontes.estatuto.nome }}</a></dd>
</dl>
</details>

## Descarregar

| Ficheiro | Conteúdo | Cobertura |
|---|---|---|
| [base.csv](/dados/base.csv) | um contrato por linha: adjudicante, adjudicatário, preço, procedimento, data de assinatura, número de concorrentes e origem da linha (`açores.net` ou `IMPIC`) | <span data-meta="base"></span> |
| [alra.csv](/dados/alra.csv) | requerimentos (com estado e resposta), iniciativas, votos, petições, intervenções, diários, audições, notas de imprensa | <span data-meta="alra"></span> |
| [joraa.csv](/dados/joraa.csv) | atos do Jornal Oficial com montantes (portarias, despachos, resoluções) | <span data-meta="joraa"></span> |
| [ine.csv](/dados/ine.csv) | um valor por linha: indicador, período, local (região, concelho ou freguesia), concelho, ilha, categoria, valor, unidade | <span data-meta="ine"></span> |
| [beo.csv](/dados/beo.csv) | um valor por linha: quadro do boletim de execução orçamental, rubrica, subsetor ou departamento, medida, mês (acumulado desde janeiro), valor, boletim | <span data-meta="beo"></span> |
| [tdc.csv](/dados/tdc.csv) | o texto dos pareceres do Tribunal de Contas sobre a Conta da Região: juízo, reservas, ênfases e recomendações (com o estado que o parecer seguinte lhes deu) | <span data-meta="tdc"></span> |
| [tdc_valores.csv](/dados/tdc_valores.csv) | os números desses pareceres: conta consolidada, dívida total, receita e despesa fora da Conta | <span data-meta="tdc_valores"></span> |
| [at_irs.csv](/dados/at_irs.csv) | um valor por linha: IRS por escalão (agregados, rendimento englobado, IRS liquidado) nos Açores, na Madeira e no continente, e a taxa adicional de solidariedade | <span data-meta="at_irs"></span> |
| [acores.db](/dados/acores.db) | as tabelas acima em SQLite, com pesquisa de texto; a tabela `base` tem mais colunas (NIF, CPV, preço base e preço efetivo, propostas, local de execução, fundamentação) | ver abaixo |

Os CSV estão em UTF-8 e abrem diretamente no Excel, no LibreOffice ou no
Google Sheets. Todos os ficheiros são refeitos todos os dias a partir das
[páginas diárias](/rsss) e do código em
[`bot/datasets.py`](https://github.com/fmesqg/a-ores.net-site/blob/main/bot/datasets.py).
O `ine.csv` é atualizado uma vez por semana a partir da
[API do INE](https://www.ine.pt/xportal/xmain?xpid=INE&xpgid=ine_api), pelo
código em [`bot/ine.py`](https://github.com/fmesqg/a-ores.net-site/blob/main/bot/ine.py),
que tem a lista de indicadores. O `beo.csv` é atualizado uma vez por semana a
partir dos PDF dos boletins, por
[`bot/beo.py`](https://github.com/fmesqg/a-ores.net-site/blob/main/bot/beo.py).
Os `tdc*.csv` mudam uma vez por ano, quando sai um parecer novo, por
[`bot/tdc.py`](https://github.com/fmesqg/a-ores.net-site/blob/main/bot/tdc.py).
Os contratos anteriores a agosto de 2024 vêm dos ficheiros anuais do IMPIC,
relidos uma vez por mês por
[`bot/base_impic.py`](https://github.com/fmesqg/a-ores.net-site/blob/main/bot/base_impic.py).
O `at_irs.csv` muda uma vez por ano, quando a AT publica um dossiê estatístico
novo, por
[`bot/at_irs.py`](https://github.com/fmesqg/a-ores.net-site/blob/main/bot/at_irs.py).
Última geração: <span data-meta="gerado"></span>.

## Consultar em SQL

O ficheiro [acores.db](/dados/acores.db) tem as mesmas tabelas em SQLite,
com pesquisa de texto (`base_fts`, `alra_fts`, `joraa_fts`, `ine_fts` e as
outras `<tabela>_fts`), que ignora acentos.
Abre-se no navegador com o [Datasette Lite](https://lite.datasette.io), sem
instalar nada. A primeira abertura descarrega a base inteira (algumas dezenas de MB) e
demora alguns segundos. Também se abre com `sqlite3`, Python, R ou DuckDB.

- [Abrir a base de dados](https://lite.datasette.io/?url=https://xn--aores-yra.net/dados/acores.db#/acores): as tabelas, com filtros, facetas e caixa de pesquisa.
- [Maiores adjudicatários (BASE)](https://lite.datasette.io/?url=https://xn--aores-yra.net/dados/acores.db#/acores?sql=select%20adjudicatario%2C%20count%28%2A%29%20as%20contratos%2C%20round%28sum%28preco%29%29%20as%20total_eur%20from%20base%20group%20by%20adjudicatario%20order%20by%20total_eur%20desc%20limit%20100)
- [Ajustes diretos por entidade (BASE)](https://lite.datasette.io/?url=https://xn--aores-yra.net/dados/acores.db#/acores?sql=select%20adjudicante%2C%20count%28%2A%29%20as%20contratos%2C%20round%28sum%28preco%29%29%20as%20total_eur%20from%20base%20where%20procedimento%20like%20%27Ajuste%20Direto%25%27%20group%20by%20adjudicante%20order%20by%20total_eur%20desc%20limit%20100)
- [Pesquisa de texto em contratos (BASE)](https://lite.datasette.io/?url=https://xn--aores-yra.net/dados/acores.db#/acores?sql=select%20base.publicado%2C%20base.objeto%2C%20base.adjudicante%2C%20base.adjudicatario%2C%20base.preco%2C%20base.url%20from%20base%20join%20base_fts%20on%20base_fts.rowid%20%3D%20base.rowid%20where%20base_fts%20match%20%3Atermos%20order%20by%20base.preco%20desc&termos=bencom)
- [Contratos por ano, com e sem concorrência (BASE, desde 2012)](https://lite.datasette.io/?url=https://xn--aores-yra.net/dados/acores.db#/acores?sql=select%20substr%28publicado%2C%201%2C%204%29%20as%20ano%2C%20count%28%2A%29%20as%20contratos%2C%20round%28sum%28preco%29%20%2F%201e6%2C%201%29%20as%20milhoes_eur%2C%20round%28100.0%20%2A%20sum%28case%20when%20procedimento%20like%20%27Ajuste%20Direto%25%27%20then%20preco%20end%29%20%2F%20sum%28preco%29%2C%201%29%20as%20pct_valor_ajuste_direto%20from%20base%20group%20by%20ano%20order%20by%20ano)
- [Concursos com um só concorrente, por entidade (BASE)](https://lite.datasette.io/?url=https://xn--aores-yra.net/dados/acores.db#/acores?sql=select%20adjudicante%2C%20count%28%2A%29%20as%20contratos%2C%20round%28sum%28preco%29%29%20as%20total_eur%20from%20base%20where%20procedimento%20like%20%27Concurso%25%27%20and%20concorrentes%20%3D%201%20group%20by%20adjudicante%20order%20by%20total_eur%20desc%20limit%20100)
- [Contratos entre duas entidades, ano a ano (BASE; mude os nomes)](https://lite.datasette.io/?url=https://xn--aores-yra.net/dados/acores.db#/acores?sql=select%20substr%28publicado%2C%201%2C%204%29%20as%20ano%2C%20count%28%2A%29%20as%20contratos%2C%20round%28sum%28preco%29%29%20as%20total_eur%2C%20group_concat%28distinct%20procedimento%29%20as%20procedimentos%20from%20base%20where%20adjudicante%20like%20%3Aadjudicante%20and%20adjudicatario%20like%20%3Aadjudicatario%20group%20by%20ano%20order%20by%20ano&adjudicante=%25EDA%25&adjudicatario=%25BENCOM%25)
- [Agregados e IRS no último escalão, Açores e Madeira (AT)](https://lite.datasette.io/?url=https://xn--aores-yra.net/dados/acores.db#/acores?sql=select%20ano%2C%20regiao%2C%20taxa%2C%20valor%20as%20agregados%20from%20at_irs%20where%20quadro%20%3D%20%27Taxas%20de%20tributa%C3%A7%C3%A3o%27%20and%20medida%20%3D%20%27Agregados%27%20and%20titularidade%20%3D%20%27Total%27%20and%20regiao%20%21%3D%20%27Continente%27%20and%20escalao%20%3D%20%28select%20max%28escalao%29%20from%20at_irs%20b%20where%20b.ano%20%3D%20at_irs.ano%20and%20b.regiao%20%3D%20at_irs.regiao%20and%20b.quadro%20%3D%20at_irs.quadro%20and%20b.medida%20%3D%20at_irs.medida%29%20order%20by%20regiao%2C%20ano)
- [Requerimentos por deputado e resposta (ALRA)](https://lite.datasette.io/?url=https://xn--aores-yra.net/dados/acores.db#/acores?sql=select%20autores%2C%20count%28%2A%29%20as%20requerimentos%2C%20sum%28estado%20%3D%20%27RESPOSTA%20ATEMPADA%27%29%20as%20atempada%2C%20sum%28estado%20%3D%20%27RESPOSTA%20TADIA%27%29%20as%20tardia%2C%20sum%28estado%20%3D%20%27FORA%20DE%20PRAZO%27%29%20as%20fora_de_prazo%20from%20alra%20where%20tipo%20%3D%20%27Requerimentos%27%20group%20by%20autores%20order%20by%20requerimentos%20desc)
- [Rendimento médio após IRS por freguesia, 2024 (INE)](https://lite.datasette.io/?url=https://xn--aores-yra.net/dados/acores.db#/acores?sql=select%20local%2C%20concelho%2C%20ilha%2C%20valor%20as%20euros%20from%20ine%20where%20varcd%20%3D%20%270012756%27%20and%20periodo%20%3D%20%272024%27%20and%20nivel%20%3D%20%27Freguesia%27%20order%20by%20valor%20desc)
- [Renda mediana (€/m²) de novos contratos por concelho e ano (INE)](https://lite.datasette.io/?url=https://xn--aores-yra.net/dados/acores.db#/acores?sql=select%20local%2C%20group_concat%28periodo%20%7C%7C%20%27%3A%20%27%20%7C%7C%20valor%2C%20%27%20%C2%B7%20%27%29%20as%20serie%20from%20ine%20where%20varcd%20%3D%20%270014698%27%20and%20nivel%20%21%3D%20%27Freguesia%27%20group%20by%20local%20order%20by%20local)
- [População residente por concelho, 2021 e 2025 (INE)](https://lite.datasette.io/?url=https://xn--aores-yra.net/dados/acores.db#/acores?sql=select%20local%2C%20max%28case%20when%20periodo%20%3D%20%272021%27%20then%20valor%20end%29%20as%20pop_2021%2C%20max%28case%20when%20periodo%20%3D%20%272025%27%20then%20valor%20end%29%20as%20pop_2025%2C%20round%28100.0%20%2A%20%28max%28case%20when%20periodo%20%3D%20%272025%27%20then%20valor%20end%29%20%2F%20max%28case%20when%20periodo%20%3D%20%272021%27%20then%20valor%20end%29%20-%201%29%2C%201%29%20as%20variacao_pct%20from%20ine%20where%20varcd%20%3D%20%270012918%27%20group%20by%20local%20order%20by%20variacao_pct)
- [Despesa por departamento no último boletim (BEO)](https://lite.datasette.io/?url=https://xn--aores-yra.net/dados/acores.db#/acores?sql=select%20dimensao%20as%20departamento%2C%20round%28valor%20%2F%201e6%2C%201%29%20as%20milhoes_eur%20from%20beo%20where%20quadro%20%3D%20%27Despesa%20do%20GRA%20por%20departamento%27%20and%20rubrica%20%3D%20%27Despesa%20efetiva%27%20and%20data%20%3D%20%28select%20max%28data%29%20from%20beo%29%20order%20by%20valor%20desc)
- [IRS cobrado até ao mesmo mês, ano a ano (BEO)](https://lite.datasette.io/?url=https://xn--aores-yra.net/dados/acores.db#/acores?sql=select%20ano%2C%20mes%2C%20round%28valor%20%2F%201e6%2C%201%29%20as%20milhoes_eur%20from%20beo%20where%20quadro%20%3D%20%27Receita%20fiscal%20do%20GRA%27%20and%20caminho%20like%20%27%25%28IRS%29%27%20and%20medida%20like%20%27Montante%25%27%20and%20mes%20%3D%20%28select%20cast%28substr%28max%28data%29%2C%206%2C%202%29%20as%20integer%29%20from%20beo%29%20order%20by%20ano)
- [Recomendações do Tribunal de Contas por estado, ano a ano (TdC)](https://lite.datasette.io/?url=https://xn--aores-yra.net/dados/acores.db#/acores?sql=select%20conta%2C%20situacao%2C%20count%28%2A%29%20as%20recomendacoes%20from%20tdc%20where%20tipo%20%3D%20%27recomenda%C3%A7%C3%A3o%27%20and%20situacao%20%21%3D%20%27%27%20group%20by%20conta%2C%20situacao%20order%20by%20conta%2C%20recomendacoes%20desc)
- [Dívida total e receita e despesa fora da Conta, ano a ano (TdC)](https://lite.datasette.io/?url=https://xn--aores-yra.net/dados/acores.db#/acores?sql=select%20rubrica%2C%20group_concat%28ano%20%7C%7C%20%27%3A%20%27%20%7C%7C%20round%28valor%2C%201%29%2C%20%27%20%C2%B7%20%27%29%20as%20serie%20from%20tdc_valores%20where%20quadro%20%3D%20%27Indicadores%27%20group%20by%20rubrica)
- [Montantes por entidade e ano (JORAA)](https://lite.datasette.io/?url=https://xn--aores-yra.net/dados/acores.db#/acores?sql=select%20entidade%2C%20substr%28publicado%2C%201%2C%204%29%20as%20ano%2C%20count%28%2A%29%20as%20atos%2C%20round%28sum%28montante%29%29%20as%20total_eur%20from%20joraa%20group%20by%20entidade%2C%20ano%20order%20by%20total_eur%20desc%20limit%20100)

As consultas podem ser editadas na própria página do Datasette, e o endereço
de cada resultado pode ser partilhado.

<p id="limitacoes"><strong>Limitações</strong></p>

{% include joraa-atraso.html %}

- Só entra o que o robô viu. Os dias em que uma fonte falhou ficam em falta.
- **JORAA**: de 11 de agosto a 27 de novembro de 2026 o jo.azores.gov.pt
  bloqueou o robô. Os dias em falta estão a ser recolhidos (ver o aviso acima,
  enquanto durar). O montante é
  calculado pelo açores.net: a soma de todos os valores em euros que
  aparecem no resumo e no texto do ato. Um valor repetido conta duas vezes
  (o Despacho n.º 694/2025 autoriza 3 175 000 € e aparece com 6 350 000 €),
  e números mal escritos no ato dão somas absurdas (a Adenda n.º 5/2025 ao
  contrato-programa do HDES aparece com 159 864 847 000 €). Serve para
  encontrar atos. Para citar, leia o valor no próprio ato. "0" quer dizer
  que não se encontrou nenhum valor em euros.
- **BASE**: a data de publicação é o dia em que o contrato apareceu no portal,
  não o da assinatura. Um contrato republicado conta uma vez só. Desde agosto
  de 2024 é o dia em que o açores.net o viu; antes, é a data que o IMPIC
  publica (coluna `recolha`). Entram os contratos com local de execução nos
  Açores, o mesmo critério da pesquisa do BASE. As colunas extra do IMPIC
  (concorrentes, propostas, preço efetivo) são as que as entidades
  preencheram no portal e às vezes faltam.
- **IRS (AT)**: ver as notas na página [IRS por escalão](/dados/irs/#notas).
- **ALRA**: o "estado" de um requerimento é o último que o robô registou. A
  coluna `data` é a de entrada. As notas de imprensa não têm data própria, por
  isso usa-se `primeiro_dia`.
- **INE**: ver as notas na página [Indicadores do INE](/dados/ine/).
- **BEO**: ver as notas na página [Execução orçamental](/dados/beo/).
- **Tribunal de Contas**: ver as notas na página [Tribunal de Contas](/dados/tdc/).

<noscript><p>A pesquisa precisa de JavaScript. Os CSV acima funcionam sem ele.</p></noscript>

<style>
.wrapper { max-width: min(1200px, 100%); }
.dados-form fieldset { border: 1px solid #ccc; padding: .5em 1em; margin-bottom: .75em; }
.dados-form label { margin-right: 1em; display: inline-block; }
.dados-row { display: flex; flex-wrap: wrap; gap: .5em 1em; align-items: flex-end; margin-bottom: .75em; }
.dados-row label { display: flex; flex-direction: column; margin: 0; }
.dados-grow { flex: 1 1 16em; }
.dados-row label { max-width: 100%; min-width: 0; }
.dados-form select { max-width: 100%; }
.dados-form input, .dados-form select, .dados-form button { font: inherit; padding: .3em .4em; }
.dados-form input:focus-visible, .dados-form select:focus-visible, button:focus-visible, th button:focus-visible { outline: 3px solid #268bd2; outline-offset: 1px; }
.dados-scroll { overflow-x: auto; }
#tabela { font-size: .9em; width: 100%; }
.glossario { max-width: 52em; }
.glossario dt { font-weight: bold; margin-top: .5em; }
.glossario dd { margin: 0 0 .2em; }
.glossario dd.fonte, .termos p.fonte { font-size: .85em; color: #586e75; margin-bottom: .5em; }
.termos { margin: .5em 0 1.5em; max-width: 52em; }
.termos summary { cursor: pointer; }
#tabela td { vertical-align: top; }
#tabela td.num { text-align: right; white-space: nowrap; }
#tabela td.dt { white-space: nowrap; }
th button { all: unset; cursor: pointer; font-weight: bold; }
th[aria-sort="ascending"] button::after { content: " ▲"; }
th[aria-sort="descending"] button::after { content: " ▼"; }
[hidden] { display: none !important; }
.sr-only { position: absolute; width: 1px; height: 1px; overflow: hidden; clip: rect(0 0 0 0); }
</style>

<script>
(function () {
  "use strict";
  // Build time: the data files change with every deploy, so ask for this
  // build's copy and never mix a new page with cached old data.
  var BUILD = "{{ site.time | date: '%s' }}";
  // Columns shown per source: [csv column, label, kind]; kind: d=date, e=euros, l=link title, t=text
  var VIEW = {
    base: { tipo: "procedimento", data: "publicado", valor: "preco", link: "url",
      cols: [["publicado", "Publicado", "d"], ["objeto", "Objeto", "l"], ["adjudicante", "Adjudicante", "t"],
             ["adjudicatario", "Adjudicatário", "t"], ["preco", "Preço", "e"], ["procedimento", "Procedimento", "t"],
             ["data_assinatura", "Assinatura", "d"], ["concorrentes", "Concorrentes", "n"]] },
    alra: { tipo: "tipo", data: "primeiro_dia", link: "url",
      cols: [["primeiro_dia", "Visto em", "d"], ["tipo", "Tipo", "t"], ["titulo", "Título", "l"],
             ["autores", "Autores", "t"], ["data", "Entrada", "d"], ["estado", "Estado", "t"],
             ["documento", "Docs", "docs"]] },
    joraa: { tipo: "serie", data: "publicado", valor: "montante", link: "url",
      cols: [["publicado", "Publicado", "d"], ["titulo", "Título", "l"], ["ato", "Ato", "t"],
             ["entidade", "Entidade", "t"], ["montante", "Montante", "e"]] }
  };
  var PAGE = 100;
  var cache = {}, state = { fonte: "base", sort: null, dir: -1, shown: PAGE }, current = [];
  var $ = function (id) { return document.getElementById(id); };
  var eur = new Intl.NumberFormat("pt-PT", { style: "currency", currency: "EUR" });
  var num = new Intl.NumberFormat("pt-PT", { maximumFractionDigits: 2 });
  var NUM = { e: 1, n: 1 };
  var fold = function (s) { return (s || "").normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase(); };

  function parseCSV(text) {
    var rows = [], row = [], f = "", q = false, i = 0, c;
    if (text.charCodeAt(0) === 0xfeff) i = 1;
    for (; i < text.length; i++) {
      c = text[i];
      if (q) {
        if (c === '"') { if (text[i + 1] === '"') { f += '"'; i++; } else q = false; }
        else f += c;
      } else if (c === '"') q = true;
      else if (c === ",") { row.push(f); f = ""; }
      else if (c === "\n") { row.push(f); rows.push(row); row = []; f = ""; }
      else if (c !== "\r") f += c;
    }
    if (f || row.length) { row.push(f); rows.push(row); }
    var cols = rows.shift();
    return rows.map(function (r) {
      var o = {}; cols.forEach(function (k, j) { o[k] = r[j] || ""; });
      o._s = fold(r.join(" "));
      return o;
    });
  }

  function load(fonte) {
    if (!cache[fonte]) {
      cache[fonte] = fetch("/dados/" + fonte + ".csv?v=" + BUILD)
        .then(function (r) { if (!r.ok) throw new Error(r.status); return r.text(); })
        .then(parseCSV);
    }
    return cache[fonte];
  }

  function readHash() {
    var p = new URLSearchParams(location.hash.slice(1));
    if (VIEW[p.get("fonte")]) state.fonte = p.get("fonte");
    document.querySelector('input[name=fonte][value="' + state.fonte + '"]').checked = true;
    $("q").value = p.get("q") || ""; $("de").value = p.get("de") || ""; $("ate").value = p.get("ate") || "";
    $("min").value = p.get("min") || ""; state.tipo = p.get("tipo") || "";
    state.sort = p.get("ord") || null; state.dir = p.get("dir") === "asc" ? 1 : -1;
  }

  function writeHash() {
    var p = new URLSearchParams();
    p.set("fonte", state.fonte);
    [["q", $("q").value.trim()], ["tipo", $("tipo").value], ["de", $("de").value], ["ate", $("ate").value],
     ["min", $("min").value], ["ord", state.sort || ""], ["dir", state.sort ? (state.dir > 0 ? "asc" : "desc") : ""]]
      .forEach(function (kv) { if (kv[1]) p.set(kv[0], kv[1]); });
    history.replaceState(null, "", "#" + p.toString());
  }

  function fillTipos(rows, v) {
    var seen = {}, sel = $("tipo");
    rows.forEach(function (r) { var t = r[v.tipo]; if (t) seen[t] = (seen[t] || 0) + 1; });
    sel.innerHTML = '<option value="">todos</option>';
    Object.keys(seen).sort(function (a, b) { return seen[b] - seen[a]; }).forEach(function (t) {
      var o = document.createElement("option"); o.value = t; o.textContent = t + " (" + seen[t] + ")"; sel.appendChild(o);
    });
    sel.value = seen[state.tipo] ? state.tipo : "";
    $("tipo-label").textContent = v.tipoLabel || "Tipo";
    $("min-wrap").hidden = !v.valor;
  }

  function apply() {
    var v = VIEW[state.fonte];
    return load(state.fonte).then(function (rows) {
      var terms = fold($("q").value).split(/\s+/).filter(Boolean);
      var tipo = $("tipo").value, de = $("de").value, ate = $("ate").value, min = parseFloat($("min").value);
      current = rows.filter(function (r) {
        if (tipo && r[v.tipo] !== tipo) return false;
        if (de && r[v.data] < de) return false;
        if (ate && r[v.data] > ate) return false;
        if (v.valor && !isNaN(min) && !(parseFloat(r[v.valor]) >= min)) return false;
        for (var i = 0; i < terms.length; i++) if (r._s.indexOf(terms[i]) < 0) return false;
        return true;
      });
      var k = state.sort || v.sort;
      if (k) {
        var isNum = v.cols.some(function (c) { return c[0] === k && NUM[c[2]]; });
        current.sort(function (a, b) {
          var x = a[k], y = b[k];
          if (isNum) { x = parseFloat(x) || 0; y = parseFloat(y) || 0; return (x - y) * state.dir; }
          return x.localeCompare(y, "pt") * state.dir;
        });
      }
      render();
      writeHash();
    });
  }

  function cell(r, c) {
    var td = document.createElement("td"), val = r[c[0]], a;
    if (c[2] === "e") { td.className = "num"; td.textContent = val ? eur.format(parseFloat(val)) : ""; }
    else if (c[2] === "n") { td.className = "num"; td.textContent = val === "" ? "" : num.format(parseFloat(val)); if (r.unidade) td.title = r.unidade; }
    else if (c[2] === "p") { td.className = "dt"; td.textContent = r.periodo || val; }
    else if (c[2] === "d") { td.className = "dt"; td.textContent = val; }
    else if (c[2] === "l") { a = document.createElement("a"); a.href = r[VIEW[state.fonte].link]; a.textContent = val; td.appendChild(a); }
    else if (c[2] === "docs") {
      [["documento", "doc"], ["resposta", "resposta"], ["video", "vídeo"]].forEach(function (d) {
        if (!r[d[0]]) return;
        a = document.createElement("a"); a.href = r[d[0]]; a.textContent = d[1];
        td.appendChild(a); td.appendChild(document.createTextNode(" "));
      });
    } else td.textContent = val;
    return td;
  }

  function render() {
    var v = VIEW[state.fonte], thead = $("tabela").tHead, tbody = $("tabela").tBodies[0];
    var tr = document.createElement("tr");
    v.cols.forEach(function (c) {
      var th = document.createElement("th"), b = document.createElement("button");
      th.scope = "col";
      if (c[2] === "docs") { th.textContent = c[1]; tr.appendChild(th); return; }
      b.type = "button"; b.textContent = c[1];
      if ((state.sort || v.sort) === c[0]) th.setAttribute("aria-sort", state.dir > 0 ? "ascending" : "descending");
      b.addEventListener("click", function () {
        if ((state.sort || v.sort) === c[0]) { state.sort = c[0]; state.dir = -state.dir; } else { state.sort = c[0]; state.dir = c[2] === "t" || c[2] === "l" ? 1 : -1; }
        state.shown = PAGE; apply();
      });
      th.appendChild(b); tr.appendChild(th);
    });
    thead.replaceChildren(tr);
    var frag = document.createDocumentFragment();
    current.slice(0, state.shown).forEach(function (r) {
      var row = document.createElement("tr");
      v.cols.forEach(function (c) { row.appendChild(cell(r, c)); });
      frag.appendChild(row);
    });
    tbody.replaceChildren(frag);
    var msg = current.length.toLocaleString("pt-PT") + " resultados";
    if (v.valor) {
      var total = current.reduce(function (s, r) { return s + (parseFloat(r[v.valor]) || 0); }, 0);
      msg += ", total " + eur.format(total);
    }
    if (current.length > state.shown) msg += " (a mostrar " + state.shown + ")";
    $("estado").textContent = msg + ".";
    $("tabela").caption.textContent = msg;
    $("mais").hidden = current.length <= state.shown;
  }

  function exportCSV(e) {
    var keys = Object.keys(current[0] || {}).filter(function (k) { return k !== "_s"; });
    var esc = function (s) { return /[",\n]/.test(s) ? '"' + s.replace(/"/g, '""') + '"' : s; };
    var body = [keys.join(",")].concat(current.map(function (r) { return keys.map(function (k) { return esc(r[k]); }).join(","); }));
    var url = URL.createObjectURL(new Blob(["﻿" + body.join("\n")], { type: "text/csv;charset=utf-8" }));
    e.currentTarget.href = url; e.currentTarget.download = state.fonte + "-filtrado.csv";
    setTimeout(function () { URL.revokeObjectURL(url); }, 10000);
  }

  function switchFonte() {
    var v = VIEW[state.fonte];
    $("estado").textContent = "A carregar…";
    return load(state.fonte).then(function (rows) { fillTipos(rows, v); return apply(); })
      .catch(function (err) { $("estado").textContent = "Não foi possível carregar os dados (" + err.message + "). Use os CSV abaixo."; });
  }

  var timer;
  $("q").addEventListener("input", function () { clearTimeout(timer); timer = setTimeout(function () { state.shown = PAGE; apply(); }, 200); });
  ["tipo", "de", "ate", "min"].forEach(function (id) { $(id).addEventListener("change", function () { state.shown = PAGE; apply(); }); });
  document.querySelectorAll("input[name=fonte]").forEach(function (r) {
    r.addEventListener("change", function () { state.fonte = r.value; state.sort = null; state.tipo = ""; state.shown = PAGE; switchFonte(); });
  });
  $("limpar").addEventListener("click", function () {
    ["q", "de", "ate", "min"].forEach(function (id) { $(id).value = ""; }); $("tipo").value = "";
    state.sort = null; state.shown = PAGE; apply();
  });
  $("mais").addEventListener("click", function () { state.shown += PAGE * 5; render(); });
  $("exportar").addEventListener("click", exportCSV);

  fetch("/dados/meta.json?v=" + BUILD).then(function (r) { return r.json(); }).then(function (m) {
    document.querySelectorAll("[data-meta]").forEach(function (el) {
      var k = el.getAttribute("data-meta"), x = m[k];
      el.textContent = k === "gerado" ? x.replace("T", " ") : x.linhas.toLocaleString("pt-PT") + " linhas, " + x.de + " a " + x.ate;
    });
  }).catch(function () {});

  readHash();
  switchFonte();
})();
</script>
