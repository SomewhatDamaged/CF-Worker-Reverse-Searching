import os
from urllib.parse import urlsplit, parse_qs
from js import fetch
from workers import Response, Request
import json
from defs import *
from typing import Any

async def fluffle(request: Request, env: Any) -> Response:
    url = urlsplit(request.url)
    queries = parse_qs(url.query)
    image_data = await fetch(queries["url"][0])
    content_type = image_data.headers.get("content-type", "image/png")
    array_buffer = await image_data.arrayBuffer()
    rpc = env.RPC
    js_result = await rpc.search(
        array_buffer,
        "8",
        content_type
    )
    result = js_result
    result = {
        "success": True,
        "data": result,
    }
    return Response(json.dumps(result), headers=json_header, status=200)