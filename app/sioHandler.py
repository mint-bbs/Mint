from collections import defaultdict
import socketio

from .cloudflare import Cloudflare

sio = socketio.AsyncServer(async_mode="asgi")

global_count = 0
max_global_count = 0
room_count: dict[int] = defaultdict(lambda: 0)
room_max_count: dict[int] = defaultdict(lambda: 0)

# Dictionary to track IPs and their associated session IDs
ip_to_sid = {}


@sio.event
async def connect(sid, environ, auth):
    global global_count
    global max_global_count

    if (Cloudflare.isCloudflareIP(environ["REMOTE_ADDR"])) and (
        "HTTP_CF_CONNECTING_IP" in environ
    ):
        client_ip = environ["HTTP_CF_CONNECTING_IP"]
    elif "HTTP_X_FORWARDED_FOR" in environ:
        client_ip = environ["HTTP_X_FORWARDED_FOR"]
    else:
        client_ip = environ["REMOTE_ADDR"]

    print(client_ip)

    if client_ip not in ip_to_sid:
        ip_to_sid[client_ip] = sid
        global_count += 1
        if global_count > max_global_count:
            max_global_count = global_count

    await sio.emit(
        "global_count_event",
        {"count": global_count, "max": max_global_count},
    )
    print(f"connected {sid}")
    print("connected member count", global_count)


@sio.event
async def disconnect(sid):
    global global_count
    client_ip = None
    for ip, connected_sid in ip_to_sid.items():
        if connected_sid == sid:
            client_ip = ip
            break

    if client_ip:
        del ip_to_sid[client_ip]

    if client_ip not in ip_to_sid:
        global_count -= 1

    await sio.emit(
        "global_count_event",
        {"count": global_count, "max": max_global_count},
    )
    for room in get_sid_rooms(sid):
        room_count[room] -= 1
        await sio.emit(
            "count_event",
            {"count": room_count[room], "max": room_max_count[room]},
            room=room,
        )
    print(f"disconnected {sid}")
    print("connected member count", global_count)


@sio.event
async def join_room(sid, room):
    await sio.enter_room(sid, room)
    room_count[room] += 1
    if room_count[room] > room_max_count[room]:
        room_max_count[room] = room_count[room]
    await sio.emit(
        "count_event",
        {"count": room_count[room], "max": room_max_count[room]},
        room=room,
    )
    print(f"joined {room}")
    print("connected member count", room_count[room])


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
