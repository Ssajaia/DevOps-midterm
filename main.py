from http.server import BaseHTTPRequestHandler, HTTPServer

ROUTES = {
    "/": "Welcome",
    "/about": "Simple server built with the standard library",
}


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        body = ROUTES.get(self.path)
        if body is None:
            self.send_response(404)
            body = "Not found"
        else:
            self.send_response(200)
        data = body.encode()
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)


def make_server(port=8000):
    return HTTPServer(("", port), Handler)


if __name__ == "__main__":
    server = make_server(8000)
    print("Listening on http://localhost:8000")
    server.serve_forever()
