---
title: RSS
layout: default
permalink: /rsss
---
## Como seguir as autualizações automáticas

1. [Escolhe o teu leitor de RSS](https://lifehacker.com/tech/best-rss-readers). Eu uso:
    1. [Feeder](https://play.google.com/store/apps/details?id=com.nononsenseapps.feeder.play), para Android.
    2. [Feedbro](https://addons.mozilla.org/en-US/firefox/addon/feedbroreader/) para Firefox.

2. Descarrega um ficheiro `.opml` — ficheiro único que permite seguir vários feeds pré-definidos. Exemplos:
    * [Ficheiro com todos os RSS do Açores.net](/assets/açores-net.opml)
    * [Ficheiro com os RSS seguidos por Francisco Mesquita](/assets/exported-rss-feeds-francisco.opml)

3. No leitor de RSS, seleciona `Import feeds from OPML` ou equivalente e faz upload do ficheiro descarregado.
    * ![rss-add](/assets/img/rss-add.jpeg){: width="250"}
4. Já está! Segue as novidades no teu leitor de RSS.
    * ![rss-home](/assets/img/rss-home.jpeg){: width="250"}
    * ![rss-single-feed](/assets/img/rss-single-feed.jpeg){: width="250"}
    * ![rss-single-entry](/assets/img/rss-single-entry.jpeg){: width="250"}

Alternativamente, é possível adicionar um feed RSS de cada vez, através da hipótese `Add feed` ou equivalente. Nesse caso, será necessário copiar e colar cada URL — por exemplo `https://xn--aores-yra.net/rss/alra.xml`. Neste caso, carrega nos _links_ abaixo com o botão direito e seleciona  `Copy link` ou equivalente.

### Feeds RSS (individualmente)

<p class="feed-subscribe">
    <a href="rss/alra.xml">
    <svg class="svg-icon orange">
        <use xlink:href="{{ 'assets/minima-social-icons.svg#rss' | relative_url }}"></use>
    </svg><span>ALRA feed</span>
    </a>
</p>

<p class="feed-subscribe">
    <a href="rss/joraa.xml">
    <svg class="svg-icon orange">
        <use xlink:href="{{ 'assets/minima-social-icons.svg#rss' | relative_url }}"></use>
    </svg><span>JORAA feed</span>
    </a>
</p>

<p class="feed-subscribe">
    <a href="rss/base.xml">
    <svg class="svg-icon orange">
        <use xlink:href="{{ 'assets/minima-social-icons.svg#rss' | relative_url }}"></use>
    </svg><span>BASE feed</span>
    </a>
</p>

<p class="feed-subscribe">
    <a href="rss/portal.xml">
    <svg class="svg-icon orange">
        <use xlink:href="{{ 'assets/minima-social-icons.svg#rss' | relative_url }}"></use>
    </svg><span>portal.azores.gov.pt feed</span>
    </a>
</p>

<p class="feed-subscribe">
    <a href="{{ site.feed.path | default: 'feed.xml' | absolute_url }}">
    <svg class="svg-icon orange">
        <use xlink:href="{{ 'assets/minima-social-icons.svg#rss' | relative_url }}"></use>
    </svg><span>feed posts não automáticos</span>
    </a>
</p>
