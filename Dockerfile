# Etapa 1: instala las dependencias en un entorno virtual aislado.
FROM python:3.12-slim AS builder

ENV PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

WORKDIR /app

# Primero las dependencias: si el código cambia, esta capa sigue en caché.
COPY requirements.txt ./
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Etapa 2: imagen final, solo con el entorno ya construido y el código.
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH"

# Usuario sin privilegios: el proceso nunca corre como root.
RUN groupadd --system aura && \
    useradd --system --gid aura --home-dir /app --shell /usr/sbin/nologin aura && \
    mkdir -p /app && \
    chown aura:aura /app

WORKDIR /app

COPY --from=builder /opt/venv /opt/venv
COPY --chown=aura:aura app ./app

USER aura

EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "--access-logfile", "-", "app:create_app()"]
