#from client import *
"""import threading

class thread1(threading.Thread):
    def __init__(self):
        Thread.__init__(self)
        

    def run(self):
        while 1:
            if cli.connected==False :
                
                root.text1("Error")
                
            if cli.connected==True :
                root.text1("Working")
    


    thread1().start()
"""

from Tkinter import *
root = Tk()


# Connection options
MAIN_HOST=StringVar()
MAIN_PORT=StringVar()
SECOND_HOST=StringVar()
SECOND_PORT=StringVar()

#window scale
opt= Toplevel(root,bd=5,bg="grey")
opt.title("Connection")
opt.geometry("200x200")


#but=Button(opt, text="ololo", state=DISABLED)
#but.grid(padx=50, pady=140)



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
PORT_ent1.grid(row=4,column=1,padx=1)




Label(text="GALLOWS GAME!", bg="red").pack()

separator = Frame(height=2, bd=1, relief=SUNKEN)
separator.pack(fill=X, padx=5, pady=5)

v=StringVar()
lab=Label(root,textvariable=v,wraplength="0", anchor=CENTER, justify=CENTER).pack()
# v.set(cli.parsedanswer[0]['#213'][0]) 

text = Text()
text1=Text()

e = Entry(root)
e.pack()
e.focus_set()

def callback():
    v.set(e.get())
b = Button(root, text="get", width=10, command=callback)
b.pack()



root.mainloop()

