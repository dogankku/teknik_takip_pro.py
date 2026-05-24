# ── Teknik Takip Pro — Docker Image ──────────────────────────────────────────
# Kullanım:
#   docker build -t teknik-takip-pro .
#   docker run -p 8501:8501 -v $(pwd)/data:/app/data teknik-takip-pro

FROM python:3.11-slim

# Sistem bağımlılıkları (barcode/QR kod için)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libfreetype6-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Önce bağımlılıkları yükle (layer cache için)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Uygulama dosyalarını kopyala
COPY . .

# Veri dizini oluştur (SQLite veritabanı burada saklanır)
RUN mkdir -p /app/data

# Streamlit ayarları
ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0
ENV STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
ENV STREAMLIT_SERVER_HEADLESS=true

# Port
EXPOSE 8501

# Sağlık kontrolü
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

# Başlatma
CMD ["streamlit", "run", "tekniktakip_pro.py", \
     "--server.port=8501", \
     "--server.address=0.0.0.0", \
     "--server.headless=true", \
     "--browser.gatherUsageStats=false"]
