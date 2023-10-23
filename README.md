# trabalho-sd-python

Trabalho de sistemas distribuídos com implementação de OAuth utilizando Python e o GitHub.

## Requisitos

- Python >= 3.8
- Pip >= 20.0.2

## Instalação

Crie um novo ambiente virtual com o comando:

```bash
python -m venv ./venv
```

Ative o ambiente virtual com o comando:

```bash
# Para Linux ou MAC
source ./venv/bin/activate
```

Instale as dependências com o comando:

```bash
pip install -r requirements.txt
```

## Credenciais

Para rodar o projeto com o fluxo de OAuth, serão necessárias credenciais do GitHub com o client_id e client_secret. No arquivo `.env.example` tem um exemplo de como deve ser o arquivo `.env` com as credenciais. Basta copiar o arquivo `.env.example` para `.env` e preencher os valores das variáveis.

## Execução

Para executar o projeto, basta executar o comando:

```bash
python src/main.py
```

Pronto, agora você pode acessar o servidor na url: http://localhost:8081
