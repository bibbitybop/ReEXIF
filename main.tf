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
# Criação da Role de Execução do Lambda
resource "aws_iam_role" "lambda_role" {
  name = "exif_processor_lambda_role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action    = "sts:AssumeRole"
      Effect    = "Allow"
      Principal = { Service = "://amazonaws.com" }
    }]
  })
}

# Permissão para o Lambda escrever logs e salvar dados no DynamoDB
resource "aws_iam_policy" "lambda_policy" {
  name = "exif_processor_lambda_policy"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action   = [
          "dynamodb:PutItem"
        ]
        Resource = "${aws_dynamodb_table.exif_table.arn}"
      },
      {
        Effect   = "Allow"
        Action   = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = "arn:aws:logs:*:*:*"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_logs" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = aws_iam_policy.lambda_policy.arn
}

# Compactação do código Python em ZIP para o deploy
data "archive_file" "lambda_zip" {
  type        = "zip"
  source_file = "lambda_function.py"
  output_path = "lambda_function.zip"
}

# Declaração da Função Lambda
resource "aws_lambda_function" "exif_lambda" {
  filename         = data.archive_file.lambda_zip.output_path
  function_name    = "exif_cleaner_backend"
  role             = aws_iam_role.lambda_role.arn
  handler          = "lambda_function.lambda_handler"
  runtime          = "python3.11"
  source_code_hash = data.archive_file.lambda_zip.output_base64sha256
  timeout          = 15

  # Layer que contém a biblioteca Pillow instalada para processar imagens
  layers = ["arn:aws:lambda:us-east-1:770693421928:layer:Klayers-p311-Pillow:2"]

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
  principal     = "://amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.http_api.execution_arn}/*/*"
}

# Output para copiar a URL gerada e colar no Frontend
output "api_url" {
  value       = aws_apigatewayv2_stage.default_stage.invoke_url
  description = "Cole esta URL na variável API_URL do seu arquivo index.html"
}
