from urllib.parse import urlsplit, parse_qs
from js import fetch
from workers import Response, Request
from json import dumps
from defs import *
from typing import Any

async def fluffle(request: Request, env: Any) -> Response:
    url = urlsplit(request.url)
    queries = parse_qs(url.query)
    image_url = queries["url"][0]
    raise ValueError(f"{image_url = }")
    headers = {"User-Agent": user_agent, "content-type": "image/*"}
    image_data = await fetch(image_url)
    content_type = image_data.headers.get("content-type", None)
    if content_type is None:
        content_type = "image/" + url.path.rsplit(".", 1)[1]
    array_buffer = await image_data.arrayBuffer()
    js_result = await env.RPC.search(
        array_buffer,
        "8",
        content_type
    )
    result = {
        "success": True,
        "data": js_result,
    }
    return Response(dumps(result), headers=json_header, status=200)