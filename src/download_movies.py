import csv
import requests
from datetime import datetime
from typing import Any
from tqdm import tqdm


base_query = """
SELECT ?film ?filmLabel
    (GROUP_CONCAT(DISTINCT ?genreLabel; separator=", ") AS ?genres)
    (GROUP_CONCAT(DISTINCT ?countryLabel; separator=", ") AS ?countries)
    (GROUP_CONCAT(DISTINCT ?directorLabel; separator=", ") AS ?directors)
WHERE {
    ?film wdt:P31 wd:Q11424;
        wdt:P577 ?releaseDate;
    OPTIONAL { ?film wdt:P136 ?genre.
        ?genre rdfs:label ?genreLabel.
        FILTER(LANG(?genreLabel) = "en") }
    OPTIONAL { ?film wdt:P495 ?country.
        ?country rdfs:label ?countryLabel.
        FILTER(LANG(?countryLabel) = "en") }
    OPTIONAL { ?film wdt:P57 ?director.
        ?director rdfs:label ?directorLabel.
        FILTER(LANG(?directorLabel) = "en") }
    SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }
}
GROUP BY ?film ?filmLabel
    """


def fetch_by_year(year: int) -> list[dict[str, Any]]:
    data = []
    limit = 1000
    offset = 0

    while True:
        query = base_query.replace(
            "FILTER(YEAR(?releaseDate) = 2010)", f"FILTER(YEAR(?releaseDate) = {year})")

        query += f" LIMIT {limit} OFFSET {offset}"
        url = "https://query.wikidata.org/sparql"

        response = requests.get(
            url, headers={"Accept": "application/json"}, params={"query": query})

        if response.status_code == 200:
            batch_data = response.json()["results"]["bindings"]

            if not batch_data:
                break

            data.extend(batch_data)
            offset += limit

        else:
            print(f"Failed to retrieve data for {
                  year}, status code: {response.status_code}")
            break

        return data


def fetch_all_data():
    current_year = datetime.now().year

    for year in tqdm(range(1888, current_year + 1), total=current_year + 1 - 1888):
        data = fetch_by_year(year)

    csv_file_name = f"movies_data_{year}_to_current.csv"

    with open(csv_file_name, mode="w", newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["title", "genres", "country", "extra_data"])

        for item in data:
            directors = item.get("directors", {}).get("value", "")

            writer.writerow([
                item.get("film", {}).get("value", ""),
                item.get("filmLabel", {}).get("value", ""),
                item.get("genres", {}).get("value", ""),
                item.get("countries", {}).get("value", ""),
                {"directors", directors}
            ])


if __name__ == "__main__":
    fetch_all_data()
