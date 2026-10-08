FROM python:3.12-slim
WORKDIR /app
COPY *.py ./
COPY static ./static
RUN useradd --uid 10001 --create-home castle && mkdir /data && chown castle:castle /data
USER castle
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 CASTLE_HOST=0.0.0.0 CASTLE_PORT=8080 CASTLE_DATA_DIR=/data
VOLUME ["/data"]
EXPOSE 8080
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8080/api/health', timeout=2)"
CMD ["python", "server.py"]
