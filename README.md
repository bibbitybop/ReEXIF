## EXIF Viewer & Cleaner (Cloud-Native / Serverless)
Este projeto consiste em uma aplicação web leve e minimalista de três camadas (Frontend, Backend e Banco de Dados) projetada para visualizar e remover metadados EXIF de imagens. A arquitetura foi desenhada para ser totalmente Serverless na nuvem AWS, contando também com um ambiente de emulação local para testes rápidos.
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
* server.py           # Backend de testes local (Python)*
*  run_app.py          # Script gerenciador para rodar o ambiente local
* lambda_function.py  # Código-fonte do Backend para o AWS Lambda
* main.tf             # Infraestrutura como Código (Terraform)

------------------------------
## 🚀 Como Executar Localmente
Você pode testar e rodar o projeto inteiro no seu próprio computador ou dispositivo móvel (via Termux/Acode no Android) sem realizar nenhum deploy na nuvem.
## Pré-requisitos
Certifique-se de ter o Python instalado e a biblioteca de processamento de imagens Pillow:

pip install Pillow

## Execução Simplificada (Orquestrada)
Para iniciar o Frontend e o Backend locais simultaneamente com um único comando, execute:

python run_app.py

O script configurará o ambiente nos seguintes endereços:

* 🔗 Frontend: http://localhost:8080
* 🔗 Backend: http://localhost:8000/upload [3, 4] 

Se preferir rodar manualmente por terminais separados, utilize python server.py para o backend e python -m http.server 8080 para o frontend.
------------------------------
## 🛠️ Tecnologias Utilizadas

* Linguagens: HTML5, JavaScript (Vanilla ES6), Python 3.11
* Processamento de Imagem: Pillow (PIL)
* Infraestrutura/Nuvem: AWS (Lambda, API Gateway, DynamoDB)
* Ferramentas de IaC: Terraform

------------------------------
Gostaria que eu adicione as instruções detalhadas de como aplicar o comando do Terraform para subir o ambiente de produção na nuvem ou prefere incluir os detalhes de instalação do Termux para desenvolvimento no Android?

[1] [https://www.ic.unicamp.br](https://www.ic.unicamp.br/~reltech/PFG/2021/PFG-21-37.pdf)
[2] [https://www.dio.me](https://www.dio.me/articles/explorando-vuejs-o-caminho-para-uma-interface-frontend-mais-dinamica)
[3] [https://www.dio.me](https://www.dio.me/articles/explorando-vuejs-o-caminho-para-uma-interface-frontend-mais-dinamica)
[4] [https://dev.to](https://dev.to/davidrios/como-configurar-um-ambiente-de-desenvolvimento-com-docker-vs-code-2pc8)
