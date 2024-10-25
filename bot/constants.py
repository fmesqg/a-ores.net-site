from datetime import date, datetime, timedelta

CATEGORIAS_REQUERIMENTOS = [
    "RESPOSTA ATEMPADA",
    "NO PRAZO",
    "RESPOSTA TADIA",
    "FORA DE PRAZO",
    "JUSTIFICADO",
]

STATE_FILE = "state.jsonl"
YESTERDAY_DATE: str = (date.today() - timedelta(days=1)).strftime("%Y-%m-%d")
NOW_DATETIME: str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
