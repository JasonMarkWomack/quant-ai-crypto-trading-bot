import requests


class VegaWallet:
    def __init__(self, token: str, wallet_url: str, pub_key: str):
        self.token = token
        self.wallet_url = wallet_url
        self.pub_key = pub_key

        self.session = requests.Session()
        self.session.headers = {
            "Origin": "VegaBot",
            "Authorization": f"VWT {self.token}",
        }

    def submit_transaction(self, transaction: dict) -> None:
        self.session.post(
            self.wallet_url + "/api/v2/requests",
            json={
                "jsonrpc": "2.0",
                "method": "client.send_transaction",
                "params": {
                    "publicKey": self.pub_key,
                    "sendingMode": "TYPE_SYNC",
                    "transaction": transaction,
                },
                "id": "request",
            },
        )
