# Proposta de schema MySQL — camada de sincronização

> Documento de projeto para a Sprint 1. Isto **não é uma migration aplicada**.
> A versão desktop continua usando o SQLite atual até autorização da Mont Casa.

## Premissas

- MySQL 8.0+, InnoDB e `utf8mb4`.
- Datas são gravadas em UTC (`DATETIME(6)`) e convertidas apenas na apresentação.
- A integração é exclusivamente read-only nos marketplaces.
- Segredos OAuth, tokens, partner keys e senhas não pertencem a estas tabelas.
- Payloads brutos não são persistidos por padrão, evitando dados sensíveis e acoplamento ao fornecedor.

## DDL proposto

```sql
CREATE TABLE products (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    sku VARCHAR(100) NOT NULL,
    name VARCHAR(255) NOT NULL,
    category VARCHAR(120) NULL,
    official_stock INT UNSIGNED NOT NULL DEFAULT 0,
    created_at DATETIME(6) NOT NULL,
    updated_at DATETIME(6) NOT NULL,
    PRIMARY KEY (id),
    UNIQUE KEY uq_products_sku (sku),
    KEY idx_products_name (name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE marketplaces (
    id SMALLINT UNSIGNED NOT NULL AUTO_INCREMENT,
    code VARCHAR(32) NOT NULL,
    name VARCHAR(80) NOT NULL,
    PRIMARY KEY (id),
    UNIQUE KEY uq_marketplaces_code (code),
    UNIQUE KEY uq_marketplaces_name (name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE marketplace_accounts (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    marketplace_id SMALLINT UNSIGNED NOT NULL,
    external_account_id VARCHAR(120) NOT NULL,
    display_name VARCHAR(255) NULL,
    enabled BOOLEAN NOT NULL DEFAULT TRUE,
    created_at DATETIME(6) NOT NULL,
    updated_at DATETIME(6) NOT NULL,
    PRIMARY KEY (id),
    UNIQUE KEY uq_accounts_marketplace_external
        (marketplace_id, external_account_id),
    CONSTRAINT fk_accounts_marketplace
        FOREIGN KEY (marketplace_id) REFERENCES marketplaces (id)
        ON UPDATE RESTRICT ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE marketplace_listings (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    marketplace_account_id BIGINT UNSIGNED NOT NULL,
    product_id BIGINT UNSIGNED NULL,
    external_item_id VARCHAR(160) NOT NULL,
    external_variant_id VARCHAR(160) NULL,
    external_variant_key VARCHAR(160)
        GENERATED ALWAYS AS (COALESCE(external_variant_id, '')) STORED,
    external_sku VARCHAR(100) NULL,
    product_name VARCHAR(255) NOT NULL,
    status VARCHAR(30) NOT NULL,
    created_at DATETIME(6) NOT NULL,
    updated_at DATETIME(6) NOT NULL,
    PRIMARY KEY (id),
    UNIQUE KEY uq_listing_external_identity
        (marketplace_account_id, external_item_id, external_variant_key),
    KEY idx_listings_product (product_id),
    KEY idx_listings_external_sku (external_sku),
    CONSTRAINT fk_listings_account
        FOREIGN KEY (marketplace_account_id) REFERENCES marketplace_accounts (id)
        ON UPDATE RESTRICT ON DELETE RESTRICT,
    CONSTRAINT fk_listings_product
        FOREIGN KEY (product_id) REFERENCES products (id)
        ON UPDATE RESTRICT ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE sync_runs (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    marketplace_id SMALLINT UNSIGNED NOT NULL,
    marketplace_account_id BIGINT UNSIGNED NULL,
    idempotency_key CHAR(36) NOT NULL,
    started_at DATETIME(6) NOT NULL,
    finished_at DATETIME(6) NULL,
    status VARCHAR(20) NOT NULL,
    record_count INT UNSIGNED NOT NULL DEFAULT 0,
    error_message VARCHAR(500) NULL,
    PRIMARY KEY (id),
    UNIQUE KEY uq_sync_runs_idempotency (idempotency_key),
    KEY idx_sync_runs_marketplace_started (marketplace_id, started_at),
    KEY idx_sync_runs_account_started (marketplace_account_id, started_at),
    KEY idx_sync_runs_status_started (status, started_at),
    CONSTRAINT fk_sync_runs_marketplace
        FOREIGN KEY (marketplace_id) REFERENCES marketplaces (id)
        ON UPDATE RESTRICT ON DELETE RESTRICT,
    CONSTRAINT fk_sync_runs_account
        FOREIGN KEY (marketplace_account_id) REFERENCES marketplace_accounts (id)
        ON UPDATE RESTRICT ON DELETE SET NULL,
    CONSTRAINT chk_sync_runs_status
        CHECK (status IN ('RUNNING', 'SUCCESS', 'FAILED'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE inventory_snapshots (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    marketplace_listing_id BIGINT UNSIGNED NOT NULL,
    sync_run_id BIGINT UNSIGNED NOT NULL,
    quantity INT UNSIGNED NOT NULL,
    location_id VARCHAR(160) NULL,
    location_key VARCHAR(160)
        GENERATED ALWAYS AS (COALESCE(location_id, '')) STORED,
    captured_at DATETIME(6) NOT NULL,
    PRIMARY KEY (id),
    UNIQUE KEY uq_snapshot_run_listing_location
        (sync_run_id, marketplace_listing_id, location_key),
    KEY idx_snapshots_listing_captured
        (marketplace_listing_id, captured_at),
    KEY idx_snapshots_captured (captured_at),
    CONSTRAINT fk_snapshots_listing
        FOREIGN KEY (marketplace_listing_id) REFERENCES marketplace_listings (id)
        ON UPDATE RESTRICT ON DELETE RESTRICT,
    CONSTRAINT fk_snapshots_run
        FOREIGN KEY (sync_run_id) REFERENCES sync_runs (id)
        ON UPDATE RESTRICT ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

## Decisões de integridade e idempotência

- `marketplaces.code` terá somente `shopee` e `mercado_livre`; a aplicação nunca usa o ID físico como regra de domínio.
- `product_id` em `marketplace_listings` é nulo durante a reconciliação inicial. Um listing sem SKU ou ainda não associado pode ser sincronizado sem criar produto interno incorreto.
- A coluna gerada `external_variant_key` torna única também a publicação sem variante. Um `UNIQUE` direto sobre coluna nula não impediria duplicatas no MySQL.
- A identidade externa é conta + item + variante. O mesmo item em contas distintas continua válido.
- `external_sku` tem índice para reconciliação; a associação definitiva continua sendo a FK `product_id`.
- Cada tentativa recebe uma `idempotency_key`. Repetir a mesma requisição não cria outra execução.
- `sync_runs.marketplace_id` permite registrar inclusive falhas anteriores à identificação da conta. O repository associa `marketplace_account_id` assim que o contrato normalizado fornece `account_id`.
- Um snapshot é único por execução + listing + localização. Uma nova execução preserva o histórico mesmo que a quantidade não mude.
- O lote de snapshots e a conclusão de `sync_runs` devem ser gravados em transação. Uma falha deve executar rollback do lote e marcar a execução como `FAILED` em uma transação separada.
- `error_message` recebe somente texto sanitizado. O schema deliberadamente não possui colunas para client secret, tokens, partner key ou senha.

## Pontos a confirmar antes da migration

- Versão e collation oficiais do MySQL, inclusive sensibilidade desejada para SKU.
- Contas/lojas efetivamente autorizadas e política de rotação de credenciais.
- Semântica real de estoque por localização em cada API.
- Retenção necessária do histórico de snapshots.
- Estratégia segura de secrets (variáveis injetadas pelo ambiente ou cofre gerenciado).
