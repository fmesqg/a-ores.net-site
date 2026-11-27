---
title: Fontes e limitações
layout: default
permalink: /dados/notas/
secao: dados
---
{% include dados-nav.html %}

# Fontes e limitações

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
  <dt>Fundos europeus (PRR e Kohesio)</dt>
  <dd>Os projetos do Plano de Recuperação e Resiliência com uma parte nos
  Açores e as suas entidades, dos
  <a href="https://dados.gov.pt/datasets/dataset-estrutura-de-missao-prr-projetos-2">dados
  abertos da Recuperar Portugal</a>; e os projetos dos fundos de coesão
  (2014-2020 e 2021-2027) que o <a href="https://kohesio.ec.europa.eu/">Kohesio</a>,
  da Comissão Europeia, situa nos Açores. A parte do Kohesio está em
  construção. Ver <a href="/financas/fundos-europeus/">Fundos europeus</a>.</dd>
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

<h2 id="limitacoes">Limitações</h2>

{% include joraa-atraso.html %}

- Só entra o que o robô viu. Os dias em que uma fonte falhou ficam em falta.
- **JORAA**: de 11 de agosto a 27 de novembro de 2026 o jo.azores.gov.pt
  bloqueou o robô. Os dias em falta estão a ser recolhidos (ver o aviso acima,
  enquanto durar). O montante é calculado pelo açores.net, e a coluna
  `montante_tipo` diz como:
  - **preço base**: nos anúncios de concursos, o preço base do procedimento
    todo (não o de cada lote);
  - **soma de N valores**: nos atos que listam vários apoios (portarias de
    apoios a empresas, despachos da habitação), a soma dos apoios;
  - **valor** ou **maior valor**: nos outros, o maior valor em euros das
    cláusulas ou artigos (ou do texto todo, se não os tiver), sem contar
    prestações nem o custo do projeto. Num acordo de cooperação é a
    comparticipação; num aditamento, o valor novo.
  - **soma de todos os valores (método antigo)**: até 27 de novembro de 2026
    o robô somava todos os valores em euros do ato. Um valor repetido contava
    duas vezes (o Despacho n.º 694/2025 autoriza 3 175 000 € e aparece com
    6 350 000 €), o custo do projeto somava-se ao apoio, e números mal
    escritos davam somas absurdas (a Adenda n.º 5/2025 ao contrato-programa
    do HDES aparece com 159 864 847 000 €). Esses atos não foram relidos.

  Os valores que só estão em anexos (as portarias com as verbas de cada
  freguesia) não são lidos: esses atos ficam sem montante. Serve para
  encontrar atos. Para citar, leia o valor no próprio ato.
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
- **Fundos europeus**: ver as notas na página
  [Fundos europeus](/financas/fundos-europeus/#notas). Os dados do Kohesio
  estão em construção.
