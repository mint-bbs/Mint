from collections import defaultdict
import socketio

from .cloudflare import Cloudflare

sio = socketio.AsyncServer(async_mode="asgi")

globalList = list()
maxGlobalCount = 0
roomList: dict[list] = defaultdict(lambda: list())
roomMaxCount: dict[int] = defaultdict(lambda: 0)

sidToAddr = {}


@sio.event
async def connect(sid, environ, auth):
    global globalList
    global maxGlobalCount

    if (Cloudflare.isCloudflareIP(environ["REMOTE_ADDR"])) and (
        "HTTP_CF_CONNECTING_IP" in environ
    ):
        clientAddr = environ["HTTP_CF_CONNECTING_IP"]
    elif "HTTP_X_FORWARDED_FOR" in environ:
        clientAddr = environ["HTTP_X_FORWARDED_FOR"]
    else:
        clientAddr = environ["REMOTE_ADDR"]

    sidToAddr[sid] = clientAddr

    globalList.append(clientAddr)
    if len(set(globalList)) > maxGlobalCount:
        maxGlobalCount = len(globalList)

    await sio.emit(
        "global_count_event",
        {"count": len(set(globalList)), "max": maxGlobalCount},
    )


@sio.event
async def disconnect(sid):
    global globalList
    clientAddr = sidToAddr[sid]

    del clientAddr[sid]

    globalList.remove(clientAddr)

    await sio.emit(
        "global_count_event",
        {"count": len(set(globalList)), "max": maxGlobalCount},
    )
    for room in get_sid_rooms(sid):
        roomList[room].remove(clientAddr)
        await sio.emit(
            "count_event",
            {"count": len(set(roomList[room])), "max": roomMaxCount[room]},
            room=room,
        )


@sio.event
async def join_room(sid, room):
    await sio.enter_room(sid, room)
    clientAddr = sidToAddr[sid]
    roomList[room].append(clientAddr)
    if len(set(roomList[room])) > roomMaxCount[room]:
        roomMaxCount[room] = len(set(roomList[room]))
    await sio.emit(
        "count_event",
        {"count": len(set(roomList[room])), "max": roomMaxCount[room]},
        room=room,
    )


def get_sid_rooms(sid):
    """
    Get the rooms that a given sid is subscribed to.

    Args:
            sid: The SID of the client to get the rooms for.

    Returns:
            A set of room names.
    """
    rooms = set()
    room_ids = sio.rooms(sid)
    for room_id in room_ids:
        rooms.add(room_id)

    return rooms
