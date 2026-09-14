"""Adapters das funções SQLite atuais para as interfaces dos services."""

from contracts.inventory_snapshot import Marketplace
from connection import auditoria_repository, produto_repository


class SQLiteProductRepository:
    def create(self, name, sku, category):
        return produto_repository.cadastrar_produto(name, sku, category)

    def list_all(self):
        return produto_repository.listar_produtos()

    def find_by_id(self, product_id):
        return produto_repository.buscar_produto_por_id(product_id)

    def update_stock(self, product_id, quantity):
        return produto_repository.atualizar_estoque_oficial(product_id, quantity)

    def remove(self, product_id):
        return produto_repository.remover_produto(product_id)

    def sku_exists(self, sku):
        return produto_repository.sku_existe(sku)


class SQLiteAuditRepository:
    def create(self, consolidated_stock, status, audited_at, product_id):
        return auditoria_repository.criar_auditoria(
            consolidated_stock,
            status,
            audited_at,
            product_id,
        )

    def save_marketplace_stock(self, found_stock, audit_id, marketplace):
        saved = auditoria_repository.salvar_estoque_marketplace(
            found_stock,
            audit_id,
            Marketplace.from_value(marketplace),
        )
        if not saved:
            raise RuntimeError("Não foi possível persistir o estoque da auditoria.")
        return saved

    def list_all(self):
        return auditoria_repository.listar_auditorias()

    def list_marketplaces(self, audit_id):
        return auditoria_repository.listar_marketplaces_auditoria(audit_id)
