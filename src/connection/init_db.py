from connection.conexao import conn, cursor


def inicializar_banco():

    # Tabela de produtos
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS produtos (

        id_produto INTEGER PRIMARY KEY AUTOINCREMENT,

        nome TEXT NOT NULL,

        sku TEXT UNIQUE NOT NULL,

        categoria TEXT,

        estoque_oficial INTEGER DEFAULT 0
            CHECK(estoque_oficial >= 0)

    );
    """)

    # Tabela de marketplaces
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS marketplaces (

        id_marketplace INTEGER PRIMARY KEY AUTOINCREMENT,

        nome TEXT UNIQUE NOT NULL

    );
    """)

    # Tabela de auditorias
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS auditorias (

        id_auditoria INTEGER PRIMARY KEY AUTOINCREMENT,

        estoque_consolidado INTEGER NOT NULL,

        status TEXT NOT NULL
            CHECK(status IN (
                'CONSISTENTE',
                'DIVERGENTE',
                'REVISAR'
            )),

        data_auditoria TEXT NOT NULL,

        id_produto INTEGER NOT NULL,

        FOREIGN KEY (id_produto)
            REFERENCES produtos(id_produto)
            ON DELETE CASCADE
    );
    """)

    # Auditoria marketplace
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS auditoria_marketplace (

        id_auditoria_market INTEGER PRIMARY KEY AUTOINCREMENT,

        estoque_encontrado INTEGER NOT NULL
            CHECK(estoque_encontrado >= 0),

        id_auditoria INTEGER NOT NULL,

        id_marketplace INTEGER NOT NULL,

        FOREIGN KEY (id_auditoria)
            REFERENCES auditorias(id_auditoria)
            ON DELETE CASCADE,

        FOREIGN KEY (id_marketplace)
            REFERENCES marketplaces(id_marketplace)

    );
    """)

    # Marketplaces iniciais
    cursor.execute("""
    INSERT OR IGNORE INTO marketplaces (nome)
    VALUES
        ('Shopee'),
        ('Mercado Livre'),
        ('Amazon')
    """)

    conn.commit()

    print("Banco de dados inicializado com sucesso.")