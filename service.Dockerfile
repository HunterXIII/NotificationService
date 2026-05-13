# --- Этап сборки (Builder) ---
FROM python:3.11-slim AS builder

WORKDIR /app

# Устанавливаем переменные для чистоты установки
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Ставим системные зависимости (если нужны для psycopg2 или др.)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Копируем ТОЛЬКО requirements и устанавливаем их в отдельную папку
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt


# --- Финальный этап (Runtime) ---
FROM python:3.11-slim

WORKDIR /app

# Копируем только установленные библиотеки из билдера
COPY --from=builder /install /usr/local
# Копируем код приложения (теперь это не инвалидирует кэш библиотек)
COPY . .

# Безопасность: работаем не от root
RUN adduser --disabled-password appuser
USER appuser

# Порт приложения
EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]