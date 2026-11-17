# Microsserviço de Autenticação (JWT + FastAPI + MongoDB)

Microsserviço responsável pelo cadastro, login, validação e revogação de sessões de usuários via tokens **JWT (RS256)** para a disciplina de **Sistemas Distribuídos**.

Esta aplicação foi projetada para rodar de forma isolada em containers **Docker**, permitindo que os demais serviços do projeto (banco de séries temporais e armazenamento de imagens no MinIO) validem o acesso dos usuários utilizando a chave pública JWT.

---

## Tecnologias Utilizadas

* **Python 3.11 + FastAPI:** Framework web para construção da API REST e documentação automática (Swagger).
* **PyJWT (RS256) + bcrypt:** Assinatura assimétrica de tokens JWT e criptografia de senhas.
* **MongoDB 7:** Banco de dados NoSQL para armazenamento de usuários e lista de revogação de tokens (*blacklist*).
* **Docker & Docker Compose:** Orquestração e isolamento dos containers da API e do banco de dados.

---

## Pré-requisitos

Você **não precisa** instalar Python nem MongoDB diretamente no seu computador. Basta ter instalado:

1. **Docker:**
   * **Windows / macOS:** [Docker Desktop](https://www.docker.com/products/docker-desktop/) (deixe-o aberto antes de executar os comandos).
   * **Linux:** Docker Engine + plugin Docker Compose.
2. **Git** ou **GitHub Desktop** (para clonar o repositório).

---

## Como Executar o Projeto

### 1. Clone o repositório
Abra o terminal (ou o GitHub Desktop) e baixe o projeto para sua máquina:

```bash
git clone <URL-DO-REPOSITORIO-DO-GRUPO>
cd <NOME-DA-PASTA-DO-PROJETO>
```

### 2. Configure o arquivo `.env`
Caso o arquivo `.env` não venha junto ao clonar o repositório (por estar listado no `.gitignore`), crie um arquivo chamado `.env` na raiz do projeto (ao lado do `docker-compose.yml`) e cole o conteúdo abaixo:

```env
MONGO_INITDB_ROOT_USERNAME=admin
MONGO_INITDB_ROOT_PASSWORD=password123
MONGO_INITDB_DATABASE=fastapi

DATABASE_URL=mongodb://admin:password123@mongo:27017/fastapi?authSource=admin

ACCESS_TOKEN_EXPIRES_IN=30
REFRESH_TOKEN_EXPIRES_IN=60
JWT_ALGORITHM=RS256

CLIENT_ORIGIN=http://localhost:3000

JWT_PRIVATE_KEY=LS0tLS1CRUdJTiBSU0EgUFJJVkFURSBLRVktLS0tLQpNSUlCT2dJQkFBSkJBSSs3QnZUS0FWdHVQYzEzbEFkVk94TlVmcWxzMm1SVmlQWlJyVFpjd3l4RVhVRGpNaFZuCi9KVHRsd3h2a281T0pBQ1k3dVE0T09wODdiM3NOU3ZNd2xNQ0F3RUFBUUpBYm5LaENOQ0dOSFZGaHJPQ0RCU0IKdmZ2ckRWUzVpZXAwd2h2SGlBUEdjeWV6bjd0U2RweUZ0NEU0QTNXT3VQOXhqenNjTFZyb1pzRmVMUWlqT1JhUwp3UUloQU84MWl2b21iVGhjRkltTFZPbU16Vk52TGxWTW02WE5iS3B4bGh4TlpUTmhBaUVBbWRISlpGM3haWFE0Cm15QnNCeEhLQ3JqOTF6bVFxU0E4bHUvT1ZNTDNSak1DSVFEbDJxOUdtN0lMbS85b0EyaCtXdnZabGxZUlJPR3oKT21lV2lEclR5MUxaUVFJZ2ZGYUlaUWxMU0tkWjJvdXF4MHdwOWVEejBEWklLVzVWaSt6czdMZHRDdUVDSUVGYwo3d21VZ3pPblpzbnU1clBsTDJjZldLTGhFbWwrUVFzOCtkMFBGdXlnCi0tLS0tRU5EIFJTQSBQUklWQVRFIEtFWS0tLS0t
JWT_PUBLIC_KEY=LS0tLS1CRUdJTiBQVUJMSUMgS0VZLS0tLS0KTUZ3d0RRWUpLb1pJaHZjTkFRRUJCUUFEU3dBd1NBSkJBSSs3QnZUS0FWdHVQYzEzbEFkVk94TlVmcWxzMm1SVgppUFpSclRaY3d5eEVYVURqTWhWbi9KVHRsd3h2a281T0pBQ1k3dVE0T09wODdiM3NOU3ZNd2xNQ0F3RUFBUT09Ci0tLS0tRU5EIFBVQkxJQyBLRVktLS0tLQ==
```

### 3. Suba os containers com Docker Compose
Na raiz do projeto, execute:

```bash
docker compose up --build -d
```

* Na primeira execução, o Docker baixará as imagens do Python e do MongoDB e instalará as dependências automaticamente.
* Para verificar se os containers estão ativos:
  ```bash
  docker ps
  ```
* Para acompanhar os logs da API em tempo real:
  ```bash
  docker logs -f microsservico-auth
  ```

---

## Como Testar a API

Com os containers em execução, acesse a interface interativa do Swagger no navegador:

**`http://localhost:8000/docs`**

### Rotas Disponíveis

| Método | Rota | Descrição |
| :--- | :--- | :--- |
| `GET` | `/api/healthchecker` | Verifica se o serviço está online. |
| `POST` | `/api/auth/register` | Cadastra um novo usuário (`name`, `email`, `password`). Retorna `409` se o e-mail já existir. |
| `POST` | `/api/auth/login` | Autentica o usuário e retorna o `access_token` (JWT válido por 30 min). |
| `GET` | `/api/auth/verify` | Valida o token JWT enviado no cabeçalho `Authorization: Bearer <token>`. |
| `POST` | `/api/auth/logout` | Revoga o token atual (adiciona à *blacklist* no MongoDB). |

### Passo a passo rápido no Swagger (`/docs`)
1. Execute **`POST /api/auth/register`** para criar uma conta.
2. Execute **`POST /api/auth/login`** com o mesmo e-mail e senha e copie o valor de `access_token` (sem as aspas).
3. Clique no botão **Authorize** (no topo direito da tela), cole o token no campo `Value` e clique em **Authorize** $\rightarrow$ **Close**.
4. Teste **`GET /api/auth/verify`** para confirmar que o token é válido.
5. Teste **`POST /api/auth/logout`** para encerrar a sessão e tente rodar `/verify` novamente para confirmar o bloqueio (`401 Unauthorized`).

---

## Comandos Úteis do Docker

* **Parar os containers:**
  ```bash
  docker compose down
  ```
* **Parar os containers e apagar todos os dados salvos no MongoDB:**
  ```bash
  docker compose down -v
  ```
* **Reconstruir após alterar dependências (`requirements.txt`):**
  ```bash
  docker compose up --build -d
  ```

---

## Resolução de Problemas Comuns

* **Erro de conexão com o daemon do Docker:** Certifique-se de que o **Docker Desktop** está aberto e com o status *Running* antes de rodar `docker compose up`.
* **Porta `8000` ou `6000` já está em uso:** Verifique se não há outro container ou serviço local ocupando essas portas (`docker ps`) ou altere o mapeamento de portas no `docker-compose.yml`.