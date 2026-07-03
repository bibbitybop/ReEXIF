import json
import base64
import os
from datetime import datetime
from io import BytesIO
import boto3
from PIL import Image, ExifTags

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['TABLE_NAME'])

def lambda_handler(event, context):
    try:
        # Garante a leitura correta do corpo enviado pelo HTTP API v2.0
        body_raw = event.get('body', '{}')
        
        # O API Gateway pode codificar o body inteiro em base64 se for binário
        if event.get('isBase64Encoded', False):
            body_raw = base64.b64decode(body_raw).decode('utf-8')
            
        body = json.loads(body_raw)
        image_base64 = body.get('image')
        
        if not image_base64:
            return {
                "statusCode": 400,
                "headers": { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" },
                "body": json.dumps({"error": "Falta a imagem"})
            }
        
        # Mapeamento seguro de IP no Payload v2.0 da AWS
        request_context = event.get('requestContext', {})
        http_info = request_context.get('http', {})
        user_ip = http_info.get('sourceIp', '0.0.0.0')
        timestamp = datetime.utcnow().isoformat()
        
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

        # Criar nova imagem limpa (sem metadados)
        output_buffer = BytesIO()
        clean_img = Image.new(img.mode, img.size)
        clean_img.putdata(img.getdata())
        clean_img.save(output_buffer, format=img.format if img.format else 'JPEG')
        clean_image_base64 = base64.b64encode(output_buffer.getvalue()).decode('utf-8')

        # Gravar log de segurança no DynamoDB
        table.put_item(
            Item={
                'id': context.aws_request_id,
                'timestamp': timestamp,
                'user_ip': user_ip,
                'exif': exif_data
            }
        )

        # Retorno HTTP de sucesso com CORS embutido
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Content-Type",
                "Access-Control-Allow-Methods": "POST, OPTIONS"
            },
            "body": json.dumps({
                "exif": exif_data,
                "clean_image": clean_image_base64
            })
        }

    except Exception as e:
        # Em caso de pane, retorna o log do erro de forma transparente no navegador
        return {
            "statusCode": 500,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*"
            },
            "body": json.dumps({"error": f"Erro interno no Lambda: {str(e)}"})
        }
