import os

from openpyxl import Workbook
from openpyxl.styles import Font

from connection.auditoria_repository import (
    listar_auditorias,
    listar_marketplaces_auditoria
)


def gerar_relatorio_xlsx():
    auditorias = listar_auditorias()

    if not auditorias:
        print("\n⚠ Nenhuma auditoria encontrada.")
        return

    os.makedirs("relatorios", exist_ok=True)

    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Auditorias"

    cabecalhos = [
        "ID Auditoria",
        "Produto",
        "Estoque Consolidado",
        "Status",
        "Data",
        "Marketplace",
        "Estoque Marketplace"
    ]

    sheet.append(cabecalhos)

    for cell in sheet[1]:
        cell.font = Font(bold=True)

    for auditoria in auditorias:
        id_auditoria = auditoria[0]
        produto = auditoria[1]
        estoque_consolidado = auditoria[2]
        status = auditoria[3]
        data = auditoria[4]

        marketplaces = listar_marketplaces_auditoria(
            id_auditoria
        )

        if marketplaces:
            for marketplace in marketplaces:
                nome_marketplace = marketplace[0]
                estoque_marketplace = marketplace[1]

                sheet.append([
                    id_auditoria,
                    produto,
                    estoque_consolidado,
                    status,
                    str(data),
                    nome_marketplace,
                    estoque_marketplace
                ])
        else:
            sheet.append([
                id_auditoria,
                produto,
                estoque_consolidado,
                status,
                str(data),
                "",
                ""
            ])

    larguras = {
        "A": 15,
        "B": 30,
        "C": 20,
        "D": 20,
        "E": 22,
        "F": 20,
        "G": 22
    }

    for coluna, largura in larguras.items():
        sheet.column_dimensions[coluna].width = largura

    caminho_arquivo = "relatorios/relatorio_auditoria.xlsx"
    workbook.save(caminho_arquivo)

    print(f"""
✅ Relatório gerado com sucesso.

Local:
{caminho_arquivo}
""")