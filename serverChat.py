import socket
import threading
import mysql.connector


host = '127.0.0.1'
port = 59000
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((host,port))
server.listen()
connection = mysql.connector.connect(
    host = "chatproject.cfe4xydjdmfh.us-east-1.rds.amazonaws.com",
    user = "root",
    password = "cs3800pass",
    database = "chatproject"
)
cursor = connection.cursor()

clients = []
aliases = []

def broadcast(message):
    for client in clients:
            client.send(message)
            
            
# Function to handle clients connections            
def handle_client(client, cursor, connection):
    while True:
        try:
            message = client.recv(1024).decode('utf-8')
            # saving messages to database
            save_messages(cursor, message, sender_alias)
            broadcast(message)
        except:
            index = clients.index(client)
            clients.remove(client)
            client.close()
            alias = aliases[index]
            broadcast(f'{alias} has left the chat room!'.encode('utf-8'))
            aliases.remove(alias)
            break
# Function to insert the message into database
def save_messages(cursor, message, sender_alias):
    sender = sender_alias
    # we need to split the message itself to extract
    content = message.split(':', 1)[1].strip()
    cursor.execute("INSERT INTO messages (sender, receiver, content) VALUES (%s, %s, %s)",
                   (sender, 'Placeholder', content))
    connection.commit()
# Main function to receive the connection
def receive():
    while True:
        print('Server is running and listening...')
        client, address = server.accept()
        print(f"Connection established with {str(address)}")
        client.send('alias?'.encode('utf-8'))
        alias = client.recv(1024)
        aliases.append(alias)
        clients.append(client)
        print(f'The alias of this client is {alias}'.encode('utf-8'))
        broadcast(f'{alias} has connected to the chat room'.encode('utf-8'))

        #send chat history
        send_chat_history(client, cursor)
        client.send('You are now connected!'.encode('utf-8'))
        thread = threading.Thread(target = handle_client, args=(client,))
        thread.start()

def send_chat_history(client, cursor):
    cursor.execute("SELECT * FROM messages ORDER BY timestamp")
    messages = cursor.fetchall()
    for message in messages:
        client.send(str(message).encode('utf-8'))

if __name__ == '__main__':
    receive()
    cursor.close()
    connection.close()
