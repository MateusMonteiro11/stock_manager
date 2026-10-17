"""Regras de negócio do cadastro e estoque interno."""

from typing import Optional

from repositories.interfaces import ProductRepository


def _repository(repository: Optional[ProductRepository] = None) -> ProductRepository:
    if repository is not None:
        return repository
    from connection.sqlite_repositories import SQLiteProductRepository

    return SQLiteProductRepository()


def cadastrar_novo_produto(nome, sku, categoria, repository=None):
    if not nome.strip():
        print("\n❌ Nome inválido.")
        return False
    if not sku.strip():
        print("\n❌ SKU inválido.")
        return False

    repo = _repository(repository)
    if repo.sku_exists(sku):
        print("\n⚠ SKU já cadastrado.")
        return False

    repo.create(nome, sku, categoria)
    return True


def listar_produtos_cadastrados(repository=None):
    return _repository(repository).list_all()


def buscar_produto(id_produto, repository=None):
    return _repository(repository).find_by_id(id_produto)


def alterar_estoque(id_produto, estoque, repository=None):
    repo = _repository(repository)
    if not repo.find_by_id(id_produto):
        print("\n⚠ Produto não encontrado.")
        return False
    if estoque < 0:
        print("\n❌ Estoque inválido.")
        return False

    repo.update_stock(id_produto, estoque)
    return True


def excluir_produto(id_produto, repository=None):
    repo = _repository(repository)
    if not repo.find_by_id(id_produto):
        print("\n⚠ Produto não encontrado.")
        return False

    repo.remove(id_produto)
    return True
