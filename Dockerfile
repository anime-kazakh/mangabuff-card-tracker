ARG PYTHON_VERSION=3.13.9
FROM python:${PYTHON_VERSION}-slim

# .pyc файлы
ENV PYTHONDONTWRITEBYTECODE=1
# буффер
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "src/main.py"]