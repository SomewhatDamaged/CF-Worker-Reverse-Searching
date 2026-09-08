import io
from js import fetch, Uint8Array, Object
from workers import Response, Request
from json import dumps
from defs import *
from typing import Any
from yarl import URL

async def fluffle(request: Request, env: Any) -> Response:
    url = URL(request.url)
    queries = url.query
    image_url = queries["url"]
    fetch_options = Object.new()
    js_cf_block = Object.new()
    js_image_opts = Object.new()
    js_image_opts.width = 1200
    js_image_opts.height = 1200
    js_image_opts.fit = "scale-down"
    js_image_opts.format = "webp"
    js_image_opts.quality = 80
    js_cf_block.image = js_image_opts
    fetch_options.cf = js_cf_block
    image_data = await fetch(image_url, fetch_options)
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