import requests
import mysql.connector
import schedule
import time

# Conectar ao banco de dados MySQL
def connect_db():
    connection = mysql.connector.connect(
        host='localhost',
        user='seu_usuario',
        password='sua_senha',
        database='seu_banco'
    )
    return connection

# Função para verificar e armazenar o novo conteúdo
def fetch_and_store():
    url = 'https://www.tabnews.com.br/api/v1/contents?page=1&per_page=1&strategy=new'
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()

        if data:
            item = data[0]
            content_id = item['id']
            title = item['title']
            body = item.get('body', '')  # Alguns posts podem não ter corpo
            created_at = item['created_at']

            # Conectar ao banco de dados
            connection = connect_db()
            cursor = connection.cursor()

            # Verificar se o conteúdo já existe no banco de dados
            cursor.execute("SELECT COUNT(*) FROM tabnews_contents WHERE id = %s", (content_id,))
            count = cursor.fetchone()[0]

            if count == 0:
                # Inserir o novo conteúdo no banco de dados
                cursor.execute(
                    "INSERT INTO tabnews_contents (id, title, body, created_at) VALUES (%s, %s, %s, %s)",
                    (content_id, title, body, created_at)
                )
                connection.commit()
                print("Novo conteúdo salvo no banco de dados.")
            else:
                print("Conteúdo já existe no banco de dados.")

            # Fechar a conexão com o banco de dados
            cursor.close()
            connection.close()
        else:
            print("Nenhum conteúdo novo encontrado.")
    else:
        print(f"Erro ao fazer a requisição: {response.status_code}")

# Função para rodar o bot a cada 5 minutos
def run_bot():
    schedule.every(5).minutes.do(fetch_and_store)

    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    run_bot()
