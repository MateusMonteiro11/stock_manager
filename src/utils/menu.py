import os


# Limpa buffer

def limpar_console():

    os.system('cls' if os.name == 'nt' else 'clear')

# Cabeçalho

def exibir_cabecalho():

    limpar_console()

    print("""
==================================================
        CENTRAL DE AUDITORIA DE ESTOQUE
==================================================
""")

# Menu principal

def menu_principal():

    exibir_cabecalho()

    print("""
[ 1 ] Cadastrar Produto
[ 2 ] Listar Produtos
[ 3 ] Buscar Produto
[ 4 ] Atualizar Estoque Oficial
[ 5 ] Remover Produto

[ 6 ] Realizar Auditoria
[ 7 ] Histórico de Auditorias
[ 8 ] Gerar Relatório

[ 0 ] Sair
""")

    opcao = input("Selecione uma opção: ")

    return opcao

# Menu de cadastrar um produto

def menu_cadastrar_produto():

    exibir_cabecalho()

    print("CADASTRO DE PRODUTO\n")

    nome = input("Nome do produto: ")
    sku = input("SKU do produto: ")
    categoria = input("Categoria do produto: ")

    return nome, sku, categoria


# Menu de buscar um produto

def menu_buscar_produto():

    exibir_cabecalho()

    print("BUSCAR PRODUTO\n")

    id_produto = input("Digite o ID do produto: ")

    return id_produto


# Menu de atualização de estoque

def menu_atualizar_estoque():

    exibir_cabecalho()

    print("ATUALIZAR ESTOQUE OFICIAL\n")

    id_produto = input("ID do produto: ")

    estoque = input("Novo estoque oficial: ")

    return id_produto, estoque


# Menu para remover um produto

def menu_remover_produto():

    exibir_cabecalho()

    print("REMOVER PRODUTO\n")

    id_produto = input("Digite o ID do produto: ")

    return id_produto


# Menu de auditoria, para realizar a auditoria de um produto

def menu_auditoria():

    exibir_cabecalho()

    print("REALIZAR AUDITORIA\n")

    id_produto = input("ID do produto: ")

    print("\n=== ESTOQUES ENCONTRADOS ===\n")

    shopee = input("Shopee: ")
    mercado_livre = input("Mercado Livre: ")
    amazon = input("Amazon: ")

    return (
        id_produto,
        shopee,
        mercado_livre,
        amazon
    )

# Pausa o sistema

def pausar():

    input("\nPressione ENTER para continuar...")