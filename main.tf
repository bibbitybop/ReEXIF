provider "aws" {
  region = "us-east-1"
}

# 1. BANCO DE DADOS (DynamoDB)
resource "aws_dynamodb_table" "exif_table" {
  name         = "exif_metadata_log"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "id"

  attribute {
    name = "id"
    type = "S"
  }
}

# 2. BACKEND (AWS Lambda)
# Compactação do código Python em ZIP para o deploy
data "archive_file" "lambda_zip" {
  type        = "zip"
  source_dir  = "." # Passa a ler o diretório completo atual
  output_path = "lambda_function.zip"
  
  # Evita colocar arquivos de configuração do próprio Terraform dentro da sua função Lambda
  excludes    = ["main.tf", "terraform.tfstate", "terraform.tfstate.backup", "lambda_function.zip", ".terraform", ".terraform.lock.hcl"]
}

# Declaração da Função Lambda utilizando a Role padrão do laboratório Vocareum
resource "aws_lambda_function" "exif_lambda" {
  filename         = data.archive_file.lambda_zip.output_path
  function_name    = "exif_cleaner_backend"
  
  # AQUI ESTÁ A MUDANÇA: Usando a Role pré-existente da AWS Academy / Vocareum
  role             = "arn:aws:iam::803047874156:role/LabRole"
  
  handler          = "lambda_function.lambda_handler"
  runtime          = "python3.11"
  source_code_hash = data.archive_file.lambda_zip.output_base64sha256
  timeout          = 60

  environment {
    variables = {
      TABLE_NAME = aws_dynamodb_table.exif_table.name
    }
  }
}

# 3. CAMADA DE CONEXÃO (API Gateway v2 HTTP)
resource "aws_apigatewayv2_api" "http_api" {
  name          = "exif_cleaner_api"
  protocol_type = "HTTP"
  cors_configuration {
    allow_origins = ["*"]
    allow_methods = ["POST", "OPTIONS"]
    allow_headers = ["content-type"]
  }
}

resource "aws_apigatewayv2_integration" "lambda_integration" {
  api_id           = aws_apigatewayv2_api.http_api.id
  integration_type = "AWS_PROXY"
  integration_uri  = aws_lambda_function.exif_lambda.invoke_arn
}

resource "aws_apigatewayv2_route" "upload_route" {
  api_id    = aws_apigatewayv2_api.http_api.id
  route_key = "POST /upload"
  target    = "integrations/${aws_apigatewayv2_integration.lambda_integration.id}"
}

resource "aws_apigatewayv2_stage" "default_stage" {
  api_id      = aws_apigatewayv2_api.http_api.id
  name        = "$default"
  auto_deploy = true
}

resource "aws_lambda_permission" "api_gw_per_lambda" {
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.exif_lambda.function_name
  
  # Ensure this contains ONLY the string without spaces or hidden characters
  principal     = "apigateway.amazonaws.com"
  
  source_arn    = "${aws_apigatewayv2_api.http_api.execution_arn}/*/*"
}

# Output para copiar a URL gerada e colar no Frontend
output "api_url" {
  value       = "https://t9p1pbc0ve.execute-api.us-east-1.amazonaws.com/"
  description = "Cole esta URL na variável API_URL do seu arquivo index.html"
}
