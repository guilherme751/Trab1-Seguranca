from ownca import CertificateAuthority
import os

def create_root_ca():
    """
    Cria a CA Raiz autoassinada usando ownca
    """
    print("[*] Gerando CA Raiz usando ownca...")
    
    # Criar diretório certs se não existir
    os.makedirs("certs", exist_ok=True)
    
    # Configurar dados da CA Raiz
    ca_data = {
        'common_name': 'UFES Root CA',
        'country': 'BR',
        'state': 'Espirito Santo',
        'locality': 'Vitoria',
        'organization': 'UFES',
        'organizational_unit': 'Departamento de Informatica',
        'email': 'admin@ufes.br'
    }
    
    # Criar CA Raiz
    # ownca cria automaticamente a estrutura de diretórios
    ca = CertificateAuthority(
        ca_storage="certs/ca_root",
        common_name=ca_data['common_name'],
        dns_names=[],  # CA Raiz não precisa de DNS names
        public_exponent=65537,
        key_size=4096,  # RSA 4096 bits
        maximum_days=825,  # 10 anos
        country=ca_data['country'],
        state=ca_data['state'],
        locality=ca_data['locality'],
        organization=ca_data['organization'],
        organizational_unit=ca_data['organizational_unit'],
        email_address=ca_data['email']
    )
    
    print("[✓] CA Raiz criada com sucesso!")
    
    return ca


def export_root_ca():
    """
    Exporta os arquivos da CA Raiz para o formato padrão
    """
    print("\n[*] Exportando certificados para formato padrão...")
    
    # ownca cria os arquivos em ca_root/
    # Vamos criar cópias no formato esperado
    source_cert = "certs/ca_root/ca.crt"
    source_key = "certs/ca_root/ca.key"
    
    dest_cert = "certs/ca_root.pem"
    dest_key = "certs/ca_root.key"
    
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
    print("CRIAÇÃO DA CA RAIZ (ROOT CERTIFICATE AUTHORITY)")
    print("Usando biblioteca ownca")
    print("="*60 + "\n")
    
    # Criar CA Raiz
    ca = create_root_ca()
    
    # Exportar para formato padrão
    # export_root_ca()
    
    # # Exibir informações
    # print_certificate_info()
    
    print("\n[✓] Processo concluído!")
    print("\nArquivos criados:")
    print("  - certs/ca_root/ca.crt (certificado original)")
    print("  - certs/ca_root/ca.key (chave privada original)")
    print("  - certs/ca_root.pem (certificado copiado)")
    print("  - certs/ca_root.key (chave privada copiada)")
    print("\n[i] Próximo passo: Execute create_ca_intermediate.py")