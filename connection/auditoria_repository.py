from connection.conexao import conn, cursor
from contracts.inventory_snapshot import Marketplace

# Cria a auditoria

def criar_auditoria(

    estoque_consolidado,
    status,
    data_auditoria,
    id_produto

):

    try:

        cursor.execute("""
        INSERT INTO auditorias (

            estoque_consolidado,
            status,
            data_auditoria,
            id_produto

        )
        VALUES (?, ?, ?, ?)
        """, (

            estoque_consolidado,
            status,
            data_auditoria,
            id_produto

        ))

        conn.commit()

        return cursor.lastrowid

    except Exception as erro:

        print(f"\n❌ Erro ao criar auditoria: {erro}")
        return None

# Salva o estoque encontrado no marketplace, associando com a auditoria e o marketplace

def salvar_estoque_marketplace(

    estoque_encontrado,
    id_auditoria,
    marketplace

):

    try:

        marketplace = Marketplace.from_value(marketplace)
        cursor.execute(
            "SELECT id_marketplace FROM marketplaces WHERE nome = ?",
            (marketplace.display_name,),
        )
        registro_marketplace = cursor.fetchone()
        if not registro_marketplace:
            raise ValueError("Marketplace não cadastrado no banco.")

        cursor.execute("""
        INSERT INTO auditoria_marketplace (

            estoque_encontrado,
            id_auditoria,
            id_marketplace

        )
        VALUES (?, ?, ?)
        """, (

            estoque_encontrado,
            id_auditoria,
            registro_marketplace[0]

        ))

        conn.commit()

        return True

    except Exception as erro:

        print(f"\n❌ Erro ao salvar marketplace: {erro}")
        return False


# Faz a listagem de auditorias

def listar_auditorias():

    try:

        cursor.execute("""
        SELECT

            a.id_auditoria,
            p.nome,
            a.estoque_consolidado,
            a.status,
            a.data_auditoria

        FROM auditorias a

        INNER JOIN produtos p
            ON a.id_produto = p.id_produto

        ORDER BY a.data_auditoria DESC
        """)

        auditorias = cursor.fetchall()

        return auditorias

    except Exception as erro:

        print(f"\n❌ Erro ao listar auditorias: {erro}")
        return []
    
# Busca a auditoria pelo ID

def buscar_auditoria_por_id(id_auditoria):

    try:

        cursor.execute("""
        SELECT

            a.id_auditoria,
            p.nome,
            a.estoque_consolidado,
            a.status,
            a.data_auditoria

        FROM auditorias a

        INNER JOIN produtos p
            ON a.id_produto = p.id_produto

        WHERE a.id_auditoria = ?
        """, (id_auditoria,))

        auditoria = cursor.fetchone()

        return auditoria

    except Exception as erro:

        print(f"\n❌ Erro ao buscar auditoria: {erro}")
        return None

# Faz as lista dos marketplaces da auditoria, trazendo o nome do marketplace e o estoque encontrado

def listar_marketplaces_auditoria(id_auditoria):

    try:

        supported_names = tuple(
            marketplace.display_name for marketplace in Marketplace
        )
        placeholders = ", ".join("?" for _ in supported_names)

        cursor.execute(f"""
        SELECT

            m.nome,
            am.estoque_encontrado

        FROM auditoria_marketplace am

        INNER JOIN marketplaces m
            ON am.id_marketplace = m.id_marketplace

        WHERE am.id_auditoria = ?
          AND m.nome IN ({placeholders})

        ORDER BY m.nome
        """, (id_auditoria,) + supported_names)

        marketplaces = cursor.fetchall()

        return marketplaces

    except Exception as erro:

        print(f"\n❌ Erro ao listar marketplaces: {erro}")
        return []
