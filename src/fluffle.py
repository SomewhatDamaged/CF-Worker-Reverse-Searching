import io
from js import fetch, Uint8Array, Object
from workers import Response, Request
from json import dumps
from defs import *
from typing import Any
from yarl import URL

MAX_BYTES = 4 * 1024 * 1024

async def fluffle(request: Request, env: Any) -> Response:
    url = URL(request.url)
    queries = url.query
    image_url = queries["url"]
    image_config = {
        "width": 1000,
        "height": 1000,
        "fit": "scale-down",
        "format": "jpeg",
        "quality": 85
    }
    js_image_opts = Object.fromEntries(Object.entries(image_config))
    js_cf_block = Object.fromEntries(Object.entries({
        "image": js_image_opts
    }))
    fetch_options = Object.fromEntries(Object.entries({
        "cf": js_cf_block
    }))
    image_data = await fetch(image_url, fetch_options)
    raise ValueError(f"Resized Header: {image_data.headers.get('cf-resized')}")
    array_buffer = await image_data.arrayBuffer()

    js_result = await env.RPC.search(
        array_buffer,
        "16",
        "image/jpeg"
    )
    result = {
        "success": True,
        "data": js_result,
    }
    return Response(dumps(result), headers=json_header, status=200)