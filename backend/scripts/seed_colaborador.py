"""Bootstrap: cria um colaborador diretamente no banco, sem passar pela API.

Necessario porque POST /api/colaboradores exige um colaborador ja autenticado
(RBAC) - sem este script nao haveria como criar o primeiro colaborador do
sistema.

Uso: python scripts/seed_colaborador.py --matricula 000001 --pin 1234 \
    --nome "Admin Inicial" --perfil medico
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.core.database import SessionLocal
from app.core.security import hash_pin
from app.models.colaborador import PERFIS_COLABORADOR, Colaborador


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--matricula", required=True, help="6 digitos numericos")
    parser.add_argument("--pin", required=True, help="4 digitos numericos")
    parser.add_argument("--nome", required=True)
    parser.add_argument("--perfil", required=True, choices=PERFIS_COLABORADOR)
    args = parser.parse_args()

    if not (args.matricula.isdigit() and len(args.matricula) == 6):
        parser.error("--matricula deve ter exatamente 6 digitos numericos")
    if not (args.pin.isdigit() and len(args.pin) == 4):
        parser.error("--pin deve ter exatamente 4 digitos numericos")

    db = SessionLocal()
    try:
        existente = db.query(Colaborador).filter(Colaborador.matricula == args.matricula).first()
        if existente is not None:
            parser.error(f"matricula {args.matricula} ja cadastrada")

        colaborador = Colaborador(
            matricula=args.matricula,
            pin_hash=hash_pin(args.pin),
            nome=args.nome,
            perfil=args.perfil,
        )
        db.add(colaborador)
        db.commit()
        print(f"Colaborador {args.matricula} ({args.perfil}) criado com sucesso.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
