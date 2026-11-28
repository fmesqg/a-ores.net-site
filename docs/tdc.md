---
title: Tribunal de Contas
layout: default
permalink: /dados/tdc/
secao: financas
---
{% include financas-nav.html %}

# Tribunal de Contas

O que o Tribunal de Contas diz, todos os anos, sobre as contas da Região. A
Secção Regional dos Açores audita a Conta da Região Autónoma dos Açores e
publica um
[Relatório e Parecer](https://www.tcontas.pt/pt-pt/ProdutosTC/PareceresTribunalContas/pareceres-craa/Paginas/pareceres-craa.aspx)
com um juízo sobre a Conta, reservas, ênfases e recomendações ao Governo
Regional. Aqui estão os números principais, o que o Tribunal disse em cada
ano e o que aconteceu às recomendações, desde o parecer sobre a Conta de 2023.
Ver também a [execução orçamental](/dados/beo/) mês a mês e os
[outros dados abertos](/dados/).

<p id="ultimo" class="ine-sub" hidden></p>

<div id="app" hidden>

<h2 id="numeros">Números</h2>
<p class="ine-sub">Milhões de euros. Escolha uma linha para a ver em gráfico.</p>
<div id="grafico" class="ine-grafico">
  <h3 id="g-titulo"></h3>
  <div id="g-area" class="g-area">
    <svg id="g-svg" role="img" aria-labelledby="g-titulo" tabindex="0"></svg>
    <div id="g-tip" class="g-tip" hidden></div>
  </div>
</div>
<div class="ine-scroll">
  <table id="tabela">
    <caption class="sr-only">Números dos pareceres, em milhões de euros, por ano</caption>
    <thead></thead><tbody></tbody>
  </table>
</div>
<p class="ine-sub" id="nota-numeros"></p>

<h2 id="parecer">O que o Tribunal disse</h2>
<div id="anos" class="ine-vista" role="group" aria-label="Parecer sobre a Conta de"></div>
<div id="texto"></div>

<h2 id="recomendacoes">Recomendações</h2>
<p class="ine-sub">Cada parecer volta às recomendações do ano anterior e diz
se foram implementadas. Uma linha por recomendação; nas colunas, o que o
parecer de cada ano disse sobre ela.</p>
<form class="ine-form" onsubmit="return false">
  <div class="ine-row">
    <label class="ine-grow">Procurar <input type="search" id="busca" placeholder="ex.: dívida, tesouraria, SNC-AP" autocomplete="off"></label>
  </div>
</form>
<div class="ine-scroll">
  <table id="recs">
    <caption class="sr-only">Recomendações do Tribunal de Contas e o seu acompanhamento</caption>
    <thead></thead><tbody></tbody>
  </table>
</div>
<p><a href="/dados/tdc.csv">tdc.csv</a> (texto dos pareceres) ·
   <a href="/dados/tdc_valores.csv">tdc_valores.csv</a> (números)</p>
</div>

<noscript><p>Esta página precisa de JavaScript. Os ficheiros <a href="/dados/tdc.csv">tdc.csv</a> e <a href="/dados/tdc_valores.csv">tdc_valores.csv</a> têm os mesmos dados.</p></noscript>

## Notas

- O texto e os números vêm dos PDF dos pareceres, lidos por
  [`bot/tdc.py`](https://github.com/fmesqg/a-ores.net-site/blob/main/bot/tdc.py).
  Cada linha dos ficheiros tem o endereço do parecer de onde saiu, que é o
  que se deve citar.
- A conta do sector público administrativo regional junta o Governo
  Regional, os serviços e fundos autónomos e as entidades públicas
  reclassificadas, já consolidada. Cada parecer traz dois anos: quando dois
  pareceres dão valores para o mesmo ano, fica o mais recente. Em 2023 este
  quadro do parecer é uma imagem; os valores desse ano vêm do parecer de 2024.
- A dívida total, a receita e a despesa que ficaram fora da Conta e as
  transferências do Estado ao abrigo do princípio da solidariedade são os
  valores, já arredondados, que o Tribunal escreve no juízo sobre a Conta.
- O estado de cada recomendação é o que o parecer do ano seguinte lhe deu
  (Apêndice I). "Desde" é o ano do parecer em que o Tribunal a fez pela
  primeira vez. O parecer de 2023 não traz esse apêndice em texto (é uma
  imagem), por isso a coluna de 2023 diz apenas se a recomendação foi feita.
- Os pareceres anteriores a 2023, com outro formato, estão na
  [página do Tribunal](https://www.tcontas.pt/pt-pt/ProdutosTC/PareceresTribunalContas/pareceres-craa/Paginas/pareceres-craa.aspx).
- Também na base de dados SQLite (tabelas `tdc` e `tdc_valores`), descrita
  em [Dados abertos](/dados/sql/).

<style>
.wrapper { max-width: min(1200px, 100%); }
.ine-form input { font: inherit; padding: .3em .4em; max-width: 100%; }
.ine-form input:focus-visible, #tabela tr:focus-visible { outline: 3px solid #268bd2; outline-offset: 1px; }
#tabela, #recs { display: table; font-size: .9em; border-collapse: collapse; width: auto; min-width: 100%; }
#tabela td.lugar { white-space: normal; min-width: 12em; }
#tabela td.lugar.n1 { padding-left: 1.6em; }
#tabela tr.n0 td { font-weight: bold; }
#tabela tr.grupo td { font-weight: normal; color: var(--s01); font-size: .9em; padding-top: 1em; }
#tabela tbody tr:not(.grupo) { cursor: pointer; }
#tabela tbody tr:not(.grupo):hover td { background: var(--s2); }
#tabela tr[aria-selected="true"] td { background: rgba(38,139,210,.15); }
#recs th, #recs td { padding: .45em .6em; vertical-align: top; text-align: left; }
#recs td.txt { min-width: 18em; max-width: 40em; }
#recs td.txt small { display: block; color: var(--s01); }
#recs td.st { white-space: nowrap; font-size: .9em; }
#recs td.desde { font-variant-numeric: tabular-nums; }
.st i { font-style: normal; display: inline-block; width: 1.2em; text-align: center; }
.st-nao i { color: #b03a2e; }
.st-parc i { color: #b07d00; }
.st-sim i { color: #2d7a2d; }
.st-outra i, .st-feita i { color: var(--s01); }
.ine-vista button:focus-visible, #g-svg:focus-visible { outline: 3px solid #268bd2; outline-offset: 1px; }
#texto h3 { font-size: 1.05em; margin: 1em 0 .3em; }
#texto .juizo { font-size: 1.05em; }
#texto li { margin-bottom: .4em; }
.ine-grafico { margin-bottom: 1em; max-width: 640px; }
#g-titulo { font-size: 1em; margin: 0 0 .3em; }
#g-svg { display: block; width: 100%; overflow: visible; }
#g-svg rect.barra { fill: #257de0; }
#g-svg rect.barra.ativa { fill: #1a5fae; }
.g-tip { position: absolute; pointer-events: none; background: #fffdf5; border: 1px solid var(--s1); border-radius: 6px; padding: .4em .6em; font-size: .85em; box-shadow: 0 2px 6px rgba(0,0,0,.12); z-index: 3; white-space: nowrap; }
@media (max-width: 640px) {
  #recs, #recs tbody, #recs tr, #recs td { display: block; min-width: 0; }
  #recs thead { display: none; }
  #recs tr { border-top: 1px solid var(--s1); padding: .5em 0; }
  #recs td { border: 0; padding: .15em 0; }
  #recs td.txt { max-width: none; }
  #recs td.st, #recs td.desde { white-space: normal; }
  #recs td[data-h]::before { content: attr(data-h) ": "; color: var(--s01); }
}
</style>

<script>
(function () {
  "use strict";
  var BUILD = "{{ site.time | date: '%s' }}";
  var $ = function (id) { return document.getElementById(id); };
  var fold = function (s) { return (s || "").normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase(); };
  // the same key as bot/tdc.py key()[:40]: letters only, "sector" = "setor"
  var key = function (s) { return fold(s).replace(/[^a-z]/g, "").replace(/sector/g, "setor").slice(0, 40); };
  var fmt = new Intl.NumberFormat("pt-PT", { minimumFractionDigits: 1, maximumFractionDigits: 1, useGrouping: "always" });
  var esc = function (s) { return String(s).replace(/[&<>"]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]; }); };
  var CONTA = "Conta do sector público administrativo regional";

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
    return rows.map(function (r) { var o = {}; cols.forEach(function (k, j) { o[k] = r[j] || ""; }); return o; });
  }

  var st = { linha: "", ano: "" };
  function readHash() {
    var h = new URLSearchParams(location.hash.slice(1));
    st.linha = h.get("linha") || ""; st.ano = h.get("ano") || ""; $("busca").value = h.get("q") || "";
  }
  function writeHash() {
    var h = new URLSearchParams();
    if (st.linha) h.set("linha", st.linha);
    if (st.ano) h.set("ano", st.ano);
    if ($("busca").value) h.set("q", $("busca").value);
    history.replaceState(null, "", "#" + h.toString());
  }

  var T = [], V = [], years = [], series = [], contas = [];

  // ---- Números ----
  function buildSeries() {
    var by = {};
    V.forEach(function (v) {
      var k = v.quadro + "|" + v.caminho;
      if (!by[k]) by[k] = { key: k, quadro: v.quadro, nome: v.rubrica, nivel: +v.nivel, ordem: +v.ordem, v: {} };
      var x = parseFloat(v.valor);
      by[k].v[v.ano] = v.unidade === "€" ? x / 1e6 : x;
      if (years.indexOf(v.ano) < 0) years.push(v.ano);
    });
    years.sort();
    series = Object.keys(by).map(function (k) { return by[k]; }).sort(function (a, b) {
      return (a.quadro === CONTA ? 0 : 1) - (b.quadro === CONTA ? 0 : 1) || a.ordem - b.ordem;
    });
    if (!series.some(function (s) { return s.key === st.linha; })) {
      var d = series.filter(function (s) { return s.nome === "Dívida total"; })[0] || series[0];
      st.linha = d ? d.key : "";
    }
  }

  function renderTable() {
    var head = "<tr><th scope=\"col\">Rubrica</th>" + years.map(function (y) { return "<th scope=\"col\" class=\"num\">" + y + "</th>"; }).join("") + "</tr>";
    $("tabela").tHead.innerHTML = head;
    var html = "", grupo = "";
    series.forEach(function (s) {
      if (s.quadro !== grupo) {
        grupo = s.quadro;
        var g = grupo === CONTA ? "Conta consolidada do sector público administrativo regional" : "Indicadores do juízo sobre a Conta";
        html += "<tr class=\"grupo\"><td colspan=\"" + (years.length + 1) + "\">" + esc(g) + "</td></tr>";
      }
      html += "<tr class=\"n" + s.nivel + "\" tabindex=\"0\" data-k=\"" + esc(s.key) + "\" aria-selected=\"" + (s.key === st.linha) + "\">" +
        "<td class=\"lugar n" + s.nivel + "\">" + esc(s.nome) + "</td>" +
        years.map(function (y) {
          var v = s.v[y];
          return v === undefined ? "<td class=\"num falta\">–</td>" : "<td class=\"num\">" + fmt.format(v) + "</td>";
        }).join("") + "</tr>";
    });
    $("tabela").tBodies[0].innerHTML = html;
  }

  function renderChart() {
    var s = series.filter(function (x) { return x.key === st.linha; })[0];
    var svg = $("g-svg");
    if (!s) { svg.innerHTML = ""; return; }
    $("g-titulo").textContent = s.nome + " (milhões de euros)";
    var ys = years.filter(function (y) { return s.v[y] !== undefined; });
    var W = Math.max(280, $("g-area").clientWidth || 600), H = 220, L = 8, R = 8, Tp = 22, B = 24;
    var vals = ys.map(function (y) { return s.v[y]; });
    var lo = Math.min(0, Math.min.apply(null, vals)), hi = Math.max(0, Math.max.apply(null, vals));
    if (lo === hi) hi = lo + 1;
    var pad = (hi - lo) * 0.12; if (hi > 0) hi += pad; if (lo < 0) lo -= pad;
    var y = function (v) { return Tp + (hi - v) / (hi - lo) * (H - Tp - B); };
    var band = (W - L - R) / Math.max(ys.length, 1), bw = Math.min(64, band * 0.55);
    var out = "<line class=\"eixo\" x1=\"" + L + "\" x2=\"" + (W - R) + "\" y1=\"" + y(0) + "\" y2=\"" + y(0) + "\"/>";
    ys.forEach(function (yr, i) {
      var v = s.v[yr], cx = L + band * (i + 0.5), y0 = y(0), y1 = y(v), top = Math.min(y0, y1), h = Math.max(1, Math.abs(y1 - y0));
      var r = Math.min(4, bw / 2, h);
      // rounded at the data end, square on the baseline
      var d = v >= 0
        ? "M" + (cx - bw / 2) + "," + y0 + "V" + (top + r) + "q0,-" + r + " " + r + ",-" + r + "H" + (cx + bw / 2 - r) + "q" + r + ",0 " + r + "," + r + "V" + y0 + "Z"
        : "M" + (cx - bw / 2) + "," + y0 + "V" + (top + h - r) + "q0," + r + " " + r + "," + r + "H" + (cx + bw / 2 - r) + "q" + r + ",0 " + r + ",-" + r + "V" + y0 + "Z";
      out += "<path class=\"barra\" fill=\"#257de0\" data-i=\"" + i + "\" d=\"" + d + "\"/>";
      out += "<rect fill=\"transparent\" data-i=\"" + i + "\" x=\"" + (cx - band / 2) + "\" y=\"" + Tp + "\" width=\"" + band + "\" height=\"" + (H - Tp - B) + "\"/>";
      out += "<text class=\"rotulo\" text-anchor=\"middle\" x=\"" + cx + "\" y=\"" + (v >= 0 ? top - 6 : top + h + 14) + "\">" + fmt.format(v) + "</text>";
      out += "<text text-anchor=\"middle\" x=\"" + cx + "\" y=\"" + (H - 6) + "\">" + yr + "</text>";
    });
    svg.setAttribute("viewBox", "0 0 " + W + " " + H);
    svg.setAttribute("height", H);
    svg.setAttribute("aria-label", s.nome + ": " + ys.map(function (yr) { return yr + " " + fmt.format(s.v[yr]) + " milhões de euros"; }).join("; "));
    svg.innerHTML = out;
    var tip = $("g-tip");
    var show = function (i) {
      if (i === null) { tip.hidden = true; return; }
      var yr = ys[i], v = s.v[yr], prev = s.v[ys[i - 1]];
      var ch = prev !== undefined && prev > 0 && v > 0 ? " (" + (v >= prev ? "+" : "") + fmt.format((v / prev - 1) * 100) + "%)" : "";
      tip.innerHTML = yr + ": <b>" + fmt.format(v) + "</b> M€" + ch;
      tip.hidden = false;
      var cx = (L + band * (i + 0.5)) / W * svg.clientWidth;
      tip.style.left = Math.max(0, Math.min(svg.clientWidth - tip.offsetWidth, cx - tip.offsetWidth / 2)) + "px";
      tip.style.top = "0px";
    };
    svg.onmousemove = function (e) { var i = e.target.getAttribute("data-i"); show(i === null ? null : +i); };
    svg.onmouseleave = function () { show(null); };
    var kb = -1;
    svg.onkeydown = function (e) {
      if (e.key !== "ArrowRight" && e.key !== "ArrowLeft") return;
      e.preventDefault(); kb = Math.max(0, Math.min(ys.length - 1, kb + (e.key === "ArrowRight" ? 1 : -1))); show(kb);
    };
    svg.onblur = function () { show(null); kb = -1; };
  }

  function pick(k) {
    st.linha = k; writeHash();
    Array.prototype.forEach.call($("tabela").tBodies[0].rows, function (tr) { tr.setAttribute("aria-selected", tr.getAttribute("data-k") === k); });
    renderChart();
  }

  // ---- O que o Tribunal disse ----
  function renderAnos() {
    if (contas.indexOf(st.ano) < 0) st.ano = contas[contas.length - 1];
    $("anos").innerHTML = contas.map(function (c) {
      return "<button type=\"button\" data-c=\"" + c + "\" aria-pressed=\"" + (c === st.ano) + "\">" + c + "</button>";
    }).join("");
    var rows = T.filter(function (r) { return r.conta === st.ano; });
    var first = rows[0] || {};
    var list = function (tipo, titulo) {
      var items = rows.filter(function (r) { return r.tipo === tipo; });
      if (!items.length) return "";
      return "<h3>" + titulo + " (" + items.length + ")</h3><ul>" + items.map(function (r) { return "<li>" + esc(r.texto) + "</li>"; }).join("") + "</ul>";
    };
    var j = rows.filter(function (r) { return r.tipo === "juízo"; })[0];
    var nrec = rows.filter(function (r) { return r.tipo === "recomendação"; }).length;
    $("texto").innerHTML =
      "<p class=\"juizo\">Sobre a Conta de " + st.ano + ", o Tribunal emitiu um <strong>" + esc(j ? j.texto.replace(/^Juízo/, "juízo") : "juízo") + "</strong>." +
      " Fez " + nrec + " recomendações (ver abaixo).</p>" +
      list("reserva", "Reservas") + list("ênfase", "Ênfases") +
      "<p>Ler: <a href=\"" + esc(first.parecer) + "\">parecer completo (PDF)</a>" +
      (first.sintese ? " · <a href=\"" + esc(first.sintese) + "\">síntese em duas páginas (PDF)</a>" : "") + "</p>";
  }

  // ---- Recomendações ----
  var recs = [];
  function buildRecs() {
    var by = {};
    T.filter(function (r) { return r.tipo === "recomendação"; }).forEach(function (r) {
      var k = key(r.texto);
      if (!by[k]) by[k] = { key: k, desde: "", anos: {} };
      var x = by[k];
      x.texto = r.texto; x.ref = r.referencia; x.parecer = r.parecer; x.ultima = r.conta;  // the latest wording
      if (r.desde && (!x.desde || r.desde < x.desde)) x.desde = r.desde;
      x.anos[r.conta] = x.anos[r.conta] || {};
      x.anos[r.conta].feita = true;
      var m = /^(.*) \((\d{4})\)$/.exec(r.situacao);
      if (m) { x.anos[m[2]] = x.anos[m[2]] || {}; x.anos[m[2]].situacao = m[1]; }
    });
    recs = Object.keys(by).map(function (k) { return by[k]; }).sort(function (a, b) {
      return (b.ultima - a.ultima) || ((a.desde || "9999") < (b.desde || "9999") ? -1 : (a.desde || "9999") > (b.desde || "9999") ? 1 : 0);
    });
  }

  function stCell(a, c, desde) {
    var h = " data-h=\"Parecer " + c + "\"";
    if (!a) return "<td class=\"st st-outra\"" + h + "><i aria-hidden=\"true\">·</i><span class=\"sr-only\">sem referência</span></td>";
    var s = a.situacao, cls = "st-feita", icon = "•", txt = "";
    if (s === "Não implementada") { cls = "st-nao"; icon = "✗"; }
    else if (s === "Parcialmente implementada") { cls = "st-parc"; icon = "◐"; }
    else if (s === "Implementada") { cls = "st-sim"; icon = "✓"; }
    else if (s) { cls = "st-outra"; icon = "–"; }
    if (s) txt = s;
    var feita = a.feita ? (desde === c ? "feita" : s ? "e reiterada" : "reiterada") : (s ? "e não reiterada" : "");
    if (a.feita && desde === c) txt = (txt ? txt + ", " : "") + "feita pela 1.ª vez";
    else if (feita) txt = txt ? txt + " " + feita : feita.charAt(0).toUpperCase() + feita.slice(1);
    return "<td class=\"st " + cls + "\"" + h + "><i aria-hidden=\"true\">" + icon + "</i> " + esc(txt) + "</td>";
  }

  function renderRecs() {
    var terms = fold($("busca").value).split(/\s+/).filter(Boolean);
    var list = recs.filter(function (r) { var s = fold(r.texto); return terms.every(function (w) { return s.indexOf(w) >= 0; }); });
    $("recs").tHead.innerHTML = "<tr><th scope=\"col\">Recomendação</th><th scope=\"col\">Desde</th>" +
      contas.map(function (c) { return "<th scope=\"col\">Parecer " + c + "</th>"; }).join("") + "</tr>";
    $("recs").tBodies[0].innerHTML = list.map(function (r) {
      return "<tr><td class=\"txt\">" + esc(r.texto) + "<small>Parecer de " + r.ultima + ", " + esc(r.ref) + "</small></td>" +
        "<td class=\"desde\" data-h=\"Desde\">" + (r.desde || "–") + "</td>" +
        contas.map(function (c) { return stCell(r.anos[c], c, r.desde); }).join("") + "</tr>";
    }).join("") || "<tr><td colspan=\"" + (contas.length + 2) + "\">Nenhuma recomendação com esses termos.</td></tr>";
  }

  // ---- arranque ----
  readHash();
  Promise.all([
    fetch("/dados/tdc.csv?v=" + BUILD).then(function (r) { if (!r.ok) throw new Error(r.status); return r.text(); }),
    fetch("/dados/tdc_valores.csv?v=" + BUILD).then(function (r) { if (!r.ok) throw new Error(r.status); return r.text(); })
  ]).then(function (res) {
    T = parseCSV(res[0]); V = parseCSV(res[1]);
    T.forEach(function (r) { if (contas.indexOf(r.conta) < 0) contas.push(r.conta); });
    contas.sort();
    buildSeries(); buildRecs();
    var last = contas[contas.length - 1], j = T.filter(function (r) { return r.conta === last && r.tipo === "juízo"; })[0];
    if (j) {
      $("ultimo").innerHTML = "Último parecer: <a href=\"" + esc(j.parecer) + "\">Conta de " + last + "</a>, " + esc(j.texto.replace(/^Juízo/, "juízo")) + ".";
      $("ultimo").hidden = false;
    }
    $("app").hidden = false;
    renderTable(); renderChart(); renderAnos(); renderRecs();
    $("nota-numeros").textContent = "Fonte: pareceres do Tribunal de Contas de " + contas[0] + " a " + last + ". A conta é a do sector público administrativo regional, consolidada.";
    $("tabela").tBodies[0].addEventListener("click", function (e) { var tr = e.target.closest("tr[data-k]"); if (tr) pick(tr.getAttribute("data-k")); });
    $("tabela").tBodies[0].addEventListener("keydown", function (e) {
      var tr = e.target.closest("tr[data-k]"); if (!tr) return;
      if (e.key === "Enter" || e.key === " ") { e.preventDefault(); pick(tr.getAttribute("data-k")); }
    });
    $("anos").addEventListener("click", function (e) { var b = e.target.closest("button[data-c]"); if (b) { st.ano = b.getAttribute("data-c"); writeHash(); renderAnos(); } });
    $("busca").addEventListener("input", function () { writeHash(); renderRecs(); });
    window.addEventListener("resize", renderChart);
  }).catch(function (e) {
    $("ultimo").textContent = "Não foi possível carregar os dados (" + e.message + ").";
    $("ultimo").hidden = false;
  });
})();
</script>
