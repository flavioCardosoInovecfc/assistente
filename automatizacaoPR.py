import os
import sys
import requests
import time
from datetime import datetime, timedelta
from playwright.sync_api import sync_playwright
from playwright_stealth import stealth
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
            print("######   Senha não localizada                             ######")
            print("######   Pressione CTRL+F5 na grade prática convencional   ######")

    # Helper robusto para obter o iframe 'content'
    def _get_target_frame(self, timeout_ms: int = 10000):
        import time
        page = self.pagina
        end = time.time() + timeout_ms / 1000.0
        while time.time() < end:
            fr = page.frame(name="content")
            if fr:
                return fr
            el = page.query_selector(
                'iframe[name="content"], iframe#content, frame[name="content"]')
            if el:
                try:
                    fr = el.content_frame()
                    if fr:
                        return fr
                except Exception:
                    pass
            time.sleep(0.2)
        return None

    def on_open(self):
        # --- User-Agents realistas ---
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_5_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Linux; Android 12; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.5993.89 Mobile Safari/537.36"
        ]
        random_user_agent = random.choice(user_agents)

        # --- Args do Chrome (corrigido --disable-features em um único argumento) ---
        args = [
            f"--user-agent={random_user_agent}",
            "--disable-infobars",
            "--log-level=2",
            "--lang=pt-BR",
            "--disable-webgl",
            "--disable-blink-features=AutomationControlled",
            "--disable-client-side-phishing-detection",
            "--disable-features=IsolateOrigins,site-per-process,PasswordLeakDetection,PasswordManagerOnboarding,AutofillServerCommunication,CredentialManager",
            "--disable-save-password-bubble",
            "--no-first-run",
            "--no-default-browser-check",
            "--password-store=basic",
        ]

        # --- Base dir da app (PyInstaller-friendly) ---
        BASE_DIR = sys._MEIPASS if getattr(
            sys, 'frozen', False) else os.path.dirname(os.path.abspath(__file__))
        os.environ["PLAYWRIGHT_BROWSERS_PATH"] = os.path.join(
            BASE_DIR, "playwright_stealth/js")

        # --- Perfil persistente dedicado da automação ---
        user_data_dir = os.path.join(BASE_DIR, "chrome-profile")
        default_dir = os.path.join(user_data_dir, "Default")
        os.makedirs(default_dir, exist_ok=True)

        # --- Preferências: desativa Password Manager e Leak Detection (remove o alerta do Chrome) ---
        prefs_path = os.path.join(default_dir, "Preferences")
        prefs = {}
        if os.path.exists(prefs_path):
            try:
                with open(prefs_path, "r", encoding="utf-8") as f:
                    prefs = json.load(f)
            except Exception:
                prefs = {}

        prefs.setdefault("profile", {})
        prefs["profile"]["password_manager_enabled"] = False
        prefs["profile"]["password_manager_leak_detection"] = False
        # não oferecer salvar senhas
        prefs["credentials_enable_service"] = False

        with open(prefs_path, "w", encoding="utf-8") as f:
            json.dump(prefs, f, ensure_ascii=False)

        # --- Lança o Chrome com perfil persistente ---
        with sync_playwright() as p:
            self.context = p.chromium.launch_persistent_context(
                user_data_dir,     # raiz do perfil (NÃO inclua /Default)
                channel="chrome",
                headless=False,
                args=args
            )
            self.pagina = self.context.new_page()
            # Evita travar em alert()/confirm() e aplica stealth
            try:
                self.pagina.on("dialog", lambda d: d.dismiss())
            except Exception:
                pass
            try:
                stealth(self.pagina)
            except Exception:
                pass

            try:
                self.pagina.goto(self.url, wait_until="domcontentloaded")
                acesso = self.fazLogin()
                if acesso == "OK":
                    print(
                        f"**** Iniciando o envio da placa {self.placaCFC} ****")
                    self.menu()
                    self.startSinc()
                    print(f"**** Fim do envio da placa {self.placaCFC} ****")
                else:
                    self.acessoDetran = False
                    self.acessoNegado()
            except Exception as e:
                print("##### Perda de comunicação #####")
                print(repr(e))
            finally:
                # encerra o contexto corretamente (Playwright não tem quit())
                try:
                    self.context.close()
                except Exception:
                    pass

        time.sleep(1)

    def acessoNegado(self):
        requests.get(
            "https://" + self.siteInoveCFC +
            "/sistemas/python/detranpr/acessoNegadoDetran.php?usuario=" +
            self.hasSinc['user_inove'],
            verify=self.verificaSSL
        )
        print("###   Sistema identificou que o acesso ao Detran-PR foi alterado. ####")

    def fazLogin(self):
        page = self.pagina
        # evita alert()/confirm() travando
        try:
            page.on("dialog", lambda d: d.dismiss())
        except Exception:
            pass
        page.wait_for_load_state("domcontentloaded", timeout=20000)

        # 1) obtém o iframe 'content'; se não houver, usa a própria página
        target = self._get_target_frame(timeout_ms=10000) or page
        self.myFrame = target  # mantém compatível com o restante do seu fluxo

        # 2) Preenche os campos (com espera) e clica
        try:
            self.myFrame.locator(self.input_user).wait_for(
                state="visible", timeout=15000)
            self.myFrame.fill(
                self.input_user, self.hasSinc['user_detran'], timeout=12000)

            self.myFrame.locator(self.input_pwd).wait_for(
                state="visible", timeout=15000)
            self.myFrame.fill(
                self.input_pwd, self.hasSinc['pwd_detran'], timeout=12000)

            self.myFrame.locator(self.botao_entrar).click(timeout=15000)

            # 3) Aguardar rede estabilizar e reobter frame (caso recarregue)
            page.wait_for_load_state("networkidle", timeout=20000)
            self.myFrame = self._get_target_frame(timeout_ms=6000) or page

            # 4) Mantém sua lógica original
            return self.verificaLogin()

        except Exception as e:
            # debug útil caso algo mude na página
            ts = int(time.time())
            try:
                page.screenshot(path=f"erro_login_{ts}.png")
                with open(f"erro_login_{ts}.html", "w", encoding="utf-8") as f:
                    f.write(page.content())
            except Exception:
                pass
            print(f"[LOGIN] Falhou: {e!r}")
            self.acessoDetran = False
            self.acessoNegado()
            return "FAIL"

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
                # Gera um valor aleatório entre 1 e 3
                tempo_aleatorio = round(random.uniform(1, 3), 1)
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
                                erro = self.verificaMSGMarcacao(str(aula[1]))
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
            'xpath=//*[@id="msg_ajax"]/table/tbody/tr/td[2]').text_content()
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
        e = "placa " + placa + " não localizada"
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
                elemt = self.myFrame.locator(self.msg1).text_content()
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
        duracao = timedelta(hours=horas, minutes=minutos, seconds=segundos)
        termino = hora_inicio + duracao
        if termino.hour == 0:
            termino = datetime.strptime("23:59:00", "%H:%M:%S")

        return termino.strftime('%H:%M:%S')

    def verificaQuantidadeAulasSeguidas(self, row, tempo_aula, intervalo, id_categoria):
        duracao_aula = (int(tempo_aula) + int(intervalo))

        if duracao_aula < 60:
            duracao_aula = "00:" + str(duracao_aula) + ":00"
        elif duracao_aula == 60:
            duracao_aula = "01:00:00"

        dataInicial = row[8]
        dataFinal = self.hasSinc['dt_inicial'] + " " + \
            self.somaHora(row[5] + ":00", "04:00:00")
        id_aluno = row[1]

        hI = dataInicial.replace(':', '').split(' ')
        hF = dataFinal.replace(':', '').split(' ')

        if hF[1] < hI[1]:
            dataFinal = hF[0] + " 23:59:00"

        id_grade_pratica = row[3]

        sequencia = self.checkAulasSeguidas(
            dataInicial, dataFinal, id_categoria, id_grade_pratica
        )

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
                        ids += ',' + str(linha[0])
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
            '() => abrirUrl("https://www.habilitacao.detran.pr.gov.br:443/detran-habilitacao/agendarVeiculoAluno.do?action=iniciarProcesso")'
        )

    def _send_iframe(self, obj):
        # sleep(0.1)
        self.browser.switch_to.frame(self.browser.find_element(*obj))

    def verificaLogin(self):
        try:
            # self.myFrame.locator('//*[@id="overlay"]/div/button').click()
            self.myFrame.locator(
                'xpath=//*[@id="conteudo_corpo"]/div/table/tbody/tr/td[1]/table/tbody/tr[1]/td/img'
            ).click()
            return "OK"
        except:
            return "Senha incorreta"

    def gravarByInoveCFC(self, msg, id, intintegracao="0"):
        tabela = 'inove_presenca_pratica'
        where = " id_presenca_pratica in (" + id + ")"

        if intintegracao != "0":
            campos = ("int_agenda", "erroSinc")
            data = (intintegracao, "")
        else:
            campos = ('erroSinc')
            data = (msg)

        request = requests.get(
            "https://" + self.siteInoveCFC +
            "/sistemas/python/detranpr/gravarByInoveCFC.php?user="
            + self.hasSinc['user_inove'] + "&pwd=" + self.hasSinc['pwd_inove']
            + "&id_presenca_pratica=" + id +
            "&intintegracao=" + str(intintegracao)
            + "&msg=" + msg + "&funcionario=" + self.hasSinc['usuario'],
            verify=self.verificaSSL
        )
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
