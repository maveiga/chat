from typing import List, Dict


class VehicleView:

    @staticmethod
    def format_results(vehicles: List[Dict]) -> str:
        if not vehicles:
            return "Nenhum veículo encontrado com esses critérios."

        result = f"\nEncontrei {len(vehicles)} veículo(s):\n\n"

        for i, v in enumerate(vehicles, 1):
            result += f"{i}. {v['marca']} {v['modelo']} ({v['ano']})\n"
            result += f"Cor: {v['cor']}\n"
            result += f"KM: {v['quilometragem']:,}\n"
            result += f"Preço: R$ {v['preco']:,.2f}\n"
            result += f"Combustível: {v['combustivel']}\n"
            result += f"Transmissão: {v['transmissao']}\n\n"

        return result
