"""Geração do relatório operacional de auditoria em XLSX."""

from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Font

from repositories.interfaces import ReportRepository


def _repository(repository=None) -> ReportRepository:
    if repository is not None:
        return repository
    from connection.sqlite_repositories import SQLiteAuditRepository

    return SQLiteAuditRepository()


def gerar_relatorio_xlsx(
    caminho_arquivo="relatorios/relatorio_auditoria.xlsx",
    repository=None,
):
    report_repository = _repository(repository)
    auditorias = report_repository.list_all()
    if not auditorias:
        print("\n⚠ Nenhuma auditoria encontrada.")
        return None

    destino = Path(caminho_arquivo)
    destino.parent.mkdir(parents=True, exist_ok=True)

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
        "Estoque Marketplace",
    ]
    sheet.append(cabecalhos)
    for cell in sheet[1]:
        cell.font = Font(bold=True)

    for auditoria in auditorias:
        id_auditoria, produto, estoque_consolidado, status, data = auditoria
        marketplaces = report_repository.list_marketplaces(id_auditoria)
        if marketplaces:
            for nome_marketplace, estoque_marketplace in marketplaces:
                sheet.append([
                    id_auditoria,
                    produto,
                    estoque_consolidado,
                    status,
                    str(data),
                    nome_marketplace,
                    estoque_marketplace,
                ])
        else:
            sheet.append([
                id_auditoria,
                produto,
                estoque_consolidado,
                status,
                str(data),
                "",
                "",
            ])

    for coluna, largura in {
        "A": 15,
        "B": 30,
        "C": 20,
        "D": 20,
        "E": 22,
        "F": 20,
        "G": 22,
    }.items():
        sheet.column_dimensions[coluna].width = largura

    workbook.save(destino)
    print(f"""
Relatório gerado com sucesso.

Local:
{destino}
""")
    return destino
