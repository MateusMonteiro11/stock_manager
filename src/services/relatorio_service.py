from connection.auditoria_repository import (
    listar_auditorias,
    listar_marketplaces_auditoria
)

# Gera um relatorio em TXT (Por enquanto, iremos gerar apenas em TXT, mas futuramente podemos expandir para PDF ou Excel)

def gerar_relatorio_txt():

    auditorias = listar_auditorias()

    if not auditorias:

        print("\n⚠ Nenhuma auditoria encontrada.")
        return

    with open(

        "relatorios/relatorio_auditoria.txt",

        "w",

        encoding="utf-8"

    ) as arquivo:

        arquivo.write(
            "====================================\n"
        )

        arquivo.write(
            "RELATÓRIO DE AUDITORIA DE ESTOQUE\n"
        )

        arquivo.write(
            "====================================\n\n"
        )

        for auditoria in auditorias:

            id_auditoria = auditoria[0]

            marketplaces = listar_marketplaces_auditoria(
                id_auditoria
            )

            arquivo.write(
                f"AUDITORIA #{auditoria[0]}\n"
            )

            arquivo.write(
                f"Produto: {auditoria[1]}\n"
            )

            arquivo.write(
                f"Estoque Consolidado: {auditoria[2]}\n"
            )

            arquivo.write(
                f"Status: {auditoria[3]}\n"
            )

            arquivo.write(
                f"Data: {auditoria[4]}\n\n"
            )

            arquivo.write(
                "ESTOQUES ENCONTRADOS\n"
            )

            for marketplace in marketplaces:

                arquivo.write(
                    f"- {marketplace[0]}: "
                    f"{marketplace[1]}\n"
                )

            arquivo.write(
                "\n------------------------------------\n\n"
            )

    print("""
✅ Relatório gerado com sucesso.

Local:
relatorios/relatorio_auditoria.txt
""")