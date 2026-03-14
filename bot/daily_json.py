import json
import os
from datetime import date

from .classes import FetchError, WebData
from .constants import YESTERDAY_DATE
from .record import (
    AudiARep,
    AudiGRep,
    Diario,
    Info,
    Iniciativa,
    Interven,
    Peti,
    Requerimento,
    Voto,
)
from .utils import find_monies, parse_currency_to_number

_ALRA_KEY_MAP = {
    Info: "informacoes",
    Diario: "diarios",
    Voto: "votos",
    Iniciativa: "iniciativas",
    Interven: "intervencoes",
    Peti: "peticoes",
    AudiGRep: "audi_gr",
    AudiARep: "audi_ar",
}

_OUTPUT_DIR = os.path.join(
    os.path.dirname(__file__), "..", "docs", "_data", "daily"
)


def _joraa_item(entry: dict) -> dict:
    text_integral = entry.get("textoIntegral", "") or ""
    excerpt = text_integral[:500] if text_integral else ""
    total = sum(
        parse_currency_to_number(m)
        for m in find_monies(str(entry))
    )
    entities = [e["nome"] for e in entry.get("entidades", [])]
    return {
        "id": entry.get("id"),
        "summary": (entry.get("sumario") or "").strip(),
        "text_excerpt": excerpt,
        "human_id": entry.get("humanId"),
        "entity": entities[0] if entities else None,
        "publication": entry.get("descricaoPublicacao"),
        "total_value": total if total else None,
        "url": f"https://jo.azores.gov.pt/#/ato/{entry.get('id')}",
    }


def _base_item(entry: dict) -> dict:
    return {
        "id": entry.get("id"),
        "title": (
            entry.get("objectBriefDescription", "").strip()
        ),
        "price": entry.get("initialContractualPrice"),
        "buyer": entry.get("contracting"),
        "seller": entry.get("contracted"),
        "procedure": entry.get("contractingProcedureType"),
        "signing_date": entry.get("signingDate"),
        "url": (
            "https://www.base.gov.pt/Base4/pt/detalhe/"
            f"?type=contratos&id={entry.get('id')}"
        ),
    }


def _alra_section(alra_data: dict) -> dict:
    result = {}

    # Requerimentos are special: list of (record, prev, now)
    if Requerimento in alra_data:
        result["requerimentos"] = [
            req.to_dict(prev=prev, now=now)
            for req, prev, now in alra_data[Requerimento]
        ]

    for cls, key in _ALRA_KEY_MAP.items():
        if cls in alra_data:
            result[key] = [
                rec.to_dict() for rec in alra_data[cls]
            ]

    return result


def _portal_section(portal_data: dict) -> dict:
    return {
        k: sorted(v) if isinstance(v, (set, list)) else list(v)
        for k, v in portal_data.items()
    }


def _write_json(day_str: str, data: dict):
    os.makedirs(_OUTPUT_DIR, exist_ok=True)
    path = os.path.join(_OUTPUT_DIR, f"{day_str}.json")

    # Merge with existing file if present
    if os.path.exists(path):
        with open(path) as f:
            existing = json.load(f)
        existing.update(data)
        data = existing

    data["date"] = day_str
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def write_daily_json(web_data: WebData):
    # Collect all dates that have data
    dates_data: dict[str, dict] = {}

    # JORAA — keyed by date
    if isinstance(web_data.joraa, FetchError):
        dates_data.setdefault(
            str(YESTERDAY_DATE), {}
        )["joraa"] = {"error": str(web_data.joraa.info)}
    else:
        for day, entries in web_data.joraa.items():
            day_str = (
                day.strftime("%Y-%m-%d")
                if isinstance(day, date)
                else str(day)
            )
            dates_data.setdefault(day_str, {})["joraa"] = [
                _joraa_item(e) for e in entries
            ]

    # BASE — keyed by date
    if isinstance(web_data.base, FetchError):
        dates_data.setdefault(
            str(YESTERDAY_DATE), {}
        )["base"] = {"error": str(web_data.base.info)}
    else:
        for day, entries in web_data.base.items():
            day_str = (
                day.strftime("%Y-%m-%d")
                if isinstance(day, date)
                else str(day)
            )
            dates_data.setdefault(day_str, {})["base"] = [
                _base_item(e) for e in entries
            ]

    # ALRA — always yesterday
    yesterday_str = str(YESTERDAY_DATE)
    if isinstance(web_data.alra, FetchError):
        dates_data.setdefault(yesterday_str, {})["alra"] = {
            "error": str(web_data.alra.info)
        }
    else:
        dates_data.setdefault(yesterday_str, {})["alra"] = (
            _alra_section(web_data.alra)
        )

    # Portal — always yesterday
    if isinstance(web_data.portal, FetchError):
        dates_data.setdefault(yesterday_str, {})["portal"] = {
            "error": str(web_data.portal.info)
        }
    else:
        dates_data.setdefault(yesterday_str, {})["portal"] = (
            _portal_section(web_data.portal)
        )

    # Write one JSON file per date
    for day_str, data in dates_data.items():
        _write_json(day_str, data)
