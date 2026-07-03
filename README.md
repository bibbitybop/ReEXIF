## Removedor de metadados EXIF
Web app minimalista de três camadas (Frontend, Backend e Banco de Dados) projetada para visualizar e remover metadados EXIF de imagens. A aplicação é serverless e foi desenhada para usar a plataforma AWS.
------------------------------
## 🏛️ Arquitetura do Projeto## Cenário de Produção (AWS Serverless)

* Frontend: Página estática hospedada e servida de forma simples (ex: AWS S3).
* Backend: Função AWS Lambda (Python 3.11) exposta via AWS API Gateway (HTTP API). Processa imagens de forma leve usando a biblioteca Pillow.
* Banco de Dados: AWS DynamoDB, armazenando logs de upload (IP do usuário, timestamp e metadados extraídos) com cobrança sob demanda (Pay-per-request). [1] 
* Infraestrutura como Código (IaC): Provisionamento automatizado global via Terraform.

## Cenário de Teste (Local)

* Frontend: Servidor HTTP nativo do Python na porta 8080.
* Backend: Servidor HTTP nativo em Python (http.server) na porta 8000 emulando o comportamento do Lambda.
* Banco de Dados: Persistência simulada em um arquivo local banco_dados.json. [2] 

------------------------------
## 📂 Estrutura de Arquivos Recomendada

* index.html          # Frontend minimalista (HTML5/JavaScript)
* server.py           # Backend de testes local (Python)
* lambda_function.py  # Código-fonte do Backend para o AWS Lambda
* main.tf             # Infraestrutura como Código (Terraform)

------------------------------
## 🚀 Como Executar a Versão Local de Testes

Instale a biblioteca Pillow: pip install Pillow
Para rodar o backend: python server.py 
Para rodar o frontend: python -m http.server 8080

------------------------------
## 🛠️ Tecnologias Utilizadas

* Linguagens: HTML5, JavaScript, Python 3.11
* Processamento de Imagem: Pillow (PIL)
* Infraestrutura/Nuvem: AWS (Lambda, API Gateway, DynamoDB)
* Ferramentas de IaC: Terraform
