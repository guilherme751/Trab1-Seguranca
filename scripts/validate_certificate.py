#!/usr/bin/env python3
"""
Script para validar a cadeia de certificação
Verifica se o certificado do servidor foi assinado corretamente
Compatible com ownca
"""

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.exceptions import InvalidSignature
import os

def load_certificate(cert_path):
    """
    Carrega um certificado PEM
    """
    with open(cert_path, "rb") as f:
        return x509.load_pem_x509_certificate(f.read(), default_backend())


def print_cert_details(cert, name):
    """
    Exibe detalhes do certificado
    """
    print(f"\n{'='*60}")
    print(f"CERTIFICADO: {name}")
    print('='*60)
    print(f"Subject: {cert.subject.rfc4514_string()}")
    print(f"Issuer: {cert.issuer.rfc4514_string()}")
    print(f"Serial: {cert.serial_number}")
    print(f"Válido de: {cert.not_valid_before}")
    print(f"Válido até: {cert.not_valid_after}")
    print(f"Algoritmo: {cert.signature_algorithm_oid._name}")
    
    # Verificar se é CA
    try:
        basic_constraints = cert.extensions.get_extension_for_oid(
            x509.ExtensionOID.BASIC_CONSTRAINTS
        ).value
        print(f"É CA: {basic_constraints.ca}")
        if basic_constraints.ca:
            print(f"Path Length: {basic_constraints.path_length}")
    except x509.ExtensionNotFound:
        print("É CA: False")


def verify_signature(cert, issuer_cert):
    """
    Verifica se o certificado foi assinado pelo issuer
    """
    try:
        issuer_public_key = issuer_cert.public_key()
        issuer_public_key.verify(
            cert.signature,
            cert.tbs_certificate_bytes,
            padding.PKCS1v15(),
            cert.signature_hash_algorithm,
        )
        return True
    except InvalidSignature:
        return False
    except Exception as e:
        print(f"Erro ao verificar assinatura: {e}")
        return False


