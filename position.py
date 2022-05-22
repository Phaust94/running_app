"""
Modeling a user position
"""

from __future__ import annotations

import copy
import time
import typing
from dataclasses import dataclass
import re
import binascii
from sqlite3 import connect, Connection

import pandas as pd

import helpers
import secrets
import constants

__all__ = [
    "UserPosition",
    "BadRequestDataError",
]


USER_LOC_RE = re.compile(r"user_loc\[([a-zA-Z0-9]+)\]")


class BadRequestDataError(ValueError):
    pass


@dataclass
class UserPosition:
    user_id: int
    team_id: int
    latitude: float
    longitude: float
    accuracy: float
    ts: float

    @classmethod
    def from_form(cls, request_data: typing.Dict[str, typing.Any]) -> UserPosition:
        user_loc = {}
        for k, v in request_data.items():
            dc = re.findall(USER_LOC_RE, k)
            if not dc:
                continue
            inner_key = dc[0]
            user_loc[inner_key] = v
        game_data = request_data.get("game_data")
        if game_data is None:
            raise BadRequestDataError("Game data is not defined")
        try:
            game_data_decoded = helpers.decrypt_qeng_data(game_data, secrets.API_KEY)
        except (binascii.Error, ValueError) as e:
            raise BadRequestDataError("Game data is not valid")

        try:
            loc_data = dict(
                latitude=float(user_loc["latitude"]),
                longitude=float(user_loc["longitude"]),
                accuracy=float(user_loc["accuracy"])
            )
        except KeyError as e:
            raise BadRequestDataError("Missing one of the required location fields")
        except ValueError:
            raise BadRequestDataError("Incorrect data passed to location data")

        try:
            game_data_renamed = dict(
                user_id=game_data_decoded["u"],
                team_id=game_data_decoded["tm"],
                game_id=game_data_decoded["gid"],
            )
        except KeyError:
            raise BadRequestDataError("Missing required fields in game-data")

        if game_data_renamed["game_id"] not in secrets.VALID_GAME_IDS:
            raise BadRequestDataError(f"Wrong game ID passed: {game_data_renamed['game_id']}")

        game_data_renamed.pop("game_id")

        inst = cls(
            **game_data_renamed,
            **loc_data,
            ts=time.time(),
        )
        return inst

    def to_dict(self) -> typing.Dict[str, typing.Union[int, float]]:
        res = copy.copy(self.__dict__)
        return res

    def to_db(self, db_conn: Connection) -> None:
        s = pd.DataFrame([self.to_dict()])
        s.to_sql(constants.RAW_DATA_TNAME, db_conn, if_exists="append", index=False)
        return None

