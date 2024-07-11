import datetime
import logging
import os
import time

import dotenv

import bot.submission as sub
import bot.vega_api_client as client
from bot.wallet import VegaWallet


def main(
    node_rest_url: str,
    market_id: str,
    party_id: str,
    token: str,
    wallet_url: str,
    max_abs_position: int =1,
):
    market_info = client.get_market(node_url=node_rest_url, market_id=market_id)
    market_price_decimals = int(market_info["decimalPlaces"])
    market_pos_decimals = int(market_info["positionDecimalPlaces"])
    wallet = VegaWallet(token=token, wallet_url=wallet_url, pub_key=party_id)
    while True:
        time.sleep(1)
        latest_data = client.get_market_data(
            node_url=node_rest_url, market_id=market_id
        )
        best_bid = sub.convert_to_decimals(
            number=int(latest_data["bestBidPrice"]),
            decimal_places=market_price_decimals,
        )
        best_offer = sub.convert_to_decimals(
            number=int(latest_data["bestOfferPrice"]),
            decimal_places=market_price_decimals,
        )

        # This get_positions query will return an empty list if there
        # has never been trading on the market, so handle that case.
        position = client.get_positions(
            party_id=party_id, market_id=market_id, node_url=node_rest_url
        )

        position = (
            sub.convert_to_decimals(
                number=int(position[0]["openVolume"]),
                decimal_places=market_pos_decimals,
            )
            if len(position) > 0
            else 0
        )

        submissions = []
        if position < max_abs_position:
            submissions.append(
                sub.OrderSubmission(
                    market_id=market_id,
                    size=1,
                    price=best_bid,
                    time_in_force="TIME_IN_FORCE_GTC",
                    type="TYPE_LIMIT",
                    side="SIDE_BUY",
                )
            )
        if position > -1 * max_abs_position:
            submissions.append(
                sub.OrderSubmission(
                    market_id=market_id,
                    size=1,
                    price=best_offer,
                    time_in_force="TIME_IN_FORCE_GTC",
                    type="TYPE_LIMIT",
                    side="SIDE_SELL",
                )
            )
        batch_tx = sub.BatchMarketInstruction(
            submissions=submissions,
            cancellations=[sub.OrderCancellation(market_id=market_id)],
            amendments=[],
        )

        wallet.submit_transaction(
            sub.instruction_to_json(
                instruction=batch_tx,
                price_decimals=market_price_decimals,
                position_decimals=market_pos_decimals,
            )
        )

        print("--------------------------------------")
        print(f"At time {datetime.datetime.now()}")
        print(f"Latest prices are {best_bid} - {best_offer}")
        print(f"Position is {position}")
        print("--------------------------------------")


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(message)s",
    )
    dotenv.load_dotenv()
    main(
        node_rest_url=os.environ["NODE_URL"],
        market_id=os.environ["MARKET_ID"],
        token=os.environ["WALLET_TOKEN"],
        party_id=os.environ["PARTY_ID"],
        wallet_url=os.environ["WALLET_URL"],
        max_abs_position=1,
    )
