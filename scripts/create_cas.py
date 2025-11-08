from ownca import CertificateAuthority
import os

class CAroot:
    def __init__(self, path, common_name):
        self.path = path
        self.common_name = common_name    

    def create_root_ca(self):
        os.makedirs(self.path, exist_ok=True)
        ca = CertificateAuthority(
            ca_storage=self.path,
            common_name=self.common_name,
            key_size=4096
        )
        return ca   


class CAintermediate:
    def __init__(self, path, common_name):
        self.path = path
        self.common_name = common_name    

    def create_intermediate_ca(self):
        os.makedirs(self.path, exist_ok=True)

        ica = CertificateAuthority(
            ca_storage=self.path,
            common_name=self.common_name,
            key_size=4096,
            intermediate=True
        )

        return ica  

if __name__ == "__main__":

    print("[*] Gerando CA Raiz usando ownca...")
    ca_root = CAroot(path="certs/ca_root", common_name="Guilherme Root CA")
    ca_root_obj = ca_root.create_root_ca()
   
    print("[*] Gerando CA Intermediária usando ownca...")
    ca_int = CAintermediate(path="certs/ca_intermediate", common_name="Guilherme Intermediate CA")
    csr_int_obj = ca_int.create_intermediate_ca()  # retorna o objeto Intermediate CA

    # Extrair CSR e chave pública
    csr_intermediate = csr_int_obj.csr
    csr_pub = csr_int_obj.public_key
    
    print("[*] Assinando CSR da CA Intermediária com a CA Raiz...")

    signed_intermediate_obj = ca_root_obj.sign_csr(
        csr=csr_intermediate,
        csr_public_key=csr_pub
    )
    with open("certs/ca_intermediate/ca.crt", "wb") as f:
        f.write(signed_intermediate_obj.cert_bytes)

    print("[✓] CA Intermediária assinada com sucesso!")
    print("[✓] Certificado salvo em: certs/ca_intermediate/ca.crt")







    

