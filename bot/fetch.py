import datetime

import requests
from bs4 import BeautifulSoup

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
    # 1 - votos
    # 2 - gov rep
    # 3 - iniciativas
    # 4 - requerimentos
    # 5 - assembleia republica
    # 6 - petições
    # 7 - programa gov reg (? unused)
    # 8 - infos
    # 9 - intervenções
    # 10- diários
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


def fetch_all_ids(record_type, url=None):
    internals = _ALRA_INTERNALS.get(record_type, None)
    assert internals is not None, record_type
    num_pesquisa_registo = internals["internal_db_int"]
    if not url:
        url = internals["url_all_items"]
    response = requests.get(
        url,
        verify=False,
    )
    soup = BeautifulSoup(response.content, "html.parser")
    a_tags = soup.find_all("a")
    return [
        int(href.split("/")[-1])
        for a in a_tags
        if (href := a.get("href"))
        and f"/w_pesquisa_registo/{num_pesquisa_registo}/" in href
    ]


def fetch_day_joraa(date):
    url = (
        f"https://jo.azores.gov.pt/api/public/search/ato?fromDate={date}&toDate={date}"
    )
    response = requests.get(
        url,
    )
    if (res := response.json())["resultSize"] > 0:
        return res["list"]


def fetch_beo_all():
    url = "https://portal.azores.gov.pt/web/drot/beo-boletim-de-execu%C3%A7%C3%A3o-or%C3%A7amental"  # noqa: E501
    response = requests.get(
        url,
    )
    base_url = "https://portal.azores.gov.pt"
    soup = BeautifulSoup(response.content, "html.parser")
    a_tags = soup.find_all("a")
    return [
        base_url + "/".join(href.split("/")[:-1])
        for a in a_tags
        if (href := a.get("href")) and "/BEO" in href
    ]


def fetch_sigica_all():
    url = "https://portal.azores.gov.pt/web/drs/sigica-boletins-informativos-2024"
    response = requests.get(
        url,
    )
    base_url = "https://portal.azores.gov.pt/web/drs/"
    soup = BeautifulSoup(response.content, "html.parser")
    a_tags = soup.find_all("a")
    return [
        base_url + href.split("/")[-1]
        for a in a_tags
        if (href := a.get("href")) and "/sigica" in href
    ]


# https://portal.azores.gov.pt/web/drs/sigica-junho-2024
# https://portal.azores.gov.pt/web/drs/sigica-boletins-informativos-2024 # SIGICA 2024


def fetch_joraa_ato(id):
    base_url = "https://jo.azores.gov.pt/api/public/ato/"
    return requests.get(
        base_url + id,
    )


def fetch_requerimentos():
    reqs_today = {}
    categories_to_internal_int: dict = _ALRA_INTERNALS[Requerimento][
        "categories_to_internal_int"
    ]
    for cat, i in categories_to_internal_int.items():
        reqs_today[cat] = fetch_all_ids(
            Requerimento,
            url=f"http://base.alra.pt:82/4DACTION/w_req_prazo_resp/{i}",
        )

    return reqs_today


def fetch_current_state() -> dict:
    return {
        "datetime": str(
            datetime.datetime.now(datetime.UTC).strftime("%Y-%m-%d %H:%M:%S")
        ),
        "audi_ar": fetch_all_ids(AudiARep),
        "audi_gr": fetch_all_ids(AudiGRep),
        "diarios": fetch_all_ids(Diario),
        "informacoes": fetch_all_ids(Info),
        "iniciativas": fetch_all_ids(Iniciativa),
        "intervencoes": fetch_all_ids(Interven),
        "peticoes": fetch_all_ids(Peti),
        "requerimentos": fetch_requerimentos(),
        "votos": fetch_all_ids(Voto),
        "boletins": fetch_beo_all(),
        "sigica": fetch_sigica_all(),
    }


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


def fetch_record(cls: type, id: int) -> Record:
    data = _fetch_data_dict_by_id(cls, id)
    return cls(data)


def fetch_contratos_RAA(from_pub_date, to_pub_date=None):
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
    return response.json()["items"]
