import { connect } from "cloudflare:sockets";

export default {
  async search(imageBytes, limit, contentType) {
    const boundary = "----WebKitFormBoundaryExcessiveSpace";
    const host = "api.fluffle.xyz";

    // 1. Dynamically append the correct content-type header inside the multi-part partition
    const headerPart =
      `--${boundary}\r\n` +
      `Content-Disposition: form-data; name="file"; filename="image"\r\n` +
      `Content-Type: ${contentType}\r\n\r\n`; // <--- Dynamic entry mapping

    const footerPart =
      `\r\n--${boundary}\r\n` +
      `Content-Disposition: form-data; name="limit"\r\n\r\n` +
      `${limit}\r\n` +
      `--${boundary}--\r\n`;

    const encoder = new TextEncoder();
    const headerBuffer = encoder.encode(headerPart);
    const footerBuffer = encoder.encode(footerPart);

    // Stitch chunks cleanly into a single unified array layout
    const fullBody = new Uint8Array(headerBuffer.length + imageBytes.length + footerBuffer.length);
    fullBody.set(headerBuffer, 0);
    fullBody.set(imageBytes, headerBuffer.length);
    fullBody.set(footerBuffer, headerBuffer.length + imageBytes.length);

    // 2. Clear case-preserved headers
    const httpHeaders =
      `POST /exact-search-by-file HTTP/1.1\r\n` +
      `Host: ${host}\r\n` +
      `User-Agent: ExcessiveSpaceSearcher/1.0 (by dev at excessive space)\r\n` +
      `Content-Type: multipart/form-data; boundary=${boundary}\r\n` +
      `Content-Length: ${fullBody.length}\r\n` +
      `Connection: close\r\n\r\n`;

    // 3. Connect raw TCP streaming socket tunnel
    const socket = connect(`${host}:443`, { secureTransport: "on" });
    const writer = socket.writable.getWriter();
    const reader = socket.readable.getReader();

    await writer.write(encoder.encode(httpHeaders));
    await writer.write(fullBody);
    await writer.close();

    // 4. Capture streaming results data
    let chunks = [];
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      chunks.push(value);
    }

    const totalLength = chunks.reduce((acc, chunk) => acc + chunk.length, 0);
    const responseBuffer = new Uint8Array(totalLength);
    let offset = 0;
    for (const chunk of chunks) {
      responseBuffer.set(chunk, offset);
      offset += chunk.length;
    }

    const rawResponse = new TextDecoder("utf-8").decode(responseBuffer);

    const parts = rawResponse.split("\r\n\r\n");
    return JSON.parse(parts[1]);
  }
};
