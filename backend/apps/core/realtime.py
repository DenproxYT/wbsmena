"""In-process pub/sub для Server-Sent Events (один процесс воркера)."""
import json
import queue
import threading
from typing import Dict, Iterable, Optional

_lock = threading.Lock()
_subscribers: list[tuple[int, queue.Queue]] = []


def subscribe(user_id: int) -> queue.Queue:
    q: queue.Queue = queue.Queue(maxsize=100)
    with _lock:
        _subscribers.append((user_id, q))
    return q


def unsubscribe(user_id: int, q: queue.Queue) -> None:
    with _lock:
        _subscribers[:] = [(uid, sq) for uid, sq in _subscribers if not (uid == user_id and sq is q)]


def _put(q: queue.Queue, event_type: str, data: Optional[Dict] = None) -> None:
    try:
        q.put_nowait({'type': event_type, 'data': data or {}})
    except queue.Full:
        pass


def publish_user(user_id: int, event_type: str, data: Optional[Dict] = None) -> None:
    with _lock:
        targets = [q for uid, q in _subscribers if uid == user_id]
    for q in targets:
        _put(q, event_type, data)


def publish_users(user_ids: Iterable[int], event_type: str, data: Optional[Dict] = None) -> None:
    ids = set(user_ids)
    if not ids:
        return
    with _lock:
        targets = [q for uid, q in _subscribers if uid in ids]
    for q in targets:
        _put(q, event_type, data)


def publish_all(event_type: str, data: Optional[Dict] = None) -> None:
    with _lock:
        targets = [q for _, q in _subscribers]
    for q in targets:
        _put(q, event_type, data)


def format_sse(event_type: str, data: Optional[Dict] = None) -> str:
    payload = json.dumps(data or {}, ensure_ascii=False)
    return f'event: {event_type}\ndata: {payload}\n\n'
