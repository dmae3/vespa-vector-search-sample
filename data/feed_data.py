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

    for item in tqdm(data):
        doc = {
            "id": item["_id"],
            "name": item["name"],
            "space": item["space"],
            "amenities": item["amenities"],
            "price": item["price"],
            "text_embeddings": {"values": item["text_embeddings"]},
        }

        response = requests.post(f"{base_url}{item['_id']}", json=doc)
        if response.status_code not in [200, 201]:
            print(f"Error feeding document {item['_id']}: {response.text}")


def main():
    wait_for_vespa()

    print("Loading dataset...")
    dataset = load_dataset("MongoDB/airbnb_embeddings")

    print("Feeding data to Vespa...")
    feed_to_vespa(dataset["train"])


if __name__ == "__main__":
    main()
