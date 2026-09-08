import os
from urllib.parse import urlsplit, parse_qs
from js import globalThis, eval as js_eval, fetch
from workers import Response, Request
import json
from defs import *
from pyodide.ffi import to_js
from typing import Any

async def fluffle(request: Request, env: Any) -> Response:
    url = urlsplit(request.url)
    queries = parse_qs(url.query)
    image_data = await fetch(queries["url"][0])
    content_type = image_data.headers.get("content-type", "image/png")
    blob = await image_data.blob()

    js_path = os.path.join(os.path.dirname(__file__), "bridge.js")
    with open(js_path, "r") as f:
        js_code = f.read()
    js_eval(js_code)
    js_result = await globalThis.search(
        to_js(blob),
        "8",
        content_type
    )

    result = json.loads(js_result.to_py())
    result = {
        "success": True,
        "data": result,
    }
    return Response(json.dumps(result), headers=json_header, status=200)