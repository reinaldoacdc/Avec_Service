import datetime
import fdb
from configuracao import Configuracao

class Jornada:

    def __init__(self, profissional_idweb):
        self.profissional_idweb = profissional_idweb

    def get_agenda(self):
        configuracao = Configuracao()
        con = fdb.connect(
            dsn=configuracao.db_host + ':' + configuracao.db_path,
            user=configuracao.db_user, password=configuracao.db_password, fb_library_name=configuracao.db_lib)
        cur = con.cursor()
        qry_sync=("SELECT INICIO_AGENDA, FIM_AGENDA FROM PARAMETROS_SISTEMA WHERE CODIGO_EMPRESA = {empresa} ".format(empresa=configuracao.emp_padrao))

        cur.execute(qry_sync)
        row = cur.fetchone()
        return row


    def parse_to_json(self):
        data_inicio = datetime.date.today()
        data_fim = datetime.date(data_inicio.year + 2, data_inicio.month, data_inicio.day )
        hora_ini, hora_fim = self.get_agenda()
        return {
            'profissional_id': self.profissional_idweb,
            'tipo': 1,
            'data_inicio': str(data_inicio),
            'data_fim': str(data_fim),
            'hora_inicio': hora_ini * 60,
            'hora_fim': hora_fim * 60,
            'semana': '1,1,1,1,1,1,1'
        }
