import time
import socket
import threading

class Server:
    def __init__(self, ip, port):
        """Создаем конструктор, принмающий ip и порт, чтобы запустить прслушививание
        по определенному ip порту, к которому будут подключаться наши клиенты"""
        self.ip = ip            #Сздаем перeменную ip
        self.port = port        #Сздаем перeменную port
        self.all_client = []    #Список в котором будут находится все клиенты данного чата

        """Запускаем прслушивание соединения"""
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #Создаем переменную server
        # и обращаемся к сокету, создаем константу первого арумента AF_INET с протоколом IPv4,
        # вторым аргументом указываем SOCK_STREAM, чтобы проводить через TCP службу
        self.server.bind((self.ip, self.port)) # начинаем прослушивание по определнному ip порту
        #(инициализируем IP-адрес и порт)
        self.server.listen(0) # Указываем сколько клиентов может сервер прослушивать (0-неограничено)
        threading.Thread(target=self.connect_handler).start() # Запускаем поток для того чтобы
        # отслеживать новое соединение
        print("Сервер запущен.")

    """Обрабатываем входящие соединения"""
    def connect_handler(self):
        while True: # Запускаем бесконечный цикл, в котором определяем переменные
            # client, address и от self.server принимаем поключение
            client, address = self.server.accept()
            if client not in self.all_client:
                """Если нашего клиента нету в списке all_client, то мы его добавляем,
                 и с этого потока запускаем другой поток, который будет использоваться
                 для обработки сообщений, передаем наш client сокет и запускаем наш поток"""
                self.all_client.append(client)
                threading.Thread(target=self.message_handler, args=(client,)).start()
                client.send("Успешное поключение к чату.".encode("utf-8")) # Отправляем нашему клиенту используя
                                                                           # сокет client о том то, что он
                                                                           # поключился к чату.
            time.sleep(1)
    """Обрабатываем отправленный текст"""
    def message_handler(self, client_socket): # Поток, созданный для клиента.
        while True:
            """Запускаем бесконечный цикл в котором принимаем данные от клиента в двоичном формате(1024)"""
            message = client_socket.recv(1024)
            # Удаляем текущий сокет
            if message == b'exit': # Если сообщение будет содержать
                # " b'exit' "(означает, что наш клиент покинул чат), то нужно оключить его сокеты
                # и удалить из списка all_client, после закончить наш поток с message_handler и
                # connect_handler.
                self.all_client.remove(client_socket)
                break
            for client in self.all_client:  # Иначе мы пробегаемся по всем клиентам, что есть в списке
                if client != client_socket: # client.send и сравниваем не является этот клиент сокетом
                    client.send(message)    # с тем, который сейчас указан, чтобы самомоу себе не написать сообещние
            time.sleep(1)                   # и отправляет каждому клиенту сообщение

myserver = Server('127.0.0.1', 5555)