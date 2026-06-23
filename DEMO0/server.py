import socket
import threading
import os
import mimetypes
from concurrent.futures import ThreadPoolExecutor

HOST = "0.0.0.0"
PORT = 8080
PUBLIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "public")
MAX_WORKERS = 32

CRLF = b"\r\n"

STATUS_TEXTS = {
    200: "OK",
    201: "Created",
    204: "No Content",
    301: "Moved Permanently",
    400: "Bad Request",
    403: "Forbidden",
    404: "Not Found",
    405: "Method Not Allowed",
    413: "Payload Too Large",
    500: "Internal Server Error",
}


def build_response(status_code, body=b"", content_type=None, extra_headers=None):
    status_text = STATUS_TEXTS.get(status_code, "Unknown")
    header_lines = [
        f"HTTP/1.1 {status_code} {status_text}",
        f"Content-Length: {len(body)}",
        "Connection: close",
        "Server: iRoboCity2030/1.0",
    ]

    if content_type:
        header_lines.append(f"Content-Type: {content_type}")

    if extra_headers:
        header_lines.extend(extra_headers)

    raw = CRLF.join(h.encode() for h in header_lines) + CRLF + CRLF + body
    return raw


def build_error_page(status_code, message=""):
    status_text = STATUS_TEXTS.get(status_code, "Unknown")
    title = f"{status_code} {status_text}"
    body_html = f"""<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"><title>{title}</title>
<link rel="stylesheet" href="/styles.css"></head>
<body>
<div class="error-container">
<h1>{status_code}</h1>
<p>{status_text}</p>
{"<p>" + message + "</p>" if message else ""}
<a href="/" class="btn">Go Home</a>
</div>
</body>
</html>""".encode()
    return build_response(status_code, body=body_html, content_type="text/html; charset=utf-8")


def guess_mime(path):
    mime, _ = mimetypes.guess_type(path)
    if mime and mime.startswith("text/"):
        return mime + "; charset=utf-8"
    return mime or "application/octet-stream"


def is_safe_path(base, candidate):
    real_base = os.path.realpath(base)
    real_candidate = os.path.realpath(candidate)
    return real_candidate.startswith(real_base + os.sep) or real_candidate == real_base


def serve_static(conn, request_path):
    if request_path == "/":
        request_path = "/index.html"

    fs_path = os.path.join(PUBLIC_DIR, request_path.lstrip("/"))

    if not is_safe_path(PUBLIC_DIR, fs_path):
        raw_resp = build_error_page(403, "Path traversal is not allowed.")
        conn.sendall(raw_resp)
        return

    if not os.path.isfile(fs_path):
        ext = os.path.splitext(request_path)[1]
        if not ext:
            alt_path = fs_path + ".html"
            if os.path.isfile(alt_path) and is_safe_path(PUBLIC_DIR, alt_path):
                fs_path = alt_path
            else:
                raw_resp = build_error_page(404, f"File not found: {request_path}")
                conn.sendall(raw_resp)
                return
        else:
            raw_resp = build_error_page(404, f"File not found: {request_path}")
            conn.sendall(raw_resp)
            return

    mime = guess_mime(fs_path)
    try:
        with open(fs_path, "rb") as f:
            body = f.read()
    except OSError:
        raw_resp = build_error_page(500, "Could not read file.")
        conn.sendall(raw_resp)
        return

    raw_resp = build_response(200, body=body, content_type=mime)
    conn.sendall(raw_resp)

    print(f"   [->] HTTP/1.1 200 {mime} ({len(body)} bytes)")


def handle_echo(conn, body):
    ct = "text/plain; charset=utf-8"
    raw_resp = build_response(200, body=body, content_type=ct)
    conn.sendall(raw_resp)
    print(f"   [->] HTTP/1.1 200 {ct} ({len(body)} bytes)")


def handle_connection(conn, addr):
    print(f"\n[+] Connection from {addr[0]}:{addr[1]}")
    try:
        data = conn.recv(65535)
        if not data:
            return

        header_end = data.find(CRLF + CRLF)
        if header_end == -1:
            raw_resp = build_error_page(400, "Malformed HTTP request.")
            conn.sendall(raw_resp)
            return

        raw_headers = data[:header_end]
        body_start = header_end + 4
        body = data[body_start:]

        print(f"  [<<] RECV {len(data)} bytes")
        print(f"  [>>] --- raw request ---")
        for line in raw_headers.decode("utf-8", errors="replace").split(CRLF.decode()):
            print(f"  [>>] {line}")
        print(f"  [>>] --- end ---")

        first_line = raw_headers.split(CRLF, 1)[0].decode("utf-8", errors="replace")
        parts = first_line.split()
        if len(parts) < 2:
            raw_resp = build_error_page(400, "Invalid request line.")
            conn.sendall(raw_resp)
            return

        method = parts[0].upper()
        path = parts[1]

        if method == "GET":
            serve_static(conn, path)
        elif method == "POST" and path == "/echo":
            handle_echo(conn, body)
        elif method == "POST":
            raw_resp = build_error_page(404, "POST endpoint not found.")
            conn.sendall(raw_resp)
        else:
            raw_resp = build_error_page(405, f"Method {method} not supported.")
            conn.sendall(raw_resp)

    except ConnectionResetError:
        print(f"   [!] Connection reset by {addr[0]}:{addr[1]}")
    except Exception as e:
        print(f"   [!] Error handling {addr[0]}:{addr[1]}: {e}")
        try:
            raw_resp = build_error_page(500, "Internal server error.")
            conn.sendall(raw_resp)
        except Exception:
            pass
    finally:
        conn.close()
        print(f"[-] Closed connection to {addr[0]}:{addr[1]}")


def main():
    os.makedirs(PUBLIC_DIR, exist_ok=True)
    os.makedirs(os.path.join(PUBLIC_DIR, "images"), exist_ok=True)

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen(128)

    print(f"[i] iRoboCity2030 HTTP Server", flush=True)
    print(f"[i] Listening on http://{HOST}:{PORT}", flush=True)
    print(f"[i] Serving files from: {PUBLIC_DIR}", flush=True)
    print(f"[i] Press Ctrl+C to stop.\n", flush=True)

    pool = ThreadPoolExecutor(max_workers=MAX_WORKERS)

    try:
        while True:
            conn, addr = server.accept()
            pool.submit(handle_connection, conn, addr)
    except KeyboardInterrupt:
        print("\n[i] Shutting down...")
    finally:
        pool.shutdown(wait=False)
        server.close()
        print("[i] Server stopped.")


if __name__ == "__main__":
    main()
