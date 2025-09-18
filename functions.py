import os
import random
import requests
import json
import sys

import gc


import threading
from tkinter import messagebox
from banco import *


class Functions(Banco):
    def configuracao(self):
        self.verificaSSL = True
        self.consultaSinc = False
        self.siteInoveCFC = ""
        self.siteDetranPR = ""
        # (local) controla onde irei acessar o banco de dados
        self.servidor = ""
        self.setIdUser = 0
        self.setIdEstabelecimento = 0
        self.IdTerminal = 0
        self.intervalo = 5
        self.versao = "3.1"

        if self.servidor == "local":
            self.siteInoveCFC = "localhost"
            self.verificaSSL = False
        else:
            self.siteInoveCFC = "www.inovecfc.com"

        self.montaTabela()

        t = self.hasTokenTerminal()
        if t.__len__() == 0:
            self.IdTerminal = self.gerarTokenterminal()
            self.salvarTerminal()
        else:
            for val in t:
                self.IdTerminal = int(val[0])

        self.limite = "30"

    def validarAcesso(self):
        usuario = self.ipt_usuario.get()
        senha = self.ipt_senha.get()
        global driver

        if not usuario:
            messagebox.showerror("Aviso", "Usuário não informado")
            return
        if not senha:
            messagebox.showerror("Aviso", "Senha não informada")
            return

        request = requests.get("https://"+self.siteInoveCFC+"/sistemas/python/commom/login.php?usuario=" +
                               usuario+"&senha="+senha+"&terminal="+str(self.IdTerminal), verify=self.verificaSSL)
        res = json.loads(request.content)
        if not res:
            messagebox.showerror("Acesso Negado", "Usuário não localizado")
        else:
            self.frame.destroy()
            self.infoLogin = res
            self.salvarLogin()
            self.setIdUser = str(res['id_usuario'])
            self.setIdEstabelecimento = str(res['id_estabelecimento'])
            self.IdTerminal = str(res['terminal'])
            self.frames_conectado()
            self.frames_lista()
            self.myLista()
            self.startBuscaSinc()

    def trocarUsuario(self):
        self.deleteTabela()
        self.montaTabela()
        self.frame.destroy()
        self.lista.destroy()
        self.frames_login()

    def openImpressora(self):
        self.frame.destroy()
        self.lista.destroy()
        self.frames_lista_impressora()

    def gerarTokenterminal(self):
        return random.randint(10000000, 99999999)

    def hasSincronizacao(self):

        if self.consultaSinc == False:
            request = requests.get("https://"+self.siteInoveCFC+"/sistemas/python/commom/hasSincronizacao.php?id_estabelecimento=" +
                                   self.setIdEstabelecimento+"&terminal="+self.IdTerminal, verify=self.verificaSSL)
            res = json.loads(request.content)

            if not res:
                self.consultaSinc = False
                self.popular()

            else:
                self.prepararTelaSinc(res)

    def prepararTelaSinc(self, res):
        self.consultaSinc = True
        self.hasSinc = res
        self.salvarHasSinc()
        self.frames_gif(self.infoLogin['uf'])
        if (self.infoLogin['uf'] == "PR"):

            self.buscarGradePraticaPR()
            self.fimSinc()
        elif (self.infoLogin['uf'] == "MG"):
            if (self.hasSinc['acao'] == "consultar-situacao"):
                # self.buscarSolicitacaoExameMG()
                # self.atualizarByConsultaSituacaoMG()
                self.fimSinc()
            elif (self.hasSinc['acao'] == "enviar-exames"):
                # self.buscarMarcacaoExameMG()
                self.fimSinc()
            elif (self.hasSinc['acao'] == "emitir-taxa"):
                print(f"***    Iniciando a geração da Taxa     ***")
                self.prepararTaxaMG(self.hasSinc)
                self.fimSinc()

    def fimSinc(self):
        self.consultaSinc = False
        self.canvas.destroy()
        self.hasSincronizacao()

    def buscaMacacaoExameMG(self):
        print("MG")
        self.consultaSinc = False

    def gravarByInoveCFC(self, msg, id, intintegracao="0"):
        tabela = 'inove_presenca_pratica'
        where = " id_presenca_pratica in ("+id+")"

        if intintegracao != "0":
            campos = ("int_agenda", "erroSinc")
            data = (intintegracao, "")

        else:
            campos = ('erroSinc')
            data = (msg)

        request = requests.get("https://"+self.siteInoveCFC+"/sistemas/python/detranpr/gravarByInoveCFC.php?user="+self.hasSinc['user_inove']+"&pwd="+self.hasSinc[
                               'pwd_inove']+"&id_presenca_pratica="+id+"&intintegracao="+str(intintegracao)+"&msg="+msg+"&funcionario="+self.hasSinc['usuario'], verify=self.verificaSSL)
        res = json.loads(request.content)

        return True

    def gravarByInoveCFConsultaSituacaoMG(self, observacao, id_solicitacao, id_aluno):
        requests.get("https://"+self.siteInoveCFC+"/sistemas/python/detranmg/gravarBySituacao.php?user="+self.hasSinc['user_inove']+"&id_solicitacao="+id_solicitacao+"&id_aluno="+str(
            id_aluno)+"&observacao="+observacao+"&funcionario="+self.hasSinc['usuario'], verify=self.verificaSSL)
        return True

    def atualizarByConsultaSituacaoMG(self):
        requests.get("https://"+self.siteInoveCFC+"/sistemas/python/detranmg/atualizarBySituacao.php?user=" +
                     self.hasSinc['user_inove'], verify=self.verificaSSL)
        return True

    def ajustaIntAgenda(self):
        requests.get("https://"+self.siteInoveCFC+"/sistemas/python/detranpr/arrumarIntAgendaPr.php?user=" +
                     self.hasSinc['user_inove']+"&pwd="+self.hasSinc['pwd_inove'], verify=self.verificaSSL)

        self.canvas.destroy()
        return True

    def startBuscaSinc(self):
        event = threading.Event()

        k = ThreadJob(self.hasSincronizacao, event, self.intervalo)
        k.start()

    def buscarGradePraticaPR(self):
        request = requests.get("https://"+self.siteInoveCFC+"/sistemas/python/detranpr/getPlacas.php?dt_inicial=" +
                               self.hasSinc['dt_inicial']+"&user="+self.hasSinc['user_inove']+"&pwd="+self.hasSinc['pwd_inove']+"&id_categoria="+self.hasSinc['id_categoria']+"&limite="+self.hasSinc['limite'], verify=self.verificaSSL)
        placas = json.loads(request.content)
        self.salvarPlacas(placas)

        request = requests.get("https://"+self.siteInoveCFC+"/sistemas/python/detranpr/getGradePratica.php?dt_inicial=" +
                               self.hasSinc['dt_inicial']+"&user="+self.hasSinc['user_inove']+"&pwd="+self.hasSinc['pwd_inove']+"&id_categoria="+self.hasSinc['id_categoria']+"&limite="+self.hasSinc['limite'], verify=self.verificaSSL)
        aulas = json.loads(request.content)
        self.salvarAulas(aulas)

        from automatizacaoPR import AutomatizacaoPR
        obj = AutomatizacaoPR()
        return obj.iniciar(self.hasSinc, self.verificaSSL, self.siteInoveCFC)

        self.ajustaIntAgenda()

    def buscarSolicitacaoExameMG(self):
        request = requests.get("https://"+self.siteInoveCFC+"/sistemas/python/detranmg/getSolcitacaoExame.php?dt_inicial=" +
                               self.hasSinc['dt_inicial']+"&dt_final=" +
                               self.hasSinc['dt_final']+"&user="+self.hasSinc['user_inove']+"&pwd="+self.hasSinc['pwd_inove'], verify=self.verificaSSL)
        consultar = json.loads(request.content)
        self.salvarConsultarSituacaoMG(consultar)
        from consultarSituacapMG import ConsultarSituacaoMG
        obj = ConsultarSituacaoMG()
        return obj.iniciar(self.infoLogin['cnpj'], self.hasSinc['user_inove'], self.siteInoveCFC, self.verificaSSL, self.versaochrome)

    def abrirTaxaMG(self):

        from taxaMG import TaxaMG
        obj = TaxaMG()
        return obj.iniciar(self.infoLogin['cnpj'], self.hasSinc['user_inove'], self.siteInoveCFC, self.verificaSSL, self.versaochrome)

    def buscarMarcacaoExameMG(self):
        request = requests.get("https://"+self.siteInoveCFC+"/sistemas/python/detranmg/getMarcarExameNovo.php?dt_inicial=" +
                               self.hasSinc['dt_inicial']+"&dt_final=" +
                               self.hasSinc['dt_final']+"&user="+self.hasSinc['user_inove']+"&pwd="+self.hasSinc['pwd_inove'], verify=self.verificaSSL)
        consultar = json.loads(request.content)
        self.salvarExamesMG(consultar)
        from marcacaoExamePraticoMG import MarcacaoExamePratMG
        obj = MarcacaoExamePratMG()
        return obj.iniciar(self.infoLogin['cnpj'], self.hasSinc['user_inove'], self.siteInoveCFC, self.verificaSSL, self.versaochrome)

    def prepararTaxaMG(self, informacao):
        from taxaMG import TaxaMG
        obj = TaxaMG()
        return obj.iniciar(informacao, self.verificaSSL)


class ThreadJob(threading.Thread):
    def __init__(self, callback, event, interval):
        '''runs the callback function after interval seconds

        :param callback:  callback function to invoke
        :param event: external event for controlling the update operation
        :param interval: time in seconds after which are required to fire the callback
        :type callback: function
        :type interval: int
        '''
        self.callback = callback
        self.event = event
        self.interval = interval
        super(ThreadJob, self).__init__()

    def run(self):
        while not self.event.wait(self.interval):
            self.callback()
