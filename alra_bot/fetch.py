import datetime

import requests
from bs4 import BeautifulSoup

from .constants import CATEGORIAS_REQUERIMENTOS, INFO_URL, INICIATIVA_URL, VOTO_URL


def fetch_item_ids(*, url, num_pesquisa_registo):
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
    # http://base.alra.pt:82/Doc_Noticias/NI20085.pdf


def fetch_requerimentos():
    reqs_today = {}

    for i, cat in CATEGORIAS_REQUERIMENTOS.items():
        reqs_today[cat] = fetch_item_ids(
            url=f"http://base.alra.pt:82/4DACTION/w_req_prazo_resp/{i}",
            num_pesquisa_registo=4,
        )

    return reqs_today


def fetch_current_state() -> dict:
    return {
        "datetime": str(
            datetime.datetime.now(datetime.UTC).strftime("%Y-%m-%d %H:%M:%S")
        ),
        "requerimentos": fetch_requerimentos(),
        "votos": fetch_item_ids(url=VOTO_URL, num_pesquisa_registo=1),
        "informacoes": fetch_item_ids(url=INFO_URL, num_pesquisa_registo=8),
        "iniciativas": fetch_item_ids(url=INICIATIVA_URL, num_pesquisa_registo=3),
    }


def fetch_by_id(id: int, type: int, url_extra: str):
    response = requests.get(
        f"http://base.alra.pt:82/4DACTION/w_pesquisa_registo/{type}/{id}", verify=False
    )

    soup = BeautifulSoup(response.content, "html.parser")
    data_dict = {"id": id}
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
            words = 2 if type > 1 else 3
            data_dict[" ".join(link.text.split()[:words])] = (
                f"http://base.alra.pt:82/{url_extra}/" + link.get("href").split("/")[-1]
            )

    return data_dict


def fetch_requerimento(req_id):
    return fetch_by_id(req_id, 4, "Doc_Req")


def fetch_info(id):
    return fetch_by_id(id, 8, "Doc_Noticias")


def fetch_voto(id):
    return fetch_by_id(id, 1, "Doc_Voto")


def fetch_iniciativa(id):
    return fetch_by_id(id, 3, "iniciativas/iniciativas")


if __name__ == "__main__":
    print(fetch_current_state())
