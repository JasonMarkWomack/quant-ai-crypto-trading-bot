import requests
from typing import Optional


def execute_unrollable_get_request(path: str, key: str, node_url: str):
    query_url = f"{node_url}/{path}"

    response = requests.get(query_url)
    response.raise_for_status()

    results = []
    response_json = response.json()
    edges = response_json[key]["edges"]
    for edge in edges:
        results.append(edge["node"])

    # Here you unroll any paginated queries.
    # Each query will have a 'pageInfo' component which gives details about pagination.
    # Use the `endCursor` field to start the next query's results.
    while response_json[key]["pageInfo"]["hasNextPage"]:
        response = requests.get(
            query_url
            + f"&pagination.after={response_json[key]['pageInfo']['endCursor']}"
        )
        response.raise_for_status()
        response_json = response.json()
        edges = response_json[key]["edges"]
        for edge in edges:
            results.append(edge["node"])

    return results


def execute_get_request(path: str, key: str, node_url: str):
    query_url = f"{node_url}/{path}"

    response = requests.get(query_url)
    response.raise_for_status()

    return response.json()[key]


def get_markets(node_url: str) -> list[dict]:
    return execute_unrollable_get_request("markets", "markets", node_url=node_url)


def get_market(node_url: str, market_id: str) -> list[dict]:
    return execute_get_request(f"market/{market_id}", "market", node_url=node_url)


def get_market_data(node_url: str, market_id: str) -> list[dict]:
    return execute_get_request(
        f"market/data/{market_id}/latest", "marketData", node_url=node_url
    )


def get_assets(node_url: str) -> list[dict]:
    return execute_unrollable_get_request("assets", "assets", node_url=node_url)


def get_accounts(party_id: str, node_url: str) -> list[dict]:
    return execute_unrollable_get_request(
        f"accounts?filter.partyIds={party_id}", "accounts", node_url=node_url
    )


def get_open_orders(party_id: str, node_url: str) -> list[dict]:
    return execute_unrollable_get_request(
        f"orders?filter.partyIds={party_id}&filter.liveOnly=true",
        "orders",
        node_url=node_url,
    )


def get_positions(
    party_id: str, node_url: str, market_id: Optional[str] = None
) -> list[dict]:
    filt = f"positions?filter.partyIds={party_id}"
    if market_id is not None:
        filt += f"&filter.marketIds={market_id}"
    return execute_unrollable_get_request(
        filt,
        "positions",
        node_url=node_url,
    )
