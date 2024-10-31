import socket as sock
import threading as thread

HOST = '127.0.0.1' #'192.168.137.1' #127.0.0.1
PORTA = 9999

clientes = []
logados = []

#CRIAR O SOCKET DO SERVIDOR
# socket(IPv4: AF_INET, TCP: SOCK_STREAM)
s = sock.socket(sock.AF_INET, sock.SOCK_STREAM)

#FAZEMOS O "PLUG" DO IP DO SERVIDOR COM A PORTA (BIND)
s.bind((HOST, PORTA))

#COLOCAMOS O SERVIDOR NO MODO DE ESCUTA (LISTEN) - AGUARDANDO CONEXÔES
s.listen()
print(f'O servidor {HOST}:{PORTA} está aguardando conexões...')

def broadcast(mensagem, ender = ''):
  for destinatario in logados:    
    if(ender == '' or ender != destinatario['ender']):
      destinatario["conn"].sendto(str.encode(mensagem), destinatario["ender"])
  
def unicast(mensagem, ender):
  # print(logados)
  mensagem = mensagem.split()
  usuario = mensagem[0]

  # print(mensagem)
  del mensagem[0]
  destinatario = buscar_conn(usuario)
  remetente = buscar_ender(ender)
  mensagem = ' '.join(mensagem)
  mensagem = '(pv - ' + remetente + ') ' + mensagem
  destinatario['conn'].sendto(str.encode(mensagem), destinatario['ender'])


def buscar_conn(nome):
    for item in logados:
        if item['nome'] == nome:
            return item
    return None

def buscar_ender(ender):
    for item in logados:
        if item['ender'] == ender:
            return item['nome']

def entrar(nome, senha, conn, ender):
  try:
    cliente = next((cliente for cliente in clientes if cliente["nome"] == nome and cliente["senha"] == senha), False)
    if(cliente):
      conn.sendto(str.encode('Logado com sucesso!'), ender)
      broadcast(f'Servidor: {cliente["nome"]} entrou no chat!')
      return cliente
    else:
      conn.sendto(str.encode('Usuario nao cadastrado!'), ender)
  except:
    print('Falha ao autenticar usuario!')

def cadastrar(nome, senha, conn, ender):
  cliente = next((cliente for cliente in clientes if cliente["nome"] == nome), False)

  if(not cliente):
    novoUsuario = { 'nome': nome, 'senha': senha, 'conn': conn, 'ender': ender }

    clientes.append(novoUsuario)
    conn.sendto(str.encode('Seu usuario foi cadastrado!'), ender)
  else:
    conn.sendto(str.encode('Ja existe um usuario com o nome informado!'), ender)

def gerirCliente(conn, ender):
  print(f'Conexão estabelecida com {ender}')

  logado = None

  titulo = """
------ Bem-vindo ao Chat! ------

Comandos disponiveis:

/cadastrar <usuario> <senha>
/entrar <usuario> <senha>
/pv <usuario> <mensagem> -- necessário estar logado
/sair -- necessário estar logado

---------------------------------
  """

  conn.sendto(str.encode(titulo), ender)  

  while True:
    try:
      mensagem = conn.recv(1024).decode()
    except:
      continue

    print(f'Cliente - {ender} >> {mensagem}')
    if logado:
      if(mensagem == "/sair"):
        conn.sendto(str.encode('Você saiu do chat'), ender)

        broadcast(f'Servidor: {logado["nome"]} Saiu do Chat.')
        break
      if(mensagem[:3] == "/pv"):
        unicast(mensagem[3:].lstrip(), ender)
      else:
        broadcast(f'{logado["nome"]}: {mensagem}', ender)
    
    else:
      mensagemArray = mensagem.split()
      comando = mensagemArray[0]

      if(comando == '/cadastrar'):      
        try:
          nome = mensagemArray[1]
          senha = mensagemArray[2]

          cadastrar(nome, senha, conn, ender)
        except:
          conn.sendto(str.encode('Formato errado!\n/cadastrar <usuario> <senha>'), ender)
      elif(comando == '/entrar' or comando == '/login'):
        try:
          nome = mensagemArray[1]
          senha = mensagemArray[2]

          logado = entrar(nome, senha, conn, ender)
          novoLogin = { 'nome': nome, 'senha': senha, 'conn': conn, 'ender': ender }
          logados.append(novoLogin)
        except:
          conn.sendto(str.encode('Formato errado!\n/entrar <usuario> <senha>'), ender)
      elif(comando == '/sair'):
          conn.sendto(str.encode('Necessário estar logado'), ender)
      elif(comando == '/pv'):
          conn.sendto(str.encode('Necessário estar logado'), ender)
      else:
        conn.sendto(str.encode('Comando invalido'), ender)

#SERVIDOR PRECISA ACEITAR CONEXÃO
while True:
  try:
    conn, ender = s.accept() 
    clienteThread = thread.Thread(target=gerirCliente, args=(conn, ender))
    clienteThread.start()
  except:
    print("Falha ao se conectar... tente novamente")
    continue
