# Noctarflix

Aplicativo de streaming distribuído inspirado na arquitetura descrita em [`docs/system_architecture.md`](docs/system_architecture.md).
Este repositório inclui uma prova de conceito completa com gateway, seis serviços FastAPI e uma página web estática que conversa com o gateway.

## Estrutura
- `backend/`: código Python com gateway e serviços AUTH, CATALOG, STREAMING, BILLING, MONITOR/DISCOVERY e NOTIFY.
- `frontend/`: landing page 1920x1080 (responsiva) com carrosséis, destaque e ações ligadas ao gateway.
- `docker-compose.yml`: orquestra todos os serviços em rede local.

## Como rodar
1. Instale dependências back-end (opcional se usar Docker):
   ```bash
   cd backend
   pip install -r requirements.txt
   uvicorn gateway.main:app --reload --port 8000
   ```
   Em terminais separados rode cada serviço com `uvicorn <serviço>.main:app --port <porta>`.

2. Com Docker Compose (recomendado):
   ```bash
   docker compose up --build
   ```
   Gateway: http://localhost:8000

3. Frontend estático:
   ```bash
   cd frontend
   python -m http.server 4173
   ```
   A página irá chamar o gateway em `http://localhost:8000`.

## Fluxos
- **Cadastro/Login (AUTH)**: `/register` e `/login` no gateway criam tokens simples em memória.
- **Assinatura (BILLING)**: `/subscribe` ativa assinatura e dispara notificação.
- **Catálogo (CATALOG)**: `/catalog` retorna títulos recomendados.
- **Play (STREAMING)**: `/play` valida token, consulta assinatura e cria sessão com URL simulada de CDN.
- **Monitor/Discovery**: serviço registra heartbeats e resolve nomes lógicos para endereços primário/backup.
- **Notify**: registra notificações enviadas por BILLING.

Cada serviço expõe `/health` para observabilidade básica.
