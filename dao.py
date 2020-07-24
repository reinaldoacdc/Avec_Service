from configuracao import Configuracao
import fdb


class Dao:

    def __init__(self):
        configuracao = Configuracao()
        self.connection = fdb.connect(
            dsn=configuracao.db_host + ':' + configuracao.db_path,
            user=configuracao.db_user, password=configuracao.db_password, fb_library_name=configuracao.db_lib)
        self.cursor = self.connection.cursor()

    def __del__(self):
        pass
        #self.cursor.close()
        #self.connection.close()

    def get_sincronismo(self):
        sql = ("SELECT * FROM SINCRONISMO_WEB "
               " WHERE STATUS = 'ABE' "
               "   AND TABELA IN (3, 4, 5, 7)"
               " ORDER BY TABELA, ACAO      ")
        self.cursor.execute(sql)

        columns = [column[0] for column in self.cursor.description]
        results = []
        for row in self.cursor.fetchall():
            results.append(dict(zip(columns, row)))
        return results

    def get_pushs(self):
        sql=("SELECT * FROM PUSH WHERE ENVIADO = 'N' ")
        self.cursor.execute(sql)

        columns = [column[0] for column in self.cursor.description]
        results = []
        for row in self.cursor.fetchall():
         results.append(dict(zip(columns, row)))
        return results
