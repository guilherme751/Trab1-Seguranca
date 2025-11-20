from cryptography import x509
from cryptography.x509.oid import NameOID, ExtensionOID
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from datetime import datetime, timedelta, timezone
import sys
import ipaddress

def load_intermediate_ca():
    """Carrega chave e certificado da CA Intermediária"""
    with open("certs/ca-intermediate.key", "rb") as f:
        ca_key = serialization.load_pem_private_key(f.read(), password=None)
    with open("certs/ca-intermediate.pem", "rb") as f:
        ca_cert = x509.load_pem_x509_certificate(f.read())
    return ca_key, ca_cert

def generate_server_certificate(domain, country_name, state, 
                                locality, organization, organization_unit_name):
    """Gera e assina certificado de servidor"""
    # Carregar CA Intermediária
    ca_key, ca_cert = load_intermediate_ca()
    
    # Gerar chave do servidor
    server_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    
    # Criar CSR (simulado via CertificateBuilder)
    server_name = x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, country_name),
        x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, state),
        x509.NameAttribute(NameOID.LOCALITY_NAME, locality),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, organization),
        x509.NameAttribute(NameOID.ORGANIZATIONAL_UNIT_NAME, organization_unit_name),
        x509.NameAttribute(NameOID.COMMON_NAME, domain),
    ])
    
    # Assinar certificado com CA Intermediária
    server_cert = (
        x509.CertificateBuilder()
        .subject_name(server_name)
        .issuer_name(ca_cert.subject)
        .public_key(server_key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(datetime.now(timezone.utc))
        .not_valid_after(datetime.now(timezone.utc) + timedelta(days=3650))
        .add_extension(
            x509.SubjectAlternativeName([
                x509.DNSName(domain),
                x509.IPAddress(ipaddress.IPv4Address("127.0.0.1"))
            ]),
            critical=False
        )
        .add_extension(x509.BasicConstraints(ca=False, path_length=None), critical=True)
        .add_extension(x509.KeyUsage(
            digital_signature=True, key_encipherment=True,
            key_cert_sign=False, crl_sign=False, content_commitment=False,
            data_encipherment=False, key_agreement=False,
            encipher_only=False, decipher_only=False
        ), critical=True)
        .add_extension(x509.ExtendedKeyUsage([x509.oid.ExtendedKeyUsageOID.SERVER_AUTH]), critical=True)
        .sign(ca_key, hashes.SHA256())
    )
    
    # Salvar chave e certificado do servidor
    with open("certs/server.key", "wb") as f:
        f.write(server_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        ))
    
    with open("certs/server.crt", "wb") as f:
        f.write(server_cert.public_bytes(serialization.Encoding.PEM))
    
    # Criar fullchain (servidor + intermediária)
    with open("certs/ca-intermediate.pem", "rb") as f:
        intermediate_pem = f.read()
    
    with open("certs/server-fullchain.crt", "wb") as f:
        f.write(server_cert.public_bytes(serialization.Encoding.PEM))
        f.write(intermediate_pem)
    
    print(f"✓ Certificado emitido para: {domain}")
    print("✓ Arquivos criados: certs/server.key, certs/server.crt, certs/server-fullchain.crt")

if __name__ == "__main__":
    
    domain = input('Qual do domínio do servidor?')
    country_name = input('Qual o país?')
    state = input('Qual o estado ou província?')
    locality = input('Qual a cidade?')
    organization = input('Qual a organização?')
    organization_unit_name = input('Qual a unidade de organização?')
    generate_server_certificate(domain, country_name, state, locality, 
                                organization, organization_unit_name)