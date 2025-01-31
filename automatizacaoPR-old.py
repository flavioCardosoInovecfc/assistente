
import os
import requests
import time
from datetime import datetime, timedelta
from playwright.sync_api import sync_playwright
import random
import json

from banco import *


class AutomatizacaoPR(Banco):

    def iniciar(self, informacao, verificaSSL, siteInoveCFC):
        self.siteInoveCFC = siteInoveCFC
        self.hasSinc = informacao
        self.user_inove = informacao['user_inove']
        self.verificaSSL = verificaSSL
        self.acessoDetran = True
        self.mapeamento()
        if (self.hasSinc['pwd_detran']):
            self.getPlacasByCFC()
        else:
            print("######   Senha não localizada                              ######")
            print("######   Pressione CTRL+F5 na grade prática convencional   ######")

    def on_open(self):

        user_agents = [
            "Mozilla/5.0 (Android 12; Mobile; rv:121.0) Gecko/121.0 Firefox/121.0",
            "Mozilla/5.0 (iPhone; CPU iPhone OS 16_1_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Mobile/15E148 Safari/604.1",
            "Mozilla/5.0 (iPhone; CPU iPhone OS 16_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/120.0.6099.119 Mobile/15E148 Safari/604.1",
            "Mozilla/5.0 (iPhone; CPU iPhone OS 16_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/120.0.6099.119 Mobile/15E148 Safari/604.1",
            "Mozilla/5.0 (iPhone; CPU iPhone OS 16_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) GSA/298.0.595435837 Mobile/15E148 Safari/604.1",
            "Mozilla/5.0 (iPhone; CPU iPhone OS 16_3_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.3 Mobile/15E148 Safari/604.1",
            "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1",
            "Mozilla/5.0 (iPhone; CPU iPhone OS 16_7 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/120.0.6099.119 Mobile/15E148 Safari/604.1",
            "Mozilla/5.0 (iPhone; CPU iPhone OS 16_7_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1",
            "Mozilla/5.0 (iPhone; CPU iPhone OS 16_7_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1",
            "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) GSA/298.0.595435837 Mobile/15E148 Safari/604.1",
            "Mozilla/5.0 (iPhone; CPU iPhone OS 17_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/120.0.6099.119 Mobile/15E148 Safari/604.1",
            "Mozilla/5.0 (iPhone; CPU iPhone OS 17_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) GSA/298.0.595435837 Mobile/15E148 Safari/604.1",
            "Mozilla/5.0 (iPhone; CPU iPhone OS 17_1_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1.1 Mobile/15E148 Safari/604.1",
            "Mozilla/5.0 (iPhone; CPU iPhone OS 17_1_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1.2 Mobile/15E148 Safari/604.1",
            "Mozilla/5.0 (iPhone; CPU iPhone OS 17_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/120.0.6099.119 Mobile/15E148 Safari/604.1",
            "Mozilla/5.0 (iPhone; CPU iPhone OS 17_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) GSA/298.0.595435837 Mobile/15E148 Safari/604.1",
            "Mozilla/5.0 (iPhone; CPU iPhone OS 17_2_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1",
            "Mozilla/5.0 (iPhone; CPU iPhone OS 17_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3 Mobile/15E148 Safari/604.1",
            "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Mobile Safari/537.36",
            "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Mobile Safari/537.36",
            "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Mobile Safari/537.36",
            "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Mobile Safari/537.36",
            "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
            "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36 EdgA/120.0.0.0",
            "Mozilla/5.0 (Linux; Android 13; SAMSUNG SM-A225M) AppleWebKit/537.36 (KHTML, like Gecko) SamsungBrowser/23.0 Chrome/115.0.0.0 Mobile Safari/537.36",
            "Mozilla/5.0 (Linux; Android 13; SAMSUNG SM-M236B) AppleWebKit/537.36 (KHTML, like Gecko) SamsungBrowser/23.0 Chrome/115.0.0.0 Mobile Safari/537.36",
            "Mozilla/5.0 (Linux; U; Android 10; pt-br; Redmi Note 8 Pro Build/QP1A.190711.020) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/112.0.5615",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Safari/605.1.15",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.6.1 Safari/605.1.15",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Safari/605.1.15",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1.2 Safari/605.1.15",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2.1 Safari/605.1.15",
            "Mozilla/5.0 (Windows NT 10.0; rv:121.0) Gecko/20100101 Firefox/121.0",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Avast/120.0.0.0",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
            "Mozilla/5.0 (Windows NT 6.1; rv:109.0) Gecko/20100101 Firefox/115.0",
            "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0",
            "Mozilla/5.0 (Windows NT 6.3; rv:109.0) Gecko/20100101 Firefox/115.0",
            "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36 Edg/109.0.1518.140",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        ]

        random_user_agent = random.choice(user_agents)
        app_data_path = os.getenv('LOCALAPPDATA')
        user_data_path = os.path.join(
            app_data_path, 'Google\\Chrome\\User Data\\Profile 1\\Default')

        with sync_playwright() as p:

            # self.context = p.chromium.launch_persistent_context(user_data_path, channel="chrome", headless=False, args=[f"--user-agent={random_user_agent}",
            #                                                                                                            "--start-maximized", "--disable-gpu", "--disable-infobars", "--log-level=2", "--lang=pt-br", "--no-first-run", "--no-session-restore"])
            self.context = p.chromium.launch_persistent_context(user_data_path, channel="chrome", headless=True, args=[f"--user-agent={random_user_agent}",
                                                                                                                       "--window-position=-1000,-1000", "--window-size=50,50", "--disable-infobars", "--log-level=2",
                                                                                                                       "--lang=pt-br", "--disable-webgl", "--enable-ipv6"
                                                                                                                       ])
            # self.navegador = p.chromium.launch(channel="chrome", args=["--start-maximized", f"--user-agent={random_user_agent}","--disable-gpu","--disable-infobars","--log-level=2","--lang=pt-br"])
            # context = self.navegador.new_context(no_viewport=True)

            self.pagina = self.context.new_page()

            try:
                self.pagina.goto(self.url)
                acesso = self.fazLogin()
                if acesso == "OK":
                    print(
                        f"**** Iniciando o envio da placa {self.placaCFC} ****")
                    self.menu()
                    self.startSinc()
                    print(
                        f"**** Fim do envio da placa {self.placaCFC} ****")
                else:
                    self.acessoDetran = False
                    self.acessoNegado()
                    self.context.close()
                    self.context.quit()

            except:
                print("#####    Perda de comunicação     #####")

        time.sleep(2)

    def acessoNegado(self):
        requests.get("https://"+self.siteInoveCFC+"/sistemas/python/detranpr/acessoNegadoDetran.php?usuario=" +
                     self.hasSinc['user_inove'], verify=self.verificaSSL)

        print("###   Sistema identificou que o acesso ao Detran-PR foi alterado. ####")

    def fazLogin(self):

        self.myFrame = self.pagina.frame("content")
        self.myFrame.fill(self.input_user, self.hasSinc['user_detran'])
        self.myFrame.fill(self.input_pwd, self.hasSinc['pwd_detran'])
        self.myFrame.locator(self.botao_entrar).click()
        time.sleep(1)
        return self.verificaLogin()

    def getPlacasByCFC(self):
        self.contador = 0
        placas = self.getPlacas()

        for placa in placas:
            results = self.getAulasByPlaca(
                self.hasSinc['dt_inicial'], placa[2])
            if results:
                if (self.acessoDetran):
                    self.tempo_aula = placa[3]
                    self.intervalo = placa[4]
                    self.id_categoria = placa[1]
                    self.placaCFC = placa[2]
                    self.on_open()

        print("####    FIM    ####")

    def startSinc(self):

        results = self.getAulasByPlaca(
            self.hasSinc['dt_inicial'], self.placaCFC)
        id_aluno = 0

        for row in results:
            erro = False
            if row[10] == "A":
                id_aluno = 0

            if id_aluno != row[1]:
                processo = row[7]
                codMotoPista = row[9]
                id_aluno = row[1]
                # Gera um valor aleatório entre 2 e 10
                tempo_aleatorio = round(random.uniform(4, 8), 1)
                # Pausa o programa por esse tempo aleatório
                time.sleep(tempo_aleatorio)
                aula = self.verificaQuantidadeAulasSeguidas(
                    row, self.tempo_aula, self.intervalo, self.id_categoria)

                self.informarProcesso(processo)

                valor = self.myFrame.locator(
                    self.input_numeroProcesso).input_value()
                if (valor):
                    erro = self.verificaMSG(str(aula[1]))
                else:
                    erro = True

                if erro == False:
                    idIntergracao = self.gerarNumeroRandomico()
                    dataAula = row[4]
                    horaAula = row[5]
                    id_aluno = row[1]
                    id_presenca_pratica = row[0]
                    placa = row[6]
                    categoria = row[10]
                    qtdeAula = aula[0]
                    self.contador = self.contador + 1
                    contador = self.contador
                    categoriaSelecionada = ''

                    print(str(contador) + "-Enviando: "+dataAula + " " +
                          horaAula + " | placa: " + placa + " | processo: " + processo + " | Espera: " + str(tempo_aleatorio))

                    erro = self.hasMaisCategoria()

                    if erro == True:
                        erro = self.setaCategoriaByAB(categoria)
                        categoriaSelecionada = categoria
                    else:
                        categoriaSelecionada = self.myFrame.locator(
                            self.hasHiden).input_value()

                    erro = self.verificaMSG(str(aula[1]))

                    if categoriaSelecionada != categoria:
                        mens = "Categoria a ser marcada " + categoria + \
                            " mas quando informado o processo setou categoria " + categoriaSelecionada
                        print(mens)
                        self.gravarByInoveCFC(mens, str(aula[1]))
                        erro = True

                    if erro == False:
                        erro = self.setaPlaca(placa)
                        self.adicionarNovaAula()

                        self.preencherMarcacaoAula(
                            qtdeAula, dataAula, horaAula, categoria, codMotoPista)

                        self.botaoGravar()

                        erro = self.verificaMSGMarcacao(str(aula[1]))
                        if erro == False:
                            erro = self.verificaMSGMarcacao(str(aula[1]))
                            if erro == False:
                                self.salvarAula(aula[1], idIntergracao)
                            elif erro == "novamente":
                                self.botaoGravar()
                                erro = self.verificaMSGMarcacao(
                                    str(aula[1]))
                                if erro == False:
                                    self.salvarAula(aula[1], idIntergracao)
                                else:
                                    self.botaoCancelar()
                            else:
                                self.botaoCancelar()
                        elif erro == 'novamente':  # aqui se for categoria de moto
                            self.botaoGravar()
                            erro = self.verificaMSGMarcacao(str(aula[1]))
                            if erro == False:
                                self.salvarAula(aula[1], idIntergracao)
                            else:
                                self.botaoCancelar()
                        elif erro == True:
                            self.botaoCancelar()

                    else:
                        self.myFrame.locator(self.btnVoltar).click()
                        # self.menu()
                else:
                    self.myFrame.locator(self.btnVoltar).click()
                    self.menu()

    def botaoCancelar(self):
        self.pop.locator(self.btnCancelar).click()
        self.novoRegistro()

    def novoRegistro(self):
        self.menu()

    def salvarAula(self, aula, idIntergracao):

        self.gravarByInoveCFC("", aula, idIntergracao)

        self.novoRegistro()

    def verificaMSGMarcacao(self, ids):

        elemt = self.pop.locator(
            'xpath=//*[@id="msg_ajax"]/table/tbody/tr/td[2]') .text_content()
        msg = elemt.lower()
        if 'realizada com sucesso' in msg:
            return False
        elif 'vagas' in msg:
            return "novamente"
        else:
            print(msg)
            self.gravarByInoveCFC(elemt, ids)
            return True

    def preencherMarcacaoAula(self, qtdeAula, dataAula, horaAula, categoria, codMotoPista):
        self.pop = self.myFrame.frame_locator('xpath=//*[@id="popupFrame"]')
        self.pop.locator(self.selectByCurso).select_option("PRATICO")
        qtde = self.pop.locator(self.input_QtdeAula)
        qtde.fill(qtdeAula)

        qtde.evaluate(
            '() => document.getElementById("dataInicio").value = "'+dataAula+'"')
        qtde.evaluate(
            '() => document.getElementById("horaInicio").value = "'+horaAula+'"')

        if categoria == "A":
            self.pop.locator(self.selectMotoPista).select_option(codMotoPista)

    def botaoGravar(self):
        self.pop.locator(self.botaoGravarAula).click()

    def adicionarNovaAula(self):
        self.myFrame.locator(self.calendario).click()
        self.myFrame.evaluate('() => adicionar()')

    def verificaHiddenProcesso(self):
        e = False
        try:
            elemt = self.myFrame.get_by_alt_text(self.hasHiddenProcesso)
            msg = elemt.text.lower()
            e = False
        except:
            e = True

        return e

    def hasMaisCategoria(self):
        e = False
        time.sleep(.2)
        if (self.myFrame.locator(self.selectByCategoria).count() > 0):
            e = True

        return e

    def setaCategoriaByAB(self, categoria):
        e = False
        try:
            self.myFrame.locator(
                self.selectByCategoria).select_option(categoria)
            self.myFrame.locator(self.botao_select_categoria).click()
            e = True
        except:
            e = False

        return e

    def setaPlaca(self, placa):
        e = "placa "+placa + " não localizada"
        optionToSelect = self.myFrame.locator(self.selectByPlaca)
        optionToSelect = optionToSelect.filter(has_text=placa)
        options_txt = optionToSelect.text_content()
        options = options_txt.split('\n')
        full_label = ""
        for item in options:
            if placa in item:
                full_label = item.strip()
        if full_label:
            self.myFrame.locator(self.selectByPlaca).select_option(full_label)
            e = False

        return e

    def gerarNumeroRandomico(self):
        return random.randrange(1000000, 10000000)

    def verificaMSG(self, ids):
        time.sleep(.2)
        try:

            if (self.myFrame.locator(self.msg1).count() > 0):
                elemt = self.myFrame.locator(self.msg1) .text_content()
                msg = elemt.lower()
                if 'não realizou' in msg:
                    self.gravarByInoveCFC(elemt, ids)
                elif 'operação não autorizada' in msg:
                    self.gravarByInoveCFC(elemt, ids)
                elif 'coleta biométria' in msg:
                    self.gravarByInoveCFC(elemt, ids)
                elif 'não concluiu os exames' in msg:
                    self.gravarByInoveCFC(elemt, ids)
                elif 'aula não pode ocorrer entre' in msg:
                    self.gravarByInoveCFC(elemt, ids)

                print(elemt)
                return True
            else:
                return False
        except:
            return False

    def informarProcesso(self, processo):
        self.myFrame.fill(self.input_numeroProcesso, processo)
        self.myFrame.locator(self.botao_pesquisa).click()

    def somaHora(self, time_str, duracao="02:00:00"):
        hora_inicio = datetime.strptime(time_str, "%H:%M:%S")
        horas, minutos, segundos = map(int, duracao.split(':'))
        # transforma a string em timedelta
        duracao = timedelta(hours=horas, minutes=minutos, seconds=segundos)
        termino = hora_inicio + duracao
        if termino.hour == 0:
            termino = datetime.strptime("23:59:00", "%H:%M:%S")

        return termino.strftime('%H:%M:%S')

    def verificaQuantidadeAulasSeguidas(self, row, tempo_aula, intervalo, id_categoria):

        duracao_aula = (int(tempo_aula) + int(intervalo))

        if duracao_aula < 60:
            duracao_aula = "00:"+str(duracao_aula)+":00"
        elif duracao_aula == 60:
            duracao_aula = "01:00:00"

        dataInicial = row[8]
        dataFinal = self.hasSinc['dt_inicial']+" " + \
            self.somaHora(row[5]+":00", "04:00:00")
        id_aluno = row[1]

        hI = dataInicial.replace(':', '').split(' ')
        hF = dataFinal.replace(':', '').split(' ')

        if hF[1] < hI[1]:
            dataFinal = hF[0]+" 23:59:00"

        id_grade_pratica = row[3]

        sequencia = self.checkAulasSeguidas(
            dataInicial, dataFinal, id_categoria, id_grade_pratica)

        i = 0
        ids = ""
        for linha in sequencia:
            i = i + 1
            t = linha[2].split(' ')
            if i == 1:
                proximaaula = self.somaHora(t[1], duracao_aula)
                ids = str(linha[0])
            else:
                if id_aluno == linha[1]:
                    if self.hasProximaAula(proximaaula, t[1]):
                        proximaaula = self.somaHora(t[1], duracao_aula)
                        ids += ','+str(linha[0])
                    else:
                        i = i - 1
                        break
                else:
                    i = i - 1
                    break

        return (str(i), ids)

    def hasProximaAula(self, proxima, hora):

        if proxima == hora:
            return True
        else:
            return False

    def menu(self):
        # self.myFrame.locator(self.oCMenu1136).click()
        # self.myFrame.locator(self.oCMenu203).click()
        # self.myFrame.locator(self.oCMenu1139).click()
        self.myFrame.evaluate(
            '() => abrirUrl("https://www.habilitacao.detran.pr.gov.br:443/detran-habilitacao/agendarVeiculoAluno.do?action=iniciarProcesso")')

    def _send_iframe(self, obj):
        # sleep(0.1)
        self.browser.switch_to.frame(self.browser.find_element(*obj))

    def verificaLogin(self):
        try:
            # self.myFrame.locator('//*[@id="overlay"]/div/button').click()

            self.myFrame.locator(
                'xpath=//*[@id="conteudo_corpo"]/div/table/tbody/tr/td[1]/table/tbody/tr[1]/td/img').click()
            return "OK"
        except:
            return "Senha incorreta"

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

    def mapeamento(self):
        self.url = "https://www.habilitacao.detran.pr.gov.br/detran-habilitacao/"

        self.iframe = ('xpath=/html/frameset')
        self.iframe_form = ('xpath=/html/frameset/frame')
        self.input_user = ('xpath=//*[@id="CHAVE"]')
        self.input_pwd = ('xpath=//*[@id="CHAVE_ENCRIPT"]')
        self.btnVoltar = ('xpath=//*[@id="conteudo_corpo"]/div[2]/input[2]')
        self.botao_entrar = (
            'xpath=//*[@id="formLogin"]/table/tbody/tr[1]/td/table/tbody/tr[3]/td[2]/input')
        self.oCMenu1136 = ('xpath=//*[@id="oCMenu__1136"]')
        self.oCMenu203 = ('xpath=//*[@id="oCMenu__188"]')
        self.oCMenu1139 = ('xpath=//*[@id="oCMenu__1139"]')
        self.oCMenu1951 = ('xpath=//*[@id="oCMenu__1951"]')
        self.msg1 = ('xpath=//*[@id="msg"]/table/tbody/tr/td[2]')
        self.input_numeroProcesso = (
            'xpath=//*[@id="conteudo_corpo"]/table/tbody/tr[2]/td[2]/input')
        self.botao_pesquisa = (
            'xpath=//*[@id="conteudo_corpo"]/div[2]/input[1]')
        self.hasHiddenProcesso = (
            'xpath=//*[@id="conteudo_corpo"]/table/tbody/tr[2]/td[2]/input')
        self.fecharPop = ('xpath=//*[@id="popCloseBox"]')
        self.hasHiden = (
            'xpath=//*[@id="conteudo_corpo"]/table/tbody/tr[3]/td[2]/input')
        self.selectByCategoria = (
            'xpath=//*[@id="conteudo_corpo"]/table/tbody/tr[3]/td[2]/select')
        self.botao_select_categoria = (
            'xpath=//*[@id="conteudo_corpo"]/div[2]/input[1]')
        self.selectByPlaca = (
            'xpath=//*[@id="conteudo_corpo"]/table[2]/tbody/tr[1]/td[2]/select')
        self.calendario = ('xpath=//*[@id="minical"]/tbody/tr[4]/td[4]/a')
        self.barra_paginacao = (
            'xpath=//*[@id="barra_paginacao"]/tbody/tr/td[1]/a')
        self.selectByCurso = (
            'xpath=//*[@id="conteudo_corpo"]/table/tbody/tr[1]/td[2]/select')
        self.iframe_MarcacaoAula = ('xpath=//*[@id="popupFrame"]')
        self.input_QtdeAula = (
            'xpath=//*[@id="conteudo_corpo"]/table/tbody/tr[1]/td[4]/input')
        self.input_horaAula = ('xpath=//*[@id="horaInicio"]')
        self.selectMotoPista = (
            'xpath=//*[@id="conteudo_corpo"]/table/tbody/tr[3]/td[2]/select')
        self.botaoGravarAula = (
            'xpath=//*[@id="conteudo_corpo"]/div[3]/input[1]')
        self.msgGravarAula = (
            'xpath=/html/body/div[2]/div[1]/div[1]/table/tbody/tr/td[2]')
        self.btnCancelar = ('xpath=//*[@id="conteudo_corpo"]/div[3]/input[2]')
        self.msgUltima = ('xpath=//*[@id="msg"]/table/tbody/tr/td[2]')
        self.msgAviso = (
            'xpath=/html/body/div[19]/div/div[2]/table/tbody/tr/td[2]')
