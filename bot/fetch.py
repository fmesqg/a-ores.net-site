import asyncio
import functools
from datetime import date, datetime, timedelta

import aiohttp
import requests
from bs4 import BeautifulSoup

from bot.classes import FetchError, WebData
from bot.state import State
from bot.utils import compute_delta_ids

from .record import (
    AudiARep,
    AudiGRep,
    Diario,
    Info,
    Iniciativa,
    Interven,
    Peti,
    Record,
    Requerimento,
    Voto,
)

_ALRA_INTERNALS: dict[Record, dict] = {
    Voto: {
        "internal_db_int": 1,
        "url_prefixed_to_document": "Doc_Voto",
        "url_all_items": "http://base.alra.pt:82/4DACTION/w_recebe_pesquisa_voto?wformvalida2.x=13&wformvalida2.y=11&w_legis=XIII&w_entrada_voto=&w_entrada_voto_fim=&w_d_entrada_voto=&w_d_entrada_voto_fim=&POPtitulovoto=&w_assunto_voto=&POPpartidos=&w_d_apre_voto=&w_d_apre_voto_fim=&POPresultado=",  # noqa: E501
    },
    AudiGRep: {
        "internal_db_int": 2,
        "url_all_items": "http://base.alra.pt:82/4DACTION/w_recebe_pesquisa_audi/2?wformvalida.x=19&wformvalida.y=16&w_legis=XIII&w_numero_audi=&w_numero_audi_fim=&w_entrada_audi=&w_entrada_audi_fim=&w_d_entrada_audi=&w_d_entrada_audi_fim=&w_processo_audi=&POPtitulo=&POPcomissao=&w_assunto_audi=&w_d_envio_audi=&w_d_envio_audi_fim=&w_d_governo_audi=&w_d_governo_audi_fim=&w_d_apre1_audi=&w_d_apre1_audi_fim=&w_d_limite_audi=&w_d_limite_audi_fim=&w_d_resp_audi=&w_d_resp_audi_fim=&w_d_prorro_audi=&w_d_prorro_audi_fim=&w_d_envioar_audi=&w_d_envioar_audi_fim=&w_d_apre2_audi=&w_d_apre2_audi_fim=",  # noqa: E501
    },
    Iniciativa: {
        "internal_db_int": 3,
        "url_prefixed_to_document": "iniciativas/iniciativas",
        "url_all_items": "http://base.alra.pt:82/4DACTION/w_recebe_pesquisa_inicia/?wformvalida.x=18&wformvalida.y=23&w_legis=XIII&w_proposta_inicio=&w_proposta_fim=&POPiniciativa=&POPtema=&w_d_abertura_inicio=&w_d_abertura_fim=&w_d_apresenta_inicio=&w_d_apresenta_fim=&w_assunto_iniciativa=&POPautor_inici=&POPurgencia=&POPcomissao=&w_d_comissao_inicio=&w_d_comissao_fim=&w_d_plenario_inicio=&w_d_plenario_fim=&POPresulplena=&w_decreto_plenario=&w_titulo_publicacao=&w_sumario_publicacao=",  # noqa: E501
    },
    Requerimento: {
        "internal_db_int": 4,
        "url_prefixed_to_document": "Doc_Req",
        "categories_to_internal_int": {
            "RESPOSTA ATEMPADA": 1,
            "NO PRAZO": 2,
            "RESPOSTA TADIA": 3,
            "FORA DE PRAZO": 4,
            "JUSTIFICADO": 5,
        },
    },
    AudiARep: {
        "internal_db_int": 5,
        "url_prefixed_to_document": "Doc_Audi",
        "url_all_items": "http://base.alra.pt:82/4DACTION/w_recebe_pesquisa_audi/1%20method=?wformvalida2.x=15&wformvalida2.y=21&w_legis=XIII&w_numero_audi=&w_numero_audi_fim=&w_entrada_audi=&w_entrada_audi_fim=&w_d_entrada_audi=&w_d_entrada_audi_fim=&w_processo_audi=&w_titulo_audi=&POPcomissao=&w_assunto_audi=&w_d_envio_audi=&w_d_envio_audi_fim=&w_d_governo_audi=&w_d_governo_audi_fim=&w_d_apre1_audi=&w_d_apre1_audi_fim=&w_d_limite_audi=&w_d_limite_audi_fim=&w_d_resp_audi=&w_d_resp_audi_fim=&w_d_prorro_audi=&w_d_prorro_audi_fim=&w_d_envioar_audi=&w_d_envioar_audi_fim=&w_d_apre2_audi=&w_d_apre2_audi_fim=",  # noqa: E501
    },
    Peti: {
        "internal_db_int": 6,
        "url_prefixed_to_document": ["Peticao_abaixo", "peticao_abaixo"],
        "url_all_items": "http://base.alra.pt:82/4DACTION/w_recebe_pesquisa_peti/40?wformvalida.x=24&wformvalida.y=15&w_legis=XIII&w_numero_peti=&w_numero_peti_fim=&w_d_entrada_peti=&w_d_entrada_peti_fim=&w_assunto_peti=&w_autor_peti=&POPcomissao=&w_d_plena_peti=&w_d_plena_peti_fim=",  # noqa: E501
    },
    Info: {
        "internal_db_int": 8,
        "url_prefixed_to_document": "Doc_Noticias",
        "url_all_items": "http://base.alra.pt:82/4DACTION/w_recebe_pesquisa_informacao?wformvalida3.x=10&wformvalida3.y=21&w_legis=XIII&w_d_noticia=&w_d_noticia_fim=&POPnoticiatipo=&POPnoticiaautor=&w_assunto_noticia=",  # noqa: E501
    },
    Interven: {
        "internal_db_int": 9,
        "url_all_items": "http://base.alra.pt:82/4DACTION/w_recebe_pesquisa_inter?wformvalida2.x=3&wformvalida2.y=14&w_legis=XIII&w_d_inter=&w_d_inter_fim=&POPintergoverno=&POPinterorador=&POPpartidos=&w_assunto_inter=",  # noqa: E501
    },
    Diario: {
        "internal_db_int": 10,
        "url_prefixed_to_document": "Diario",
        "url_all_items": "http://base.alra.pt:82/4DACTION/w_recebe_pesquisa_diario?wformvalida3.x=15&wformvalida3.y=21&w_legis=XIII&w_tipo=T&w_d_diario=&w_d_diario_fim=&w_numero_diario=&w_sumario_diario=",  # noqa: E501
    },
}


