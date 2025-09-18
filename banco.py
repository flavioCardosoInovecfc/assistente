import sqlite3


class Banco():

    def connect_bd(self):
        self.conn = sqlite3.connect("inovecfc.db")
        self.cursor = self.conn.cursor()

    def disconect_bd(self):
        self.conn.close()

    def montaTabela(self):
        self.sql = ("""
                CREATE TABLE IF NOT EXISTS automatizacao_login (
                codigo VARCHAR(20) NULL DEFAULT NULL,
                cnpj VARCHAR(20) NULL DEFAULT NULL,
                razao_social VARCHAR(100) NULL DEFAULT NULL,
                nome_funcionario VARCHAR(50) NULL DEFAULT NULL,
                usuario VARCHAR(50) NULL DEFAULT NULL,
                senha VARCHAR(15) NULL DEFAULT NULL,
                id_usuario VARCHAR(15) NULL DEFAULT NULL,
                id_estabelecimento VARCHAR(15) NULL DEFAULT NULL,
                acesso VARCHAR(20) NULL DEFAULT NULL,
                terminal VARCHAR(6) NULL DEFAULT NULL,
                uf VARCHAR(3) NULL DEFAULT NULL)
        """)
        self.executandoByQuery()

        self.sql = ("""
                CREATE TABLE IF NOT EXISTS terminal (
                terminal VARCHAR(8) NULL DEFAULT NULL)
        """)
        self.executandoByQuery()

        self.sql = ("""
                DROP TABLE inove_assistente_python;
        """)
        self.executandoByQuery()

        self.sql = ("""
                CREATE TABLE IF NOT EXISTS inove_assistente_python (
                codigo int(11) NOT NULL,
                id_estabelecimento int(11) DEFAULT '0',
                terminal int(11) DEFAULT '0',
                usuario varchar(50) DEFAULT NULL,
                dt_inicial date DEFAULT NULL,
                dt_final date DEFAULT NULL,
                user_detran varchar(50) DEFAULT NULL,
                pwd_detran varchar(50) DEFAULT NULL,
                user_inove varchar(100) DEFAULT NULL,
                pwd_inove varchar(100) DEFAULT NULL,
                acao varchar(20) DEFAULT NULL,
                detran varchar(3) DEFAULT NULL,
                dt_solicitacao datetime DEFAULT CURRENT_TIMESTAMP,
                impresso VARCHAR(1) NULL DEFAULT 'N',
                geral VARCHAR(350) DEFAULT NULL
                )
        """)
        self.executandoByQuery()

    def executandoByQuery(self):
        try:
            self.connect_bd()
            self.cursor.execute(self.sql)
            self.mySelect = self.cursor.fetchall()
            self.conn.commit()
            self.disconect_bd()
        except:
            True

    def salvarLogin(self):
        self.deleteTabela()
        self.montaTabela()
        self.sql = f'INSERT INTO automatizacao_login (codigo,cnpj, razao_social, nome_funcionario, usuario, senha, id_usuario, id_estabelecimento, acesso, terminal, uf) VALUES ("{self.infoLogin["codigo"]}","{self.infoLogin["cnpj"]}","{self.infoLogin["razao_social"]}","{self.infoLogin["nome_funcionario"]}","{self.infoLogin["usuario"]}","{self.infoLogin["senha"]}","{self.infoLogin["id_usuario"]}","{self.infoLogin["id_estabelecimento"]}","{self.infoLogin["acesso"]}","{self.infoLogin["terminal"]}","{self.infoLogin["uf"]}")'
        self.executandoByQuery()

    def salvarHasSinc(self):
        self.sql = f'INSERT INTO inove_assistente_python (codigo,id_estabelecimento, terminal, usuario, dt_inicial, dt_final, user_detran, pwd_detran,user_inove, pwd_inove,acao,detran, dt_solicitacao, impresso) VALUES ("{self.hasSinc["codigo"]}","{self.hasSinc["id_estabelecimento"]}","{self.hasSinc["terminal"]}","{self.hasSinc["usuario"]}","{self.hasSinc["dt_inicial"]}","{self.hasSinc["dt_final"]}","{self.hasSinc["user_detran"]}","{self.hasSinc["pwd_detran"]}","{self.hasSinc["user_inove"]}","{self.hasSinc["pwd_inove"]}","{self.hasSinc["acao"]}","{self.hasSinc["detran"]}","{self.hasSinc["dt_solicitacao"]}","{self.hasSinc["impresso"]}")'
        self.executandoByQuery()

    def salvarPlacas(self, placas):
        self.sql = f'DROP TABLE IF EXISTS inove_veiculos'
        self.executandoByQuery()

        self.sql = ("""
                CREATE TABLE IF NOT EXISTS inove_veiculos (
                id_grade_pratica int(4) NOT NULL,
                id_categoria int(2) NOT NULL,
                placa varchar(8) DEFAULT NULL,
                tempo_aula varchar(3) DEFAULT NULL,
                intervalo varchar(3) DEFAULT NULL
               
                )
        """)
        self.executandoByQuery()

        for placa in placas:
            if isinstance(placa, dict):
                self.sql = f'INSERT INTO inove_veiculos (placa,tempo_aula,intervalo, id_grade_pratica, id_categoria) VALUES ("{placa["placa"]}","{placa["tempo_aula"]}","{placa["intervalo"]}","{placa["id_grade_pratica"]}","{placa["id_categoria"]}")'
                self.executandoByQuery()
            else:
                self.sql = f'INSERT INTO inove_veiculos (placa,tempo_aula,intervalo, id_grade_pratica, id_categoria) VALUES ("{placas["placa"]}","{placas["tempo_aula"]}","{placas["intervalo"]}","{placas["id_grade_pratica"]}","{placas["id_categoria"]}")'
                self.executandoByQuery()

    def salvarConsultarSituacaoMG(self, consultar):
        self.sql = f'DROP TABLE IF EXISTS inove_consultar_situacao_mg'
        self.executandoByQuery()

        self.sql = ("""
                CREATE TABLE IF NOT EXISTS inove_consultar_situacao_mg (
                id_solicitacao int(11) NOT NULL,
                id_aluno int(11) NOT NULL,
                cpf varchar(15) NOT NULL, 
                observacao varchar(300) NULL
               
                )
        """)
        self.executandoByQuery()

        if len(consultar) == 1:
            self.sql = f'INSERT INTO inove_consultar_situacao_mg (id_solicitacao,id_aluno,cpf) VALUES ("{consultar["id_solicitacao"]}","{consultar["id_aluno"]}","{consultar["cpf"]}")'
            self.executandoByQuery()
        else:
            for linha in consultar:
                self.sql = f'INSERT INTO inove_consultar_situacao_mg (id_solicitacao,id_aluno,cpf) VALUES ("{linha["id_solicitacao"]}","{linha["id_aluno"]}","{linha["cpf"]}")'
                self.executandoByQuery()

    def salvarExamesMG(self, consultar):
        self.sql = f'DROP TABLE IF EXISTS inove_exames_mg'
        self.executandoByQuery()

        # self.sql = ("""
        #       CREATE TABLE IF NOT EXISTS inove_exames_mg (
        #      id_solicitacao int(11) NOT NULL,
        #     id_aluno int(11) NOT NULL,
        #    cpf varchar(15) NOT NULL,
        #   tipo_exame varchar(15) NULL,
        #  placa varchar(8) NULL,
        # local varchar(5) NULL,
        # veiculo varchar(2) NULL
        # )
        # """)

        self.sql = ("""
                CREATE TABLE IF NOT EXISTS inove_exames_mg (
                qtde int(11) NOT NULL,
                exames varchar(1000) NULL
                )
        """)
        self.executandoByQuery()

        # if len(consultar) == 7:
        #    self.sql = f'INSERT INTO inove_exames_mg (id_solicitacao,id_aluno,cpf, tipo_exame, placa, local, veiculo) VALUES ("{consultar["id_solicitacao"]}","{consultar["id_aluno"]}","{consultar["cpf"]}","{consultar["tipo_exame"]}","{consultar["placa"]}","{consultar["local"]}","{consultar["veiculo"]}")'
        #    self.executandoByQuery()
        # else:
        #    for linha in consultar:
        #        self.sql = f'INSERT INTO inove_exames_mg (id_solicitacao,id_aluno,cpf, tipo_exame, placa, local, veiculo) VALUES ("{linha["id_solicitacao"]}","{linha["id_aluno"]}","{linha["cpf"]}","{linha["tipo_exame"]}","{linha["placa"]}","{linha["local"]}","{linha["veiculo"]}")'
        #       self.executandoByQuery()

        if len(consultar) == 2:
            self.sql = f'INSERT INTO inove_exames_mg (qtde,exames) VALUES ("{consultar["qtde"]}","{consultar["exames"]}")'
            self.executandoByQuery()
        else:
            for linha in consultar:
                self.sql = f'INSERT INTO inove_exames_mg (qtde,exames) VALUES ("{linha["qtde"]}","{linha["exames"]}")'
                self.executandoByQuery()

    def updateConsultarSituacaoMG(self, observacao, id_solicitacao):
        self.sql = f'UPDATE inove_consultar_situacao_mg SET observacao = "{observacao}" WHERE id_solicitacao ="{id_solicitacao}"'
        self.executandoByQuery()
        return True

    def salvarAulas(self, aulas):
        self.sql = f'DROP TABLE IF EXISTS inove_presenca_pratica'
        self.executandoByQuery()

        self.sql = ("""
                CREATE TABLE IF NOT EXISTS inove_presenca_pratica (
                id_presenca_pratica int(11) NOT NULL,
                id_aluno int(11) NOT NULL,
                id_categoria int(2) NOT NULL,
                id_grade_pratica int(4) NOT NULL,
                dataAula varchar(11) DEFAULT NULL,
                horaAula varchar(6) DEFAULT NULL,
                placa varchar(8) DEFAULT NULL,
                processo varchar(11) DEFAULT NULL,
                dt_aula_pratica datetime DEFAULT CURRENT_TIMESTAMP,
                motopista varchar(5) DEFAULT NULL,
                categoria varchar(2) DEFAULT NULL
                )
        """)
        self.executandoByQuery()

        for placa in aulas:
            try:
                self.sql = f'INSERT INTO inove_presenca_pratica (id_presenca_pratica,id_aluno,id_categoria, id_grade_pratica, dataAula, horaAula, placa,processo,dt_aula_pratica, motopista, categoria) VALUES ("{placa["id_presenca_pratica"]}","{placa["id_aluno"]}","{placa["id_categoria"]}","{placa["id_grade_pratica"]}","{placa["dataAula"]}","{placa["horaAula"]}","{placa["placa"]}","{placa["processo"]}","{placa["dt_aula_pratica"]}","{placa["motopista"]}","{placa["categoria"]}")'
                self.executandoByQuery()
            except:
                placa = aulas
                self.sql = f'INSERT INTO inove_presenca_pratica (id_presenca_pratica,id_aluno,id_categoria, id_grade_pratica, dataAula, horaAula, placa,processo,dt_aula_pratica, motopista, categoria) VALUES ("{placa["id_presenca_pratica"]}","{placa["id_aluno"]}","{placa["id_categoria"]}","{placa["id_grade_pratica"]}","{placa["dataAula"]}","{placa["horaAula"]}","{placa["placa"]}","{placa["processo"]}","{placa["dt_aula_pratica"]}","{placa["motopista"]}","{placa["categoria"]}")'
                self.executandoByQuery()

    def salvarTerminal(self):
        self.sql = f'INSERT INTO terminal (terminal) VALUES ("{self.IdTerminal}")'
        self.executandoByQuery()

    def hasLogin(self):
        self.sql = f'select usuario, senha, cnpj from automatizacao_login where terminal={self.IdTerminal}'
        self.executandoByQuery()

    def getPlacas(self):
        self.sql = f"select * from inove_veiculos order by id_categoria asc"
        self.executandoByQuery()
        return self.mySelect

    def getPlacasMG(self):
        self.sql = f"select placa from inove_exames_mg group by placa"
        self.executandoByQuery()
        return self.mySelect

    def getConsultaSituacao(self):
        self.sql = f"select * from inove_consultar_situacao_mg order by id_solicitacao asc"
        self.executandoByQuery()
        return self.mySelect

    def getExamesMG(self):
        self.sql = f"select * from inove_exames_mg order by qtde desc"
        self.executandoByQuery()
        return self.mySelect

    def getLista(self):
        self.sql = f'delete from inove_assistente_python where  strftime("%Y-%m-%d",dt_solicitacao) <= date( "now", "-1 day")'
        self.executandoByQuery()

        self.sql = f'select usuario, strftime("%d/%m/%Y", dt_inicial),  strftime("%d/%m/%Y",dt_solicitacao), acao from inove_assistente_python'
        self.executandoByQuery()
        return self.mySelect

    def checkAulasSeguidas(self, dataInicial, dataFinal, id_categoria, id_grade_pratica):
        query = f'SELECT p.id_presenca_pratica, p.id_aluno, p.dt_aula_pratica'
        query += ' FROM inove_presenca_pratica p '
        query += ' WHERE p.dt_aula_pratica BETWEEN "' + \
            dataInicial+'" AND "'+dataFinal + '" '
        query += ' AND p.id_categoria =   ' + str(id_categoria)
        query += ' AND p.id_grade_pratica = ' + str(id_grade_pratica)
        query += ' ORDER BY p.dt_aula_pratica'
        if id_categoria == 1:
            query += ' limit 1'
        self.sql = query
        self.executandoByQuery()
        return self.mySelect

    def getAulasByPlaca(self, dt_inicial, placa):
        query = f'SELECT  * '
        query += ' FROM inove_presenca_pratica p'
        query += ' WHERE p.dt_aula_pratica BETWEEN "' + \
            dt_inicial + ' 00:01:00" AND "'+dt_inicial+' 23:59:00"'
        query += ' AND p.placa = "' + placa+'"'
        query += ' ORDER BY p.dt_aula_pratica'
        self.sql = query
        self.executandoByQuery()
        return self.mySelect

    def hasTokenTerminal(self):
        self.sql = f'select terminal from terminal'
        self.executandoByQuery()
        return self.mySelect

    def deleteTabela(self):
        self.sql = f'DROP TABLE IF EXISTS automatizacao_login'
        self.executandoByQuery()
