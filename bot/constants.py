from datetime import date, datetime, timedelta

CATEGORIAS_REQUERIMENTOS = [
    "RESPOSTA ATEMPADA",
    "NO PRAZO",
    "RESPOSTA TADIA",
    "FORA DE PRAZO",
    "JUSTIFICADO",
]

STATE_FILE = "state.json"
OLD_STATE_FILE = "state.jsonl"  # until 2026-11: one line per run
YESTERDAY_DATE: date = date.today() - timedelta(days=1)
NOW_DATETIME: datetime = datetime.now()
