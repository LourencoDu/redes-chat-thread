import socket as sock
import threading as thread
import time

HOST = '127.0.0.1'
PORTA = 9999

status = True

s = sock.socket(sock.AF_INET, sock.SOCK_STREAM)

s.connect((HOST, PORTA))

on = True

def receber():
  while True:
    global status
    if status:
      dados = s.recv(1024)
      print(f'{dados.decode()}')

def digitar():
  while True:
    comando = input('')
    s.sendall(str.encode(f'{comando}'))
    if(comando == '/sair'):
      global status 
      status = False


receberThread = thread.Thread(target=digitar)
receberThread.start()

receber()

receberThread.join()

