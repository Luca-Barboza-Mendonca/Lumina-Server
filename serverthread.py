import socket
import json
import select
import util

def receive_json_data(sock):
    data = b""
    while True:
        chunk = sock.recv(4096)
        if not chunk:
            break
        data += chunk
        if b'}' in chunk:
            break
    return data

def server(port):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = ('localhost', port)  # Change the address and port as needed
    server_socket.bind(server_address)
    server_socket.listen(3)  # Allow up to 3 simultaneous connections

    print(f"Waiting for connections... at {server_socket.getsockname()}")

    # List to keep track of connected clients
    client_sockets = [server_socket]
    client_counter = 1

    playerData = {"cum" :{'request': 'playerdata', 'id': '4', 'xPos': -0.34188613295555115, 'yPos': 0.09804494678974152, 'xlocalScale': 1.0, 'timestamp': 1700463725.6888394, 'pesos': 90, 'experience': 10, 'weaponLevel': 5, 'hitpoints': 20, 'isAlive': 1, 'swing': 0}}
    playerHealth = {"cum": ['4', 20]}

    c = 0

    while True:
        # Use select to wait for any of the sockets to be ready for reading
        readable, _, _ = select.select(client_sockets, [], [])

        for ready_socket in readable:
            if ready_socket == server_socket:
                # Accept a new connection
                connection, client_address = server_socket.accept()
                print(f"Connection from {client_address}")

                connection_number = "id_" + str(client_counter)
                peer_name = connection.getpeername()
                identifier = ':'.join(map(str, peer_name))
                playerData[identifier] = {'request': 'playerdata', 'id': str(client_counter), 'xPos': 0.0, 'yPos': 0.0, 'timestamp': 1, 'pesos': 0, 'experience': 0, 'weaponLevel': 0, 'hitpoints': 20, 'isAlive': 1, 'swing': 0}
                playerHealth[identifier] = [str(client_counter),20]
                client_counter += 1

                connection.sendall(str(connection_number).encode("utf-8"))

                client_sockets.append(connection)
            else:
                try:
                    # Receive data from a connected client
                    #data = recvall(ready_socket, 4096)
                    data = receive_json_data(ready_socket)
                    data_str = data.decode("utf-8")

                    json_list = util.makeJsonList(data_str)

                    peer_name = ready_socket.getpeername()
                    peer = ':'.join(map(str, peer_name))

                    if not data:
                        # Maybe we don't close here idk
                        print(f"Connection closed by {peer}")
                        del playerData[peer]
                        ready_socket.close()
                        client_sockets.remove(ready_socket)
                    else:
                        for i in range(0, len(json_list)):
                            json_data = json_list[i]
                            if (json_data["request"] == "playerdata"):

                                playerData[peer] = json_data
                                playerData[peer]["hitpoints"] = playerHealth[peer][1]
                                # if c%200 ==0:
                                #     print(f"Received JSON data from {ready_socket.getpeername()}")
                                #     print(playerData[peer])

                                ready_socket.sendall(str(playerData).encode("utf-8"))
                            elif (json_data["request"] == "damage"):
                                # Apply damage to the desired playerId
                                # For some reason this executes several times per swing
                                key = util.find_item_by_id(playerData, json_data["id"])
                                key2 = util.find_item(playerHealth, json_data["id"])
                                if (key != None):
                                    id = json_data["id"]
                                    hitpoints = json_data["hitpoints"]
                                    print(f"Updating Id number {id} hitpoints to {hitpoints}")
                                    playerData[key]["hitpoints"] = json_data["hitpoints"]
                                    playerHealth[key2][1] = json_data["hitpoints"]
                except ConnectionResetError:
                    continue
                except ConnectionAbortedError:
                    continue
            c += 1  