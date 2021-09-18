# AnonimChat
  Описание и состав кода:
  
  В данном проекте реализован анонимный крипточат с использованием ассиметричного rsa шифрования, что позволяет быть защищенным от MITM и тайминг атак, а также сам 
держатель сервера не сможет определить отправителя, получателя и данные их сообщений. Чат построен на модуле Socket с генерацией файлов аутентификации. Каждый 
узел подключается ТОЛЬКО по файлу ключу другого узла, который заранее генерируется и передается между участниками чата. Весь процесс переписки не сохраняется на
компьютере и будет очищен после завершения программы, так как хранится только в оперативной памяти. Анонимный чат полностью написан на языке Python c использованием
модулей и библиотек таких как: PyQt5, socket, rsa, shelve, threading и др. Сам интерфейс чата создавался с помощью программы PyQt5 Designer, что в последующем был
сконвертирован под язык Python.
  Сервер используется только для обмена пакетов клиентов чата, модель сервера и клиента полностью построена на TCP.
  
  Принцип работы:
  
  Для начала небходимо запустить сам сервер(server.py)

  В данной директории моего проекта находятся 3 папки, функционирующие между собой. 
  Здесь имеется:
1. client - непосредственно сама папка клиента;
2. client1 - папка второго клиента;
3. server - папка самого сервера, с помощью которого будет происходить обмен пакетов клиентов.

  Также в самом коде я подробно описал почти каждую строчку, так сказать обогатил комментариями, своего кода, дабы досконально понять его функционал и принцип
работы. В папках тоже имеется описание самой директории и зачем там эти файлы. =D
