from ownca import CertificateAuthority
import os

class CertificateService:
    def __init__(self, ca_path):
        self.ca_intermediate = CertificateAuthority(ca_storage=ca_path)

    def issue_server_certificate(self, hostname, output_dir="certs/server"):
        """
        Emite um certificado de servidor assinado pela CA Intermediária
        """

        print("\n[*] Emitindo certificado de servidor...")
        try:
            cert_obj = self.ca_intermediate.issue_certificate(hostname=hostname, ca=False)
            print("[✓] Certificado de servidor emitido com sucesso!")
            
        except Exception as e:
            print(f"[✗] Erro ao emitir certificado de servidor: {e}")
            return None
        
        # salvar server.key
        os.makedirs(output_dir, exist_ok=True)
        server_key_path = os.path.join(output_dir, "server.key")
        with open(server_key_path, "wb") as f:
            f.write(cert_obj.key_bytes)

        # salvar server.crt
        server_crt_path = os.path.join(output_dir, "server.crt")        
        with open(server_crt_path, "wb") as f:
            f.write(cert_obj.cert_bytes)

        # pegar certificado da CA intermediária
        intermediate_crt_path = os.path.join(self.ca_intermediate.ca_storage, "ca.crt")
        if not os.path.exists(intermediate_crt_path):
            raise FileNotFoundError("O certificado da CA intermediária não foi encontrado.")        
        with open(intermediate_crt_path, "rb") as f:
            intermediate_crt_bytes = f.read()

        # salvar chain.pem
        chain_path = os.path.join(output_dir, "chain.pem")
        with open(chain_path, "wb") as f:
            f.write(intermediate_crt_bytes)

        # salvar fullchain.pem (com server + intermediate)
        fullchain_path = os.path.join(output_dir, "fullchain.pem")
        with open(fullchain_path, "wb") as f:
            f.write(cert_obj.cert_bytes)
            f.write(intermediate_crt_bytes)

        # chain.total.pem (server + intermediária + raiz)
        root_crt_path = os.path.join("certs/ca_root", "ca.crt")
        if not os.path.exists(root_crt_path):
            raise FileNotFoundError("O certificado da CA raiz não foi encontrado.")
        with open(root_crt_path, "rb") as f:
            root_crt_bytes = f.read()
        chain_total_path = os.path.join(output_dir, "chain.total.pem")
        with open(chain_total_path, "wb") as f:
            f.write(cert_obj.cert_bytes)
            f.write(intermediate_crt_bytes)
            f.write(root_crt_bytes)

        print("[✓] Arquivos salvos em:", output_dir)
        print("    - server.key")
        print("    - server.crt")
        print("    - chain.pem")
        print("    - fullchain.pem")
        print("    - chain.total.pem  (usar no curl do Windows)")

        return {
            "server_key": server_key_path,
            "server_cert": server_crt_path,
            "chain": chain_path,
            "fullchain": fullchain_path,
            "chain_total": chain_total_path
        }

if __name__ == "__main__":
    ca_service = CertificateService(ca_path="certs/ca_intermediate")
    cert = ca_service.issue_server_certificate(hostname="localhost", output_dir="certs/server")
    print(cert)