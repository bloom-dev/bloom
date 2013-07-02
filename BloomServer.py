from http.server import SimpleHTTPRequestHandler
import socketserver
 

class MyServer (SimpleHTTPRequestHandler):
	def do_GET(s):
		page = """<html><head><title>Hello</title></head><body><h2> It works </h2></body></html>"""
		s.send_response(200)
		s.send_header("Content-type","text/html")
		s.send_header("Content-length",len(page))
		s.end_headers()
		s.wfile.write(page.encode('utf-8'))


def bloomGo(port):
	httpd = socketserver.TCPServer(("",port), MyServer)
	httpd.serve_forever()

