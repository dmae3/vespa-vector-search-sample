# Vespa Vector Search Sample

Vespaを使用したAirbnbデータセットのベクトル検索サンプルアプリケーションです。OpenAIのテキスト埋め込みを使用して、自然言語でAirbnb物件を検索できます。

## 主な特徴 🌟

- Vespaを使用した高速なベクトル検索
- OpenAI text-embedding-3-smallモデルによる自然言語クエリの埋め込み
- MongoDB/airbnb_embeddings データセットを使用
- 価格範囲とWiFiの有無でフィルタリング可能

## 必要条件 📋

- Docker と Docker Compose
- OpenAI API キー

## セットアップと使用方法 🚀

1. リポジトリのクローン:
```bash
git clone https://github.com/yourusername/vespa-vector-search-sample.git
cd vespa-vector-search-sample
```

2. 環境変数の設定:
```bash
export OPENAI_API_KEY="your_openai_api_key"
```

3. アプリケーションの起動:
```bash
docker compose up --build
```

4. 検索の実行:
```bash
docker attach vespa-vector-search-sample-search-1
```


## システム構成 🔍

### コンポーネント
- **Vespa**: ベクトル検索エンジン
- **Feeder**: データセットをVespaにロードするサービス
- **Search**: 検索APIを提供するサービス

### データフロー
1. Feederサービスが起動時にMongoDBのAirbnbデータセットをダウンロード
2. 各物件データをVespaにインデックス化
3. Searchサービスが検索APIを提供
4. ユーザーの検索クエリをOpenAIで埋め込みベクトルに変換
5. Vespaで類似度検索を実行

### 検索機能
- テキストによる意味的検索
- 価格範囲でのフィルタリング
- WiFi有無でのフィルタリング
- 類似度スコアの表示

## 技術スタック 🛠

- Vespa 8.0
- Python 3.11
- OpenAI API (text-embedding-3-small)
- Docker & Docker Compose
- Hugging Face Datasets

## ライセンス

このプロジェクトは[MITライセンス](LICENSE)の下で公開されています。
