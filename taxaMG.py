import json
import os
import random
from playwright.sync_api import sync_playwright
import time
import base64

import requests


class TaxaMG():

    def iniciar(self, informacao, verificaSSL):

        self.user_inove = informacao['user_inove']
        self.verificaSSL = verificaSSL

        self.mapeamento()
        self.ajustarParms(informacao)
        self.on_open()

    def ajustarParms(self, informacao):
        # assigning our sample to a variable
        convertsample = informacao['geral']
        # converting the base64 code into ascii characters
        convertbytes = convertsample.encode("ascii")
        # converting into bytes from base64 system
        convertedbytes = base64.b64decode(convertbytes)
        # decoding the ASCII characters into alphabets
        decodedsample = convertedbytes.decode("ascii").split("&")

        rows = len(decodedsample)
        for i in range(rows):
            temp = []
            temp = decodedsample[i].split("=")
            if temp[0] == 'codigoTaxa':
                self.codigoTaxa = temp[1]
            elif temp[0] == 'codigo_municipio':
                self.codigo_municipio = temp[1]
            elif temp[0] == 'codigo-municipio':
                self.codigo_municipio = temp[1]
            elif temp[0] == 'id_aluno':
                self.id_aluno = temp[1]
            elif temp[0] == 'categoria_pretendida':
                self.categoria_pretendida = temp[1]

        request = requests.get("https://www.inovecfc.com/sistemas/python/detranmg/getAluno.php?user=" +
                               self.user_inove+"&id_aluno="+self.id_aluno+"&codigo="+str(self.codigoTaxa), verify=self.verificaSSL)
        self.dados = json.loads(request.content)

    def openServico(self):
        if self.codigoTaxa == '15':
            self.tempo = 30
            self.inscricaoprimeirahabiltacao()
        elif self.codigoTaxa == '16':
            self.tempo = 30
            self.adicaocategoria()
        elif self.codigoTaxa == '17':
            self.tempo = 30
            self.mudancacategoria()
        elif self.codigoTaxa == '18':
            self.tempo = 20
            self.examelegislacaorepetencia()
        elif self.codigoTaxa == '19':
            self.tempo = 30
            self.examedirecaorepetencia()
        elif self.codigoTaxa == '23':
            self.tempo = 20
            self.expedicaolicendaaprendizagem()
        elif self.codigoTaxa == '34':
            self.tempo = 20
            self.registroouimportacaoprontuario()
        elif self.codigoTaxa == '27':
            self.tempo = 30
            self.cnhDefenitiva()

    def registroouimportacaoprontuario(self):
        self.pagina.goto(
            "https://transito.mg.gov.br/habilitacao/taxas-1/emitir-taxa-de-servico-de-habilitacao/preencher-dados-da-habilitacao/34")

        self.pagina.fill(
            'xpath=//*[@id="nome-contribuinte"]',  self.dados['nome_aluno'])
        self.pagina.fill(
            'xpath=//*[@id="cpf-cnpj-contribuinte"]',  self.dados['cpf'])
        self.pagina.fill(
            'xpath=//*[@id="data-nascimento"]', self.dados['dt_nascimento'])
        self.pagina.locator(
            'xpath=//*[@id="codigo-municipio"]').select_option(self.codigo_municipio)
        time.sleep(2)
        self.pagina.locator('xpath=//*[@id="content"]/form/button').click()
        time.sleep(2)
        self.pagina.locator('xpath=//*[@id="btn-forma-pagamento-dae"]').click()

    def examedirecaorepetencia(self):
        self.pagina.goto(
            "https://transito.mg.gov.br/habilitacao/taxas-1/emitir-taxa-de-servico-de-habilitacao/preencher-dados-da-habilitacao/19")

        self.pagina.fill(
            'xpath=//*[@id="nome-contribuinte"]',  self.dados['nome_aluno'])
        self.pagina.fill(
            'xpath=//*[@id="cpf-cnpj-contribuinte"]',  self.dados['cpf'])
        self.pagina.fill(
            'xpath=//*[@id="data-nascimento"]', self.dados['dt_nascimento'])
        self.pagina.locator(
            'xpath=//*[@id="codigo-municipio"]').select_option(self.codigo_municipio)
        time.sleep(2)
        self.pagina.locator('xpath=//*[@id="content"]/form/button').click()
        time.sleep(2)
        self.pagina.locator('xpath=//*[@id="btn-forma-pagamento-dae"]').click()

    def expedicaolicendaaprendizagem(self):
        self.pagina.goto(
            "https://transito.mg.gov.br/habilitacao/taxas-1/emitir-taxa-de-servico-de-habilitacao/preencher-dados-da-habilitacao/23")

        time.sleep(.1)
        self.pagina.fill(
            'xpath=//*[@id="nome-contribuinte"]',  self.dados['nome_aluno'])
        self.pagina.fill(
            'xpath=//*[@id="cpf-cnpj-contribuinte"]',  self.dados['cpf'])
        self.pagina.fill(
            'xpath=//*[@id="data-nascimento"]', self.dados['dt_nascimento'])
        self.pagina.locator(
            'xpath=//*[@id="codigo-municipio"]').select_option(self.codigo_municipio)
        time.sleep(2)
        self.pagina.locator(
            'xpath=/html/body/main/div/div/div[1]/div/div/div[4]/div/form/button').click()
        time.sleep(2)
        self.pagina.locator('xpath=//*[@id="btn-forma-pagamento-dae"]').click()

    def cnhDefenitiva(self):
        self.pagina.goto(
            "https://transito.mg.gov.br/habilitacao/taxas-1/emitir-taxa-de-servico-de-habilitacao/preencher-dados-da-habilitacao/19?????")
        time.sleep(.1)
        self.pagina.fill(
            'xpath=//*[@id="cpf"]',  self.dados['cpf'])
        self.pagina.fill(
            'xpath=//*[@id="nome-condutor"]',  self.dados['nome_aluno'])
        self.pagina.fill(
            'xpath=//*[@id="data-nascimento"]',  self.dados['dt_nascimento'])
        time.sleep(2)
        self.pagina.locator(
            'xpath=//*[@id="content"]/form/button').click()
        time.sleep(2)
        self.pagina.locator('xpath=//*[@id="btn-forma-pagamento-dae"]').click()

    def examelegislacaorepetencia(self):
        self.pagina.goto(
            "https://transito.mg.gov.br/habilitacao/taxas-1/emitir-taxa-de-servico-de-habilitacao/preencher-dados-da-habilitacao/18")
        time.sleep(.1)
        self.pagina.fill(
            'xpath=//*[@id="nome-contribuinte"]',  self.dados['nome_aluno'])
        self.pagina.fill(
            'xpath=//*[@id="cpf-cnpj-contribuinte"]',  self.dados['cpf'])
        self.pagina.fill(
            'xpath=//*[@id="data-nascimento"]', self.dados['dt_nascimento'])
        self.pagina.locator(
            'xpath=//*[@id="codigo-municipio"]').select_option(self.codigo_municipio)

        time.sleep(2)
        self.pagina.locator('xpath=//*[@id="content"]/form/button[1]').click()

        self.pagina.locator('xpath=//*[@id="btn-forma-pagamento-dae"]').click()

        # parei pois diz que o aluno ja tem exame marcado       //*[@id="content"]/div

    def adicaocategoria(self):
        self.pagina.goto(
            "https://transito.mg.gov.br/habilitacao/taxas-1/emitir-taxa-de-servico-de-habilitacao/preencher-dados-da-habilitacao/16")
        time.sleep(.1)
        self.pagina.fill(
            'xpath=//*[@id="nome-contribuinte"]',  self.dados['nome_aluno'])
        self.pagina.fill(
            'xpath=//*[@id="cpf-cnpj-contribuinte"]',  self.dados['cpf'])
        self.pagina.fill(
            'xpath=//*[@id="data-nascimento"]', self.dados['dt_nascimento'])
        self.pagina.locator(
            'xpath=//*[@id="codigo-municipio"]').select_option(self.codigo_municipio)
        time.sleep(2)
        self.pagina.locator('xpath=//*[@id="content"]/form/button[1]').click()

        self.pagina.locator('xpath=//*[@id="btn-forma-pagamento-dae"]').click()

    def mudancacategoria(self):
        self.pagina.goto(
            "https://transito.mg.gov.br/habilitacao/taxas-1/emitir-taxa-de-servico-de-habilitacao/preencher-dados-da-habilitacao/17")
        time.sleep(.1)
        self.pagina.fill(
            'xpath=//*[@id="nome-contribuinte"]',  self.dados['nome_aluno'])
        self.pagina.fill(
            'xpath=//*[@id="cpf-cnpj-contribuinte"]',  self.dados['cpf'])
        self.pagina.fill(
            'xpath=//*[@id="data-nascimento"]', self.dados['dt_nascimento'])
        self.pagina.locator(
            'xpath=//*[@id="codigo-municipio"]').select_option(self.codigo_municipio)
        time.sleep(2)

        self.pagina.locator('xpath=//*[@id="content"]/form/button[1]').click()

        self.pagina.locator('xpath=//*[@id="btn-forma-pagamento-dae"]').click()

    def inscricaoprimeirahabiltacao(self):
        self.pagina.goto(
            "https://transito.mg.gov.br/habilitacao/taxas-1/emitir-taxa-de-servico-de-habilitacao/preencher-dados-da-habilitacao/15")
        self.pagina.fill(
            'xpath=//*[@id="nome-contribuinte"]', self.dados['nome_aluno'])
        self.pagina.fill(
            'xpath=//*[@id="cpf-cnpj-contribuinte"]',  self.dados['cpf'])
        self.pagina.fill(
            'xpath=//*[@id="data-nascimento"]', self.dados['dt_nascimento'])
        self.pagina.locator(
            'xpath=//*[@id="codigo-municipio"]').select_option(self.codigo_municipio)
        time.sleep(2)
        self.pagina.locator('xpath=//*[@id="content"]/form/button').click()
        self.pagina.locator('xpath=//*[@id="btn-forma-pagamento-dae"]').click()

    def microfilmagem(self):
        # self.pagina.locator(self.COPIAMICROFILMAGEM).click() detran mudou novamente
        self.pagina.locator(
            '//*[@id="nome-contribuinte"]',  self.nome_contribuinte)
        self.pagina.locator('//*[@id="cpf-cnpj-contribuinte"]',
                            self.cpf_cnpj_contribuinte)
        time.sleep(2)

        self.gerarDae()

    def gerarDae(self):
        self.percorreSelectByOption(
            self.codigo_municipio, '//*[@id="codigo-municipio"]')
        self.pagina.locator('//*[@id="content"]/form/button').click()
        self.pagina.locator('//*[@id="btn-forma-pagamento-dae"]').click()

    def atalhoTaxas(self):
        self.pagina.locator(self.menuTaxa).click()
        self.pagina.locator(self.emissaoTaxa).click()

    def logarDetran(self):
        self.pagina.locator(self.logindetran).click()
        self.pagina.locator(self.certificadoDigital).click()

    def on_open(self):
        app_data_path = os.getenv('LOCALAPPDATA')
        user_data_path = os.path.join(
            app_data_path, 'Google\\Chrome\\User Data\\Profile 1\\Default')

        with sync_playwright() as p:

            context = p.chromium.launch_persistent_context(
                user_data_path, channel="chrome", headless=False)
            # self.navegador = p.chromium.launch(channel="chrome", args=["--start-maximized", f"--user-agent={random_user_agent}","--disable-gpu","--disable-infobars","--log-level=2","--lang=pt-br"])

            self.pagina = context.new_page()
            self.pagina.goto(self.url)
            # self.pagina.goto(self.url+self.codigoTaxa)
            # self.pagina.goto(self.url)
            # self.logarDetran()
            # self.atalhoTaxas()
            self.openServico()
            time.sleep(self.tempo)

    def mapeamento(self):
        self.url = "https://transito.mg.gov.br/habilitacao"

        self.logindetran = 'xpath=/html/body/header/div/div[1]/div/div/div[2]/ul/li/a'
        self.certificadoDigital = 'xpath=//*[@id="cert-digital"]/button'
        self.menuTaxa = 'xpath=//*[@id="nav"]/ul/li[4]/a'
        self.emissaoTaxa = 'xpath=/html/body/main/div/div[1]/div[2]/div/div[2]/div/div[6]/ul/li[1]/a/span'
        self.INSCRICAOPARAPRIMEIRAHABILITACAO = 'xpath=//*[@id="content"]/table/tbody[2]/tr[1]/td[2]/a'
        self.MUDANCADECATEGORIA = 'xpath=//*[@id="content"]/table/tbody[2]/tr[3]/td[2]/a'
        # camila do cfc são judas passou a correta self.EXAMELEGISLREPETPRIMEIRAHABILITACAO = 'xpath=//*[@id="content"]/table/tbody[2]/tr[4]/td[2]/a'
        self.EXAMELEGISLREPETPRIMEIRAHABILITACAO = 'xpath=/html/body/main/div/div/div[1]/div/div/div[4]/div/table/tbody[2]/tr[4]/td[5]/a'

        self.EXAMEPPORTADORESDEDEFFISICA = 'xpath=//*[@id="content"]/table/tbody[2]/tr[6]/td[2]/a'
        self.OPENCNHDEFENITIVA = 'xpath=/html/body/main/div/div[1]/div[2]/div/div[2]/div/div[3]/ul/li[2]/a/span'
        self.EXPEDICAODA2aVIADAHABILITACAO = 'xpath=//*[@id="content"]/table/tbody[2]/tr[8]/td[2]/a'
        self.ALTERACAODEDADOSDAHABILITACAO = 'xpath=//*[@id="content"]/table/tbody[2]/tr[9]/td[2]/a'
        self.EXPEDICAODACARTEIRADEFINITIVA = 'xpath=//*[@id="content"]/table/tbody[2]/tr[10]/td[2]/a'
        self.RENOVACAODODOCUMENTODEHABILITACAO = 'xpath=//*[@id="content"]/table/tbody[2]/tr[11]/td[2]/a'
        self.USOINTERNODODETRANAVALPSICOLOGICA = 'xpath=//*[@id="content"]/table/tbody[2]/tr[12]/td[2]/a'
        self.USOINTERNODODETRANEXAMEMEDICO = 'xpath=//*[@id="content"]/table/tbody[2]/tr[13]/td[2]/a'
        self.EXPEDICAODASEGUNDAVIADOEXAMEMEDICO = 'xpath=//*[@id="content"]/table/tbody[2]/tr[14]/td[2]/a'
        self.REGISTRODEPRONTUARIODEESTRANGEIRO = 'xpath=//*[@id="content"]/table/tbody[2]/tr[15]/td[2]/a'

        self.REGISTROIMPDEPRONTDAPERMISSAO = 'xpath=//*[@id="content"]/table/tbody[2]/tr[17]/td[2]/a'
        self.EXPEDICAODECERTIDAOOUPRINTHABILITAC = 'xpath=//*[@id="content"]/table/tbody[2]/tr[18]/td[2]/a'
        self.COPIAMICROFILMAGEM = 'xpath=//*[@id="content"]/table/tbody[2]/tr[19]/td[2]/a'
        self.CREDENCIAMENTOOUREVALIDACAODECLINICA = 'xpath=//*[@id="content"]/table/tbody[2]/tr[20]/td[2]/a'
        self.EXAMELEGISLACAORENOVACAORECICLDACNH = 'xpath=//*[@id="content"]/table/tbody[2]/tr[21]/td[2]/a'
        self.PERMISSAOINTERNACIONALPARADIRIGIR = 'xpath=//*[@id="content"]/table/tbody[2]/tr[22]/td[2]/a'
        self.REGIMPORTACAODEPRONTUARIOCANDIDATO = 'xpath=//*[@id="content"]/table/tbody[2]/tr[23]/td[2]/a'
        self.CREDENCIAMENTOREVALANUALDESPACHANTE = 'xpath=//*[@id="content"]/table/tbody[2]/tr[24]/td[2]/a'
        self.a2VIADOCERTIFICADODIRETORINSTRUTOR = 'xpath=//*[@id="content"]/table/tbody[2]/tr[25]/td[2]/a'
        self.RELATORIOSEESTATISTICASITEM59TABD = 'xpath=//*[@id="content"]/table/tbody[2]/tr[26]/td[2]/a'

        # parametros
        self.codigoTaxa = ''
        self.nome_contribuinte = ''
        self.cpf_cnpj_contribuinte = ''
        self.documento_identificacao = ''
        self.uf_orgao_identificacao = ''
        self.uf_orgao_expedidor_identificacao = ''
        self.codigo_municipio = ''
        self.id_aluno = ''
        self.categoria_pretendida = ''
