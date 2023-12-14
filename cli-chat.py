import socket
import threading
import os
import json
import random

emojis={':)': '\U0001F642', ':(': '\U0001F641', ':D': '\U0001F600', ':*': '\U0001F618', ":'(": '\U0001F622', ':/': '\U0001F615', '8)': '\U0001F913', ':P': '\U0001F60B', ':O': '\U0001F62E', 'B)': '\U0001F60E', 'D:': '\U0001F626', '<3': '\U0001F496', ':|': '\U0001F610'}


# thread receiver function
def receiver(usr, prt):

    # Create a UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    self_address = ('localhost', prt)
    sock.bind(self_address)

    # Loop, printing any data we receive
    while True:
        data, server = sock.recvfrom(4096)
        query = json.loads(data.decode())

        # New user join the server
        if query.get('type') == 0:
            print('\n[{}] has join the session\n'.format(query.get('user')))

        # Message to multicast group
        elif query['type'] == 1:
            print('<', query.get('user'), '>', query.get('message'))

        # User left the server
        elif query['type'] == 2:
            print('\n[{}] has left the session'.format(query.get('user')))

        # List of users in room chat server
        elif query['type'] == 3:
            print('\n', query['message'])


# thread sender function
def sender(usr, typ, prt):
    # Create a UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_address = ('localhost', 10000)

    multicast = {
        'message': '',
        'user': user_nick,
        'type': 0,
        'port': prt
    }
    sock.sendto(json.dumps(multicast).encode(), server_address)
    typ = b''

    while True:
        msg = input(' ')
        if msg == 'exit':
            multicast = {
                'message': msg,
                'user': usr,
                'type': 2,
                'port': prt
            }
            sock.sendto(json.dumps(multicast).encode(), server_address)
            break
        else:
            for text, emoji in emojis.items():
                    msg = msg.replace(text, emoji)
            multicast = {
                'message': msg,
                'user': usr,
                'type': 1,
                'port': prt
            }
            sock.sendto(json.dumps(multicast).encode(), server_address)
    sock.close()
    exit(0)


# start chat client
user_nick = input('INGRESA TU USUARIO >>> ')

# Assignment port to new user
port = random.randint(1000, 9000)

# start communication udp multithreading
message_receiver = threading.Thread(target=receiver, args=(user_nick, port))
message_sender = threading.Thread(target=sender, args=(user_nick, 0, port))

message_receiver.start()
message_sender.start()