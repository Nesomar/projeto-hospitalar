import pytest

from app.services.manchester import calcular_manchester


@pytest.mark.parametrize(
    "vitais,cor_esperada",
    [
        ({"pas": 100, "fc": 80, "temp": 36.5, "spo2": 89, "dor": 0}, "vermelho"),  # spo2 < 90
        ({"pas": 100, "fc": 151, "temp": 36.5, "spo2": 98, "dor": 0}, "vermelho"),  # fc > 150
        ({"pas": 79, "fc": 80, "temp": 36.5, "spo2": 98, "dor": 0}, "vermelho"),  # pas < 80
        ({"pas": 100, "fc": 80, "temp": 36.5, "spo2": 98, "dor": 9}, "vermelho"),  # dor >= 9
        ({"pas": 100, "fc": 80, "temp": 36.5, "spo2": 93, "dor": 0}, "laranja"),  # spo2 < 94
        ({"pas": 100, "fc": 121, "temp": 36.5, "spo2": 98, "dor": 0}, "laranja"),  # fc > 120
        ({"pas": 100, "fc": 80, "temp": 39.5, "spo2": 98, "dor": 0}, "laranja"),  # temp >= 39.5
        ({"pas": 100, "fc": 80, "temp": 36.5, "spo2": 98, "dor": 7}, "laranja"),  # dor >= 7
        ({"pas": 100, "fc": 80, "temp": 36.5, "spo2": 95, "dor": 0}, "amarelo"),  # spo2 < 96
        ({"pas": 100, "fc": 101, "temp": 36.5, "spo2": 98, "dor": 0}, "amarelo"),  # fc > 100
        ({"pas": 100, "fc": 80, "temp": 38.0, "spo2": 98, "dor": 0}, "amarelo"),  # temp >= 38
        ({"pas": 100, "fc": 80, "temp": 36.5, "spo2": 98, "dor": 4}, "amarelo"),  # dor >= 4
        ({"pas": 100, "fc": 91, "temp": 36.5, "spo2": 98, "dor": 0}, "verde"),  # fc > 90
        ({"pas": 100, "fc": 80, "temp": 36.5, "spo2": 98, "dor": 1}, "verde"),  # dor >= 1
        ({"pas": 100, "fc": 80, "temp": 36.5, "spo2": 98, "dor": 0}, "azul"),  # tudo normal
        ({"pas": 200, "fc": 60, "temp": 36.0, "spo2": 100, "dor": 0}, "azul"),
    ],
)
def test_classificacao_manchester(vitais, cor_esperada):
    resultado = calcular_manchester(**vitais)
    assert resultado.cor == cor_esperada


def test_cascata_prioriza_criterio_mais_grave():
    # dor=9 (vermelho) e temp=39.5 (laranja) simultaneos -> vence o mais grave
    resultado = calcular_manchester(pas=100, fc=80, temp=39.5, spo2=98, dor=9)
    assert resultado.cor == "vermelho"


def test_tempo_meta_por_cor():
    assert calcular_manchester(pas=100, fc=80, temp=36.5, spo2=98, dor=0).tempo_meta == "Até 240 minutos"
    assert calcular_manchester(pas=70, fc=80, temp=36.5, spo2=98, dor=0).tempo_meta == "Atendimento imediato"