def validate_chain():
    """
    Valida toda a cadeia de certificação
    """
    print("\n" + "="*60)
    print("VALIDAÇÃO DA CADEIA DE CERTIFICAÇÃO")
    print("="*60)  
    
    
    # Carregar certificados
    root_cert = load_certificate('certs/ca_root/ca.crt')
    intermediate_cert = load_certificate('certs/ca_intermediate/ca.crt')
    server_cert = load_certificate('certs/server/server.crt')
    
    print("[✓] Certificados carregados com sucesso!")
   
    
    # Exibir detalhes
    print_cert_details(root_cert, "CA Raiz")
    print_cert_details(intermediate_cert, "CA Intermediária")
    print_cert_details(server_cert, "Servidor")
    
    # Validar cadeia
    print("\n" + "="*60)
    print("VALIDAÇÃO DAS ASSINATURAS")
    print("="*60)
    
    all_valid = True
    
    # 1. Verificar se CA Raiz é autoassinada
    print("\n[*] Verificando autoassinatura da CA Raiz...")
    if verify_signature(root_cert, root_cert):
        print("[✓] CA Raiz é autoassinada corretamente!")
    else:
        print("[✗] FALHA: CA Raiz não está autoassinada corretamente!")
        all_valid = False
    
    # 2. Verificar se CA Intermediária foi assinada pela Raiz
    print("\n[*] Verificando assinatura da CA Intermediária pela CA Raiz...")
    if verify_signature(intermediate_cert, root_cert):
        print("[✓] CA Intermediária foi assinada pela CA Raiz!")
    else:
        print("[✗] FALHA: CA Intermediária não foi assinada pela CA Raiz!")
        all_valid = False
    
    # 3. Verificar se Certificado do Servidor foi assinado pela Intermediária
    print("\n[*] Verificando assinatura do Certificado do Servidor pela CA Intermediária...")
    if verify_signature(server_cert, intermediate_cert):
        print("[✓] Certificado do Servidor foi assinado pela CA Intermediária!")
    else:
        print("[✗] FALHA: Certificado do Servidor não foi assinado pela CA Intermediária!")
        all_valid = False
    
    # Verificar validade das datas
    print("\n" + "="*60)
    print("VALIDAÇÃO DE DATAS")
    print("="*60)
    
    from datetime import datetime
    now = datetime.utcnow()
    
    certs_to_check = [
        ("CA Raiz", root_cert),
        ("CA Intermediária", intermediate_cert),
        ("Servidor", server_cert)
    ]
    
    for name, cert in certs_to_check:
        print(f"\n[*] Verificando validade de {name}...")
        if cert.not_valid_before <= now <= cert.not_valid_after:
            print(f"[✓] {name} está dentro do período de validade!")
        else:
            print(f"[✗] {name} NÃO está dentro do período de validade!")
            all_valid = False
    
    # Verificar extensões importantes
    print("\n" + "="*60)
    print("VALIDAÇÃO DE EXTENSÕES")
    print("="*60)
    
    # Verificar se as CAs têm BasicConstraints corretos
    print("\n[*] Verificando extensões das CAs...")
    
    # CA Raiz deve ser CA
    try:
        bc_root = root_cert.extensions.get_extension_for_oid(
            x509.ExtensionOID.BASIC_CONSTRAINTS
        ).value
        if bc_root.ca:
            print("[✓] CA Raiz tem BasicConstraints: CA=TRUE")
        else:
            print("[✗] CA Raiz não está marcada como CA!")
            all_valid = False
    except:
        print("[✗] CA Raiz não tem extensão BasicConstraints!")
        all_valid = False
    
    # CA Intermediária deve ser CA
    try:
        bc_int = intermediate_cert.extensions.get_extension_for_oid(
            x509.ExtensionOID.BASIC_CONSTRAINTS
        ).value
        if bc_int.ca:
            print("[✓] CA Intermediária tem BasicConstraints: CA=TRUE")
        else:
            print("[✗] CA Intermediária não está marcada como CA!")
            all_valid = False
    except:
        print("[✗] CA Intermediária não tem extensão BasicConstraints!")
        all_valid = False
    
    # Servidor NÃO deve ser CA
    try:
        bc_server = server_cert.extensions.get_extension_for_oid(
            x509.ExtensionOID.BASIC_CONSTRAINTS
        ).value
        if not bc_server.ca:
            print("[✓] Certificado do Servidor tem BasicConstraints: CA=FALSE")
        else:
            print("[✗] Certificado do Servidor está marcado como CA!")
            all_valid = False
    except:
        print("[✓] Certificado do Servidor não tem BasicConstraints (correto para servidor)")
    
    # Resultado final
    print("\n" + "="*60)
    print("RESULTADO FINAL")
    print("="*60)
    
    if all_valid:
        print("\n✅ SUCESSO! A cadeia de certificação está válida!")
        print("\nCadeia completa:")
        print("  └─ CA Raiz (autoassinada)")
        print("      └─ CA Intermediária")
        print("          └─ Certificado do Servidor (localhost)")
        print("\n[i] A cadeia de confiança foi estabelecida corretamente!")
    else:
        print("\n❌ FALHA! Existem problemas na cadeia de certificação!")
        print("\n[!] Revise os erros acima e reexecute os scripts de criação.")
    
    return all_valid


def main():
    """
    Função principal
    """
    print("\n" + "="*60)
    print("SCRIPT DE VALIDAÇÃO DE CERTIFICADOS")
    print("UFES - Segurança em Computação")
    print("Compatível com ownca")
    print("="*60)
    
    # Validar cadeia
    success = validate_chain()
    
    if success:
        print("\n" + "="*60)
        print("TESTES ADICIONAIS")
        print("="*60)
        print("\nVocê pode testar a cadeia também com OpenSSL:")
        print("\n  # Verificar certificado do servidor")
        print("  openssl verify -CAfile certs/ca_root.pem \\")
        print("    -untrusted certs/ca_intermediate.pem \\")
        print("    certs/server.crt")
        print("\n  # Ver detalhes do certificado")
        print("  openssl x509 -in certs/server.crt -text -noout")
        print("\n  # Testar conexão HTTPS")
        print("  curl --cacert certs/ca_root.pem https://localhost")


if __name__ == "__main__":
    main()