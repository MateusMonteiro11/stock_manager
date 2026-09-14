# MyStock / Stock Manager

Aplicação desktop Python para gerenciamento e auditoria de estoque da Mont Casa Construção. A versão atual mantém o cadastro interno, o SQLite, a auditoria manual e a exportação XLSX, enquanto a arquitetura é preparada para sincronização read-only com marketplaces.

## Marketplaces atuais

- Shopee
- Mercado Livre

Esses são os únicos marketplaces do domínio. A aplicação não depende dos IDs físicos nem da ordem dos registros na tabela `marketplaces`.

## Funcionalidades atuais

- Cadastro, busca, edição de estoque e remoção de produtos.
- Auditoria dos estoques observados na Shopee e no Mercado Livre.
- Consolidação pelo menor estoque observado e identificação de divergências.
- Histórico de auditorias.
- Geração de relatório operacional em Excel (`.xlsx`).
- Interface desktop em PySimpleGUI e persistência SQLite.

## Arquitetura da Sprint 1

```text
Marketplace API
      |
      v
Read-only Adapter
      |
      v
Normalizer -> InventorySnapshot (contrato interno)
      |
      v
SyncService -> Repository -> Database
      |
      v
AuditService -> UI / XLSX
```

O JSON externo fica restrito aos normalizers. Services e UI trabalham com o contrato interno `InventorySnapshot` e com interfaces de repository. A interface `MarketplaceAdapter` oferece apenas autenticação, leitura de conta, leitura de inventário e health check; não há operação de escrita em marketplace.

O fluxo operacional planejado é:

```text
READ -> NORMALIZE -> STORE -> AUDIT -> RECOMMEND -> EXPORT XLSX
```

O funcionário analisa o relatório e faz manualmente qualquer ajuste nos marketplaces. Uma sincronização posterior poderá confirmar se a divergência foi resolvida.

## Estado das integrações externas

As APIs reais ainda dependem da autorização formal e das credenciais oficiais da Mont Casa. Nesta etapa:

- não são realizadas chamadas HTTP;
- não existem endpoints, tokens ou credenciais fictícios;
- os clientes reais falham de forma segura enquanto não configurados/autorizados;
- fixtures locais exercitam adapters, normalizers, contrato e `SyncService` sem internet;
- mensagens de erro de sync não reproduzem conteúdo de exceptions externas, evitando vazamento de tokens.

Os arquivos em `tests/fixtures/` são exemplos de desenvolvimento do contrato necessário e não representam dados reais da empresa nem uma cópia integral das APIs.

## Persistência

O SQLite continua sendo a persistência da versão desktop atual e não recebeu migration destrutiva. A nova camada de services depende de interfaces, com wrappers explícitos para os repositories SQLite existentes.

MySQL é o alvo futuro dos dados sincronizados. A proposta de tabelas, chaves, índices, idempotência e integridade referencial está em [`docs/mysql_sync_schema.md`](docs/mysql_sync_schema.md). Ela ainda não foi aplicada e deverá ser revisada com payloads e contas reais na próxima etapa da Sprint 1.

## Configuração e secrets

Copie apenas os nomes necessários de `.env.example` para o mecanismo de configuração do ambiente. O projeto não carrega arquivos `.env` automaticamente e não exige valores para executar o fluxo SQLite atual.

Nunca versione Client Secret, OAuth token, refresh token, Partner Key, `shop_id` real ou credenciais MySQL. O arquivo `.env` está ignorado pelo Git. Secrets não devem ser gravados em snapshots, logs, exceptions da UI ou banco relacional.

## Estrutura relevante

```text
contracts/                 contrato InventorySnapshot
integrations/base/         interface MarketplaceAdapter
integrations/mercadolivre/ cliente seguro, adapter e normalizer
integrations/shopee/       cliente seguro, adapter e normalizer
repositories/              interfaces e repository em memória para desenvolvimento
connection/                SQLite e wrappers das interfaces
services/                  estoque, auditoria, relatório e sincronização
tests/fixtures/            payloads locais de desenvolvimento
docs/                      proposta do schema MySQL
main.py                    interface desktop
```

## Como executar pelo código-fonte

Requer Python 3 e as dependências de `requirements.txt`.

```bash
python -m venv .venv
```

Windows:

```bat
.venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

Linux/macOS:

```bash
source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

## Testes offline

```bash
python -m unittest discover -s tests -v
```

Os testes não usam internet nem credenciais e cobrem normalização, validação do contrato, variantes, isolamento de falhas no sync, domínio sem marketplaces obsoletos, auditoria com os dois marketplaces e geração XLSX.

## Executável Windows

O build atual continua baseado em PyInstaller:

```bash
pyinstaller main.spec
```

## Próxima etapa (aguardando autorização)

- Registrar e configurar as aplicações oficiais.
- Implementar OAuth/autenticação e clientes HTTP reais.
- Validar os payloads reais e ajustar normalizers.
- Implementar o repository MySQL e converter a proposta em migrations.
- Fazer a primeira sincronização read-only e comparar os resultados com os estoques atuais.

## Autor

Desenvolvido por Mateus Monteiro e Arthur Souza em parceria com projeto acadêmico vinculado à faculdade e empresa colaboradora.
