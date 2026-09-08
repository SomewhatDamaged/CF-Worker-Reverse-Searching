import io
from js import fetch, Uint8Array
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
    image_data = await fetch(image_url)
    array_buffer = await image_data.arrayBuffer()

    from PIL import Image
    image_bytes = bytes(Uint8Array.new(array_buffer))
    img = Image.open(io.BytesIO(image_bytes))
    img_format = img.format if img.format else "JPEG"
    content_type = "image/" + img_format.lower()
    scale_factor = 0.95
    while True:
        output_buffer = io.BytesIO()
        if img_format.upper() in ["JPEG", "MPO"]:
            img.save(output_buffer, format=img_format, quality=95, optimize=True)
        else:
            img.save(output_buffer, format=img_format, optimize=True)

        output_bytes = output_buffer.getvalue()
        if len(output_bytes) <= MAX_BYTES:
            break
        width, height = img.size
        new_width = int(width * scale_factor)
        new_height = int(height * scale_factor)
        if new_width < 10 or new_height < 10:
            break
        img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

    output_buffer = io.BytesIO()
    img.save(output_buffer, format="PNG")
    final_bytes = output_buffer.getvalue()
    output_array_buffer = Uint8Array.new(final_bytes).buffer
    js_result = await env.RPC.search(
        output_array_buffer,
        "8",
        content_type
    )
    result = {
        "success": True,
        "data": js_result,
    }
    return Response(dumps(result), headers=json_header, status=200)