"""Opcional: recria os CSVs a partir do ZIP oficial UCI."""
import argparse
from ecolar_ia.dados import preparar

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--zip", help="Caminho para o ZIP original já baixado")
    args = parser.parse_args()
    preparar(args.zip)
