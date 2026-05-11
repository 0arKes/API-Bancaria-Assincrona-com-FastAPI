FROM python:3.14-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# instala poetry
RUN pip install poetry

RUN poetry config installer.max-workers 10
# copia dependências
COPY BackendAPI/pyproject.toml BackendAPI/poetry.lock* ./

# instala deps (sem dev e sem instalar o projeto)
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --no-root --without dev

# copia código
COPY BackendAPI/ .

# expõe porta
EXPOSE 8000

# 🔥 CORREÇÃO AQUI (caminho correto do FastAPI)
CMD ["sh", "-c", "poetry run alembic upgrade head && poetry run uvicorn backendapi.app:app --host 0.0.0.0 --port 8000"]