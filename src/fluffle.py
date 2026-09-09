import io
from js import fetch, Uint8Array, Object
from workers import Response, Request
from json import dumps
from defs import *
from typing import Any
from yarl import URL

async def fluffle(request: Request, env: Any) -> Response:
    # Process url
    url = URL(request.url)
    queries = url.query
    image_url = queries["url"]
    if url.path.endswith(".mp4") or url.path.endswith(".webm"):
        result = {
            "success": False,
            "error": "This URL ends with .mp4 or .webm format",
        }
        return Response(dumps(result), headers=json_header, status=415)
    # JS wrapping for the Cloudflare Image Resizing on fetch()
    fetch_options = Object.new()
    js_cf_block = Object.new()
    js_image_opts = Object.new()
    js_image_opts.width = 2000
    js_image_opts.height = 2000
    js_image_opts.fit = "scale-down"
    js_image_opts.format = "webp"
    js_image_opts.quality = 80
    js_cf_block.image = js_image_opts
    fetch_options.cf = js_cf_block
    # Actually do the fetch()
    image_data = await fetch(image_url, fetch_options)
    if not image_data.ok:
        return Response(dumps({"success": False}), status=400)
    # Convert into an array buffer
    array_buffer = await image_data.arrayBuffer()
    # Hit up the RPC to prod Fluffle
    js_result = await env.RPC.search(
        array_buffer,
        "16",
        "image/jpeg"
    )
    results = format_output(dict(js_result))
    try:
        result = {
            "success": True,
            "hits": results,
            "num_hits": len(results),
        }
        return Response(dumps(result), headers=json_header, status=200)
    except Exception:
        return Response(dumps({"success": False}), status=500)

def format_output(input_array: dict) -> list:
    assert "results" in input_array
    output_array = []
    for result in input_array["results"]:
        if float(result["distance"]) < 0.8:
            continue
        output_array.append(result["url"])
    return output_array