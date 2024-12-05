import requests
import openai
import time
import json


class AirbnbSearch:
    def __init__(self):
        self.client = openai.OpenAI()
        self.base_url = "http://vespa:8080/search/"

    def get_text_embedding(self, text):
        response = self.client.embeddings.create(
            input=text, model="text-embedding-3-small"
        )
        return response.data[0].embedding

    def search(self, query_text, min_price=None, max_price=None, wifi_required=False):
        # テキストをベクトル化
        query_vector = self.get_text_embedding(query_text)

        # 検索クエリの構築
        yql = "select id, name, space, amenities, price, text_embeddings from airbnb where {}"

        # Price pre-filtering
        conditions = ["{targetHits:10}nearestNeighbor(text_embeddings,q)"]
        if min_price is not None:
            conditions.append(f"price >= {min_price}")
        if max_price is not None:
            conditions.append(f"price <= {max_price}")

        # 条件がある場合は追加、ない場合はtrue（すべてのドキュメントにマッチ）
        where_clause = " and ".join(conditions) if conditions else "true"
        yql = yql.format(where_clause)

        search_request = {
            "yql": yql,
            "hits": 10,
            "ranking": "closeness",
            "input.query(q)": query_vector,
            "timeout": "10s",
        }

        response = requests.post(self.base_url, json=search_request)
        results = response.json()

        # 結果の処理
        return [
            {
                "id": hit.get("fields", {}).get("id"),
                "name": hit.get("fields", {}).get("name"),
                "space": hit.get("fields", {}).get("space"),
                "amenities": hit.get("fields", {}).get("amenities", []),
                "price": hit.get("fields", {}).get("price"),
                "similarity_score": hit.get("relevance", 0.0),
            }
            for hit in results.get("root", {}).get("children", [])
        ]


def wait_for_vespa():
    base_url = "http://vespa:8080"
    max_attempts = 30

    for attempt in range(max_attempts):
        try:
            response = requests.get(f"{base_url}/state/v1/health")
            if response.status_code == 200:
                print("Vespa is ready!")
                return True
        except requests.exceptions.ConnectionError:
            print(
                f"Waiting for Vespa to be ready... (attempt {attempt + 1}/{max_attempts})"
            )
            time.sleep(10)

    raise Exception("Vespa failed to become ready")


def main():
    wait_for_vespa()
    searcher = AirbnbSearch()

    while True:
        try:
            # ユーザー入力の受付
            query = input("検索テキストを入力してください（終了する場合は 'quit'）: ")
            if query.lower() == "quit":
                break

            min_price = input("最小価格を入力してください（スキップする場合はEnter）: ")
            max_price = input("最大価格を入力してください（スキップする場合はEnter）: ")
            wifi_required = input("WiFiは必須すか？ (y/n): ").lower() == "y"

            # 価格のバリデーション
            min_price = int(min_price) if min_price else None
            max_price = int(max_price) if max_price else None

            # 検索実行
            results = searcher.search(query, min_price, max_price, wifi_required)

            # 結果の表示
            for result in results:
                print("\n---")
                print(f"Name: {result['name']}")
                space_text = result["space"] if result["space"] else ""
                print(f"Space: {space_text[:200]}...")
                print(f"Price: ${result['price']}")
                print(f"Score: {result['similarity_score']:.3f}")
                amenities_text = (
                    ", ".join(result["amenities"]) if result["amenities"] else ""
                )
                print(f"Amenities: {amenities_text}")

        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"エラーが発生しました: {e}")


if __name__ == "__main__":
    main()
