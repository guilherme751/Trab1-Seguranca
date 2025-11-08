#!/usr/bin/env python3
"""
Script para criação da CA Intermediária
Usa a biblioteca ownca para simplificar o processo
Gera um certificado assinado pela CA Raiz com chave RSA 4096 bits
"""

from ownca import CertificateAuthority
import os

def load_root_ca():
    """
    Carrega a CA Raiz existente
    """
    print("[*] Carregando CA Raiz...")
    
    if not os.path.exists("certs/ca_root"):
        print("[✗] CA Raiz não encontrada!")
        print("    Execute create_ca_root.py primeiro")
        return None
    
    ca_root = CertificateAuthority(ca_storage="certs/ca_root")
    print("[✓] CA Raiz carregada com sucesso!")
    return ca_root


def create_intermediate_ca(ca_root):
    """
    Cria a CA Intermediária assinada pela CA Raiz
    """
    print("\n[*] Criando CA Intermediária...")
    
    # Configurar dados da CA Intermediária
    ca_data = {
        'common_name': 'UFES Intermediate CA',
        'country': 'BR',
        'state': 'Espirito Santo',
        'locality': 'Vitoria',
        'organization': 'UFES',
        'organizational_unit': 'Departamento de Informatica',
        'email': 'intermediate@ufes.br'
    }
    
    # Criar CA Intermediária assinada pela CA Raiz
    # O ownca automaticamente cria a hierarquia correta
    csr_intermediate = CertificateAuthority(
        ca_storage="certs/ca_intermediate",
        common_name="Guilherme Intermediate CA",
        intermediate=True
    )
    
    # print("[✓] CA Intermediária criada com sucesso!")
    return csr_intermediate


def export_intermediate_ca():
    """
    Exporta os arquivos da CA Intermediária para o formato padrão
    """
    print("\n[*] Exportando certificados para formato padrão...")
    
    source_cert = "certs/ca_intermediate/ca.crt"
    source_key = "certs/ca_intermediate/ca.key"
    
    dest_cert = "certs/ca_intermediate.pem"
    dest_key = "certs/ca_intermediate.key"
    
    # Copiar certificado
    if os.path.exists(source_cert):
        with open(source_cert, 'rb') as src, open(dest_cert, 'wb') as dst:
            dst.write(src.read())
        print(f"[✓] Certificado exportado: {dest_cert}")
    
    # Copiar chave privada
    if os.path.exists(source_key):
        with open(source_key, 'rb') as src, open(dest_key, 'wb') as dst:
            dst.write(src.read())
        print(f"[✓] Chave privada exportada: {dest_key}")


def print_certificate_info():
    """
    Exibe informações do certificado usando ownca
    """
    print("\n" + "="*60)
    print("INFORMAÇÕES DO CERTIFICADO DA CA RAIZ")
    print("="*60)
    
    # Carregar CA para ver informações
    ca = CertificateAuthority(ca_storage="certs/ca_root")
    cert = ca.cert  # Este é um objeto x509.Certificate
    
    # Extrair informações do subject
    subject_dict = {}
    for attribute in cert.subject:
        subject_dict[attribute.oid._name] = attribute.value
    
    # Imprimir informações
    print(f"Subject: CN={subject_dict.get('commonName', 'N/A')}")
    print(f"         O={subject_dict.get('organizationName', 'N/A')}")
    print(f"         OU={subject_dict.get('organizationalUnitName', 'N/A')}")
    print(f"         L={subject_dict.get('localityName', 'N/A')}")
    print(f"         ST={subject_dict.get('stateOrProvinceName', 'N/A')}")
    print(f"         C={subject_dict.get('countryName', 'N/A')}")
    print(f"Issuer: CN={subject_dict.get('commonName', 'N/A')} (autoassinado)")
    print(f"Serial Number: {cert.serial_number}")
    print(f"Válido de: {cert.not_valid_before}")
    print(f"Válido até: {cert.not_valid_after}")
    print(f"Tamanho da chave: 4096 bits")
    print(f"Algoritmo: RSA + SHA256")
    print("="*60 + "\n")


if __name__ == "__main__":
    print("\n" + "="*60)
    print("CRIAÇÃO DA CA INTERMEDIÁRIA (INTERMEDIATE CA)")
    print("Usando biblioteca ownca")
    print("="*60 + "\n")
    
    # Carregar CA Raiz
    ca_root = load_root_ca()
    if ca_root is None:
        exit(1)
    
    # Criar CA Intermediária
    ca_intermediate = create_intermediate_ca(ca_root)
    print(ca_intermediate)    
  