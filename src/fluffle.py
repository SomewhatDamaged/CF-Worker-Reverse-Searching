import os
from urllib.parse import urlsplit, parse_qs
from js import globalThis, eval as js_eval, fetch
from workers import Response, Request
import json
from defs import *
from pyodide.ffi import to_js
from typing import Any
from pathlib import Path

async def fluffle(request: Request, env: Any) -> Response:
    url = urlsplit(request.url)
    queries = parse_qs(url.query)
    image_data = await fetch(queries["url"][0])
    content_type = image_data.headers.get("content-type", "image/png")
    blob = await image_data.blob()
    data = []
    current_dir = os.getcwd()
    data.append(f"{current_dir = }")

    # Recursively loop through directories and files
    print("All files and directories underneath:")
    for root, dirs, files in os.walk(current_dir):
        # Print subdirectories
        for directory in dirs:
            data.append(str(os.path.join(root, directory)))
        # Print files
        for file in files:
            data.append(str(os.path.join(root, file)))
    raise ValueError(f"Path: {'/n'.join(data)}")
    js_path = os.path.join("bridge.js")
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