import socket
import select

HEADER_LENGTH = 10

IP = "127.0.0.1"
PORT = 1234
s_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

s_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s_socket.bind((IP, PORT))

s_socket.listen()

sockets_list = [s_socket]

clients = {}

print(f'Listening for connections on {IP}:{PORT}...')

def receive_message(c_socket):

    try:

        message_header = c_socket.recv(HEADER_LENGTH)

        if not len(message_header):
            return False

        message_length = int(message_header.decode('utf-8').strip())

        return {'header': message_header, 'data': c_socket.recv(message_length)}

    except:
        return False

while True:
    read_sockets, _, exception_sockets = select.select(sockets_list, [], sockets_list)

    for notified_socket in read_sockets:

        if notified_socket == s_socket:

            c_socket, client_address = s_socket.accept()

            user = receive_message(c_socket)

            if user is False:
                continue

            sockets_list.append(c_socket)

            clients[c_socket] = user

            print('Accepted new connection from {}:{}, username: {}'.format(*client_address, user['data'].decode('utf-8')))

        else:

            message = receive_message(notified_socket)

            if message is False:
                print('Closed connection from: {}'.format(clients[notified_socket]['data'].decode('utf-8')))

                sockets_list.remove(notified_socket)

                del clients[notified_socket]

                continue

            user = clients[notified_socket]

            print(f'Received message from {user["data"].decode("utf-8")}: {message["data"].decode("utf-8")}')

            for c_socket in clients:

                if c_socket != notified_socket:

                    c_socket.send(user['header'] + user['data'] + message['header'] + message['data'])

    for notified_socket in exception_sockets:

        sockets_list.remove(notified_socket)

        del clients[notified_socket]
