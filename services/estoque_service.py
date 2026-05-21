from connection.produto_repository import (
    cadastrar_produto,
    listar_produtos,
    buscar_produto_por_id,
    atualizar_estoque_oficial,
    remover_produto,
    sku_existe
)

# Cadastra um novo produto no banco

def cadastrar_novo_produto(nome, sku, categoria):

    if not nome.strip():

        print("\n❌ Nome inválido.")
        return

    if not sku.strip():

        print("\n❌ SKU inválido.")
        return

    if sku_existe(sku):

        print("\n⚠ SKU já cadastrado.")
        return

    cadastrar_produto(nome, sku, categoria)


# Exibe os produtos do banco

def exibir_produtos():

    produtos = listar_produtos()

    if not produtos:

        print("\n⚠ Nenhum produto cadastrado.")
        return

    print("\n==============================")
    print("LISTA DE PRODUTOS")
    print("==============================")

    for produto in produtos:

        print(f"""
ID: {produto[0]}
Nome: {produto[1]}
SKU: {produto[2]}
Categoria: {produto[3]}
Estoque Oficial: {produto[4]}
------------------------------
""")

# Exibe um produto por ID

def exibir_produto(id_produto):

    produto = buscar_produto_por_id(id_produto)

    if not produto:

        print("\n⚠ Produto não encontrado.")
        return

    print(f"""
==============================
PRODUTO ENCONTRADO
==============================

ID: {produto[0]}
Nome: {produto[1]}
SKU: {produto[2]}
Categoria: {produto[3]}
Estoque Oficial: {produto[4]}
""")

# Altera o estoque oficial de um produto

def alterar_estoque(id_produto, estoque):

    produto = buscar_produto_por_id(id_produto)

    if not produto:

        print("\n⚠ Produto não encontrado.")
        return

    if estoque < 0:

        print("\n❌ Estoque inválido.")
        return

    atualizar_estoque_oficial(id_produto, estoque)


# Excluir um produto

def excluir_produto(id_produto):

    produto = buscar_produto_por_id(id_produto)

    if not produto:

        print("\n⚠ Produto não encontrado.")
        return

    remover_produto(id_produto)