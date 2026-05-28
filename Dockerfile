# 使用官方的 Python 輕量版基礎映像檔
# python:3.12-slim 體積小、安全性高，非常適合雲端部署
FROM python:3.12-slim


# 設定環境變數
# PYTHONDONTWRITEBYTECODE=1: 避免 Python 寫入 .pyc 快取檔案，保持容器乾淨
# PYTHONUNBUFFERED=1: 避免 Python 緩衝輸出，確保 log 能即時顯示於 stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 設定工作目錄
WORKDIR /app

# 先複製 requirements.txt 以利用 Docker 的快取機制 (Cache Layering)
# 如果 requirements.txt 沒有變更，重構時就不需要重新下載並安裝套件
COPY requirements.txt .

# 升級 pip 並安裝 Python 依賴套件
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# 複製其餘的專案原始碼與靜態檔案
COPY . .

# 宣告容器內部運行的連接埠 (Port)
# 根據 run.py 中的設定，本應用程式運作於 1919 port
EXPOSE 1919

# 啟動命令
# 運行 Flask 應用程式
CMD ["python", "run.py"]
