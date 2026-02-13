import shutil
import os
from datetime import datetime

def realizar_backup():
    # Configurações
    db_original = "estoque.db"
    pasta_backup = "backups"
    
    # Verifica se o banco existe
    if not os.path.exists(db_original):
        print("❌ Erro: arquivo estoque.db não encontrado!")
        return

    # Cria a pasta de backup se não existir
    if not os.path.exists(pasta_backup):
        os.makedirs(pasta_backup)

    # Gera o nome do arquivo com data e hora: estoque_2026-02-13_14-30.db
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
    nome_backup = f"estoque_{timestamp}.db"
    caminho_final = os.path.join(pasta_backup, nome_backup)

    # Copia o arquivo
    try:
        shutil.copy2(db_original, caminho_final)
        print(f"✅ Backup realizado com sucesso: {caminho_final}")
    except Exception as e:
        print(f"❌ Falha ao realizar backup: {e}")

if __name__ == "__main__":
    realizar_backup()