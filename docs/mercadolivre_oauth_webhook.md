# Mercado Livre: OAuth e notificações

O desktop continua sendo executado com `python main.py`. Somente os dois endpoints em `api/` e o suporte `oauth_bridge/` são publicados na Vercel. Não existe acesso remoto ao SQLite, MySQL ou banco operacional.

## Endpoints

| Endpoint | Comportamento |
| --- | --- |
| `GET /api/mercadolivre/oauth/callback` | Valida `code/state` e retorna 302 para o listener local. Erros OAuth são encaminhados de forma genérica. |
| `POST /api/mercadolivre/notifications` | Valida um JSON com `topic`, `resource` e `user_id`, responde 200 e descarta o evento. |

O destino local padrão é `http://127.0.0.1:8765/oauth/mercadolivre/callback`. O navegador segue o redirect no computador do usuário; a Function não acessa localhost. O destino não é controlado por parâmetros da requisição.

O callback exige `state` e exatamente um entre `code` e `error`. Parâmetros ausentes, vazios, duplicados ou inválidos retornam 400. Métodos incorretos retornam 405 com o header `Allow`.

O webhook aceita `application/json`, com `topic` não vazio, `resource` como caminho iniciado por `/` (sem `//`) e `user_id` positivo. Campos extras são ignorados. Estrutura/JSON inválidos retornam 400; corpo acima de 64 KiB retorna 413; content type incorreto retorna 415.

Este webhook satisfaz o endpoint público necessário para recebimento de notificações, mas a Sprint atual não utiliza notificações como fonte de estado. O estado autoritativo é obtido posteriormente pelas operações read-only da API.

```text
Marketplace -> aviso de evento -> webhook retorna 200 -> descarte

Separadamente, no fluxo planejado:
MyStock local -> GET API marketplace -> Normalizer -> InventorySnapshot
             -> processamento e persistência locais -> auditoria / XLSX
```

Uma notificação não contém necessariamente o estado autoritativo completo do recurso. O MyStock utiliza chamadas GET autenticadas para obter o estado atualizado.

## Configuração e privacidade

Defina as variáveis no ambiente; o listener não carrega `.env` automaticamente.

| Variável | Uso |
| --- | --- |
| `MERCADO_LIVRE_CLIENT_ID` | App ID oficial, usado somente pelo listener |
| `MERCADO_LIVRE_REDIRECT_URI` | URL HTTPS pública com o caminho exato do callback |
| `MERCADO_LIVRE_NOTIFICATION_URL` | URL HTTPS pública com o caminho exato das notificações |
| `MERCADO_LIVRE_LOCAL_CALLBACK_HOST` | Exclusivamente `127.0.0.1` |
| `MERCADO_LIVRE_LOCAL_CALLBACK_PORT` | Porta local de 1 a 65535; padrão 8765 |

Client Secret, access token e refresh token não são utilizados nesta etapa. Não configure credenciais ou banco na Vercel. Se alterar a porta, ajuste tanto a Function quanto o listener; `--port` altera apenas o listener.

URLs públicas não aceitam localhost, IPs privados, HTTP, query, fragmento ou credenciais. Nenhum domínio de deployment é usado como default na aplicação.

As respostas usam `Cache-Control: no-store` e `Referrer-Policy: no-referrer`. A aplicação não registra queries nem corpos. O header `Location` precisa conter `code/state` para encaminhá-los; não compartilhe URLs de callback ou capturas de rede com dados reais. Os logs de infraestrutura dependem da plataforma. Não use `vercel dev --debug` com callbacks reais, pois o CLI registra URLs completas.

O listener gera um state criptograficamente aleatório por tentativa, compara em tempo constante, expira em 300s e consome o state no primeiro sucesso ou erro OAuth válido. Retém somente o resultado e descarta o code. Não solicita nem persiste tokens.

O webhook não autentica a origem e não confia no payload para executar ações. Não há fila em memória, banco, arquivo ou processamento posterior. O 200 reconhece e descarta o aviso deliberadamente; o estoque não depende desses eventos.

## Vercel local no Windows

Use Python >= 3.12 e Node/npm. Na raiz:

```powershell
python -m venv .venv
.venv\Scripts\python.exe -m pip install uv==0.10.11
npm install -g vercel@64.5.0
```

O runtime procura `python3` e `uv`. Para evitar o alias da Microsoft Store e o erro de aspas do CLI com caminhos que contêm espaços, configure somente este terminal:

```powershell
Copy-Item -LiteralPath .venv\Scripts\python.exe -Destination .venv\Scripts\python3.exe
$taskFileSystem = New-Object -ComObject Scripting.FileSystemObject
$taskScripts = $taskFileSystem.GetFolder((Resolve-Path .venv\Scripts).Path).ShortPath
$env:PATH = $taskScripts + ';' + $env:PATH
python3 --version
uv --version
$env:VERCEL_TELEMETRY_DISABLED = '1'
vercel dev --local --listen 127.0.0.1:3000
```

Se o volume não oferecer caminhos curtos, use um diretório de ferramentas sem espaços ou WSL. O modo `--local` não exige login, link ou projeto remoto. Os simuladores locais iniciados pelo CLI não são usados pelos handlers.

Em outro terminal, confira as respostas com dados sintéticos:

