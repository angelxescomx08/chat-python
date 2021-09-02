#se importan 2 modulos para el socket y controlar errores
from socket import socket, error
#se importa para la familia de protocolos y el tipo de socket
import socket as s1
#modulo para limpiar la terminal
import os
#modulo para el manejo de hilos
import threading

import sys
import time

from tkinter import END

#diccionario chat
dic_chat = {}
#
chats = {}

#funcion escribir para la interfaz
def escribir_interfaz(s, codigo, caja_texto, caja_archivo, mensajes_recibidos):
    s.send(codigo.encode())
    opciones_Cliente(codigo, s, caja_texto, caja_archivo, mensajes_recibidos)

#funcion ocupada en la interfaz
def opciones_Servidor(codigo, conn, addr, dic_chat, mylist):
    #nick
    if codigo == "0":
        pass  
    #recibir texto
    elif codigo == "1":
        msg = conn.recv(1024)
        mensaje = msg.decode()
        num = mylist.size()
        for i in range(num):
            item = mylist.get(i)
            ip = item.split(":")
            if ip[0] == addr[0]:
                mylist.delete(i)
                mylist.insert(i, ip[0]+':'+mensaje)
                if ip[0] in dic_chat:
                    mensajes_recibidos = dic_chat[ip[0]]
                    mensajes_recibidos.append(ip[0]+':'+mensaje)
                    chat = chats[ip[0]]
                else:
                    mensajes_recibidos = list()
                    mensajes_recibidos.append(ip[0]+':'+mensaje)
                    dic_chat[ip[0]] = mensajes_recibidos
                break        
    #recibir archivos
    elif codigo == "2":
        archivoSerializado = conn.recv(1024)
        archivo = archivoSerializado.decode()
        num = mylist.size()
        for i in range(num):
            item = mylist.get(i)
            ip = item.split(":")
            if ip[0] == addr[0]:
                mylist.delete(i)
                mylist.insert(i, ip[0]+':recibiste '+archivo)
                if ip[0] in dic_chat:
                    mensajes_recibidos = dic_chat[ip[0]]
                    mensajes_recibidos.append(ip[0]+':recibiste '+archivo)
                    chat = chats[ip[0]]
                else:
                    mensajes_recibidos = list()
                    mensajes_recibidos.append(ip[0]+':recibiste '+archivo)
                    dic_chat[ip[0]] = mensajes_recibidos
                break
        with open(archivo, "wb") as f:        
            data = conn.recv(1024)
            while data:
                f.write(data)
                data = conn.recv(1024)
                if len(data) == 1:
                    if data.decode() == "9":
                        break         
        f.close()
        print("Archivo recibido correctamente")        

#funcion para la interfaz
def opciones_Cliente(codigo, s, caja_texto, caja_archivo, mensajes_recibidos):
    if codigo == "0":
        pass
    elif codigo == "1":
        mensaje = caja_texto.get()
        s.send(mensaje.encode())
        mensajes_recibidos.append('Yo:'+mensaje)
    elif codigo == "2":
        aux = caja_archivo.get()
        aux2 = aux.split("/")
        archivo = aux2[-1]
        s.send(archivo.encode())
        mensajes_recibidos.append('Yo:enviaste '+archivo)
        time.sleep(1)
        with open(aux, 'rb') as f:
            data = f.read(1024)
            while data:
                s.send(data)
                data = f.read(1024)
        f.close()
        time.sleep(1)
        bandera = "9"
        s.send(bandera.encode())
        print("Archivo enviado correctamente")

def hiloCliente(conn, addr, mylist, dic_chat):
    while True:
        #se recibe el codigo serializado (TEXTO_CODE, ARCHIVO_CODE, SALIR_CODE)
        codSerializado = conn.recv(1024)
        #se descerializa
        codigo = codSerializado.decode()
        #se busca que quiere hacer el cliente (ENVIAR TEXTO, ENVIAR ARCHIVOS)
        opciones_Servidor(codigo, conn, addr, dic_chat, mylist)

def cliente(IP):
    #se crea el socket con la familia AF_INET, de tipo SOCK_STREAM y con el protocolo por default
    s = socket(s1.AF_INET,s1.SOCK_STREAM,proto=0)
    s.connect((IP, 8102))

    return s

def servidor(s, mylist, dic_chat):
    #se pone a la escucha de peticiones, el argumento es backlog que hace referencia al numero
    #de petiniones que puede encolar minimo 0
    s.listen(100)
    while True:
        #el metodo accept  regresa 2 objetos conn que es el objetos que nos permitira enviar y recibir
        #informacion desde el servidor y addr el objeto que nos aporta informacion del cliente
        conn, addr = s.accept()

        chat_existente = False
        num = mylist.size()
        for i in range(num):
            item = mylist.get(i)
            ip_aux = item.split(":")
            if ip_aux[0] == addr[0]:
                chat_existente = True
                break
        
        if chat_existente == False:
            mylist.insert(END, addr[0]+':')

        #se crea el hilo del cliente
        hilo = threading.Thread(target=hiloCliente, args=(conn, addr, mylist, dic_chat))
        hilo.setDaemon(True)
        #se inicia el hilo del cliente
        hilo.start()
        
def iniciar_socket():
    try:
        s = socket(s1.AF_INET, s1.SOCK_STREAM,proto=0)
    except Exception as e:
        print("Error al crear el socket: ",e)
        exit(-1)

    # se enlaza a la direcccion IP, con el puerto especificado
    #el metodo bind recibe una tupla(similar a un arreglo [], pero con PARENTESIS () *IMPORTANTE*)
    s.bind(("192.168.1.66", 8102))

    return s

def iniciar_servidor(s, mylist, dic_chat):
    threadServidor = threading.Thread(target=servidor,args=(s,mylist,dic_chat))
    threadServidor.start()
    
    return threadServidor

def iniciar_cliente(IP):
    s = cliente(IP)
    return s