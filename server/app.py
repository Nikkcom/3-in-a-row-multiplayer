import asyncio
import json
import itertools
from multiprocessing.managers import Array
from secrets import token_urlsafe

from websockets.asyncio.server import broadcast, serve

from threeinarow import PLAYER_ONE, PLAYER_TWO, Threeinarow

JOIN = {}

async def error(websocket, message):
    """
    Send an error message
    """

    event = {
        "type": "ERROR",
        "message": message
    }
    print(f"Sending event: {json.dumps(event)}")
    await websocket.send(json.dumps(event))

async def start(websocket):
    """
    Handles the connection from first player. First connection starts a game.
    """

    game = Threeinarow()

    connected = {websocket}

    join_key = token_urlsafe(3)

    JOIN[join_key] = game, connected

    try:
        event = {
            "type": "INIT",
            "join_key": join_key,
        }

        await websocket.send(json.dumps(event))

        await play(websocket, game, PLAYER_ONE, connected)

    finally:
        del JOIN[join_key]

async def play(websocket, game, player, connected):
    """
    Receive and process moves from a player
    """

    async for message in websocket:
        # Logging
        print(f"Received message in play: {message}")

        # Parse a PLAY event from the UI
        event = json.loads(message)

        assert(event["type"] == "PLAY")

        row = event["row"]
        column = event["column"]

        try:

            # Plays the move
            game.play(PLAYER_ONE, column, row)

        except ValueError as exc:

            # Send an ERROR event if the move was illegal.
            await error(websocket, str(exc))
            continue

        event = {
            "type": "PLAY",
            "player": player,
            "row": row,
            "column": column,
        }
        print(f"broadcasts event: {json.dumps(event)}")
        broadcast(connected, json.dumps(event))

        if game.winner is not None:
            event = {
                "type": "WIN",
                "player": player,
            }
            print(f"broadcasts event: {json.dumps(event)}")
            broadcast(connected, json.dumps(event))

async def join(websocket, join_key):
    """
    Handles the connection for the second player. Joining an already initialized gme.
    """


    try:
        game, connected = JOIN[join_key]

    except KeyError:
        await error(websocket, "Game not found.")
        return

    # Adds the connection
    connected.add(websocket)

    try:

        await play(websocket, game, PLAYER_TWO, connected)
    finally:
        connected.remove(websocket)

async def handler(websocket):
    """
    Handles a connection based on who is connecting
    """

    # Initializes a game.
    game = Threeinarow()
    print(f"Game initialized")
    print(f"Game= {len(game.board)}")

    # Players alternate turns in the same browser.
    turns = itertools.cycle([PLAYER_ONE, PLAYER_TWO])
    player = next(turns)

    async for message in websocket:
        print(f"Received message in handler: {message}")
        # Parses a PLAY event from the UI
        event = json.loads(message)
        assert(event["type"] == "PLAY")
        row = event["row"]
        column = event["column"]

        try:

            # Tries to play the move.
            game.play(player, row, column)
            print(f"game.play success")
        except ValueError as exc:
            print(f"Error: {exc}")  # Debugging line
            # Send an ERROR event if the move was illegal.
            event = {
                "type": "ERROR",
                "message": str(exc),
            }
            print(f"Sending event: {json.dumps(event)}")
            await websocket.send(json.dumps(event))
            continue
        # Send a PLAY event to update the UI
        event = {
            "type": "PLAY",
            "player": player,
            "row": row,
            "column": column,
        }
        print(f"Sending event: {json.dumps(event)}")
        await websocket.send(json.dumps(event))

        if game.winner is not None:
            event = {
                "type": "WIN",
                "player": player,
                "winning_pos": game.winning_position,
            }
            print(f"Sending event: {json.dumps(event)}")
            await websocket.send(json.dumps(event))

        player = next(turns)

async def main():

    async with serve(handler, "", 8001):

        await asyncio.get_running_loop().create_future()  # run forever

if __name__ == "__main__":
    asyncio.run(main())