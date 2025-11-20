# Trabalho T1 - Infraestrutura de Certificação Digital e Servidor Web Seguro

**Disciplina:** Segurança em Computação - 2025/2  
**Professor:** Rodolfo da Silva Villaça  
**Alunos:** Guilherme Silveira Gomes Brotto  
**Link dos Vídeos:**  
[Demonstração - Tarefa 1](https://youtube.com/watch?v=gkwXvUsuurU)  
[Demonstração - Tarefa 2](https://youtube.com/watch?v=_HibHEtrjyU)

## Sumário

1. [Introdução](#introdução)
2. [Ambiente de Desenvolvimento](#ambiente-de-desenvolvimento)
3. [Tarefa 1 - Implementação com Python](#tarefa-1---implementação-com-python)
4. [Tarefa 2 - Implementação com OpenSSL](#tarefa-2---implementação-com-openssl)
5. [Validação e Testes](#validação-e-testes)
6. [Diferenças entre CA Pública e Privada](#diferenças-entre-ca-pública-e-privada)
7. [Conclusão](#conclusão)
8. [Referências](#referências)

---

## Introdução

Este trabalho tem como objetivo implementar uma Infraestrutura de Chaves Públicas (PKI) completa, composta por uma CA Raiz e uma CA Intermediária, utilizando duas abordagens diferentes: Python (com a biblioteca `cryptography`) e OpenSSL. Ambas as implementações criam certificados digitais válidos para um servidor HTTPS rodando em Nginx via Docker.

A estrutura de certificação implementada replica o modelo hierárquico usado em ambientes corporativos, onde uma CA Raiz (mantida offline e segura) assina uma CA Intermediária, que por sua vez emite certificados para servidores e clientes.

---

## Ambiente de Desenvolvimento

### Especificações Técnicas

- **Sistema Operacional:** Linux Ubuntu
- **Docker:** 26.1.3
- **NGINX:** 1.29.3
- **Python:** 3.x
- **Biblioteca Python:** cryptography
- **OpenSSL:** 3.x

### Estrutura de Diretórios
```
trabalho-pki/
├── tarefa1-python/
│   ├── create_cas.py
│   ├── certificate_service.py
│   ├── validate_chain.py
│   ├── certs/
│   ├── nginx/
│   │   ├── html/
│   │   ├── certs/
│   │   └── nginx.conf
│   └── docker-compose.yml
│
└── tarefa2-openssl/
    ├── ca/
    │   ├── root/
    │   ├── intermediate/
    │   └── server/
    ├── nginx/
    │   ├── html/
    │   ├── certs/
    │   └── nginx.conf
    └── docker-compose.yml
```

---

## Tarefa 1 - Implementação com Python

### Objetivo

Implementar um serviço completo de emissão de certificados digitais utilizando Python, demonstrando a criação programática de uma PKI funcional.

### Pré-requisitos
```bash
# Instalar biblioteca cryptography
pip install cryptography
```

### Passo 1: Criar Estrutura de Diretórios
```bash
mkdir -p tarefa1-python/{certs,nginx/html,nginx/certs}
cd tarefa1-python
```

### Passo 2: Criar CAs (Raiz e Intermediária)
```bash
# Executar script para criar CA Raiz e CA Intermediária
python3 create_cas.py
```

**Saída esperada:**
```
✓ CA Raiz criada: certs/ca-root.key, certs/ca-root.pem
✓ CA Intermediária criada: certs/ca-intermediate.key, certs/ca-intermediate.pem
```

**Arquivos gerados:**
- `certs/ca-root.key` - Chave privada RSA 4096 bits da CA Raiz
- `certs/ca-root.pem` - Certificado autoassinado da CA Raiz
- `certs/ca-intermediate.key` - Chave privada RSA 4096 bits da CA Intermediária
- `certs/ca-intermediate.pem` - Certificado da CA Intermediária assinado pela CA Raiz

### Passo 3: Emitir Certificado do Servidor
```bash
# Executar serviço de certificação para o domínio localhost
python3 certificate_service.py localhost
```

**Saída esperada:**
```
✓ Certificado emitido para: localhost
✓ Arquivos criados: certs/server.key, certs/server.crt, certs/server-fullchain.crt
```

**Arquivos gerados:**
- `certs/server.key` - Chave privada RSA 2048 bits do servidor
- `certs/server.crt` - Certificado do servidor assinado pela CA Intermediária
- `certs/server-fullchain.crt` - Cadeia completa (servidor + CA Intermediária)

### Passo 4: Validar Cadeia de Certificação
```bash
# Executar script de validação
python3 validate_chain.py
```

**Saída esperada:**
```
=== Validação da Cadeia de Certificação ===

✓ CA Intermediária verificada pela CA Raiz
✓ Certificado do Servidor verificado pela CA Intermediária

=== Estrutura da PKI ===

CA Raiz:
  Subject: CN=Root CA,OU=DI,O=UFES,L=Vitoria,ST=ES,C=BR
  Issuer:  CN=Root CA,OU=DI,O=UFES,L=Vitoria,ST=ES,C=BR

CA Intermediária:
  Subject: CN=Intermediate CA,OU=DI,O=UFES,L=Vitoria,ST=ES,C=BR
  Issuer:  CN=Root CA,OU=DI,O=UFES,L=Vitoria,ST=ES,C=BR

Certificado do Servidor:
  Subject: CN=localhost,OU=DI,O=UFES,L=Vitoria,ST=ES,C=BR
  Issuer:  CN=Intermediate CA,OU=DI,O=UFES,L=Vitoria,ST=ES,C=BR
  SANs: localhost, 127.0.0.1
```

### Passo 5: Configurar e Iniciar Servidor Nginx
```bash
# Copiar certificados para o diretório do Nginx
cp certs/server-fullchain.crt nginx/certs/
cp certs/server.key nginx/certs/

# Criar página HTML
cat > nginx/html/index.html << EOF
<!DOCTYPE html>
<html>
<head>
    <title>HTTPS Seguro - Tarefa 1 Python</title>
</head>
<body>
    <h1>Conexão HTTPS Segura com Python!</h1>
    <p>Certificado emitido via serviço Python</p>
</body>
</html>
EOF

# Criar configuração do Nginx
cat > nginx/nginx.conf << EOF
events {
    worker_connections 1024;
}

http {
    server {
        listen 443 ssl;
        server_name localhost;

        ssl_certificate /etc/nginx/certs/server-fullchain.crt;
        ssl_certificate_key /etc/nginx/certs/server.key;

        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers HIGH:!aNULL:!MD5;

        location / {
            root /usr/share/nginx/html;
            index index.html;
        }
    }
}
EOF

# Criar docker-compose.yml
cat > docker-compose.yml << EOF
version: '3'
services:
  nginx:
    image: nginx:latest
    ports:
      - "443:443"
    volumes:
      - ./nginx/html:/usr/share/nginx/html
      - ./nginx/certs:/etc/nginx/certs
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf
    restart: unless-stopped
EOF

# Iniciar container Docker
docker-compose up -d
```


### Passo 6: Importar CA Raiz no Navegador

**Arquivo a importar:** `certs/ca-root.pem`

#### Firefox:
1. Abrir **Configurações** → **Privacidade e Segurança**
2. Rolar até **Certificados** → **Ver Certificados**
3. Aba **Autoridades** → **Importar**
4. Selecionar `certs/ca-root.pem`
5. Marcar **"Confiar nesta CA para identificar sites"**
6. Clicar em **OK**

#### Chrome/Edge:
1. Abrir **Configurações** → **Privacidade e segurança** → **Segurança**
2. Clicar em **Gerenciar certificados**
3. Aba **Autoridades de Certificação Raiz Confiáveis**
4. Clicar em **Importar**
5. Selecionar `certs/ca-root.pem`
6. Concluir importação

### Passo 7: Acessar Servidor HTTPS

Acessar no navegador: `https://localhost`

**Verificações:**
- Certificado exibido como válido (ícone de cadeado seguro)
- Cadeia de certificação: localhost → Intermediate CA → Root CA
- Nenhum aviso de segurança

---

## Tarefa 2 - Implementação com OpenSSL

### Objetivo

Demonstrar a criação manual de uma PKI completa utilizando a ferramenta OpenSSL, documentando cada etapa do processo.

### Passo 1: Criar Estrutura de Diretórios
```bash
mkdir -p tarefa2-openssl/ca/{root,intermediate,server}
cd tarefa2-openssl/ca
```

### Passo 2: Criar CA Raiz (Autoassinada)
```bash
# Gerar chave privada RSA 4096 bits da CA Raiz
openssl genrsa -out root/ca-root.key 4096

# Criar certificado autoassinado da CA Raiz (validade 10 anos)
openssl req -x509 -new -nodes -key root/ca-root.key -sha256 -days 3650 \
  -out root/ca-root.pem \
  -subj "/C=BR/ST=ES/L=Vitoria/O=UFES/OU=DI/CN=Root CA"
```

### Passo 3: Criar CA Intermediária
```bash
# Gerar chave privada RSA 4096 bits da CA Intermediária
openssl genrsa -out intermediate/ca-intermediate.key 4096

# Criar CSR (Certificate Signing Request) da CA Intermediária
openssl req -new -key intermediate/ca-intermediate.key \
  -out intermediate/ca-intermediate.csr \
  -subj "/C=BR/ST=ES/L=Vitoria/O=UFES/OU=DI/CN=Intermediate CA"

# Criar arquivo de extensões para CA Intermediária
cat > intermediate/intermediate-ext.cnf << EOF
basicConstraints = critical,CA:TRUE,pathlen:0
keyUsage = critical,keyCertSign,cRLSign
subjectKeyIdentifier = hash
authorityKeyIdentifier = keyid:always,issuer
EOF

# Assinar certificado da CA Intermediária com a CA Raiz (validade 5 anos)
openssl x509 -req -in intermediate/ca-intermediate.csr \
  -CA root/ca-root.pem \
  -CAkey root/ca-root.key \
  -CAcreateserial \
  -out intermediate/ca-intermediate.pem \
  -days 1825 -sha256 \
  -extfile intermediate/intermediate-ext.cnf
```

### Passo 4: Criar Certificado do Servidor
```bash
# Gerar chave privada RSA 2048 bits do servidor
openssl genrsa -out server/server.key 2048

# Criar CSR do servidor para localhost
openssl req -new -key server/server.key \
  -out server/server.csr \
  -subj "/C=BR/ST=ES/L=Vitoria/O=UFES/OU=DI/CN=localhost"

# Criar arquivo de extensões do servidor (SANs e uso de chave)
cat > server/server-ext.cnf << EOF
subjectAltName = DNS:localhost,IP:127.0.0.1
basicConstraints = CA:FALSE
keyUsage = digitalSignature, keyEncipherment
extendedKeyUsage = serverAuth
EOF

# Assinar certificado do servidor com a CA Intermediária (validade 1 ano)
openssl x509 -req -in server/server.csr \
  -CA intermediate/ca-intermediate.pem \
  -CAkey intermediate/ca-intermediate.key \
  -CAcreateserial \
  -out server/server.crt \
  -days 365 -sha256 \
  -extfile server/server-ext.cnf

# Criar arquivo fullchain (certificado do servidor + CA Intermediária)
cat server/server.crt intermediate/ca-intermediate.pem > server/server-fullchain.crt
```

### Passo 5: Validar Cadeia de Certificação
```bash
# Verificar cadeia de certificação completa
openssl verify -CAfile root/ca-root.pem \
  -untrusted intermediate/ca-intermediate.pem \
  server/server.crt
```

**Saída esperada:**
```
server/server.crt: OK
```

**Verificar extensões da CA Intermediária:**
```bash
openssl x509 -in intermediate/ca-intermediate.pem -text -noout | grep -A 5 "X509v3 extensions"
```

**Saída esperada:**
```
        X509v3 extensions:
            X509v3 Basic Constraints: critical
                CA:TRUE, pathlen:0
            X509v3 Key Usage: critical
                Certificate Sign, CRL Sign
            X509v3 Subject Key Identifier:
```

**Exibir estrutura da PKI:**
```bash
echo "=== CA Raiz ==="
openssl x509 -in root/ca-root.pem -noout -subject -issuer

echo "=== CA Intermediária ==="
openssl x509 -in intermediate/ca-intermediate.pem -noout -subject -issuer

echo "=== Certificado do Servidor ==="
openssl x509 -in server/server.crt -noout -subject -issuer
```

**Saída esperada:**
```
=== CA Raiz ===
subject=C = BR, ST = ES, L = Vitoria, O = UFES, OU = DI, CN = Root CA
issuer=C = BR, ST = ES, L = Vitoria, O = UFES, OU = DI, CN = Root CA

=== CA Intermediária ===
subject=C = BR, ST = ES, L = Vitoria, O = UFES, OU = DI, CN = Intermediate CA
issuer=C = BR, ST = ES, L = Vitoria, O = UFES, OU = DI, CN = Root CA

=== Certificado do Servidor ===
subject=C = BR, ST = ES, L = Vitoria, O = UFES, OU = DI, CN = localhost
issuer=C = BR, ST = ES, L = Vitoria, O = UFES, OU = DI, CN = Intermediate CA
```

### Passo 6: Configurar e Iniciar Servidor Nginx
```bash
# Voltar para o diretório raiz da tarefa
cd ..

# Criar estrutura de diretórios para Nginx
mkdir -p nginx/html nginx/certs

# Copiar certificados para diretório do Nginx
cp ca/server/server-fullchain.crt nginx/certs/
cp ca/server/server.key nginx/certs/

# Criar página HTML
cat > nginx/html/index.html << EOF
<!DOCTYPE html>
<html>
<head>
    <title>HTTPS Seguro - Tarefa 2 OpenSSL</title>
</head>
<body>
    <h1>Conexão HTTPS Segura com OpenSSL!</h1>
    <p>Certificado emitido pela CA Intermediária</p>
</body>
</html>
EOF

# Criar configuração do Nginx
cat > nginx/nginx.conf << EOF
events {
    worker_connections 1024;
}

http {
    server {
        listen 443 ssl;
        server_name localhost;

        ssl_certificate /etc/nginx/certs/server-fullchain.crt;
        ssl_certificate_key /etc/nginx/certs/server.key;

        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers HIGH:!aNULL:!MD5;

        location / {
            root /usr/share/nginx/html;
            index index.html;
        }
    }
}
EOF

# Criar docker-compose.yml
cat > docker-compose.yml << EOF
version: '3'
services:
  nginx:
    image: nginx:latest
    ports:
      - "443:443"
    volumes:
      - ./nginx/html:/usr/share/nginx/html
      - ./nginx/certs:/etc/nginx/certs
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf
    restart: unless-stopped
EOF

# Iniciar container Docker
docker-compose up -d
```

**Verificar status do container:**
```bash
docker-compose ps
```

### Passo 7: Testar Conexão HTTPS
```bash
# Testar com openssl s_client
openssl s_client -connect localhost:443 -CAfile ca/root/ca-root.pem -showcerts
```

**Verificar código de retorno:**
```bash
echo | openssl s_client -connect localhost:443 -CAfile ca/root/ca-root.pem 2>/dev/null | grep "Verify return code"
```

**Saída esperada:**
```
Verify return code: 0 (ok)
```

### Passo 8: Importar CA Raiz no Navegador

**Arquivo a importar:** `ca/root/ca-root.pem`

Seguir os mesmos passos descritos na Tarefa 1.

### Passo 9: Acessar Servidor HTTPS

Acessar no navegador: `https://localhost`

---

### Capturas de Tela

#### Tarefa 1 - Python
![Certificado Raíz](tarefa1-python/prints/validate.png)
*Figura 1: Saída do comando de validação

![Página HTTPS Tarefa 1](tarefa1-python/prints/telahttps.png)
*Figura 2: Página HTTPS funcionando com certificado válido (Tarefa 1)*

![Certificado Raíz](tarefa1-python/prints/root.png)
*Figura 3: Detalhes do certificado da CA raíz*

![Certificado Intermediária](tarefa1-python/prints/intermediate.png)
*Figura 4: Detalhes do certificado da CA intermediária*

![Certificado Servidor Localhost](tarefa1-python/prints/localhost.png)
*Figura 5: Detalhes do certificado da servidor

#### Tarefa 2 - OpenSSL

![Certificado Raíz](tarefa2-openssl/prints/validate.png)
*Figura 1: Saída do comando de validação

![Página HTTPS Tarefa 1](tarefa2-openssl/prints/telahttps.png)
*Figura 2: Página HTTPS funcionando com certificado válido (Tarefa 2)*

![Certificado Raíz](tarefa2-openssl/prints/root.png)
*Figura 3: Detalhes do certificado da CA raíz*

![Certificado Intermediária](tarefa2-openssl/prints/intermediate.png)
*Figura 4: Detalhes do certificado da CA intermediária*

![Certificado Servidor Localhost](tarefa2-openssl/prints/localhost.png)
*Figura 5: Detalhes do certificado da servidor

### Comparação entre as Abordagens

| Aspecto | Python (cryptography) | OpenSSL |
|---------|----------------------|---------|
| **Complexidade** | Programática, requer conhecimento de Python | Linha de comando, mais direta |
| **Automação** | Fácil de integrar em sistemas | Requer scripts shell |
| **Flexibilidade** | Total controle sobre atributos | Configuração via arquivos |
| **Curva de Aprendizado** | Requer conhecimento da biblioteca | Sintaxe específica do OpenSSL |
| **Uso Corporativo** | Ideal para serviços automatizados | Padrão para PKI manual |

---

## Diferenças entre CA Pública e Privada

### CA Privada (Implementada neste trabalho)

**Características:**
- Controlada internamente pela organização
- Certificados confiáveis apenas após importação manual da CA Raiz
- Custo zero de operação
- Total controle sobre políticas e validade
- Ideal para ambientes internos (intranet, desenvolvimento, testes)

**Vantagens:**
- Sem custos com certificados
- Emissão instantânea
- Controle total sobre a PKI
- Personalização completa
- Sem dependência de terceiros

**Desvantagens:**
- Requer gestão manual da confiança
- Não reconhecida por navegadores por padrão
- Responsabilidade total pela segurança da CA
- Não adequada para sites públicos
- Necessidade de distribuir CA Raiz para todos os clientes

### CA Pública (Exemplo: Let's Encrypt)

**Características:**
- Operada por entidades confiáveis reconhecidas globalmente
- Certificados automaticamente confiáveis em navegadores
- Processo de validação de domínio rigoroso
- Validade limitada (90 dias no Let's Encrypt)
- Gratuita (Let's Encrypt) ou paga (DigiCert, GlobalSign)

**Let's Encrypt - Análise:**

O Let's Encrypt revolucionou o ecossistema de certificados SSL/TLS ao oferecer certificados gratuitos e automatizados através do protocolo ACME (Automatic Certificate Management Environment).

**Vantagens do Let's Encrypt:**
- Confiança universal (presente em todos os navegadores)
- Gratuito e open-source
- Automação completa via ACME
- Forte segurança e auditoria pública
- Suporte amplo da comunidade

**Desvantagens do Let's Encrypt:**
- Validade curta (90 dias) requer automação
- Apenas validação de domínio (DV), não oferece OV ou EV
- Sem suporte para certificados wildcard via HTTP-01
- Requer exposição pública do domínio para validação

### Quando Usar Cada Tipo

**Use CA Privada quando:**
- Ambiente de desenvolvimento/teste
- Rede corporativa interna (intranet)
- Comunicação entre microsserviços internos
- IoT e dispositivos controlados
- Controle total é necessário

**Use CA Pública quando:**
- Sites e aplicações públicas na internet
- E-commerce e serviços que exigem confiança do usuário
- APIs públicas
- Conformidade regulatória exige CA reconhecida
- Impossível distribuir CA Raiz para todos os clientes



## Conclusão

Este trabalho demonstrou com sucesso a implementação completa de uma Infraestrutura de Chaves Públicas (PKI) utilizando duas abordagens distintas: Python com a biblioteca `cryptography` e a ferramenta OpenSSL.

**Principais aprendizados:**

1. **Hierarquia de Certificação**: A implementação de uma CA Raiz e CA Intermediária replica fielmente a estrutura utilizada em ambientes corporativos, onde a separação de responsabilidades aumenta a segurança.

2. **Cadeia de Confiança**: O funcionamento da cadeia de certificação (servidor → intermediária → raiz) foi validado tanto programaticamente (Python) quanto via ferramentas de linha de comando (OpenSSL).

3. **Extensões X.509**: A importância das extensões corretas (`basicConstraints`, `keyUsage`, `extendedKeyUsage`, `subjectAltName`) para o funcionamento adequado dos certificados foi comprovada na prática.

4. **Automação vs. Manual**: A abordagem Python demonstrou vantagens para automação e integração em sistemas, enquanto OpenSSL oferece controle granular e é o padrão da indústria.

5. **Fullchain**: A necessidade de enviar a cadeia completa de certificados (servidor + intermediária) para que navegadores possam validar a confiança foi um aspecto crítico identificado durante a implementação.



