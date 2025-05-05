import http.server
import socketserver
import json
import pathlib
import textwrap
import google.generativeai as genai


def to_markdown(text):
    text = text.replace('•', '  *')
    return textwrap.indent(text, '> ', predicate=lambda _: True)

class TextHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/send-text':
            text_to_send = 'Python http.server から送信されたテキストです！'
            self.send_response(200)
            self.send_header('Content-type', 'text/plain; charset=utf-8')
            self.end_headers()
            self.wfile.write(text_to_send.encode('utf-8'))
        else:
            super().do_GET() # 他のファイルリクエストなどを処理

    def do_POST(self):
        if self.path == '/receive-text':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode('utf-8')
            print(f"クライアントから受信したテキスト: {post_data}")
            self.send_response(200)
            self.send_header('Content-type', 'text/plain; charset=utf-8')
            self.send_header('Access-Control-Allow-Origin', '*') # すべてのオリジンからのアクセスを許可
            self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS') # 許可するHTTPメソッド
            self.send_header('Access-Control-Allow-Headers', 'Content-Type') # 許可するリクエストヘッダー
            self.end_headers()
            genai.configure(api_key="AIzaSyAAgb6cs4phDmzek-SajupWUlXgtJCx1D8")
            model = genai.GenerativeModel('gemini-1.5-pro-latest')
            try:
                response = model.generate_content(f"この文章を新聞っぽくして！結果のみ出力して！タイトルではなく文章だよ！ {post_data}")
                markdown_output = to_markdown(response.text)
                print(markdown_output)
                self.wfile.write(markdown_output.encode('utf-8'))
            except Exception as e:
                print(f"Gemini API エラー: {e}")
                self.send_response(500)
                self.send_header('Content-type', 'text/plain; charset=utf-8')
                self.end_headers()
                self.wfile.write(f"Gemini API エラーが発生しました: {e}".encode('utf-8'))
        elif self.path == '/send-text':
            text_to_send = 'Python http.server から送信されたテキストです！'
            self.send_response(200)
            self.send_header('Content-type', 'text/plain; charset=utf-8')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(text_to_send.encode('utf-8'))
        elif self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(b"<html><body><h1>Hello from Python HTTP Server!</h1></body></html>")
        else:
            super().do_GET()

    def do_OPTIONS(self):
        if self.path == '/receive-text':
            self.send_response(200)
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
            self.end_headers()
        else:
            super().do_OPTIONS()

with socketserver.TCPServer(("", 3945), TextHandler) as httpd:
    print("serving at port", 3945)
    httpd.serve_forever()
