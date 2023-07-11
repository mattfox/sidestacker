import asyncio
import json

import aiohttp
import asyncpg_listen
from sanic import Blueprint
from sanic.log import logger
import aiopg
import psycopg2
import asyncio

game_blueprint = Blueprint("Game")


@game_blueprint.websocket("/changes")
async def changes(request, ws):
    """
    When a notification about game updates is received from PostgreSQL, emit an event on the websocket.
    """
    await ws.send(json.dumps({'event': 'connected'}))
    session_id = request.cookies.get("sessionid")
    if not session_id:
        return

    # Get the game ID associated with this session.
    async with aiohttp.ClientSession(raise_for_status=True) as session:
        try:
            async with session.get(
                    f"{request.app.config.HTTP_URL}_game/",
                    cookies={"sessionid": session_id}
            ) as response:
                result = await response.json()
                game_id = result['id']
        except aiohttp.ClientError as e:
            logger.warn(f"Failed to get game ID: {e}")

    async def handle_game_changes(conn):
        async with conn.cursor() as cur:
            await cur.execute("LISTEN game_changes")
            while True:
                try:
                    notification = await conn.notifies.get()
                    logger.debug(f'Got notification: {notification.payload}')
                    changed_game_id, changed_session_id = notification.payload.split(':')
                    changed_game_id = int(changed_game_id)
                    if game_id == changed_game_id and session_id != changed_session_id:
                        # This is the game we're interested in, and the change did not come from our session.
                        await ws.send(json.dumps({'event': 'changed'}))
                except psycopg2.Error as e:
                    logger.warn(f'Failed to receive notification: {e}')
                    return
                except KeyboardInterrupt:
                    return

    async with aiopg.connect(request.app.config.DATABASE_URL) as listenConn:
        listener = handle_game_changes(listenConn)
        await asyncio.gather(listener)
