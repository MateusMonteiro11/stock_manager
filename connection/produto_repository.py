from connection.conexao import conn, cursor

# Cadastra um novo produto

def cadastrar_produto(nome, sku, categoria):

    try:

        cursor.execute("""
        INSERT INTO produtos (
            nome,
            sku,
            categoria
        )
        VALUES (?, ?, ?)
        """, (nome, sku, categoria))

        conn.commit()

        print("\n✅ Produto cadastrado com sucesso.")

    except Exception as erro:

        print(f"\n❌ Erro ao cadastrar produto: {erro}")


# Listar os produtos cadastrados

def listar_produtos():

    try:

        cursor.execute("""
        SELECT
            id_produto,
            nome,
            sku,
            categoria,
            estoque_oficial
        FROM produtos
        ORDER BY nome
        """)

        produtos = cursor.fetchall()

        return produtos

    except Exception as erro:

        print(f"\n❌ Erro ao listar produtos: {erro}")
        return []


# Busca produto por id

def buscar_produto_por_id(id_produto):

    try:

        cursor.execute("""
        SELECT
            id_produto,
            nome,
            sku,
            categoria,
            estoque_oficial
        FROM produtos
        WHERE id_produto = ?
        """, (id_produto,))

        produto = cursor.fetchone()

        return produto

    except Exception as erro:

        print(f"\n❌ Erro ao buscar produto: {erro}")
        return None


# Busca um produto pela sku

def buscar_produto_por_sku(sku):

    try:

        cursor.execute("""
        SELECT
            id_produto,
            nome,
            sku,
            categoria,
            estoque_oficial
        FROM produtos
        WHERE sku = ?
        """, (sku,))

        produto = cursor.fetchone()

        return produto

    except Exception as erro:

        print(f"\n❌ Erro ao buscar SKU: {erro}")
        return None


# Atualiza o estoque oficial

def atualizar_estoque_oficial(id_produto, estoque):

    try:

        cursor.execute("""
        UPDATE produtos
        SET estoque_oficial = ?
        WHERE id_produto = ?
        """, (estoque, id_produto))

        conn.commit()

        print("\n✅ Estoque oficial atualizado.")

    except Exception as erro:

        print(f"\n❌ Erro ao atualizar estoque: {erro}")


# Remove um produto

def remover_produto(id_produto):

    try:

        cursor.execute("""
        DELETE FROM auditoria_marketplace
        WHERE id_auditoria IN (
            SELECT id_auditoria
            FROM auditorias
            WHERE id_produto = ?
        )
        """, (id_produto,))

        cursor.execute("""
        DELETE FROM auditorias
        WHERE id_produto = ?
        """, (id_produto,))

        cursor.execute("""
        DELETE FROM produtos
        WHERE id_produto = ?
        """, (id_produto,))

        conn.commit()

        print("\n✅ Produto removido com sucesso.")

    except Exception as erro:

        print(f"\n❌ Erro ao remover produto: {erro}")


# Verifica se um SKU já existe no banco de dados, para evitar duplicidade

def sku_existe(sku):

    try:

        cursor.execute("""
        SELECT sku
        FROM produtos
        WHERE sku = ?
        """, (sku,))

        resultado = cursor.fetchone()

        return resultado is not None

    except Exception as erro:

        print(f"\n❌ Erro ao verificar SKU: {erro}")
        return False