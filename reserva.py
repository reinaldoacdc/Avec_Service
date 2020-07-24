import math
import fdb
from configuracao import Configuracao


class Reserva:

    def __init__(self, controle):
        item = self.pesquisa_reserva(controle)[0]
        self.profissional_idweb = item['PROFISSIONAL_IDWEB']
        self.horario = item['HORARIO']
        self.fim = item['FIM']
        self.data = item['DATA']
        self.id_web = item['ID_WEB']

    def converte_hora_minutos(self, data):
        #TELES -> SVIP
        hora = math.floor( data / 100 )
        hora = ( hora * 60 )
        min =  ( data % 100 )
        return  math.floor(hora) + min

    def parse_to_json(self):
        return {
            'profissional_id': self.profissional_idweb,
            'data_inicio': str(self.data),
            'data_fim': str(self.data),
            'hora_inicio': self.converte_hora_minutos(self.horario),
            'hora_fim': self.converte_hora_minutos(self.fim),
        }

    @staticmethod
    def pesquisa_reserva(controle):
        configuracao = Configuracao()
        con = fdb.connect(
            dsn=configuracao.db_host + ':' + configuracao.db_path,
            user=configuracao.db_user, password=configuracao.db_password, fb_library_name=configuracao.db_lib)
        cur = con.cursor()
        qry_sync=("SELECT AGENDA.CONTROLE, AGENDA.ID_WEB "            
            ", PROFISSIONAIS.ID_WEB AS PROFISSIONAL_IDWEB  "
            " , AGENDA.HORARIO, AGENDA.FIM "
            " , AGENDA.DATA, AGENDA.SERVICOS, AGENDA.STATUS, AGENDA.FIXO "
            "  FROM AGENDA  "
            "  LEFT JOIN PROFISSIONAIS ON PROFISSIONAIS.codigo_profissional = AGENDA.codigo_profissional "
            "                        AND PROFISSIONAIS.codigo_empresa = AGENDA.emp_profissional            "
            " WHERE AGENDA.CONTROLE = %s ")

        cur.execute(qry_sync % controle)

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
        qry_sync=("UPDATE AGENDA SET ID_WEB = {id_web} WHERE CONTROLE = {controle}".format(controle=controle, id_web=id_web))
        cur.execute(qry_sync)
        con.commit()
        cur.close()
        con.close()
