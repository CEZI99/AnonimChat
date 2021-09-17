import os
import sys
import rsa
import time
import shelve
import socket
import threading
from PyQt5 import QtCore, QtGui, QtWidgets
from des import *


# Мониторинг входящих сообщений
class message_monitor(QtCore.QThread):
    mysignal = QtCore.pyqtSignal(str)

    def __init__(self, server_socket, private_key, parent=None):
        QtCore.QThread.__init__(self, parent)
        self.server_socket = server_socket
        self.private_key = private_key
        self.message = None

    """Когда запускаем Класс message_monitor, мы заходим в бесконечный цикл где message будет принимать пакеты
    от нашего сервера(recv(1024)). Если это зашифрованное сообщение(28 строка), то он будет его расшифровывать его
    с помощью модуля rsa и нашего приватного ключа. После посылать сигнал в переменную mysignal уже расшифрованное
    сообщение, если не зашифрованне сообщение то также передаст в обыкновенном виде(строка 34). Все это выраженно
    в блоке обработчика исключений."""
    def run(self):
        while True:
            try: # Данные от собеседника (зашифрованные)
                self.message = self.server_socket.recv(1024)
                decrypt_message = rsa.decrypt(self.message, self.private_key)
                self.mysignal.emit(decrypt_message.decode('utf-8'))
            except: # Данные от сервера (не зашифрованные)
                self.mysignal.emit(self.message.decode('utf-8'))