```powershell
curl.exe -i --max-redirs 0 "http://127.0.0.1:3000/api/mercadolivre/oauth/callback?code=synthetic-code&state=synthetic-state"
# 302 para o listener; este state fixo não valida uma tentativa real.

curl.exe -i "http://127.0.0.1:3000/api/mercadolivre/oauth/callback?code=synthetic-code"
# 400: state ausente.

@{topic='items'; resource='/items/MLB123'; user_id=123} | ConvertTo-Json -Compress | curl.exe -i -X POST "http://127.0.0.1:3000/api/mercadolivre/notifications" -H "Content-Type: application/json" --data-binary '@-'
# 200 OK.

curl.exe -i "http://127.0.0.1:3000/api/mercadolivre/notifications"
# 405, Allow: POST.
```

## Listener e DevCenter

O projeto `mystock-mercadolivre`, na equipe `mateusmonteiro11-50b0f0d6`, foi publicado em produção em 17/10/2026. O domínio permanente verificado é `mystock-mercadolivre.vercel.app`; ele aponta para o deployment de produção READY, sem depender da URL individual de cada build.

Cadastre exatamente estas URLs:

- Redirect URI: `https://mystock-mercadolivre.vercel.app/api/mercadolivre/oauth/callback`
- Notification URL: `https://mystock-mercadolivre.vercel.app/api/mercadolivre/notifications`

Não cadastre `localhost` ou a URL de `vercel dev` no DevCenter. A Notification URL precisa aceitar POST do Mercado Livre sem exigir login na Vercel.

No computador que abrirá o navegador:

```powershell
$env:MERCADO_LIVRE_CLIENT_ID = '<APP_ID_OFICIAL>'
$env:MERCADO_LIVRE_REDIRECT_URI = 'https://mystock-mercadolivre.vercel.app/api/mercadolivre/oauth/callback'
$env:MERCADO_LIVRE_NOTIFICATION_URL = 'https://mystock-mercadolivre.vercel.app/api/mercadolivre/notifications'
python -m scripts.mercadolivre_oauth_listener
```

O listener abre a autorização no navegador. `--no-browser` imprime somente a URL inicial com o state; `--timeout` ajusta a validade; `--port` ajusta a porta. Um callback válido confirma o recebimento do code e encerra o processo, sem mostrar ou armazenar o código.

```text
DevCenter -> Mercado Livre -> HTTPS Vercel -> navegador -> 127.0.0.1
          -> state validado -> code descartado
```

A prova depende de App ID e conta oficialmente autorizados, permissões de leitura e correspondência exata da Redirect URI. PKCE não está implementado: se estiver habilitado na aplicação, seus parâmetros precisam ser adicionados antes do uso real. A troca de code por tokens pertence a uma etapa separada; não existe callback da Shopee.

## Publicação de produção

A pasta está vinculada via `.vercel/project.json` ao projeto `mystock-mercadolivre`. Esse arquivo contém somente os IDs de projeto/equipe e está ignorado pelo Git. Não há conexão GitHub nem variáveis de ambiente configuradas na Vercel.

Para conferir o destino e publicar o estado local novamente:

```powershell
vercel project inspect --scope mateusmonteiro11-50b0f0d6 --non-interactive
vercel deploy --dry --json --scope mateusmonteiro11-50b0f0d6 --non-interactive
vercel deploy --prod --yes --scope mateusmonteiro11-50b0f0d6 --non-interactive
vercel inspect mystock-mercadolivre.vercel.app --scope mateusmonteiro11-50b0f0d6 --json
```

O deploy foi feito diretamente dos nove arquivos permitidos pela `.vercelignore`, sem commit, push ou PR. `vercel.json` e `.env.example` não precisaram de alterações. Se for necessário refazer o vínculo, use `vercel link --yes --scope mateusmonteiro11-50b0f0d6 --project mystock-mercadolivre --non-interactive`; o CLI pode criar `.env.local` com uma credencial OIDC temporária, desnecessária para estes endpoints. Não versione nem envie esse arquivo.

Os testes HTTPS anônimos confirmaram callback 302, headers de privacidade, erros OAuth, rejeição de parâmetros ausentes (400), métodos incorretos (405), notificação válida (200), JSON inválido (400) e content type incorreto (415). O fluxo completo até o listener local validou um state novo e descartou o code sintético. Arquivos do desktop e suporte não são servidos publicamente (404).

## Empacotamento

A estrutura usa [Functions Python por arquivo](https://vercel.com/docs/functions/runtimes/python/api-directory), com classes `handler` derivadas de `BaseHTTPRequestHandler`. `pyproject.toml` declara o runtime público sem dependências adicionais; `requirements.txt` continua exclusivo do desktop.

`vercel.json` usa `framework: null`, sem build de desktop e com saída estática `public/` vazia. `.vercelignore` limita o envio a `api/`, `oauth_bridge/`, `public/` e aos manifestos. Bancos, `.env`, GUI, services e scripts locais ficam fora do deploy.

Referências: [OAuth oficial](https://developers.mercadolivre.com.br/pt_br/autenticacao-e-autorizacao?nocache=true) e [formato das notificações](https://developers.mercadolivre.com.br/en_us/products-receive-notifications).
