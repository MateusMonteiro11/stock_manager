# MyStock / Stock Manager

Aplicação desktop Python para cadastro e auditoria de estoque da Mont Casa Construção, com SQLite local, interface PySimpleGUI e exportação XLSX.

## Execução

```powershell
python -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
python main.py
```

No Linux/macOS, ative o ambiente com `source .venv/bin/activate`. Os atalhos `RUN.bat` e `RUN.sh` também instalam as dependências e iniciam o desktop.

## Funcionalidades

- Cadastro, busca, atualização do estoque interno e remoção de produtos.
- Auditoria manual dos estoques da Shopee e do Mercado Livre.
- Consolidação pelo menor estoque observado e identificação de divergências.
- Histórico de auditorias e relatório Excel.

Os marketplaces são resolvidos pelo nome canônico, sem depender de IDs físicos ou da ordem dos registros no SQLite.

## Integrações read-only

```text
Marketplace -> Adapter -> Normalizer -> InventorySnapshot
            -> SyncService -> Repository -> processamento local
```

`MarketplaceAdapter` expõe somente `authenticate`, `get_account`, `get_inventory` e `health_check`. Os clientes reais permanecem bloqueados até autorização e configuração oficiais. Nenhuma integração cria, altera ou exclui recursos dos marketplaces.

O funcionário analisa o relatório e faz manualmente eventuais ajustes no marketplace. O SQLite continua sendo a persistência operacional do desktop. A proposta futura de MySQL está em [docs/mysql_sync_schema.md](docs/mysql_sync_schema.md); não existe conexão ou migration MySQL implementada.

## OAuth e notificações do Mercado Livre

- `GET /api/mercadolivre/oauth/callback`: encaminha `code/state` pelo navegador para o listener local, que valida o state e descarta o code.
- `POST /api/mercadolivre/notifications`: valida a estrutura, retorna 200 e descarta o evento, sem sincronização ou persistência remota.

Os dois endpoints são stateless e independentes do desktop e do banco. A configuração pública usa `pyproject.toml`; as dependências do desktop continuam em `requirements.txt`.

Consulte [docs/mercadolivre_oauth_webhook.md](docs/mercadolivre_oauth_webhook.md) para executar `vercel dev`, iniciar o listener e cadastrar as URLs no DevCenter. A troca de code por tokens e o callback da Shopee ainda não estão implementados.

Uma notificação não contém necessariamente o estado autoritativo completo do recurso. O MyStock utiliza chamadas GET autenticadas para obter o estado atualizado; os clientes HTTP dessa etapa ainda dependem de implementação e autorização oficiais.

## Configuração

`.env.example` lista as variáveis disponíveis. O desktop e o listener não carregam `.env` automaticamente. O SQLite atual não exige credenciais de marketplace.

`MYSTOCK_SQLITE_DB_PATH` permite escolher o arquivo SQLite. Sem essa variável, o comportamento legado ao executar pelo código-fonte usa `../database/estoque.db`, relativo à pasta do projeto; no executável, usa `database/estoque.db` ao lado do programa. O módulo de conexão cria a pasta do banco, e o relatório cria sua pasta somente ao exportar.

Nunca versione Client Secret, tokens, Partner Key, identificadores reais de contas ou credenciais de banco. `.env`, bancos, relatórios, ambientes virtuais e caches estão ignorados pelo Git.

## Estrutura

```text
main.py          interface desktop
connection/      persistência SQLite
services/        estoque, auditoria, relatórios e sincronização
contracts/       InventorySnapshot e valores canônicos
integrations/    contratos, adapters, clientes e normalizers
repositories/    interfaces de persistência
api/             endpoints públicos
oauth_bridge/    suporte HTTP/OAuth sem dependências de negócio
scripts/         listener OAuth local
docs/            configuração OAuth e proposta futura de persistência
public/          saída estática vazia exigida pela configuração Vercel
```

## Executável Windows

Com PyInstaller instalado no ambiente de build:

```powershell
pyinstaller main.spec
```

Bancos e relatórios são criados em execução e não são incorporados ao executável.

## Próximas etapas

Validar o fluxo OAuth com a aplicação oficial; implementar a troca de code por tokens em etapa separada; implementar clientes HTTP read-only; validar payloads reais e integrar a persistência dos snapshots ao fluxo local.

## Autor

Desenvolvido por Mateus Monteiro e Arthur Souza em parceria com projeto acadêmico vinculado à faculdade e empresa colaboradora.
