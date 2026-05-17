# projeto-integrado-backend
projeto final de tópicos especiais em engneharia de software


- Kanban: https://github.com/users/leticosta4/projects/11/views/1
- Protótipo de média fidelidade: https://www.figma.com/design/fWOUafo7wJOMO4omU0G0zC/Untitled--Copy-?node-id=0-1&p=f&t=BU6lvoRRA1Ez1BJ2-0
- Outros docs disponíveis na [pasta de documentos](./docs/)

# Rodando

# Desenvolvendo

- Instale uv: `curl -LsSf https://astral.sh/uv/install.sh | sh`

- Instalando dependências: `uv sync`

- Instalando o projeto: `uv pip install -e .`

- `uv run src/main.py`

## Testando

- `uv run pytest --cov --durations=0`
