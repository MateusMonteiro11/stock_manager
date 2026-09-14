import copy
import json
from pathlib import Path
import sqlite3
import unittest

from contracts.inventory_snapshot import (
    InventorySnapshot,
    InventoryStatus,
    Marketplace,
)
from connection.init_db import inicializar_banco
from integrations.mercadolivre.adapter import MercadoLivreAdapter
from integrations.mercadolivre.normalizer import MercadoLivreInventoryNormalizer
from integrations.shopee.adapter import ShopeeAdapter
from integrations.shopee.normalizer import ShopeeInventoryNormalizer
from repositories.memory_sync_repository import InMemorySyncRepository
from services.sync_service import SyncRunStatus, SyncService, SyncStatus


FIXTURES = Path(__file__).parent / "fixtures"


def load_fixture(name):
    with (FIXTURES / name).open(encoding="utf-8") as fixture:
        return json.load(fixture)


class FixtureClient:
    def __init__(self, payload):
        self.payload = payload
        self.authenticated = False

    def authenticate(self):
        self.authenticated = True

    def get_account(self):
        return {}

    def get_inventory_payload(self):
        return self.payload

    def health_check(self):
        return True


class FailingClient(FixtureClient):
    def get_inventory_payload(self):
        raise RuntimeError("access_token=SEGREDO_QUE_NAO_PODE_VAZAR")


class InventoryNormalizationTests(unittest.TestCase):
    def test_normaliza_mercado_livre_para_inventory_snapshot(self):
        snapshots = MercadoLivreInventoryNormalizer().normalize(
            load_fixture("mercadolivre_inventory.json")
        )

        self.assertEqual(len(snapshots), 1)
        snapshot = snapshots[0]
        self.assertIsInstance(snapshot, InventorySnapshot)
        self.assertEqual(snapshot.marketplace, Marketplace.MERCADO_LIVRE)
        self.assertEqual(snapshot.external_item_id, "MLB123456789")
        self.assertEqual(snapshot.quantity, 17)
        self.assertEqual(snapshot.status, InventoryStatus.ACTIVE)

    def test_normaliza_shopee_para_inventory_snapshot(self):
        snapshots = ShopeeInventoryNormalizer().normalize(
            load_fixture("shopee_inventory.json")
        )

        self.assertEqual(len(snapshots), 1)
        snapshot = snapshots[0]
        self.assertIsInstance(snapshot, InventorySnapshot)
        self.assertEqual(snapshot.marketplace, Marketplace.SHOPEE)
        self.assertEqual(snapshot.external_item_id, "445566")
        self.assertEqual(snapshot.quantity, 16)
        self.assertEqual(snapshot.status, InventoryStatus.ACTIVE)

    def test_quantity_negativa_e_rejeitada(self):
        payload = copy.deepcopy(load_fixture("mercadolivre_inventory.json"))
        payload["results"][0]["variations"][0]["available_quantity"] = -1

        with self.assertRaises(ValueError):
            MercadoLivreInventoryNormalizer().normalize(payload)

    def test_sku_vazio_e_normalizado_para_ausente(self):
        payload = copy.deepcopy(load_fixture("mercadolivre_inventory.json"))
        payload["results"][0]["variations"][0]["seller_custom_field"] = "   "

        snapshot = MercadoLivreInventoryNormalizer().normalize(payload)[0]

        self.assertIsNone(snapshot.sku)

    def test_marketplace_invalido_e_rejeitado(self):
        with self.assertRaises(ValueError):
            InventorySnapshot(
                marketplace="amazon",
                account_id="1",
                external_item_id="item-1",
                external_variant_id=None,
                sku="SKU-1",
                product_name="Produto",
                quantity=1,
                status="ACTIVE",
                location_id=None,
                captured_at="2026-09-13T22:00:00Z",
            )

    def test_variante_e_preservada(self):
        ml = MercadoLivreInventoryNormalizer().normalize(
            load_fixture("mercadolivre_inventory.json")
        )[0]
        shopee = ShopeeInventoryNormalizer().normalize(
            load_fixture("shopee_inventory.json")
        )[0]

        self.assertEqual(ml.external_variant_id, "987654")
        self.assertEqual(shopee.external_variant_id, "887766")

    def test_amazon_nao_existe_no_dominio(self):
        self.assertEqual(
            {marketplace.value for marketplace in Marketplace},
            {"shopee", "mercado_livre"},
        )
        with sqlite3.connect(":memory:") as connection:
            inicializar_banco(connection)
            connection.execute(
                "INSERT INTO marketplaces (nome) VALUES (?)",
                ("Marketplace legado",),
            )
            inicializar_banco(connection)
            names = {
                row[0]
                for row in connection.execute("SELECT nome FROM marketplaces")
            }
        self.assertEqual(names, {"Shopee", "Mercado Livre"})


class SyncServiceTests(unittest.TestCase):
    def test_aceita_adapters_diferentes_e_persiste_snapshots(self):
        ml_client = FixtureClient(load_fixture("mercadolivre_inventory.json"))
        shopee_client = FixtureClient(load_fixture("shopee_inventory.json"))
        repository = InMemorySyncRepository()
        service = SyncService(
            [MercadoLivreAdapter(ml_client), ShopeeAdapter(shopee_client)],
            repository,
        )

        result = service.synchronize()

        self.assertEqual(result.status, SyncStatus.SUCCESS)
        self.assertEqual(result.record_count, 2)
        self.assertEqual(len(repository.snapshots), 2)
        self.assertTrue(ml_client.authenticated)
        self.assertTrue(shopee_client.authenticated)

    def test_falha_de_adapter_nao_corrompe_outra_execucao(self):
        failing_client = FailingClient(load_fixture("mercadolivre_inventory.json"))
        shopee_client = FixtureClient(load_fixture("shopee_inventory.json"))
        repository = InMemorySyncRepository()
        service = SyncService(
            [MercadoLivreAdapter(failing_client), ShopeeAdapter(shopee_client)],
            repository,
        )

        result = service.synchronize()

        self.assertEqual(result.status, SyncStatus.PARTIAL)
        self.assertEqual(result.record_count, 1)
        self.assertEqual(len(repository.snapshots), 1)
        failed = result.marketplaces[0]
        successful = result.marketplaces[1]
        self.assertEqual(failed.status, SyncRunStatus.FAILED)
        self.assertNotIn("SEGREDO", failed.error_message)
        self.assertEqual(successful.status, SyncRunStatus.SUCCESS)


if __name__ == "__main__":
    unittest.main()
