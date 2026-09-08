from urllib.parse import urlsplit, parse_qs
from js import fetch as pyfetch
from workers import Response, Request
import json
import io
from defs import *

async def fluffle(request: Request) -> Response:
    import httpx
    from httpx_socks import AsyncProxyTransport
    url = urlsplit(request.url)
    queries = parse_qs(url.query)
    if "url" not in queries.keys():
        return Response('{"error": "Missing \'url\' parameter"}', headers=json_header, status=400)
    image_data = await pyfetch(queries["url"][0])
    content_type = image_data.headers.get("content-type")
    blob = await image_data.blob()
    array_buffer = await blob.arrayBuffer()
    python_bytes = array_buffer.to_py().tobytes()
    buffer = io.BytesIO(python_bytes)
    headers = {
        "user-agent": user_agent
    }
    files = {
        "file": ("image." + content_type.split("/")[1], buffer.getvalue(), content_type)
    }
    data = {
        "limit": "8"
    }
    transport = AsyncProxyTransport.from_url('socks5://localhost:1080')
    async with httpx.AsyncClient(headers=headers, transport=transport, http1=True, http2=False) as client:
        response = await client.post(
            'https://api.fluffle.xyz/exact-search-by-file',
            data=data,
            files=files
        )
        result = response.json()
    result = {
        "success": True,
        "data": result,
        "user-agent": user_agent,
    }
    return Response(json.dumps(result), headers=json_header, status=200)