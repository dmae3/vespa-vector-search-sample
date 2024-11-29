import requests
from sentence_transformers import SentenceTransformer
import json
import time


class AirbnbSearch:
    def __init__(self):
        self.model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
        self.base_url = "http://vespa:8080/search/"

    def get_text_embedding(self, text):
        return self.model.encode(text).tolist()

    def search(self, query_text, min_price=None, max_price=None, wifi_required=False):
        # テキストをベクトル化
        query_vector = self.get_text_embedding(query_text)

        # 検索クエリの構築
        yql = "select _id, name, space, amenities, price from airbnb where "

        # Price pre-filtering
        if min_price is not None or max_price is not None:
            price_conditions = []
            if min_price is not None:
                price_conditions.append(f"price >= {min_price}")
            if max_price is not None:
                price_conditions.append(f"price <= {max_price}")
            yql += " and ".join(price_conditions)

        search_request = {
            "yql": yql,
            "input.query(q_vec)": query_vector,
            "ranking": "vector_similarity",
            "hits": 10,
        }

        response = requests.post(self.base_url, json=search_request)
        results = response.json()

        # WiFi post-filtering
        if wifi_required:
            filtered_results = []
            for hit in results.get("root", {}).get("children", []):
                if "WiFi" in hit["fields"]["amenities"]:
                    filtered_results.append(
                        {
                            "_id": hit["fields"]["id"],
                            "name": hit["fields"]["name"],
                            "space": hit["fields"]["space"],
                            "amenities": hit["fields"]["amenities"],
                            "price": hit["fields"]["price"],
                            "similarity_score": hit["relevance"],
                        }
                    )
            return filtered_results

        return [
            {
                "_id": hit["fields"]["id"],
                "name": hit["fields"]["name"],
                "space": hit["fields"]["space"],
                "amenities": hit["fields"]["amenities"],
                "price": hit["fields"]["price"],
                "similarity_score": hit["relevance"],
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
            wifi_required = input("WiFiは必須ですか？ (y/n): ").lower() == "y"

            # 価格のバリデーション
            min_price = int(min_price) if min_price else None
            max_price = int(max_price) if max_price else None

            # 検索実行
            results = searcher.search(query, min_price, max_price, wifi_required)

            # 結果の表示
            for result in results:
                print("\n---")
                print(f"Name: {result['name']}")
                print(f"Space: {result['space'][:200]}...")
                print(f"Price: ${result['price']}")
                print(f"Score: {result['similarity_score']:.3f}")
                print(f"Amenities: {', '.join(result['amenities'][:5])}...")

        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"エラーが発生しました: {e}")


if __name__ == "__main__":
    main()
