from dataclasses import dataclass

CRITERIOS_TEMPO_META = {
    "vermelho": "Atendimento imediato",
    "laranja": "Até 10 minutos",
    "amarelo": "Até 60 minutos",
    "verde": "Até 120 minutos",
    "azul": "Até 240 minutos",
}


@dataclass(frozen=True)
class ResultadoManchester:
    cor: str
    tempo_meta: str
    justificativa: str


def calcular_manchester(
    pas: float,
    fc: float,
    temp: float,
    spo2: float,
    dor: float = 0,
) -> ResultadoManchester:
    """Protocolo de Manchester: critérios avaliados em cascata, do mais grave
    ao mais leve; o primeiro satisfeito define a cor (docs/03-casos-uso.md, UC001)."""
    if spo2 < 90 or fc > 150 or pas < 80 or dor >= 9:
        cor = "vermelho"
        justificativa = "Sinais de risco iminente de vida (SpO2, FC, PA ou dor em nível crítico)."
    elif spo2 < 94 or fc > 120 or temp >= 39.5 or dor >= 7:
        cor = "laranja"
        justificativa = "Alteração significativa em sinais vitais ou dor intensa."
    elif spo2 < 96 or fc > 100 or temp >= 38 or dor >= 4:
        cor = "amarelo"
        justificativa = "Alteração moderada em sinais vitais ou dor relevante."
    elif dor >= 1 or fc > 90:
        cor = "verde"
        justificativa = "Sinais vitais estáveis, com queixa leve."
    else:
        cor = "azul"
        justificativa = "Sinais vitais normais, sem sinais de risco."

    return ResultadoManchester(cor=cor, tempo_meta=CRITERIOS_TEMPO_META[cor], justificativa=justificativa)
