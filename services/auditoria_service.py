from datetime import datetime

from connection.auditoria_repository import (
    criar_auditoria,
    salvar_estoque_marketplace
)

from connection.produto_repository import (
    buscar_produto_por_id,
    atualizar_estoque_oficial
)

# Define o status da auditoria com base nos estoques dos marketplaces

def definir_status(estoques):

    if len(set(estoques)) == 1:

        return "CONSISTENTE"

    return "DIVERGENTE"


# Consolida o estoque

def consolidar_estoque(estoques):

    return min(estoques)


# Realiza a auditoria de um produto

def realizar_auditoria(

    id_produto,

    estoque_shopee,

    estoque_ml,

    estoque_amazon

):

    produto = buscar_produto_por_id(id_produto)

    if not produto:

        print("\n⚠ Produto não encontrado.")
        return

    estoques = [

        estoque_shopee,
        estoque_ml,
        estoque_amazon

    ]

    status = definir_status(estoques)

    estoque_consolidado = consolidar_estoque(estoques)

    data_auditoria = datetime.now().strftime(
        "%d/%m/%Y %H:%M:%S"
    )

    id_auditoria = criar_auditoria(

        estoque_consolidado,
        status,
        data_auditoria,
        id_produto

    )

    if not id_auditoria:

        return

    # ==========================================
    # Marketplaces fixos, podem ser alterados futuramente.
    # 1 = Shopee
    # 2 = Mercado Livre
    # 3 = Amazon
    # ==========================================

    salvar_estoque_marketplace(

        estoque_shopee,
        id_auditoria,
        1

    )

    salvar_estoque_marketplace(

        estoque_ml,
        id_auditoria,
        2

    )

    salvar_estoque_marketplace(

        estoque_amazon,
        id_auditoria,
        3

    )

    atualizar_estoque_oficial(

        id_produto,
        estoque_consolidado

    )

    print("\n===================================")
    print("AUDITORIA REALIZADA COM SUCESSO")
    print("===================================")

    print(f"""
Produto: {produto[1]}

Shopee: {estoque_shopee}
Mercado Livre: {estoque_ml}
Amazon: {estoque_amazon}

Status: {status}

Estoque Consolidado:
{estoque_consolidado}
""")