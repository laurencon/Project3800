import socket
import threading

alias = input('Choose an alias >>> ')
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(('127.0.0.1', 59000))

def client_receive(): 
    while True:
        try:
            message = client.recv(1024).decode('utf-8')
            if message == "alias?":
                client.send(alias.encode('utf-8'))
            else:
                print(message)
        except Exception as e:
            print(f'Error: {e}')
            client.close()
            break

def client_send():
    while True:
        try:
            message = input(f'{alias}: ')
            if message.lower() == "<exit>":
                client.send(message.encode('utf-8'))
                break
            client.send(f'{alias}: {message}'.encode('utf-8'))
        except Exception as e:
            print(f'Error: {e}')
            client.close()
            break

receive_thread = threading.Thread(target=client_receive)
receive_thread.start()

send_thread = threading.Thread(target=client_send)
send_thread.start()
