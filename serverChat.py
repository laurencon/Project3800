import socket
import threading

host = '127.0.0.1'
port = 59000
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((host, port))
server.listen()

clients = []
aliases = set()

def broadcast(message):
    for client in clients:
        client.send(message)

def handle_client(client, alias):
    while True:
        try:
            message = client.recv(1024).decode('utf-8')
            if message.lower() == "<exit>":
                index = clients.index(client)
                alias = aliases[index]
                broadcast(f'{alias} has left the chat room!\n'.encode('utf-8'))
                aliases.remove(alias)
                clients.remove(client)
                break
            broadcast_to_others(f'{alias}: {message}\n'.encode('utf-8'), client)
        except Exception as e:
            print(f'Error: {e}')
            break

def broadcast_to_others(message, sender_client):
    for client in clients:
        if client != sender_client:
            client.send(message)


def receive():
    while True:
        print('Server is running and listening...')
        client, address = server.accept()
        print(f"Connection established with {str(address)}")
        
        # Check if there are already connected clients
        if clients:
            client.send('Enter your alias: '.encode('utf-8'))

        while True:
            try:
                alias = client.recv(1024).decode('utf-8')
            except Exception as e:
                print(f'Error receiving alias: {e}')
                client.close()
                break

            if not alias:
                print('Empty alias received. Please try again.')
                client.close()
                break

            if alias in aliases:
                print(f"Rejecting duplicate alias: {alias}")
                client.send('Alias already in use. Please choose another one: '.encode('utf-8'))
            else:
                print(f'The alias of this client is {alias}'.encode('utf-8'))
                aliases.add(alias)
                clients.append(client)
                if clients.count(client) == 1:
                    broadcast(f'{alias} has connected to the chat room.\n'.encode('utf-8'))
                client.send('You are now connected!\n'.encode('utf-8'))
                thread = threading.Thread(target=handle_client, args=(client, alias))
                thread.start()
                break  # Exit the loop after successful connection

if __name__ == '__main__':
    receive()
