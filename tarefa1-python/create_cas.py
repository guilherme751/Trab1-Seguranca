from cryptography import x509
from cryptography.x509.oid import NameOID, ExtensionOID
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from datetime import datetime, timedelta, timezone

# Gerar CA Raiz
root_key = rsa.generate_private_key(public_exponent=65537, key_size=4096)
root_name = x509.Name([
    x509.NameAttribute(NameOID.COUNTRY_NAME, "BR"),
    x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "ES"),
    x509.NameAttribute(NameOID.LOCALITY_NAME, "Vitoria"),
    x509.NameAttribute(NameOID.ORGANIZATION_NAME, "CT"),
    x509.NameAttribute(NameOID.ORGANIZATIONAL_UNIT_NAME, "DI"),
    x509.NameAttribute(NameOID.COMMON_NAME, "Root CA"),
])

root_cert = (
    x509.CertificateBuilder()
    .subject_name(root_name)
    .issuer_name(root_name)
    .public_key(root_key.public_key())
    .serial_number(x509.random_serial_number())
    .not_valid_before(datetime.now(timezone.utc))
    .not_valid_after(datetime.now(timezone.utc) + timedelta(days=3650))
    .add_extension(x509.BasicConstraints(ca=True, path_length=None), critical=True)
    .add_extension(x509.KeyUsage(
        digital_signature=True, key_cert_sign=True, crl_sign=True,
        key_encipherment=False, content_commitment=False, data_encipherment=False,
        key_agreement=False, encipher_only=False, decipher_only=False
    ), critical=True)
    .add_extension(x509.SubjectKeyIdentifier.from_public_key(root_key.public_key()), critical=False)
    .sign(root_key, hashes.SHA256())
)

# Salvar CA Raiz
with open("certs/ca-root.key", "wb") as f:
    f.write(root_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    ))

with open("certs/ca-root.pem", "wb") as f:
    f.write(root_cert.public_bytes(serialization.Encoding.PEM))

print("✓ CA Raiz criada: certs/ca-root.key, certs/ca-root.pem")

# Gerar CA Intermediária
intermediate_key = rsa.generate_private_key(public_exponent=65537, key_size=4096)
intermediate_name = x509.Name([
    x509.NameAttribute(NameOID.COUNTRY_NAME, "BR"),
    x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "ES"),
    x509.NameAttribute(NameOID.LOCALITY_NAME, "Vitoria"),
    x509.NameAttribute(NameOID.ORGANIZATION_NAME, "CT"),
    x509.NameAttribute(NameOID.ORGANIZATIONAL_UNIT_NAME, "DI"),
    x509.NameAttribute(NameOID.COMMON_NAME, "Intermediate CA"),
])

intermediate_cert = (
    x509.CertificateBuilder()
    .subject_name(intermediate_name)
    .issuer_name(root_name)
    .public_key(intermediate_key.public_key())
    .serial_number(x509.random_serial_number())
    .not_valid_before(datetime.now(timezone.utc))
    .not_valid_after(datetime.now(timezone.utc) + timedelta(days=3650))
    
    .add_extension(x509.BasicConstraints(ca=True, path_length=0), critical=True)
    .add_extension(x509.KeyUsage(
        digital_signature=True, key_cert_sign=True, crl_sign=True,
        key_encipherment=False, content_commitment=False, data_encipherment=False,
        key_agreement=False, encipher_only=False, decipher_only=False
    ), critical=True)
    .add_extension(x509.SubjectKeyIdentifier.from_public_key(intermediate_key.public_key()), critical=False)
    .add_extension(x509.AuthorityKeyIdentifier.from_issuer_public_key(root_key.public_key()), critical=False)
    .sign(root_key, hashes.SHA256())
)

# Salvar CA Intermediária
with open("certs/ca-intermediate.key", "wb") as f:
    f.write(intermediate_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    ))

with open("certs/ca-intermediate.pem", "wb") as f:
    f.write(intermediate_cert.public_bytes(serialization.Encoding.PEM))

print("✓ CA Intermediária criada: certs/ca-intermediate.key, certs/ca-intermediate.pem")