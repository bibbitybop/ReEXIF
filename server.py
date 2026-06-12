import json
import base64
from datetime import datetime
from io import BytesIO
from http.server import BaseHTTPRequestHandler, HTTPServer
from PIL import Image, ExifTags

PORT = 8000

class LocalBackendHandler(BaseHTTPRequestHandler):
    # Configura o CORS para permitir que o Frontend acesse o backend local
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

    # Responde a requisições de verificação do navegador (CORS)
    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    # Processa o Upload da Imagem
    def do_POST(self):
        if self.path == '/upload':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            try:
                body = json.loads(post_data.decode('utf-8'))
                image_base64 = body.get('image')
                
                if not image_base64:
                    self.send_response(400)
                    self.end_headers()
                    self.wfile.write(json.dumps({"error": "Falta a imagem"}).encode('utf-8'))
                    return

                # Obter IP simulado e Data/Hora atual
                user_ip = self.client_address[0]
                timestamp = datetime.now().isoformat()
                
                # Processar Imagem e extrair EXIF
                image_bytes = base64.b64decode(image_base64)
                img = Image.open(BytesIO(image_bytes))
                
                exif_raw = img._getexif()
                exif_data = {}
                if exif_raw:
                    for tag, val in exif_raw.items():
                        if tag in ExifTags.TAGS:
                            exif_data[ExifTags.TAGS[tag]] = str(val)
                
                if not exif_data:
                    exif_data = {"info": "Nenhum dado EXIF encontrado"}

                # Criar imagem limpa (sem metadados)
                output_buffer = BytesIO()
                clean_img = Image.new(img.mode, img.size)
                clean_img.putdata(img.getdata())
                clean_img.save(output_buffer, format=img.format if img.format else 'JPEG')
                clean_image_base64 = base64.b64encode(output_buffer.getvalue()).decode('utf-8')

                # SIMULAÇÃO DO BANCO DE DADOS: Salva em um arquivo JSON local
                log_entry = {
                    "id": str(int(datetime.now().timestamp())),
                    "timestamp": timestamp,
                    "user_ip": user_ip,
                    "exif": exif_data
                }
                
                try:
                    with open("banco_dados.json", "r+") as db_file:
                        data = json.load(db_file)
                        data.append(log_entry)
                        db_file.seek(0)
                        json.dump(data, db_file, indent=4)
                except FileNotFoundError:
                    with open("banco_dados.json", "w") as db_file:
                        json.dump([log_entry], db_file, indent=4)

                # Resposta de Sucesso
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                
                response_body = {
                    "exif": exif_data,
                    "clean_image": clean_image_base64
                }
                self.wfile.write(json.dumps(response_body).encode('utf-8'))

            except Exception as e:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode('utf-8'))

if __name__ == '__main__':
    server = HTTPServer(('localhost', PORT), LocalBackendHandler)
    print(f"🚀 Servidor backend rodando localmente em http://localhost:{PORT}")
    server.serve_forever()
