import asyncio
import json
import itertools
import signal
import os
from secrets import token_urlsafe
from websockets.asyncio.server import broadcast, serve
from threeinarow import PLAYER_ONE, PLAYER_TWO, Threeinarow

JOIN = {}


async def error(websocket, message):
    """
    Sends an error message to the client.

    Arguments:
        websocket: The connection to the client.
        message: The error message to send.
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

    join_key = token_urlsafe(6)

    JOIN[join_key] = game, connected

    try:
        # Sends the unique join key to the browser of the player
        # initializing the game. Will be displayed in the browser to be shared.
        event = {
            "type": "INIT",
            "join_key": join_key,
        }
        # Send the unique join key to the browser of the first player
        await websocket.send(json.dumps(event))

        # Receiving the move of player 1.
        await play(websocket, game, PLAYER_ONE, connected)

    finally:
        del JOIN[join_key]


async def play(websocket, game, player, connected):
    """
    Receive and process moves from a player

    Arguments:
        websocket: The connection to the client.
        game: The game instance.
        player: The player
        connected: The connections.
    """
    async for message in websocket:
        event = json.loads(message)
        assert (event["type"] == "PLAY")
        row = event["row"]
        column = event["column"]

        try:
            # Plays the move
            game.play(player, column, row)
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
        broadcast(connected, json.dumps(event))

        # If the played move is a winning event, send a WIN event.
        if game.winner is not None:
            event = {
                "type": "WIN",
                "player": player,
            }
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
        # Receive and process moves from the second player
        await play(websocket, game, PLAYER_TWO, connected)
    finally:
        connected.remove(websocket)


async def handler(websocket):
    """
    Handles a connection based on who is connecting
    """

    message = await websocket.recv()
    event = json.loads(message)
    assert event["type"] == "INIT"

    if "join_key" in event:
        # Second player is joining a game
        await join(websocket, event["join_key"])
    else:
        # First player initiaizes the game
        await start(websocket)

async def main():

    loop = asyncio.get_running_loop()
    stop = loop.create_future()
    loop.add_signal_handler(signal.SIGINT, stop.set_result, None)

    port = int(os.environ.get("PORT", "8001"))
    async with serve(handler, "", port):
        await stop


if __name__ == "__main__":
    asyncio.run(main())
