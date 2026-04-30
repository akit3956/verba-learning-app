# ベースイメージとして軽量かつバイナリ互換性の高い python:3.11-slim を使用
FROM python:3.11-slim

# コンテナ内の作業ディレクトリを設定
WORKDIR /app

# 環境変数の設定（Pythonが.pycファイルを生成しないようにする、出力をバッファリングしない等）
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# システムの依存関係をインストール（コンパイルに必要な最小限のパッケージ）
# インストール後にキャッシュを削除してイメージサイズを軽量化
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# 依存関係ファイル（requirements.txt）を先にコピー
COPY requirements.txt .

# pipのアップグレードと依存パッケージのインストール
# --no-cache-dir: Dockerイメージの軽量化、およびメモリ枯渇(OOM)防止
# --prefer-binary: 極力ソースコンパイルを避け、コンパイル済みバイナリ(Wheel)を使用して高速化
RUN pip install --upgrade pip && \
    pip install --no-cache-dir --prefer-binary -r requirements.txt

# アプリケーションの全ソースコードをコンテナにコピー
COPY . .

# Renderなどのクラウドが自動で検知するポートを公開（今回は8080）
EXPOSE 8080

# コンテナ起動時に実行するコマンド（FastAPIサーバーの起動）
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
