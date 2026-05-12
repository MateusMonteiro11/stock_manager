from utils.menu import (
    menu_principal,
    menu_cadastrar_produto,
    menu_buscar_produto,
    menu_atualizar_estoque,
    menu_remover_produto,
    menu_auditoria,
    pausar
)

from utils.validacoes import (
    validar_inteiro,
    validar_estoque
)

from services.estoque_service import (
    cadastrar_novo_produto,
    exibir_produtos,
    exibir_produto,
    alterar_estoque,
    excluir_produto
)

from services.auditoria_service import (
    realizar_auditoria
)

from services.relatorio_service import (
    gerar_relatorio_txt
)

from connection.auditoria_repository import (
    listar_auditorias
)


# Loop
while True:

    opcao = menu_principal()

    # Cadastra um produto
    if opcao == "1":

        nome, sku, categoria = menu_cadastrar_produto()

        cadastrar_novo_produto(
            nome,
            sku,
            categoria
        )

        pausar()

    # Lista produtos cadastrados
    elif opcao == "2":

        exibir_produtos()

        pausar()

    # Busca um produto
    elif opcao == "3":

        id_produto = menu_buscar_produto()

        id_produto = validar_inteiro(
            id_produto
        )

        if id_produto is not None:

            exibir_produto(id_produto)

        pausar()

    # Atualiza o estoque de um produto
    elif opcao == "4":

        id_produto, estoque = (
            menu_atualizar_estoque()
        )

        id_produto = validar_inteiro(
            id_produto
        )

        estoque = validar_estoque(
            estoque
        )

        if (

            id_produto is not None
            and estoque is not None

        ):

            alterar_estoque(
                id_produto,
                estoque
            )

        pausar()

    # Remove um produto
    elif opcao == "5":

        id_produto = menu_remover_produto()

        id_produto = validar_inteiro(
            id_produto
        )

        if id_produto is not None:

            excluir_produto(id_produto)

        pausar()

    # Realiza auditorias
    elif opcao == "6":

        (

            id_produto,
            shopee,
            mercado_livre,
            amazon

        ) = menu_auditoria()

        id_produto = validar_inteiro(
            id_produto
        )

        shopee = validar_estoque(
            shopee
        )

        mercado_livre = validar_estoque(
            mercado_livre
        )

        amazon = validar_estoque(
            amazon
        )

        if (

            id_produto is not None
            and shopee is not None
            and mercado_livre is not None
            and amazon is not None

        ):

            realizar_auditoria(

                id_produto,

                shopee,

                mercado_livre,

                amazon

            )

        pausar()

    # Historico de auditorias
    elif opcao == "7":

        auditorias = listar_auditorias()

        if not auditorias:

            print("\n⚠ Nenhuma auditoria encontrada.")

        else:

            print("""
==================================
HISTÓRICO DE AUDITORIAS
==================================
""")

            for auditoria in auditorias:

                print(f"""
ID Auditoria: {auditoria[0]}

Produto: {auditoria[1]}

Estoque Consolidado:
{auditoria[2]}

Status:
{auditoria[3]}

Data:
{auditoria[4]}

----------------------------------
""")

        pausar()

    # Gera o relatorio
    elif opcao == "8":

        gerar_relatorio_txt()

        pausar()

    # Sai do sistema
    elif opcao == "0":

        print("\nEncerrando sistema...")
        break

    # Opção invalida
    else:

        print("\n❌ Opção inválida.")

        pausar()