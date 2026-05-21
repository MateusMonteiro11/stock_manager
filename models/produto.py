class Produto:

    def __init__(

        self,

        id_produto=None,

        nome="",

        sku="",

        categoria="",

        estoque_oficial=0

    ):

        self.id_produto = id_produto

        self.nome = nome

        self.sku = sku

        self.categoria = categoria

        self.estoque_oficial = estoque_oficial


    # ==========================================
    # REPRESENTAÇÃO TEXTO
    # ==========================================

    def __str__(self):

        return f"""
==================================
PRODUTO
==================================

ID: {self.id_produto}

Nome: {self.nome}

SKU: {self.sku}

Categoria: {self.categoria}

Estoque Oficial: {self.estoque_oficial}

==================================
"""