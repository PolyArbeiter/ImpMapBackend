FROM python:3.14-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    binutils \
    libproj-dev \
    gdal-bin \
    python3-gdal \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

WORKDIR /app/impression_map

COPY pyproject.toml ./

RUN pip install --upgrade pip && pip install -e ".[dev]" --no-cache-dir --root-user-action

COPY . .

# RUN mkdir -p staticfiles media

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
