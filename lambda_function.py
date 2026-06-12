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
        body = json.loads(event.get('body', '{}'))
        image_base64 = body.get('image')
        
        if not image_base64:
            return {"statusCode": 400, "body": json.dumps({"error": "Falta a imagem"})}
        
        # Obter IP e Data/Hora
        user_ip = event.get('requestContext', {}).get('identity', {}).get('sourceIp', '0.0.0.0')
        timestamp = datetime.utcnow().isoformat()
        
        # Processar Imagem
        image_bytes = base64.b64decode(image_base64)
        img = Image.open(BytesIO(image_bytes))
        
        # Extrair EXIF de forma simples
        exif_raw = img._getexif()
        exif_data = {}
        if exif_raw:
            for tag, val in exif_raw.items():
                if tag in ExifTags.TAGS:
                    # Converte bytes ou tipos complexos para string para evitar erros no JSON/DynamoDB
                    exif_data[ExifTags.TAGS[tag]] = str(val)
        
        if not exif_data:
            exif_data = {"info": "Nenhum dado EXIF encontrado"}

        # Criar imagem limpa (Salvar sem os metadados)
        output_buffer = BytesIO()
        # Salva apenas os dados dos pixels
        clean_img = Image.new(img.mode, img.size)
        clean_img.putdata(img.getdata())
        clean_img.save(output_buffer, format=img.format if img.format else 'JPEG')
        clean_image_base64 = base64.b64encode(output_buffer.getvalue()).decode('utf-8')

        # Salvar no Banco de Dados (DynamoDB)
        table.put_item(
            Item={
                'id': context.aws_request_id,
                'timestamp': timestamp,
                'user_ip': user_ip,
                'exif': exif_data
            }
        )

        # Retorno com cabeçalhos CORS liberados para o Frontend
        return {
            "statusCode": 200,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Content-Type",
                "Access-Control-Allow-Methods": "OPTIONS,POST"
            },
            "body": json.dumps({
                "exif": exif_data,
                "clean_image": clean_image_base64
            })
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "headers": { "Access-Control-Allow-Origin": "*" },
            "body": json.dumps({"error": str(e)})
        }
