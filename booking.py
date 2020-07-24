import fdb
import math
import helper
from configuracao import Configuracao


class Booking(object):

    def __init__(self, item):
        self.salao_cliente_id = item['salao_cliente_id'] if item['salao_cliente_id'] != None else ""
        self.servico_id = item['servico_id'] if item['servico_id'] != None else ""
        self.profissional_id = item['profissional_id'] if item['profissional_id'] != None else ""
        self.hora_ini = item['hora_ini'] if item['hora_ini'] != None else ""
        self.hora_fim = item['hora_fim'] if item['hora_fim'] != None else ""
        self.data = item['data'] if item['data'] != None else ""
        self.status = item['status'] if item['status'] != None else ""
        self.servicos = item['servicos'] if item['servicos'] != None else ""
        self.id = item['id'] if item['id'] != None else ""
        self.nome_cliente = item['cliente_nome'] if item['cliente_nome'] != None else ""
        self.preferencia = item['profissional_indiferente'] if item['profissional_indiferente'] != None else ""
        self.configuracao = Configuracao()

    def converte_hora(self, data):
        #svip -> teles
        v_hora = math.floor((data / 60))* 100
        v_min = '%02d' % (data % 60)
        return int(v_hora) + int(v_min)

    def display_hora(self, hora):
        #Ex: 600 = 6:00 / 1800 = 18:00
        minuto = (int(hora) % 100)
        hora =  math.floor(int(hora) / 100)
        # Modificado pois a Auditoria_Agenda ainda usa um tipo TTime.
        if hora == 24:
            return '23:59'
        else:
            return str(hora) + ':' + str(minuto)


    @property
    def inicio(self):
        return str(self.converte_hora(self.hora_ini))

    @property
    def fim(self):
        return str(self.converte_hora(self.hora_fim))

    def is_available(self):
        codigo_profissional, emp_profissional = self.get_id_profissional()
        con1 = fdb.connect(
        dsn=self.configuracao.db_host + ':' + self.configuracao.db_path,
        user=self.configuracao.db_user, password=self.configuracao.db_password, fb_library_name=self.configuracao.db_lib)
        cursor = con1.cursor()
        qry = ( "SELECT CONTROLE FROM AGENDA "
                "WHERE DATA = '%s' "
                "  AND CODIGO_PROFISSIONAL = %d "
                "  AND EMP_PROFISSIONAL = %d "
                "  AND   (((HORARIO <= " + self.inicio + ") AND (FIM > " + self.inicio + ")) OR "
                "         ((HORARIO < " + self.fim + ") AND (FIM >= " + self.fim + ")) OR "
                "         ((HORARIO >= " + self.inicio + ") AND (FIM <= " + self.fim + "))) ")

        cursor.execute(qry % ( self.data,  codigo_profissional, emp_profissional))
        #row = cursor.fetchall()
        #return row
        #cursor.close()
        #con1.close()

        columns = [column[0] for column in cursor.description]
        results = []
        for row in cursor.fetchall():
            results.append(dict(zip(columns, row)))
        return results


    def salva_booking(self):
        if self.preferencia==0:
            preferencial='S'
        else:
            preferencial='N'

        codigo_profissional, emp_profissional = self.get_id_profissional()
        codigo_cliente, emp_cliente = self.get_id_cliente()
        con = fdb.connect(
            dsn=self.configuracao.db_host + ':' + self.configuracao.db_path,
            user=self.configuracao.db_user, password=self.configuracao.db_password, fb_library_name=self.configuracao.db_lib)
        cur = con.cursor()

        servico_agenda = self.servicos.replace("'", "")

        add_agenda = ("INSERT INTO AGENDA "
                  "( DATA, CODIGO_PROFISSIONAL, EMP_PROFISSIONAL, CODIGO_CLIENTE, EMP_CLIENTE "
                  "   , HORARIO, FIM, STATUS, SERVICOS, CONTROLE_INTERNO "
                  "   , S, CONTROLE_CODIGO, CONTROLE_EMP_CODIGO, DATA_MARCACAO, HORA_MARCACAO "
                  "   , QTDE_MARCACOES, STATUS_ATUAL, CONTROLE_EXCLUSAO, CODIGO_FOLGA, EMP_FOLGA "
                  "   , FIXO, PREFERENCIA, CONFIRMADO, CONTROLE_CONF, EMP_CONTROLE_CONF "
                  "   , CONTROLE_FIXO, NOME_CLIENTE, RESPONSAVEL_CONTROLE, CODIGO_SALA, EMP_SALA "
                  "   , ID_WEB, APLICATIVO ) "
                  " VALUES  ( '{data}', {codigo_profissional}, {emp_profissional}, {codigo_cliente}, {emp_cliente} "
                  ", {inicio}, {fim}, 'A', UDF_COLLATEBR( '{servicos}' ), 0 "
                  ", 'N', 1, 1, CURRENT_DATE, CURRENT_TIME "
                  ", 1, 'M', 0, 0, 0 "
                  ", 'N', '{preferencia}', 'N', 0, 0 "
                  ", 0, '{nome_cliente}', 'SALAOVIP', 0, 0 "
                  ", {id_web}, '2') ".format(data=self.data, codigo_profissional=codigo_profissional, emp_profissional=emp_profissional,
                                             codigo_cliente=codigo_cliente, emp_cliente=emp_cliente, inicio=self.inicio, fim=self.fim,
                                             servicos=servico_agenda, nome_cliente=self.nome_cliente[:40], id_web=self.id, preferencia=preferencial))

        cur.execute(add_agenda)
        con.commit()
        cur.close()
        con.close()

    def salva_auditoria(self, acao):
        codigo_profissional, emp_profissional = self.get_id_profissional()
        codigo_cliente, emp_cliente = self.get_id_cliente()
        con = fdb.connect(
            dsn=self.configuracao.db_host + ':' + self.configuracao.db_path,
            user=self.configuracao.db_user, password=self.configuracao.db_password, fb_library_name=self.configuracao.db_lib)
        cur = con.cursor()

        servico_agenda = self.servicos.replace("'", "")

        add_audit = ("INSERT INTO AUDITORIA_AGENDA "
                  "( CONTROLE, DATA, HORA, CODIGO_OPERADOR, EMP_OPERADOR "
                  "   , ACAO, CODIGO_PROFISSIONAL, EMP_PROFISSIONAL, DATA_HORARIO, INICIO "
                  "   , FIM, CODIGO_CLIENTE, EMP_CLIENTE, SERVICO )"
                  " VALUES ( GEN_ID(GEN_AUDITORIA_AGENDA,1), CURRENT_DATE, CURRENT_TIME, 0, 0 "
                  ", %d, %d, %d, '%s', '%s' "
                  ", '%s', %d, %d, '%s' )")
        cur.execute(add_audit % ( acao, int(codigo_profissional), int(emp_profissional), self.data, self.display_hora(self.inicio), self.display_hora(self.fim), int(codigo_cliente), int(emp_cliente), servico_agenda ))
        con.commit()
        cur.close()
        con.close()

    def exclui_agenda(self):
        if self.id > 0:
            con = fdb.connect(
                dsn=self.configuracao.db_host + ':' + self.configuracao.db_path,
                user=self.configuracao.db_user, password=self.configuracao.db_password, fb_library_name=self.configuracao.db_lib)
            cur = con.cursor()
            qry_agenda = ("delete from agenda where id_web = '%d' ")
            cur.execute(qry_agenda % self.id )
            con.commit()
            cur.close()
            con.close()

    def get_id_profissional(self):
        con = fdb.connect(
            dsn=self.configuracao.db_host + ':' + self.configuracao.db_path,
            user=self.configuracao.db_user, password=self.configuracao.db_password, fb_library_name=self.configuracao.db_lib)
        cur = con.cursor()
        cur.execute("select codigo_profissional, codigo_empresa from profissionais where id_web = " + str(self.profissional_id))
        row = cur.fetchall()
        return row[0]

    def get_id_cliente(self):
        con = fdb.connect(
            dsn=self.configuracao.db_host + ':' + self.configuracao.db_path,
            user=self.configuracao.db_user, password=self.configuracao.db_password, fb_library_name=self.configuracao.db_lib)
        cur = con.cursor()
        print("select codigo_cliente, codigo_empresa from clientes where id_web = " + str(self.salao_cliente_id))
        cur.execute("select codigo_cliente, codigo_empresa from clientes where id_web = " + str(self.salao_cliente_id))
        row = cur.fetchall()
        return row[0]

    def cliente_importado(self):
        con = fdb.connect(
            dsn=self.configuracao.db_host + ':' + self.configuracao.db_path,
            user=self.configuracao.db_user, password=self.configuracao.db_password, fb_library_name=self.configuracao.db_lib)
        cur = con.cursor()
        cur.execute("select codigo_cliente, codigo_empresa from clientes where id_web = {id_web}".format(id_web=self.salao_cliente_id))
        row = cur.fetchall()
        print(row)

        if not(row):
            cliente = helper.get_cliente(self.salao_cliente_id)['data']['salonClient']
            con = fdb.connect(
                dsn=self.configuracao.db_host + ':' + self.configuracao.db_path,
                user=self.configuracao.db_user, password=self.configuracao.db_password, fb_library_name=self.configuracao.db_lib)
            cur = con.cursor()
            qry_cliente=("SELECT CODIGO_CLIENTE FROM CLIENTES "
                " WHERE CODIGO_EMPRESA = {codigo_empresa} "
                " AND STATUS = 'A' "
                " AND ( (ID_WEB IS NULL) OR (ID_WEB = 0) )  "
                " AND ( (EMAIL = '{email}') "
                "       OR (UDF_DIGITS(TELEFONE1) = '{celular}' )"
                "       OR (UDF_DIGITS(TELEFONE2) = '{celular}' )"
                "       OR (UDF_DIGITS(TELEFONE3) = '{celular}' ) )").format(codigo_empresa=self.configuracao.emp_padrao, email=cliente["email"], celular= cliente["celular"] )

            cur.execute(qry_cliente)
            row = cur.fetchone()

            if row:
                self.update_cliente(row[0], cliente["id"])
            else:
                self.insere_cliente(cliente)

    def update_cliente(self, codigo_cliente, id_web):
        con1 = fdb.connect(
        dsn=self.configuracao.db_host + ':' + self.configuracao.db_path,
        user=self.configuracao.db_user, password=self.configuracao.db_password, fb_library_name=self.configuracao.db_lib)
        cursor = con1.cursor()
        qry = ("UPDATE CLIENTES SET ID_WEB = %s "
           " WHERE CODIGO_CLIENTE = %s "
           "  AND CODIGO_EMPRESA = %s ")
        cursor.execute(qry % (str(id_web), str(codigo_cliente), str(self.configuracao.emp_padrao)))
        con1.commit()
        cursor.close()
        con1.close()

    def insere_cliente(self, cliente):
        cliente_nome = cliente["nome"].replace("'", "")

        con = fdb.connect(
            dsn=self.configuracao.db_host + ':' + self.configuracao.db_path,
            user=self.configuracao.db_user, password=self.configuracao.db_password, fb_library_name=self.configuracao.db_lib)
        cur = con.cursor()

        add_cliente = ("insert into clientes (codigo_cliente, codigo_empresa, data_cadastro "
                    ", data_cliente, data_nascimento, apelido "
                    ", nome, telefone1, email, nao_tem_email         "
                    ", grupo , emp_grupo, veiculo, emp_veiculo       "
                    "         , d_produtos, p_produtos, d_servicos   "
                    "         , p_servicos, mala_direta, status      "
                    "         , debitos, creditos                    "
                    "         , gasto_total, gasto_medio, cartao_fidelidade   "
                    "         , estado_civil, atacado, pontuacao, emissao_rps "
                    "         , id_web)                                       "
                    "  values (  GEN_ID(GEN_CLIENTE,1), {codigo_empresa}, CURRENT_DATE "
                    "          , CURRENT_DATE, null, UDF_UPPER(UDF_COLLATEBR('{apelido}')) "  
                    "          , UDF_UPPER(UDF_COLLATEBR('{nome}')), '{telefone}', '{email}', 'N'          "
                    "          , 1, 1, 1, 1                                           "
                    "          , 'N', 0, 'N'       "
                    "          , 0, 'N', 'A'          "
                    "          , 0, 0                                                  "
                    "          , 0, 0, 'N'                                  " 
                    "          , 'SOLTEIRO(A)', 'N', 0, 'N' "
                    "          , {id_web}) ").format(codigo_empresa=self.configuracao.emp_padrao, apelido=cliente_nome[:15], nome=cliente_nome[:40],telefone= cliente["celular"], email=cliente["email"], id_web=cliente["id"])

        cur.execute(add_cliente)
        con.commit()
        cur.close()
        con.close()
