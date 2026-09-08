from urllib.parse import urlsplit, parse_qs
from js import fetch as pyfetch
from workers import Response, Request
import json
import io
from defs import *

async def fluffle(request: Request) -> Response:
    import httpx
    url = urlsplit(request.url)
    queries = parse_qs(url.query)
    if "url" not in queries.keys():
        return Response('{"error": "Missing \'url\' parameter"}', headers=json_header, status=400)
    image_data = await pyfetch(queries["url"][0])
    blob = await image_data.blob()
    array_buffer = await blob.arrayBuffer()
    python_bytes = array_buffer.to_py().tobytes()
    buffer = io.BytesIO(python_bytes)
    headers = {
        "User-Agent": "ExcessiveSpace-ReverseSearcher-v1"
    }
    files = {
        "file": ("image", buffer.getvalue(), "image/*")
    }
    data = {
        "limit": "8"
    }
    async with httpx.AsyncClient(headers=headers) as client:
        response = await client.post(
            'https://api.fluffle.xyz/exact-search-by-file',
            data=data,
            files=files
        )
        result = response.json()
    result = {
        "success": True,
        "data": result
    }
    return Response(json.dumps(result), headers=json_header, status=200)