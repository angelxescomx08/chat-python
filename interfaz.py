from tkinter import *
from tkinter import simpledialog
import whatsapp
import threading
from tkinter.filedialog import askopenfilename

dic_chat = whatsapp.dic_chat
chats = whatsapp.chats

def actualizar_chat(chat, mensajes_recibidos,ip):
    tam = chat.size()
    if tam > 0:
        chat.delete(0, END)
    
    for mensaje in mensajes_recibidos:
        chat.insert(END, mensaje)

    root.after(1000, lambda:actualizar_chat(chat,mensajes_recibidos, ip))

def center_window(root, w=500, h=500):
    # get screen width and height
    ws = root.winfo_screenwidth()
    hs = root.winfo_screenheight()
    # calculate position x, y
    x = (ws/2) - (w/2)    
    y = (hs/2) - (h/2)
    root.geometry('%dx%d+%d+%d' % (w, h, x, y))

def seleccionar_arc(caja_archivo):
    filename = askopenfilename()
    caja_archivo.delete(0,END)
    caja_archivo.insert(0,filename)

def seleccionar_chat(evt):
    # Note here that Tkinter passes an event object to onselect()
    w = evt.widget
    index = int(w.curselection()[0])
    value = w.get(index)
    
    ip = value.split(":")
    
    iniciar_chat(dic_chat,ip[0])

def iniciar_chat(dic_chat, IP):
    if IP == '':
        #pedir ip
        ip = simpledialog.askstring(title="IP", prompt="Introduce ip a la que te quieras conectar")
    else:
        ip = IP
    
    #socket
    s = whatsapp.iniciar_cliente(ip)

    chat_existente = False
    num = mylist.size()
    for i in range(num):
        item = mylist.get(i)
        ip_aux = item.split(":")
        if ip_aux[0] == ip:
            chat_existente = True
            break
    
    if chat_existente == False:
        mylist.insert(END, ip+':')

    #añadir al diccionario
    mensajes_recibidos = list()

    #ventana de chat
    ventana_chat = Tk()
    ventana_chat.title(ip)
    ventana_chat.minsize(500, 500)

    #frame chat
    frame1 = Frame(ventana_chat)
    frame1.pack(side = TOP)

    #scroll
    scrollbar1 = Scrollbar()
    scrollbar1.pack(side = RIGHT, fill = Y )

    chat = Listbox(frame1, yscrollcommand = scrollbar1.set , width = 50)

    #button enviar archivo
    seleccionar_archivo = Button(frame1, text="Enviar archivo", command = lambda:whatsapp.escribir_interfaz(s,"2", caja_mensaje, caja_archivo,mensajes_recibidos)).pack(side = BOTTOM)

    #button seleccionar archivo
    seleccionar_archivo = Button(frame1, text="Seleccionar archivo", command = lambda:seleccionar_arc(caja_archivo)).pack(side = BOTTOM)

    #entry archivo
    caja_archivo = Entry(frame1)
    caja_archivo.pack(side=BOTTOM)

    #button mensaje
    enviar_mensaje = Button(frame1, text="Enviar mensaje", command = lambda:whatsapp.escribir_interfaz(s,"1", caja_mensaje, caja_archivo, mensajes_recibidos) ).pack(side = BOTTOM)

    #entry mensaje
    caja_mensaje = Entry(frame1)
    caja_mensaje.pack(side=BOTTOM)

    dic_chat[ip] = mensajes_recibidos
    chats[ip] = chat

    chat.pack(side = TOP)
    center_window(ventana_chat, 500, 500)
    root.after(1000, lambda:actualizar_chat(chat,mensajes_recibidos, ip))

#ventana principal
root = Tk()
root.title("Whatsapp 2.0")
root.minsize(500, 300)

#frame
frame = Frame()
frame.pack(side = TOP)

#label
label = Label(frame,text="Usuarios conectados")
label.pack(expand=True, side = TOP,fill = BOTH)

#scroll
scrollbar = Scrollbar()
scrollbar.pack(side = RIGHT, fill = Y )

#boton
Button(root, text="Iniciar chat", command=lambda:iniciar_chat(dic_chat,'')).pack(side = BOTTOM)

#lista de conectados
mylist = Listbox(root, yscrollcommand = scrollbar.set )
mylist.bind('<<ListboxSelect>>', seleccionar_chat)
mylist.pack(expand=True,side = LEFT, fill = BOTH )

scrollbar.config( command = mylist.yview )

center_window(root, 500, 300)

#funcionalidad
s = whatsapp.iniciar_socket()

hilo_servidor = whatsapp.iniciar_servidor(s, mylist, dic_chat)

mainloop()