import threading
import serverthread
import socket
import struct
import select 
import util

chat_client_adresses = []

def find_open_port(host, start_port, end_port):
    # Encontrar uma porta qualquer para o servidor principal
    open_ports = []

    for port in range(start_port, end_port + 1):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)

        try:
            sock.bind((host, port))
            open_ports.append(port)
        except socket.error:
            pass
        finally:
            sock.close()

    return open_ports


# send/receive message tem um protocolo customizado de mensagem

def send_message(sock, message):
    message_length = len(message)
    header = struct.pack('!I', message_length)
    sock.sendall(header + message.encode())

def receive_message(sock):
    header = sock.recv(4)
    if not header:
        return None
    message_length = struct.unpack('!I', header)[0]
    message = sock.recv(message_length).decode()
    return message


def chat_socket(port):
    # Fila com capacidade maxima determinada pela janela de chat do cliente
    chat_content = util.LimitedQueue(max_size=24)

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(("127.0.0.1", port))
    sock.listen(12)
    print(f"ChatRoom open on 127.0.0.1 port: {port}")
    client_sockets = [sock]

    while True:
        try:
            readable, _, _ = select.select(client_sockets, [], [])

            for ready_socket in readable:
                if ready_socket == sock:
                    # Novo cliente conectado ao chat
                    client_socket, client_address = sock.accept()
                    client_sockets.append(client_socket)
                    chat_client_adresses.append(client_address)
                else:
                    # Receber mensagem de chat do cliente, adicionar à fila e enviar o chat log
                    chatMessageFromClient = receive_message(ready_socket)

                    if chatMessageFromClient == None:
                        print("Closing connection with peer")
                        ready_socket.close()
                        client_sockets.remove(ready_socket)
                        continue

                    if chatMessageFromClient in chat_content.queue:
                        continue
                    
                    if chatMessageFromClient != "" and chatMessageFromClient is not None and chatMessageFromClient != "update":
                        print(f"New chat message: {chatMessageFromClient}")
                        chat_content.enqueue(chatMessageFromClient)
                    message = "\n".join(map(str, list(chat_content.queue)))
                    # Enviar o log completo do chat
                    ready_socket.sendall(message.encode("utf-8"))
        except ValueError:
            continue

def run_server(port):
    server_threads = []
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('localhost', port))
    server_socket.listen(1)


    chat_threads = []
    # chat_thread = threading.Thread(target=chat_socket, args=(chatPort, ))
    # chat_thread.start()

    
    client_sockets = [server_socket]
    print(f"Waiting for a connection on port {port}...")
    while True:
        readable, _, _ = select.select(client_sockets, [], [])

        for ready_socket in readable:
            if ready_socket == server_socket:
                
                client_socket, client_address = server_socket.accept()
                client_sockets.append(client_socket)
                print("Connected to", client_address)
                # Send output to client
                send_message(client_socket, "Main Server Connected to Client")

                # send_message(client_socket, "Hello from server!")
            else:
                # Abrir nova partida na porta que o cliente enviar
                received_message = receive_message(ready_socket)
                if received_message == None:
                    print(f"Closed connection with {ready_socket.getpeername()}")
                    ready_socket.close()
                    client_sockets.remove(ready_socket)
                    continue
                # Logic for threading below
                print("Received message:", received_message)
                try:
                    chatPort = result[0]
                    t = threading.Thread(target=serverthread.server, args=(int(received_message), chatPort, ))
                    t.start()
                    # Assumindo que as porta do vetor result ainda estão abertas
                    c = threading.Thread(target=chat_socket, args=(chatPort, ))
                    result.pop(0)
                    c.start()
                    chat_threads.append(c)
                    server_threads.append(t)
                    send_message(ready_socket, str(chatPort))
                except:
                    send_message(ready_socket, f"Failed to open Session on port {received_message}")

    


host = "localhost"  
start_port = 50000 
end_port = 65535
result = find_open_port(host, start_port, end_port)

port = result[0]

result.pop(0)
run_server(port)