# Shift Maker

このリポジトリは、最小限の FastAPI バックエンドと Vue.js フロントエンドを含んでいます。

## 必要条件
- Python 3.11 以上
- Node.js 18 以上
- npm

## バックエンドのセットアップ
1. 依存関係をインストールします:
   ```bash
   pip install fastapi uvicorn
   ```
2. 開発サーバーを起動します:
   ```bash
   uvicorn backend.main:app --reload
   ```

## フロントエンドのセットアップ
1. frontend ディレクトリに移動して依存関係をインストールします:
   ```bash
   cd frontend
   npm install
   ```
2. 開発サーバーを起動します:
   ```bash
   npm run dev
   ```
