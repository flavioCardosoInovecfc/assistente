from tkinter import *
from tkinter import ttk
import tkinter

from PIL import Image, ImageTk, ImageSequence
from functions import *


root = Tk()


class View(Functions):
    def __init__(self):
        self.root = root
        self.configuracao()
        self.hasLogin()
        self.user = StringVar()
        self.pwd = StringVar()
        self.cnpj = StringVar()
        entrou = False

        for val in self.mySelect:
            self.user.set(val[0])
            self.pwd.set(val[1])
            self.cnpj.set(val[2])
            entrou = True

        self.tela()
        self.frames_login()

        if entrou == True:
            self.validarAcesso()

        self.popular()
        self.root.mainloop()

    def tela(self):
        self.root.title("Assistente InoveCFC")
        self.root.configure(background='#FFFDF7')
        self.root.geometry("900x800")
        self.root.resizable(False, False)

        photo = PhotoImage(file=r'img/icoWindow.png')
        self.root.iconphoto(True, photo)

    def frames_login(self):

        self.frame = Frame(self.root, bd=4, background="white",
                           highlightbackground="red", highlightthickness=2)
        self.frame.place(relx=0.003, rely=0.01, relwidth=0.99, relheight=0.15)

        self.tj = Label(self.frame, text="Acesso ao sistema InoveCFC",
                        bg="red", fg="white", font=("arial", 14, 'bold'))
        self.tj.place(relx=0, rely=0, relwidth=1, relheight=0.4)

        self.lb_usuario = Label(
            self.frame, text="Usuário: ", bg="white", font=("arial", 10, "bold"))
        self.lb_usuario.place(relx=0.002, rely=0.6,
                              relwidth=0.08, relheight=0.2)
        self.lb_senha = Label(self.frame, text="Senha: ",
                              bg="white", font=("arial", 10, "bold"))
        self.lb_senha.place(relx=0.39, rely=0.6, relwidth=0.08, relheight=0.2)

        self.ipt_usuario = Entry(self.frame, font=(
            "arial", 10, 'bold'), border=2, textvariable=self.user)

        self.ipt_usuario.place(relx=0.08, rely=0.6,
                               relwidth=0.28, relheight=0.25)
        self.ipt_senha = Entry(self.frame, font=(
            "arial", 10, 'bold'), border=2, textvariable=self.pwd)
        self.ipt_senha.place(relx=0.47, rely=0.6, relwidth=0.3, relheight=0.25)
        self.ipt_senha.config(show="*")
        self.bt_acessar = Button(self.frame, text="Acessar", bd=2, bg="green", font=(
            "arial", 10, "bold"), fg="white", command=self.validarAcesso)
        self.bt_acessar.place(relx=0.88, rely=0.55,
                              relwidth=0.1, relheight=0.3)

    def frames_conectado(self):
        self.frame = Frame(self.root, bd=4, background="#FFFDF7",
                           highlightbackground="green", highlightthickness=2)
        self.frame.place(relx=0.003, rely=0.01, relwidth=0.99, relheight=0.1)

        self.bt_acessar = Button(self.frame, text="Trocar Usuário", bd=2, bg="blue", font=(
            "arial", 10, "bold"), fg="white", command=self.trocarUsuario)
        self.bt_acessar.place(relx=0, rely=0.45, relwidth=0.15, relheight=0.5)

        # Obtém a versão do Tkinter
        versao_tk = '15.06.26'

        self.tj = Label(self.frame, text="Conectado no Terminal ( " +
                        self.infoLogin['terminal']+" ) | v"+str(versao_tk), bg="green", fg="white", font=("arial", 14, 'bold'))
        self.tj.place(relx=0, rely=0, relwidth=1, relheight=0.4)

        self.lb_rs = Label(self.frame, text=self.infoLogin['cnpj'] + " | "+self.infoLogin['razao_social'] +
                           " | "+self.infoLogin['usuario'] + " | "+self.infoLogin['uf'], bg="white", font=("arial", 10, "bold"))
        self.lb_rs.place(relx=0.175, rely=0.6, relwidth=0.65, relheight=0.2)

    def frames_gif(self, estado):

        self.canvas = Canvas(self.root, width=900,
                             height=800, background="#FFFDF7")
        self.canvas.pack()
        if (estado == "PR"):
            _imagem = r'img/detranPR.gif'
        elif (estado == "MG"):
            _imagem = r'img/detranMG.gif'

        self.sequencia = [ImageTk.PhotoImage(img)
                          for img in ImageSequence.Iterator(
            Image.open(_imagem)
        )]
        self.image = self.canvas.create_image(
            480, 400, image=self.sequencia[0])
        self.animating = True
        self.animate(0)

    def animate(self, counter):
        if not self.animating:
            return
        try:
            self.canvas.itemconfigure(
                self.image, image=self.sequencia[counter])
            self.root.after(33, lambda: self.animate(
                (counter + 1) % len(self.sequencia)))
        except:
            self.animating = False

    def frames_lista(self):
        self.frame = Frame(self.root, bd=4, background="#FFFDF7",
                           highlightbackground="blue", highlightthickness=2)
        self.frame.place(relx=0.003, rely=0.12, relwidth=0.99, relheight=0.865)

        self.tj = Label(self.frame, text="Solicitações processadas",
                        bg="blue", fg="white", font=("arial", 14, 'bold'))
        self.tj.place(relx=0, rely=0, relwidth=1, relheight=0.05)

    def myLista(self):
        self.qtdeColumns()
        self.lista = ttk.Treeview(height=3, columns=self.columns)

        self.lista.heading("#0", text="")
        self.lista.heading("#1", text="Usuário")
        self.lista.heading("#2", text="Data Sinc")
        self.lista.heading("#3", text="Data Solicitação")
        self.lista.heading("#4", text="Ação")

        self.lista.column("#0", width=0, anchor=CENTER)
        self.lista.column("#1", width=250, anchor=CENTER)
        self.lista.column("#2", width=100, anchor=CENTER)
        self.lista.column("#3", width=150, anchor=CENTER)
        self.lista.column("#4", width=100, anchor=CENTER)

        self.lista.place(relx=0.01, rely=0.18, relwidth=0.975, relheight=0.795)

    def qtdeColumns(self):
        self.columns = ('col1', 'col2', 'col3', 'col4')

    def popular(self):

        try:
            res = self.getLista()
            entrou = False
            for i in res:
                if entrou == False:
                    self.lista.delete(*self.lista.get_children())
                    entrou = True

                self.lista.insert("", "end", values=i)
        except:
            exit()