def catch_requests_exceptions(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except requests.exceptions.RequestException as e:
            return FetchError(e)

    return wrapper


@catch_requests_exceptions
def fetch_alra_ids(record_type, url=None):
    internals = _ALRA_INTERNALS.get(record_type, None)
    assert internals is not None, record_type
    num_pesquisa_registo = internals["internal_db_int"]
    if not url:
        url = internals["url_all_items"]
    response = requests.get(url, verify=False, timeout=120)
    soup = BeautifulSoup(response.content, "html.parser")
    a_tags = soup.find_all("a")
    return [
        int(href.split("/")[-1])
        for a in a_tags
        if (href := a.get("href"))
        and f"/w_pesquisa_registo/{num_pesquisa_registo}/" in href
    ]


@catch_requests_exceptions
def fetch_day_joraa(date: str) -> list[dict]:
    url = (
        f"https://jo.azores.gov.pt/api/public/search/ato?fromDate={date}&toDate={date}"
    )
    response = requests.get(
        url,
    )
    if (res := response.json())["resultSize"] > 0:
        return res["list"]
    else:
        return []


@catch_requests_exceptions
def fetch_beo_all():
    url = "https://portal.azores.gov.pt/web/drot/beo-boletim-de-execu%C3%A7%C3%A3o-or%C3%A7amental"  # noqa: E501
    response = requests.get(
        url,
    )
    base_url = "https://portal.azores.gov.pt"
    soup = BeautifulSoup(response.content, "html.parser")
    a_tags = soup.find_all("a")
    return set(
        base_url + "/".join(href.split("/")[:-1])
        for a in a_tags
        if (href := a.get("href")) and "/BEO" in href
    )


@catch_requests_exceptions
def fetch_sigica_all():
    url = "https://portal.azores.gov.pt/web/drs/sigica-boletins-informativos-2024"
    response = requests.get(
        url,
    )
    base_url = "https://portal.azores.gov.pt/web/drs/"
    soup = BeautifulSoup(response.content, "html.parser")
    a_tags = soup.find_all("a")
    return set(
        base_url + href.split("/")[-1]
        for a in a_tags
        if (href := a.get("href")) and "/sigica" in href
    )


# https://portal.azores.gov.pt/web/drs/sigica-junho-2024
# https://portal.azores.gov.pt/web/drs/sigica-boletins-informativos-2024 # SIGICA 2024


@catch_requests_exceptions
async def fetch_joraa_ato(session: aiohttp.ClientSession, id):
    base_url = "https://jo.azores.gov.pt/api/public/ato/"
    async with session.get(base_url + id) as response:
        if response.status == 200:
            return await response.json()
        else:
            raise FetchError(f"Erro ao buscar ato '{id}'\nStatus: {response.status}")


@catch_requests_exceptions
def fetch_requerimentos():
    reqs_today = {}
    categories_to_internal_int: dict = _ALRA_INTERNALS[Requerimento][
        "categories_to_internal_int"
    ]
    for cat, i in categories_to_internal_int.items():
        reqs_today[cat] = fetch_alra_ids(
            Requerimento,
            url=f"http://base.alra.pt:82/4DACTION/w_req_prazo_resp/{i}",
        )
    for _, val in reqs_today.items():
        if isinstance(val, FetchError):
            return val
    return reqs_today


def pre_fetch_alra() -> dict:
    ids = {
        "audi_ar": fetch_alra_ids(record_type=AudiARep),
        "audi_gr": fetch_alra_ids(record_type=AudiGRep),
        "diarios": fetch_alra_ids(record_type=Diario),
        "informacoes": fetch_alra_ids(record_type=Info),
        "iniciativas": fetch_alra_ids(record_type=Iniciativa),
        "intervencoes": fetch_alra_ids(record_type=Interven),
        "peticoes": fetch_alra_ids(record_type=Peti),
        "requerimentos": fetch_requerimentos(),
        "votos": fetch_alra_ids(record_type=Voto),
    }
    for v in ids.values():
        if isinstance(v, FetchError):
            ids = v
            break
    return ids


def _fetch_data_dict_by_id(record_type: type, id: int):
    """low-level func that works with the internals of base.alra.pt:82 as of 2024-08-20"""
    internals = _ALRA_INTERNALS[record_type]
    internal_db_int, url_extra = (
        internals["internal_db_int"],
        internals.get("url_prefixed_to_document"),
    )
    url = f"http://base.alra.pt:82/4DACTION/w_pesquisa_registo/{internal_db_int}/{id}"
    response = requests.get(
        url,
        verify=False,
    )

    soup = BeautifulSoup(response.content, "html.parser")
    data_dict = {"id": id, "url": url}
    rows = soup.find_all("tr")

    def get_text(cell):
        return (
            cell.get_text(strip=True)
            .replace("\n", " ")
            .replace("\r", "")
            .replace(" \x95 ", "; ")
            .replace("\x95 ", "")
            .strip("; ")
        )

    for row in rows:
        cells = row.find_all("td")
        if len(cells) == 2:
            header = get_text(cells[0])
            value = get_text(cells[1])
            if header and value:
                data_dict[header] = value
        elif len(cells) == 1 and (link := cells[0].find("a")):
            # TODO yikes...  videos does not have url_extra
            url = (
                (
                    f"http://base.alra.pt:82/{url_extra}/"
                    + link.get("href").split("/")[-1]
                )
                if url_extra
                else link.get("href")
            )
            data_dict[link.text.split("-")[0].strip()] = url
    return data_dict


@catch_requests_exceptions
def fetch_record(cls: type, id: int) -> Record:
    data = _fetch_data_dict_by_id(cls, id)
    return cls(data)


@catch_requests_exceptions
def fetch_contratos_RAA(from_pub_date: str, to_pub_date: str = None):
    url = "https://www.base.gov.pt/Base4/pt/resultados/"

    headers = {
        "Host": "www.base.gov.pt",
        "User-Agent": "Mozilla/5.0",
        "Accept": "text/plain, */*; q=0.01",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "X-Requested-With": "XMLHttpRequest",
        "Origin": "https://www.base.gov.pt",
        "DNT": "1",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "Sec-GPC": "1",
        "Priority": "u=0",
    }
    query = f"tipo=0&tipocontrato=0&desdedatapublicacao={from_pub_date}&atedatapublicacao={to_pub_date}&pais=187&distrito=20&concelho=0"  # PT, RAA, 'todos' = 187, 20, 0 # noqa: 501
    data = {
        "type": "search_contratos",
        "version": "129.0",
        "query": query,
        "sort": "-initialContractualPrice",
        "size": "999",
    }

    response = requests.post(url, headers=headers, data=data)
    try:
        return response.json()["items"]
    except TypeError as e:
        raise FetchError("Problem fetching BASE") from e


def fetch_alra(delta: dict):
    _statejsonl_keys_to_simple_types = {
        # "requerimentos": Requerimento,
        "informacoes": Info,
        "diarios": Diario,
        "votos": Voto,
        "iniciativas": Iniciativa,
        "intervencoes": Interven,
        "peticoes": Peti,
        "audi_gr": AudiGRep,
        "audi_ar": AudiARep,
    }
    web_data = {}
    for k, ids in delta.items():
        if isinstance(ids, FetchError):
            web_data = ids
        if isinstance(web_data, FetchError):
            break
        if record_type := _statejsonl_keys_to_simple_types.get(k):
            web_data[record_type] = []
            for id in ids:
                rec = fetch_record(record_type, id)
                if isinstance(rec, FetchError):
                    web_data = rec
                    break
                else:
                    web_data[record_type].append(rec)
    if not isinstance(web_data, FetchError):
        web_data[Requerimento] = []
        if "requerimentos" in delta:
            if isinstance(delta["requerimentos"], FetchError):
                web_data = delta["requerimentos"]
            else:
                for id, prev, now in delta["requerimentos"]:
                    if isinstance(req := fetch_record(Requerimento, id), FetchError):
                        web_data = req
                        break
                    else:
                        web_data[Requerimento].append((req, prev, now))
    return web_data


def fetch_portal(prev_state: State):
    portal = {}
    for key, value in {
        "boletins": fetch_beo_all(),
        "sigica": fetch_sigica_all(),
    }.items():
        if not isinstance(value, FetchError):
            delta = value.difference(getattr(prev_state, key))
            portal[key] = delta
        else:
            portal = value
    return portal


def fetch_web_data(prev_state: State) -> WebData:
    async def process_joraa(joraa_dict):
        async with aiohttp.ClientSession() as session:
            joraa = {}
            for day, daily_items in joraa_dict.items():
                if isinstance(daily_items, FetchError):
                    return daily_items
                tasks = [fetch_joraa_ato(session, entry["id"]) for entry in daily_items]
                results = await asyncio.gather(*tasks, return_exceptions=True)

                joraa[day] = [
                    result for result in results if not isinstance(result, FetchError)
                ]

            return joraa

    alra_pre_fetch = pre_fetch_alra()
    if not isinstance(alra_pre_fetch, FetchError):
        delta = compute_delta_ids(prev_state, alra_pre_fetch)
        alra_web_data = fetch_alra(delta=delta)
    else:
        alra_web_data = alra_pre_fetch

    # FIXME this is begging for a function

    joraa_last: date = prev_state.last_joraa_update
    base_last: date = prev_state.last_base_update

    joraa_date_list = [
        joraa_last + timedelta(days=i)
        for i in range(1, (datetime.now().date() - joraa_last).days)
    ]
    base_date_list = [
        base_last + timedelta(days=i)
        for i in range(1, (datetime.now().date() - base_last).days)
    ]
    joraa_dict = {
        day: fetch_day_joraa(date=day.strftime("%Y-%m-%d")) for day in joraa_date_list
    }
    base_dict = {
        day: fetch_contratos_RAA(
            from_pub_date=day.strftime("%Y-%m-%d"), to_pub_date=day.strftime("%Y-%m-%d")
        )
        for day in base_date_list
    }

    for daily_items in base_dict.values():
        if isinstance(daily_items, FetchError):
            base_dict = daily_items
            break

    return WebData(
        alra=alra_web_data,
        joraa=asyncio.run(process_joraa(joraa_dict=joraa_dict)),
        base=base_dict,
        portal=fetch_portal(prev_state=prev_state),
        alra_ids=alra_pre_fetch,
    )