class Client(QtWidgets.QMainWindow):
    """Класс Client является файлом интерфейса"""
    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.ip = None      # Объявляем ip
        self.port = None    # Объявляем port
        self.friend_public_key = None # Объявляем публичный ключ нашего собеседника
        
        # Ключи шифрования текущего клиента
        self.mypublickey = None  # Объявляем свой публичный ключ
        self.myprivatekey = None # Объявляем свой приватный ключ
 
        # Проверка на наличие идентификатора собеседника
        """Данное условие определяет был ли помещен файл friend_id в папку клинета 
         friend_id, если в данной папке ничего нет, то мы блокируем  кнопки (False) 
         и выводим информацию message = 'Поместите идентификатор собеседника в "friend_id"'"""
        if len(os.listdir('friend_id')) == 0:
            self.ui.lineEdit.setEnabled(False)
            self.ui.pushButton.setEnabled(False)
            self.ui.pushButton_2.setEnabled(False)
            self.ui.pushButton_4.setEnabled(False)
            message = 'Поместите идентификатор собеседника в "friend_id"'
            self.ui.plainTextEdit.appendPlainText(message)

        # Проверка создан ли личный идентификатор
        """Данное условие определяет, если в директории папки client нет файла private,
         то мы блокируем  кнопки (False) и выводим информацию message = 'Также необходимо 
         сгенерировать свой идентификатор'"""
        if not os.path.exists('private'):
            self.ui.lineEdit.setEnabled(False)
            self.ui.pushButton.setEnabled(False)
            self.ui.pushButton_2.setEnabled(False)
            self.ui.pushButton_4.setEnabled(False)
            message = 'Также необходимо сгенерировать свой идентификатор'
            self.ui.plainTextEdit.appendPlainText(message)

        else:
            # Подгрузка данных текущего клиента
            """Если предыдущие условия соблюдены, то мы открывем с помощью модуля shelve(Он сохраняет 
            объекты в файл с определенным ключом, подобен словарю) и извлекаем из файла свой приватный ключ,
            после помещаем в переменные mypublickey, myprivatekey, т. е. инициализируем эти переменный из
            файла private """
            with shelve.open('private') as file:
                self.mypublickey = file['pubkey']
                self.myprivatekey = file['privkey']
                self.ip = file['ip']
                self.port = file['port']

            # Подгрузка данных собеседника
            """Также открываем с помощью модуля shelve friend_id нулевой индекс, тоесть получаем сам файл
            your_id в папке friend_id, соответсвенно после обмена ключами клиентов.
            Далее получаем публичный ключ нашего собеседника """
            with shelve.open(os.path.join('friend_id', os.listdir('friend_id')[0])) as file:
                self.friend_public_key = file['pubkey']
            """Если предыдущие усовия были соблюдены, то есть файл имеется и инициализировали переменные
            то можно подключаться к серверу"""
            message = 'Подключитесь к серверу'
            self.ui.plainTextEdit.appendPlainText(message) # Выводим сообщение о возможности поключения к сереру
            self.ui.lineEdit.setEnabled(False)
            self.ui.pushButton.setEnabled(False)
            self.ui.pushButton_4.setEnabled(False)
            self.ui.pushButton_2.setEnabled(True)


        # Обработчики кнопок
        """Создаем обработчики всех кнопок, которые есть в интерфейсе"""
        self.ui.pushButton_2.clicked.connect(self.connect_server)  # Кнопка "Подключится"
        self.ui.pushButton.clicked.connect(self.send_message)      # Кнопка "Отправить"
        self.ui.pushButton_5.clicked.connect(self.generate_encrypt)# Кнопка "Сгенерировать данные для подключения"
        self.ui.pushButton_4.clicked.connect(self.clear_panel)     # Кнопка "Очистить"

    # Подключаемся к серверу
    def connect_server(self):
        try:
            self.tcp_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # Снова создаем ipv4 протокол и TCP
                                                                                # соединение как в server.py

            self.tcp_client.connect((self.ip, self.port)); time.sleep(2) # Производим коннект по инициализированным
                                                                         # нами ip и port. Файл генерирует айпи порт
                                                                         # нашего сервера, т. е. мы поключаемся
                                                                         # конкретно к серверу.

            # Запускаем мониторинг входящих сообщений.
            """Создаем экземпляр класса message_monitor, который принимает tcp_client(сокет клиента) и 
            myprivatekey(приватный ключ)"""
            self.message_monitor = message_monitor(self.tcp_client, self.myprivatekey)
            self.message_monitor.mysignal.connect(self.update_chat) # Ссылаемся на конструтор класса message_monitor.
            # является оброботчиком переменной mysignal в которой хранится данные с сервера.
            # update_chat выводит значения которые передает mysignal.emit что находится в классе message_monitor

            self.message_monitor.start() # Запускаем обработчик, запускаем бесконечную прослушку сообщений, если
            # сообщения есть, то мы выводим в основную панель.

            # Разблокируем кнопки, которые нам нужны и заблокируем не нужные
            self.ui.lineEdit_4.setEnabled(False)   # Адрес сервера...
            self.ui.lineEdit_5.setEnabled(False)   # Порт сервера...
            self.ui.pushButton_2.setEnabled(False) # Подключится
            self.ui.pushButton.setEnabled(True)    # Отправить
            self.ui.lineEdit.setEnabled(True)      # Текст сообщения...
            self.ui.pushButton_4.setEnabled(True)  # Очистить
            self.ui.pushButton_5.setEnabled(False) # Сгенерировать данные для подключения
        except:
            """Если сервер отключен, то у нас оключается экран и выводим строку 145 и навсякий случай 146"""
            self.ui.plainTextEdit.clear()
            self.ui.plainTextEdit.appendPlainText('Ошибка подключения к серверу!')
            self.ui.plainTextEdit.appendPlainText('Измените идентификаторы и повторите попытку!')


    # Отправить сообщение
    """Функция отправки сообщения, которая првязана к кнопке 'Отправить'(self.ui.pushButton). Перед тем как 
     отправить сообщение мы проверяем в блоке обработчика сообщений содержит ли self.ui.lineEdit.text какой-то
     текст(строка 159) и присваеваем ее переменной message. После этого шифруем наше сообщение используя
     публичный ключ другого клиента(self.friend_public_key) в plainTextEdit.appendPlainText вывдим наше сообщение 
     в открытом виде(строка 163), чтобы мы могли прочитать то, что мы писали. 
     Далее используя tcp_client.send (tcp_client - это сокет нашего клиента) отправляем наше 
     зашифрованное сообщение(crypto_message)"""
    def send_message(self):
        try:
            if len(self.ui.lineEdit.text()) > 0:
                message = self.ui.lineEdit.text()
                crypto_message = rsa.encrypt(message.encode('utf-8'), self.friend_public_key)

                self.ui.plainTextEdit.appendPlainText(f'[Вы]: {message}')
                self.tcp_client.send(crypto_message)
                self.ui.lineEdit.clear()
        except:
            sys.exit()


    # Сгенерировать ключи шифрования
    def generate_encrypt(self):
        """generate_encrypt(кнопка "Сгенерировать данные для подключения" self.ui.pushButton_5). Для начала мы
         прверяем указан ли наш ip и port(Строки 178 и 179), если заполнены то генерируем публичный и приватный ключ
         используя модуль rsa (строка 180). После генерации ключей открываем файл с помощью модуля shelve, указываем
         название нашего файла и указываем ему ключ и прередаем значение(по принципу словаря). В your_id записываем
         публичный ключ, айпи и порт.
         В private записываем публичный ключ, приватный ключ, айпи и порт."""
        if len(self.ui.lineEdit_4.text()) > 0:
            if len(self.ui.lineEdit_5.text()) > 0:
                (pubkey, privkey) = rsa.newkeys(512)

                with shelve.open('your_id') as file:
                    file['pubkey'] = pubkey
                    file['ip'] = str(self.ui.lineEdit_4.text())
                    file['port'] = int(self.ui.lineEdit_5.text())
                
                with shelve.open('private') as file:
                    file['pubkey'] = pubkey
                    file['privkey'] = privkey
                    file['ip'] = str(self.ui.lineEdit_4.text())
                    file['port'] = int(self.ui.lineEdit_5.text())
                
                self.ui.plainTextEdit_2.appendPlainText('Создан "your_id" идентификатор')
                self.ui.plainTextEdit_2.appendPlainText('Передайте его собеседнику и начните диалог')
            else:
                self.ui.plainTextEdit_2.clear()
                self.ui.plainTextEdit_2.appendPlainText('Проверьте правильность вводимых данных!')     
        else:
            self.ui.plainTextEdit_2.clear()
            self.ui.plainTextEdit_2.appendPlainText('Проверьте правильность вводимых данных!')



    # Закрытия соединения
    def closeEvent(self, event):
        """Обработчик, чтобы в случае, когда пользователь просто закроет чат мы перехватываем событие о завершение
        программы и автоматически отправляем сообщение серверу b'exit', когда сервер его получит, то он удалит его
        сокет. После закрываем методом close()"""
        try:
            self.tcp_client.send(b'exit')
            self.tcp_client.close()
        except:
            pass


    # Обновляем окно чата
    def update_chat(self, value):
        self.ui.plainTextEdit.appendHtml(value)


    # Очищаем окно с чатом
    def clear_panel(self):
        self.ui.plainTextEdit.clear()
            


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    myapp = Client()
    myapp.show()
    sys.exit(app.exec_())









    