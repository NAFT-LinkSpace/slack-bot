FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl ca-certificates \
    && rm -rf /var/lib/apt/lists/*

RUN curl -L -o /tmp/slackdump.deb https://github.com/rusq/slackdump/releases/download/v3.1.8/slackdump_3.1.8_linux_amd64.deb \
    && apt-get update \
    && apt-get install -y --no-install-recommends /tmp/slackdump.deb \
    && rm -f /tmp/slackdump.deb \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

COPY . ./

RUN chmod +x /app/docker-entrypoint.sh

ENTRYPOINT ["/app/docker-entrypoint.sh"]