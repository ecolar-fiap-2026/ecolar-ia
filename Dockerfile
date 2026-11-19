FROM python:3.12-slim
WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    OMP_NUM_THREADS=1 \
    OPENBLAS_NUM_THREADS=1 \
    MKL_NUM_THREADS=1

COPY requirements-render.txt .
RUN pip install --no-cache-dir -r requirements-render.txt

COPY app.py .
COPY ecolar_ia ./ecolar_ia
COPY modelos ./modelos
COPY templates ./templates
COPY exemplos ./exemplos

RUN useradd --uid 10001 --create-home appuser
USER appuser

EXPOSE 10000
CMD ["sh", "-c", "exec gunicorn --bind 0.0.0.0:${PORT:-10000} --workers 1 --threads 2 --timeout 120 --access-logfile - --error-logfile - 'app:create_app()'"]
