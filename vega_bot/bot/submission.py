from dataclasses import dataclass
from typing import Optional


@dataclass
class OrderAmendment:
    order_id: str
    size_delta: float
    price: float


@dataclass
class OrderCancellation:
    market_id: str
    order_id: Optional[str] = None


@dataclass
class OrderSubmission:
    market_id: str
    size: float
    price: float
    time_in_force: str
    type: str
    side: str


@dataclass
class BatchMarketInstruction:
    submissions: list[OrderSubmission]
    cancellations: list[OrderCancellation]
    amendments: list[OrderAmendment]


def convert_to_decimals(decimal_places: int, number: float) -> float:
    return number / (10**decimal_places)


def convert_from_decimals(decimal_places: int, number: float) -> int:
    return int(number * (10**decimal_places))


def _submission_to_json(
    submission: OrderSubmission, price_decimals: int, position_decimals: int
) -> dict[str, str]:
    return {
        "marketId": submission.market_id,
        "timeInForce": submission.time_in_force,
        "type": submission.type,
        "side": submission.side,
        "size": str(convert_from_decimals(position_decimals, submission.size)),
        "price": str(convert_from_decimals(price_decimals, submission.price)),
    }


def _cancellation_to_json(cancellation: OrderCancellation) -> dict[str, str]:
    res = {"marketId": cancellation.market_id}
    if cancellation.order_id:
        res["orderId"] = cancellation.order_id
    return res


def _amendment_to_json(
    amendment: OrderAmendment, price_decimals: int, position_decimals: int
) -> dict[str, str]:
    return {
        "orderId": amendment.order_id,
        "size_delta": str(
            convert_from_decimals(position_decimals, amendment.size_delta)
        ),
        "price": str(convert_from_decimals(price_decimals, amendment.price)),
    }


def instruction_to_json(
    instruction: BatchMarketInstruction, price_decimals: int, position_decimals: int
) -> dict:
    return {
        "batchMarketInstructions": {
            "submissions": [
                _submission_to_json(
                    s,
                    price_decimals=price_decimals,
                    position_decimals=position_decimals,
                )
                for s in instruction.submissions
            ],
            "amendments": [
                _amendment_to_json(
                    s,
                    price_decimals=price_decimals,
                    position_decimals=position_decimals,
                )
                for s in instruction.amendments
            ],
            "cancellations": [
                _cancellation_to_json(s) for s in instruction.cancellations
            ],
        }
    }
