# projeto-integrado-backend
projeto final de tópicos especiais em engneharia de software

# Docs

- Kanban: https://github.com/users/leticosta4/projects/11/views/1
- Protótipo de média fidelidade com fluxo de navgabilidade: https://www.figma.com/design/fWOUafo7wJOMO4omU0G0zC/Untitled--Copy-?node-id=0-1&p=f&t=BU6lvoRRA1Ez1BJ2-0
- [Novo] Projeto Arquitetural (com o novo DER): https://github.com/leticosta4/projeto-integrado-tees/wiki/Projeto-Arquitetural
- Outros docs disponíveis na [pasta de documentos](./docs/)

# Setup do projeto

- Adicionar `.env` baseado no `env.example`

- Inicie container PGVector:

    - `chmod +x ./scripts/dev.sh`

    - `./scripts/dev.sh`

- Instale uv: `curl -LsSf https://astral.sh/uv/install.sh | sh`

- Instalando dependências: `uv sync`

- Instalando o projeto: `uv pip install -e .`

# Rodando:

- ETL: `uv run src/ingest.py`

- Servidor Flask: `uv run src/app.py`

# Sobre as migrations

- Criando migrações (se necessário): `uv run yoyo new --sql migrations -m "mensagem"`

- Rodando migrações: `uv run src/migrate.py`

## Testando

- `uv run pytest --cov --durations=0`

- Rode com Docker (Bash necessário): `chmod +x ./scripts/ci.sh`, `./ci.sh`

## Docs da api
Feito via swagger: porta 5000, endpoint `/api/docs`
