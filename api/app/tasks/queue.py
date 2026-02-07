from __future__ import annotations

from rq import Queue
from redis import Redis

from ..settings import settings


redis_conn = Redis.from_url(settings.redis_url)
queue = Queue("txt2video", connection=redis_conn)


def enqueue_render(render_id: int) -> None:
    from .worker import render_job

    queue.enqueue(render_job, render_id)


