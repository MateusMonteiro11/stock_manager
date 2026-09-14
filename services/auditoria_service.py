"""Regras de auditoria para os marketplaces atuais do MyStock."""

from datetime import datetime
from typing import Iterable, Optional

from contracts.inventory_snapshot import Marketplace
from repositories.interfaces import AuditRepository, ProductRepository


def _repositories(
    product_repository: Optional[ProductRepository] = None,
    audit_repository: Optional[AuditRepository] = None,
):
    if product_repository is None or audit_repository is None:
        from connection.sqlite_repositories import (
            SQLiteAuditRepository,
            SQLiteProductRepository,
        )

        product_repository = product_repository or SQLiteProductRepository()
        audit_repository = audit_repository or SQLiteAuditRepository()
    return product_repository, audit_repository


def definir_status(estoques: Iterable[int]):
    return "CONSISTENTE" if len(set(estoques)) == 1 else "DIVERGENTE"


def consolidar_estoque(estoques: Iterable[int]):
    return min(estoques)


def listar_historico_auditorias(audit_repository=None):
    if audit_repository is None:
        from connection.sqlite_repositories import SQLiteAuditRepository

        audit_repository = SQLiteAuditRepository()
    return audit_repository.list_all()


def realizar_auditoria(
    id_produto,
    estoque_shopee,
    estoque_ml,
    product_repository=None,
    audit_repository=None,
):
    product_repo, audit_repo = _repositories(product_repository, audit_repository)
    produto = product_repo.find_by_id(id_produto)
    if not produto:
        print("\n⚠ Produto não encontrado.")
        return False

    estoques_por_marketplace = {
        Marketplace.SHOPEE: estoque_shopee,
        Marketplace.MERCADO_LIVRE: estoque_ml,
    }
    estoques = tuple(estoques_por_marketplace.values())
    status = definir_status(estoques)
    estoque_consolidado = consolidar_estoque(estoques)
    data_auditoria = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    id_auditoria = audit_repo.create(
        estoque_consolidado,
        status,
        data_auditoria,
        id_produto,
    )
    if not id_auditoria:
        return False

    for marketplace, estoque in estoques_por_marketplace.items():
        audit_repo.save_marketplace_stock(estoque, id_auditoria, marketplace)

    product_repo.update_stock(id_produto, estoque_consolidado)

    print("\n===================================")
    print("AUDITORIA REALIZADA COM SUCESSO")
    print("===================================")
    print(f"""
Produto: {produto[1]}

Shopee: {estoque_shopee}
Mercado Livre: {estoque_ml}

Status: {status}

Estoque Consolidado:
{estoque_consolidado}
""")
    return True
