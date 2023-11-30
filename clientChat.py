import socket
import threading

def client_receive():
    while True:
        try:
            message = client.recv(1024).decode('utf-8')
            print(message)
        except Exception as e:
            print(f'Error: {e}')
            break

def client_send():
    while True:
        try:
            message = input()
            if message.lower() == "<exit>":
                client.send(message.encode('utf-8'))
                break
            client.send(message.encode('utf-8'))
        except Exception as e:
            print(f'Error: {e}')
            break

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(('127.0.0.1', 59000))

while True:
    alias = input('Enter your alias: ')
    client.send(alias.encode('utf-8'))
    response = client.recv(1024).decode('utf-8')
    
    if response == alias:
        print(f"Alias '{alias}' is already in use. Please choose another one.")
    else:
        print(response)
        break

receive_thread = threading.Thread(target=client_receive)
receive_thread.start()

send_thread = threading.Thread(target=client_send)
send_thread.start()