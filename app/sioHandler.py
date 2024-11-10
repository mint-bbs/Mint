from collections import defaultdict

import socketio

from app.services.database import DatabaseService

sio = socketio.AsyncServer(async_mode="asgi")

global_count = 0
room_count: dict[int] = defaultdict(lambda: 0)


@sio.event
async def connect(sid, environ, auth):
    global global_count
    global_count += 1
    await sio.emit(
        "global_count_event",
        {"message": "client connected", "global_count": global_count},
    )
    print(f"connected", sid)
    print("connected member count", global_count)


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


@sio.event
async def disconnect(sid):
    global global_count
    global_count -= 1
    await sio.emit(
        "global_count_event",
        {"message": "client disconnected", "global_count": global_count},
    )
    for room in get_sid_rooms(sid):
        room_count[room] -= 1
        await sio.emit(
            "count_event",
            {"message": "client disconnected", "clients": room_count[room]},
            room=room,
        )
    print("disconnected", sid)
    print("connected member count", global_count)


@sio.event
async def join_room(sid, room):
    await sio.enter_room(sid, room)
    room_count[room] += 1
    await sio.emit(
        "count_event",
        {"message": "client connected", "clients": room_count[room]},
        room=room,
    )
    print("joinned", room)
    print("connected member count", room_count[room])
