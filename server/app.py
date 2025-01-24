import asyncio
import json
import signal
import os
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

        # Parse a PLAY event from the UI
        event = json.loads(message)

        assert(event["type"] == "PLAY")

        column = event["column"]
        row = event["row"]

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
            "column": column,
            "row": row,
        }
        broadcast(connected, json.dumps(event))

        if game.winner is not None:
            event = {
                "type": "WIN",
                "player": player,
            }
            broadcast(connected, json.dumps(event))

async def join(websocket, join_key):
    """
    Handles the connection for the second player. Joining a already initialized gme.
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

    message = websocket.recv()

    event = json.loads(message)

    assert event["type"] == "INIT"

    if "join_key" in event:

        # Second player is joining a game
        await join(websocket, event["join_key"])

    else:

        # First player is starting a game
        await start(websocket)

async def main():

    loop = asyncio.get_running_loop()
    stop = loop.create_future()
    loop.add_signal_handler(signal.SIGTERM, stop.set_result, None)

    port = int(os.environ.get("PORT", "8001"))
    async with serve(handler, "", port):
        await stop

if __name__ == "__main__":
    asyncio.run(main())