from urllib.parse import urlsplit, parse_qs
import js
from workers import Response, Request
import json
from defs import *
from pyodide.ffi import to_js

async def fluffle(request: Request) -> Response:
    url = urlsplit(request.url)
    queries = parse_qs(url.query)
    if "url" not in queries.keys():
        return Response('{"error": "Missing \'url\' parameter"}', headers=json_header, status=400)
    image_data = await js.fetch(queries["url"][0])
    content_type = image_data.headers.get("content-type")
    blob = await image_data.blob()
    try:
        from cloudflare import sockets
    except ImportError:
        sockets = js.require("cloudflare:sockets")
    boundary = "----WebKitFormBoundaryExcessiveSpace"
    body_parts = [f"--{boundary}\r\n".encode(),
                  f'Content-Disposition: form-data; name="file"; filename="image.{content_type.split("/")[1]}"\r\n'.encode(),
                  f"Content-Type: {content_type}\r\n\r\n".encode(), blob, b"\r\n", f"--{boundary}\r\n".encode(),
                  f'Content-Disposition: form-data; name="limit"\r\n\r\n'.encode(), b"8\r\n",
                  f"--{boundary}--\r\n".encode()]
    full_body = b"".join(body_parts)
    http_headers = (
        f"POST /exact-search-by-file HTTP/1.1\r\n"
        f"Host: api.fluffle.xyz\r\n"
        f"User-Agent: {user_agent}\r\n"
        f"Content-Type: multipart/form-data; boundary={boundary}\r\n"
        f"Content-Length: {len(full_body)}\r\n"
        f"Connection: close\r\n\r\n"
    ).encode()
    socket = sockets.connect("api.fluffle.xyz/exact-search-by-file:443", to_js({"secureTransport": "on"}))
    writer = socket.writable.getWriter()
    reader = socket.readable.getReader()
    await writer.write(js.Uint8Array.new(to_js(http_headers)))
    await writer.write(js.Uint8Array.new(to_js(full_body)))
    await writer.close()
    chunks = []
    while True:
        result = await reader.read()
        if result.done:
            break
        chunks.append(bytes(result.value))

    raw_response = b"".join(chunks).decode('utf-8', errors='ignore')
    parts = raw_response.split("\r\n\r\n", 1)
    if len(parts) < 2:
        return Response(json.dumps({"error": "Invalid HTTP response raw format from server", "raw": raw_response}), headers=json_header, status=400)

    json_string = parts[1]
    result = json.loads(json_string)
    result = {
        "success": True,
        "data": result,
    }
    return Response(json.dumps(result), headers=json_header, status=200)