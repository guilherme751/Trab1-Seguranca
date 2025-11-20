from cryptography import x509
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes

def validate_chain():
    """Valida a cadeia de certificação"""
    # Carregar certificados
    with open("certs/ca-root.pem", "rb") as f:
        root_cert = x509.load_pem_x509_certificate(f.read())
    
    with open("certs/ca-intermediate.pem", "rb") as f:
        intermediate_cert = x509.load_pem_x509_certificate(f.read())
    
    with open("certs/server.crt", "rb") as f:
        server_cert = x509.load_pem_x509_certificate(f.read())
    
    print("=== Validação da Cadeia de Certificação ===\n")
    
    # Verificar CA Intermediária assinada pela Raiz
    try:
        root_cert.public_key().verify(
            intermediate_cert.signature,
            intermediate_cert.tbs_certificate_bytes,
            padding.PKCS1v15(),
            intermediate_cert.signature_hash_algorithm
        )
        print("✓ CA Intermediária verificada pela CA Raiz")
    except:
        print("✗ Falha na verificação da CA Intermediária")
    
    # Verificar Servidor assinado pela Intermediária
    try:
        intermediate_cert.public_key().verify(
            server_cert.signature,
            server_cert.tbs_certificate_bytes,
            padding.PKCS1v15(),
            server_cert.signature_hash_algorithm
        )
        print("✓ Certificado do Servidor verificado pela CA Intermediária")
    except:
        print("✗ Falha na verificação do Certificado do Servidor")
    
    print("\n=== Estrutura da PKI ===\n")
    print(f"CA Raiz:")
    print(f"  Subject: {root_cert.subject.rfc4514_string()}")
    print(f"  Issuer:  {root_cert.issuer.rfc4514_string()}")
    print(f"\nCA Intermediária:")
    print(f"  Subject: {intermediate_cert.subject.rfc4514_string()}")
    print(f"  Issuer:  {intermediate_cert.issuer.rfc4514_string()}")
    print(f"\nCertificado do Servidor:")
    print(f"  Subject: {server_cert.subject.rfc4514_string()}")
    print(f"  Issuer:  {server_cert.issuer.rfc4514_string()}")
    
    # Verificar SANs
    try:
        san = server_cert.extensions.get_extension_for_oid(x509.oid.ExtensionOID.SUBJECT_ALTERNATIVE_NAME)
        print(f"  SANs: {', '.join([str(name.value) for name in san.value])}")
    except:
        print("  SANs: Nenhum")

if __name__ == "__main__":
    validate_chain()