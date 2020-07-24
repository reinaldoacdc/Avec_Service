from configuracao import Configuracao
import fdb
import json
import math

class Agenda:

    def __init__(self, controle):
        item = self.pesquida_agenda(controle)[0]
        self.controle = item['CONTROLE']
        self.id_web = item['ID_WEB']
        self.profissional_idweb = item['PROFISSIONAL_IDWEB']
        self.cliente_idweb = item['CLIENTE_IDWEB']
        self.horario = item['HORARIO']
        self.fim = item['FIM']
        self.data = item['DATA']
        self.servicos = item['SERVICOS']
        self.status = item['STATUS']
        self.fixo = item['FIXO']
        self.nome_cliente = item['NOME_CLIENTE']
        self.codigo_cliente = item['CODIGO_CLIENTE']
        self.emp_cliente = item['EMP_CLIENTE']

    def converte_hora_minutos(self, data):
        #TELES -> SVIP
        hora = math.floor( data / 100 )
        hora = ( hora * 60 )
        min =  ( data % 100 )
        return  math.floor(hora) + min


    def parse_to_json(self):
        if self.fixo:
            envia_sms = 0
            email = 0
        else:
            envia_sms = 1
            email = 1

        return {
            'servicos': self.servicos,
            'profissional_id': self.profissional_idweb,
            'salao_cliente_id': self.cliente_idweb,
            'cliente_nome': self.nome_cliente,
            'cliente_tel': '',
            'data': str(self.data),
            'hora_ini': self.converte_hora_minutos(self.horario),
            'hora_fim': self.converte_hora_minutos(self.fim),
            'status': 1,
            'encaixe': 1,
            'envia_sms': envia_sms,
            'email': email
        }

    @staticmethod
    def pesquida_agenda(controle):
        configuracao = Configuracao()
        con = fdb.connect(
            dsn=configuracao.db_host + ':' + configuracao.db_path,
            user=configuracao.db_user, password=configuracao.db_password, fb_library_name=configuracao.db_lib)
        cur = con.cursor()
        qry_sync=("SELECT AGENDA.CONTROLE, AGENDA.ID_WEB "            
            ", PROFISSIONAIS.ID_WEB AS PROFISSIONAL_IDWEB, CLIENTES.ID_WEB AS CLIENTE_IDWEB "
            " , AGENDA.HORARIO, AGENDA.FIM, AGENDA.CODIGO_CLIENTE, AGENDA.EMP_CLIENTE "
            " , AGENDA.DATA, AGENDA.SERVICOS, AGENDA.STATUS, AGENDA.FIXO, UDF_COLLATEBR(AGENDA.NOME_CLIENTE) AS NOME_CLIENTE  "
            "  FROM AGENDA  "
            "  LEFT JOIN CLIENTES ON CLIENTES.codigo_cliente = AGENDA.codigo_cliente "
            "                    AND CLIENTES.codigo_empresa = AGENDA.emp_cliente       "
            "  LEFT JOIN PROFISSIONAIS ON PROFISSIONAIS.codigo_profissional = AGENDA.codigo_profissional "
            "                        AND PROFISSIONAIS.codigo_empresa = AGENDA.emp_profissional            "
            " WHERE AGENDA.CONTROLE = {controle} ".format(controle=controle))

        cur.execute(qry_sync)

        columns = [column[0] for column in cur.description]
        results = []
        for row in cur.fetchall():
            results.append(dict(zip(columns, row)))
        return results


    @staticmethod
    def grava_id(controle, id_web):
        configuracao = Configuracao()
        con = fdb.connect(
            dsn=configuracao.db_host + ':' + configuracao.db_path,
            user=configuracao.db_user, password=configuracao.db_password, fb_library_name=configuracao.db_lib)
        cur = con.cursor()
        qry_sync=("UPDATE AGENDA SET ID_WEB = {id_web} WHERE CONTROLE = {controle}".format(id_web=id_web, controle=controle))
        cur.execute(qry_sync)
        con.commit()
        cur.close()
        con.close()


