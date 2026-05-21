class Auditoria:

    def __init__(

        self,

        id_auditoria=None,

        estoque_consolidado=0,

        status="CONSISTENTE",

        data_auditoria=None,

        id_produto=None

    ):

        self.id_auditoria = id_auditoria

        self.estoque_consolidado = estoque_consolidado

        self.status = status

        self.data_auditoria = data_auditoria

        self.id_produto = id_produto


    # Representação em string do objeto Auditoria

    def __str__(self):

        return f"""
==================================
AUDITORIA
==================================

ID Auditoria: {self.id_auditoria}

ID Produto: {self.id_produto}

Estoque Consolidado: {self.estoque_consolidado}

Status: {self.status}

Data Auditoria: {self.data_auditoria}

==================================
"""