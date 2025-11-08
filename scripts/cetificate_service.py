#!/usr/bin/env python3
"""
Serviço de emissão de certificados para servidores
Usa biblioteca ownca para simplificar o processo de emissão
Permite criar certificados assinados pela CA Intermediária
"""

from ownca import CertificateAuthority
import os

class CertificateService:
    """
    Serviço para emissão de certificados de servidor usando ownca
    """
    
    def __init__(self, ca_storage="certs/ca_intermediate"):
        """
        Inicializa o serviço carregando a CA Intermediária
        """
        print("[*] Inicializando Serviço de Certificação...")
        
        if not os.path.exists(ca_storage):
            print(f"[✗] CA Intermediária não encontrada em {ca_storage}")
            print("    Execute create_ca_intermediate.py primeiro")
            self.ca = None
            return
        
        self.ca = CertificateAuthority(ca_storage=ca_storage)
        print("[✓] Serviço pronto para emitir certificados!\n")
    
    def create_csr_interactive(self):
        """
        Cria uma CSR (Certificate Signing Request) de forma interativa
        Retorna: dicionário com dados do certificado
        """
        print("="*60)
        print("CRIAÇÃO DE CSR (CERTIFICATE SIGNING REQUEST)")
        print("="*60)
        
        # Coletar informações do usuário
        print("\n[*] Insira as informações para o certificado:")
        print("    (Pressione Enter para usar o valor padrão)")
        
        country = input("País (BR): ").strip() or "BR"
        state = input("Estado (Espirito Santo): ").strip() or "Espirito Santo"
        locality = input("Cidade (Vitoria): ").strip() or "Vitoria"
        organization = input("Organização (UFES): ").strip() or "UFES"
        org_unit = input("Departamento (DI): ").strip() or "DI"
        
        # Domínio é sempre localhost para este trabalho
        print("\n[*] Configurando para domínio: localhost")
        common_name = "localhost"
        
        # Perguntar sobre SANs adicionais
        print("\n[*] Deseja adicionar nomes alternativos (SANs)?")
        print("    Exemplos: www.localhost, 127.0.0.1")
        add_sans = input("Adicionar SANs? (s/N): ").strip().lower()
        
        dns_names = ["localhost"]
        if add_sans == 's':
            sans_input = input("Digite os DNS names separados por vírgula: ").strip()
            for san in sans_input.split(','):
                san = san.strip()
                if san and san not in dns_names:
                    dns_names.append(san)
        
        # Criar dados da CSR
        csr_data = {
            'common_name': common_name,
            'dns_names': dns_names,
            'country': country,
            'state': state,
            'locality': locality,
            'organization': organization,
            'organizational_unit': org_unit,
        }
        
        return csr_data
    
    def issue_certificate(self, csr_data, output_dir="certs"):
        """
        Emite e assina um certificado usando a CA Intermediária
        """
        if self.ca is None:
            print("[✗] CA não foi carregada corretamente!")
            return False
        
        print("\n[*] Emitindo certificado para:", csr_data['common_name'])
        print("[*] DNS Names:", ", ".join(csr_data['dns_names']))
        
        # Criar estrutura de armazenamento para o certificado
        hostname = csr_data['common_name'].replace('.', '_')
        cert_storage = os.path.join(output_dir, f"server_{hostname}")
        
        # Emitir certificado usando ownca
        # A biblioteca cuida de toda a assinatura automaticamente
        try:
            cert = self.ca.issue_certificate(
                hostname=hostname,
                common_name=csr_data['common_name'],
                dns_names=csr_data['dns_names'],
                maximum_days=365,  # 1 ano
            )
            
            print("[✓] Certificado emitido com sucesso!")
            
            # Copiar certificado e chave para o formato esperado
            self._export_server_certificate(hostname, output_dir)
            
            return True
            
        except Exception as e:
            print(f"[✗] Erro ao emitir certificado: {e}")
            return False
    
    def _export_server_certificate(self, hostname, output_dir):
        """
        Exporta o certificado do servidor para o formato padrão
        """
        print("\n[*] Exportando certificado do servidor...")
        
        # Caminhos dos arquivos gerados pelo ownca
        source_cert = f"certs/ca_intermediate/{hostname}.crt"
        source_key = f"certs/ca_intermediate/{hostname}.key"
        
        # Caminhos de destino
        dest_cert = os.path.join(output_dir, "server.crt")
        dest_key = os.path.join(output_dir, "server.key")
        
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
        
        # Criar bundle da cadeia (servidor + intermediária + raiz)
        self._create_chain_bundle(dest_cert, output_dir)
    
    def _create_chain_bundle(self, server_cert, output_dir):
        """
        Cria um bundle com a cadeia completa de certificação
        """
        bundle_path = os.path.join(output_dir, "server-chain.crt")
        
        try:
            with open(bundle_path, 'wb') as bundle:
                # Certificado do servidor
                with open(server_cert, 'rb') as f:
                    bundle.write(f.read())
                
                # Certificado intermediário
                intermediate_cert = "certs/ca_intermediate.pem"
                if os.path.exists(intermediate_cert):
                    bundle.write(b"\n")
                    with open(intermediate_cert, 'rb') as f:
                        bundle.write(f.read())
                
                # Certificado raiz (opcional, mas útil)
                root_cert = "certs/ca_root.pem"
                if os.path.exists(root_cert):
                    bundle.write(b"\n")
                    with open(root_cert, 'rb') as f:
                        bundle.write(f.read())
            
            print(f"[✓] Bundle da cadeia criado: {bundle_path}")
        except Exception as e:
            print(f"[!] Aviso: Não foi possível criar bundle: {e}")
    
    def print_certificate_info(self, hostname="localhost"):
        """
        Exibe informações do certificado emitido
        """
        cert_file = os.path.join("certs", "server.crt")
        
        if not os.path.exists(cert_file):
            print("[!] Certificado não encontrado")
            return
        
        print("\n" + "="*60)
        print("INFORMAÇÕES DO CERTIFICADO DO SERVIDOR")
        print("="*60)
        
        from cryptography import x509
        from cryptography.hazmat.backends import default_backend
        
        # Carregar certificado
        with open(cert_file, 'rb') as f:
            cert = x509.load_pem_x509_certificate(f.read(), default_backend())
        
        print(f"Subject: {cert.subject.rfc4514_string()}")
        print(f"Issuer: {cert.issuer.rfc4514_string()}")
        print(f"Serial Number: {cert.serial_number}")
        print(f"Válido de: {cert.not_valid_before}")
        print(f"Válido até: {cert.not_valid_after}")
        print(f"Algoritmo de assinatura: {cert.signature_algorithm_oid._name}")
        
        # Exibir SANs
        try:
            from cryptography.x509.oid import ExtensionOID
            san_ext = cert.extensions.get_extension_for_oid(ExtensionOID.SUBJECT_ALTERNATIVE_NAME)
            san_list = [str(name.value) for name in san_ext.value]
            print(f"SANs: {', '.join(san_list)}")
        except:
            print("SANs: Nenhum")
        
        print("="*60 + "\n")


def main():
    """
    Função principal do serviço
    """
    print("\n" + "="*60)
    print("SERVIÇO DE EMISSÃO DE CERTIFICADOS")
    print("Usando biblioteca ownca")
    print("="*60 + "\n")
    
    # Inicializar serviço
    service = CertificateService()
    
    if service.ca is None:
        return
    
    # Criar CSR interativa
    csr_data = service.create_csr_interactive()
    
    # Emitir certificado
    success = service.issue_certificate(csr_data)
    
    if success:
        # Exibir informações
        service.print_certificate_info()
        
        print("\n[✓] Processo concluído!")
        print("\nArquivos criados:")
        print("  - certs/server.crt (certificado do servidor)")
        print("  - certs/server.key (chave privada do servidor)")
        print("  - certs/server-chain.crt (cadeia completa)")
        print("\n[i] Próximo passo: Configure o Nginx ou execute validate_certificate.py")
    else:
        print("\n[✗] Falha ao emitir certificado!")


if __name__ == "__main__":
    main()