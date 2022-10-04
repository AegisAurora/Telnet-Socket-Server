import socket
import threading

HOST_IP = socket.gethostbyname(socket.gethostname())
#HOST_IP = "10.32.200.199"
HOST_PORT = 4200

clients = []
threads = []
clientToThread = {}
clientToUsername = {}
usernames = []
messages = []

def writeAll(lock,message,username):
    global clients
    message = f"{username}: " + message + "\r\n"
    lock.acquire()
    for conn in clients:
        conn.sendall(message.encode(encoding = "utf-8"))
    lock.release()


def client(lock, conn, address):
    global clientToUsername
    global clients
    print("client function + ", address)
    gen = read(conn)
    conn.sendall(b"Welcome to our server!\r\n")
    lock.acquire()
    if address not in clientToUsername:
        lock.release()
        conn.sendall(b"Please choose a username\r\n")
        while True:
            user = next(gen)
            if user in usernames:
                conn.sendall(b"Username is already taken, try again\r\n")
            elif len(user) > 10:
                conn.sendall(b"Username is too long\r\n")
            else:
                break
        lock.acquire()
        clientToUsername[address] = user
        usernames.append(user)
    else:
        conn.sendall(b"Welcome Back " + clientToUsername[address].encode("utf-8") +b"\r\n")
    username = clientToUsername[address]
    print("logged in " + username)
    if len(messages) > 4:
        for i in range(len(messages)-1,len(messages)-4,-1):
            lock, block, username = messages[i]
            message = f"{username}: " + block + "\r\n"
            conn.sendall(message.encode(encoding = "utf-8"))
    else:
        for i in reversed(messages):
            lock, block, username = i
            message = f"{username}: " + block + "\r\n"
            conn.sendall(message.encode(encoding = "utf-8"))


    lock.release()
    writeAll(lock,f"{username} just logged in","Admin")
    while True:
        try:
            block = next(gen)
            
        except:
            lock.acquire()
            conn.close()
            clients.remove(conn)
            #del clientToUsername[address]
            lock.release()
            print(f"{username} disconnected")
            writeAll(lock,f"{username} just logged off","Admin")
            return
        messages.append((lock,block,username))
        writeAll(lock,block,username)



def read(conn):
    text = ""
    while True:
        
        data = conn.recv(2)
        print(f"AFTER RECEIVE text:{text}|data:{data}")
        if data == b"":
            return
        try:
            data = data.decode(encoding = "utf-8")
        except:
            data = " "
        if "\b" in data:
            conn.sendall(b"\x20\x08")
            text = text[:-1]
            print(f"client pressed backspace text:{text}|data:{data}")
        elif text:
            data = text + data
            text = ""
            print(f"ELIF TEXT text:{text}|data:{data}")
        
        if "\r\n" in data:
            for line in data.splitlines(True):
                if line.endswith('\r\n'):
                    yield line.replace("\r", "").replace("\n", "")
                else:
                    text = line
        
        elif "\b" not in data:
            text += data
            print(f"NOT ENTER text:{text}|data:{data}")

def main():

    listener = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    listener.bind((HOST_IP,HOST_PORT))
    listener.listen(True)
    print(f"Server hosted on {HOST_IP} {HOST_PORT}")

    lock = threading.Lock()

    while True:
        print("Looking for a client")
        conn, ip = listener.accept()
        ip, _ = ip
        print("found a client")
        t1 = threading.Thread(target=client, args=(lock,conn, ip))
        lock.acquire()
        clients.append(conn)
        
        lock.release()
        t1.start()
        
        
    else:
        listener.close()

    
    

if __name__ == "__main__":
    main()
