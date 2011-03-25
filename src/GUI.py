from client import *
import time
import threading
import constants
from Tkinter import *



#actions&log
class thread1(threading.Thread):
    
    def run(self):
        while 1:
            while len(cli.parsedanswer):
                pop=cli.parsedanswer.pop()
                #if CONN_ALLOW:
                 #   text1.insert(END,"Connection allowed"+'\n')
                    
                #if CONN_CLOSE_KICK:
                    #text1.insert(END,"You were kicked!"+'\n')

                    
                for x in pop.keys():
                    
                    if CONN_ALLOW:
                        text1.insert(END,"Connection allowed"+'\n')         

                    if x==CONN_DENY:
                        text1.insert(END,"Connection deny"+'\n')
                    
                    if x==PACKET_USERWORD:
                        
                        for items in pop[x]:
                            
                            v.set(pop[PACKET_USERWORD][0])
                            text1.insert(END,pop[PACKET_USERWORD][1]+'tries left'+'\n')
                            if pop[PACKET_USERWORD][1]=='9':
                                circle = canvas.create_oval(25, 25, 50, 50, fill="white")
                                
                            if pop[PACKET_USERWORD][1]=='8':
                                canvas.create_line(37, 50, 37, 69)

                            if pop[PACKET_USERWORD][1]=='7':
                                canvas.create_line(37, 69, 29, 78)
                                
                            if pop[PACKET_USERWORD][1]=='6':
                                canvas.create_line(37, 69, 45, 78)

                            if pop[PACKET_USERWORD][1]=='5':
                                canvas.create_line(37, 53, 26, 60)

                            if pop[PACKET_USERWORD][1]=='4':
                                canvas.create_line(37, 53, 48, 60)

                            if pop[PACKET_USERWORD][1]=='3':
                                canvas.create_line(37, 53, 42, 49) #rope
                                canvas.create_line(49, 36, 79, 8)   #rope

                            if pop[PACKET_USERWORD][1]=='2':                   
                                canvas.create_line(79, 8, 79, 87)

                            if pop[PACKET_USERWORD][1]=='1':
                                canvas.create_line(79, 87, 63, 100)
                                canvas.create_line(79, 87, 89, 100)
                    if x==LETTER_FAIL:
                        text1.insert(END,"There is no such letter :("+'\n')
    
                    if x==LETTER_WIN:
                        text1.insert(END,"BINGO!"+'\n')

                    if x==LETTER_ALREADY:
                        text1.insert(END,"This letter already showed!"+'\n')

                    if x==WORD_FAIL:
                        text1.insert(END,"Game over, try another time!"+'\n')
    
                    if x==WORD_WIN:
                        text1.insert(END,"Congratulations, you win!"+'\n')
                        
                    if x==CONN_CLOSE_SERV:
                        text1.insert(END,"Server has been closed :("+'\n')
                        
                      
thread1().start()

    

import Tkinter as tk

root = Tk()

# Connection options
MAIN_HOST=StringVar()
MAIN_PORT=StringVar()
SECOND_HOST=StringVar()
SECOND_PORT=StringVar()

#window scale
opt= Toplevel(root,bd=5,bg="grey")
opt.title("Connection")
opt.geometry("250x200+200+300")





#main server
IP_lab=Label(opt,text="ServerIP:", bg="red")
IP_ent=Entry(opt,textvariable=MAIN_HOST,width="15")
PORT_lab=Label(opt,text="ServerPort:",bg="green")
PORT_ent=Entry(opt,textvariable=MAIN_PORT,width="15")


#alt server
IP_lab1=Label(opt,text="ServerIP2:", bg="red")
IP_ent1=Entry(opt,textvariable=SECOND_HOST,width="15")
PORT_lab1=Label(opt,text="ServerPort2:",bg="green")
PORT_ent1=Entry(opt,textvariable=SECOND_PORT,width="15")

#scales


IP_lab.grid(row=0,sticky=W)
IP_ent.grid(row=0,column=1,padx=1)
PORT_lab.grid(row=1,sticky=W)
PORT_ent.grid(row=1,column=1,padx=1)

IP_lab1.grid(columnspan=1,rowspan=2,sticky=W)
IP_ent1.grid(column=1,row=3,padx=1,sticky=W)
PORT_lab1.grid(rowspan=2,sticky=W)
PORT_ent1.grid(row=4,column=1,padx=1,sticky=W)
#-----------------------

def OptGet():
    CLI_MAIN_HOST=IP_ent.get().strip()
    CLI_MAIN_PORT=PORT_ent.get().strip()
    CLI_ALT_HOST=IP_ent1.get().strip()
    CLI_ALT_PORT=PORT_ent1.get().strip()
    text1.insert(END,"Changes applyed"+'\n')

    
but1=Button(opt,text="SET",command=OptGet)
but1.grid(row=0, column=2, columnspan=2, rowspan=2,
               sticky=W+E+N+S, padx=5, pady=5)



Label(text="GALLOWS GAME!", bg="red").pack()

