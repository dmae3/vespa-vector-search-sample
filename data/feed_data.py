import os
from datasets import load_dataset
import requests
from tqdm import tqdm
import time


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


def feed_to_vespa(data):
    base_url = "http://vespa:8080/document/v1/airbnb/airbnb/docid/"
    total_count = len(data)
    success_count = 0
    error_count = 0

    print(f"データの総数: {total_count}件")

    progress_bar = tqdm(data, desc="Feeding data", unit="doc")
    for item in progress_bar:
        doc = {
            "fields": {
                "id": item["_id"],
                "name": item["name"],
                "space": item["space"],
                "amenities": item["amenities"],
                "price": item["price"],
                "text_embeddings": {"values": item["text_embeddings"]},
            }
        }

        try:
            response = requests.post(f"{base_url}{item['_id']}", json=doc)
            if response.status_code in [200, 201]:
                success_count += 1
            else:
                error_count += 1
                print(f"\nError feeding document {item['_id']}: {response.text}")
        except Exception as e:
            error_count += 1
            print(f"\nException while feeding document {item['_id']}: {str(e)}")

        # 進捗状況の更新
        progress_bar.set_postfix(
            {
                "success": success_count,
                "errors": error_count,
                "success_rate": f"{(success_count/total_count)*100:.1f}%",
            }
        )

    print("\n=== 最終結果 ===")
    print(f"成功: {success_count}件")
    print(f"エラー: {error_count}件")
    print(f"成功率: {(success_count/total_count)*100:.1f}%")


def main():
    wait_for_vespa()

    print("データセットを読み込んでいます...")
    dataset = load_dataset("MongoDB/airbnb_embeddings")
    print("データセットの読み込みが完了しました")

    print("Vespaへのデータ投入を開始します...")
    feed_to_vespa(dataset["train"])


if __name__ == "__main__":
    main()
