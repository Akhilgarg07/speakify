FROM python:3.9-slim-buster

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update \
    && apt-get install -y gcc procps \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*



WORKDIR /app

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app/

EXPOSE 8000

CMD ["hypercorn", "speakify.asgi:application", "--bind", "0.0.0.0:8000", "--log-level", "debug"]