separator = Frame(height=2, bd=1, relief=SUNKEN)
separator.pack(fill=X, padx=5, pady=5)
#main game window
v=StringVar()

lab=Label(root,textvariable=v,wraplength="0", anchor=CENTER, justify=CENTER).pack()



text = Text()

text1=Text()

e = Entry(root,justify=CENTER,width=5)

e.pack()
e.focus_set()

def callback():
    cli.send(e.get().strip())
    a=e.get()
    e.delete(0, END)
    
b = Button(root, text="Send", width=10, command=callback).pack()

frame1 = Frame(root,width=500, height=50, bg="yellow")

Q=Button(frame1, text="Q",width=3,command=lambda: e.insert(0,"q")).pack(side=LEFT)
W=Button(frame1, text="W",width=3,command=lambda: e.insert(0,"w")).pack(side=LEFT)
E=Button(frame1, text="E",width=3,command=lambda: e.insert(0,"e")).pack(side=LEFT)
R=Button(frame1, text="R",width=3,command=lambda: e.insert(0,"r")).pack(side=LEFT)
T=Button(frame1, text="T",width=3,command=lambda: e.insert(0,"t")).pack(side=LEFT)
Y=Button(frame1, text="Y",width=3,command=lambda: e.insert(0,"y")).pack(side=LEFT)
U=Button(frame1, text="U",width=3,command=lambda: e.insert(0,"u")).pack(side=LEFT)
I=Button(frame1, text="I",width=3,command=lambda: e.insert(0,"i")).pack(side=LEFT)
O=Button(frame1, text="O",width=3,command=lambda: e.insert(0,"o")).pack(side=LEFT)
P=Button(frame1, text="P",width=3,command=lambda: e.insert(0,"p")).pack(side=LEFT)

frame1.pack()

frame2 = Frame(root,width=500, height=20, bg="green", colormap="new")

A=Button(frame2, text="A",width=3,command=lambda: e.insert(0,"a")).pack(side=LEFT)
S=Button(frame2, text="S",width=3,command=lambda: e.insert(0,"s")).pack(side=LEFT)
D=Button(frame2, text="D",width=3,command=lambda: e.insert(0,"d")).pack(side=LEFT)
F=Button(frame2, text="F",width=3,command=lambda: e.insert(0,"f")).pack(side=LEFT)
G=Button(frame2, text="G",width=3,command=lambda: e.insert(0,"g")).pack(side=LEFT)
H=Button(frame2, text="H",width=3,command=lambda: e.insert(0,"h")).pack(side=LEFT)
J=Button(frame2, text="J",width=3,command=lambda: e.insert(0,"j")).pack(side=LEFT)
K=Button(frame2, text="K",width=3,command=lambda: e.insert(0,"k")).pack(side=LEFT)
L=Button(frame2, text="L",width=3,command=lambda: e.insert(0,"l")).pack(side=LEFT)

frame2.pack()

frame3 = Frame(root,width=500, height=20, bg="white", colormap="new")

Z=Button(frame3, text="Z",width=3,command=lambda: e.insert(0,"z")).pack(side=LEFT)
X=Button(frame3, text="X",width=3,command=lambda: e.insert(0,"x")).pack(side=LEFT)
C=Button(frame3, text="C",width=3,command=lambda: e.insert(0,"c")).pack(side=LEFT)
V=Button(frame3, text="V",width=3,command=lambda: e.insert(0,"v")).pack(side=LEFT)
B=Button(frame3, text="B",width=3,command=lambda: e.insert(0,"b")).pack(side=LEFT)
N=Button(frame3, text="N",width=3,command=lambda: e.insert(0,"n")).pack(side=LEFT)
M=Button(frame3, text="M",width=3,command=lambda: e.insert(0,"m")).pack(side=LEFT)
e.delete(0,END)
frame3.pack()

#------picture-----
canvas = Canvas(root, width=200, height=100)
"""circle = canvas.create_oval(25, 25, 50, 50, fill="white")
canvas.create_line(37, 50, 37, 69)
canvas.create_line(37, 69, 29, 78)
canvas.create_line(37, 69, 45, 78)
canvas.create_line(37, 53, 26, 60)
canvas.create_line(37, 53, 48, 60)
canvas.create_line(37, 53, 42, 49) #rope
canvas.create_line(49, 36, 79, 8)   #rope
canvas.create_line(79, 8, 79, 87)
canvas.create_line(79, 87, 63, 100)
canvas.create_line(79, 87, 89, 100)"""
canvas.pack()
#-----log-----
log= Toplevel(root,bd=5,bg="grey")
log.title("Info log")
log.geometry("200x200+450+300")

scrollbar = tk.Scrollbar(log)
logging=StringVar()
text1 = tk.Text(log, yscrollcommand=scrollbar.set)
text1.insert(END, "-------LOG-------"+'\n')


scrollbar.config(command=text1.yview)
scrollbar.pack(side='right', fill='y')
text1.pack(side='left', expand=0, fill='both')



root.mainloop()

