import fdb
from configuracao import Configuracao


class Cliente:
    def __init__(self, codigo_cliente, codigo_empresa):
        self.nome = ''
        self.id_web = ''
        self.pontuacao = 0
        self.email = ''
        self.telefone = ''
        self.cpf = ''
        self.count = 0

        todos = self.pesquisa_cliente(codigo_cliente, codigo_empresa)
        if (len(todos) > 0):
            item = todos[0]
            self.nome = item['NOME']
            self.id_web = item['ID_WEB']
            self.pontuacao = item['PONTUACAO']
            self.email = item['EMAIL']
            self.telefone = item['TELEFONE1']
            self.cpf = item['CPF']
            self.count = len(todos)

    def parse_to_json(self):
        return {
            'nome': self.nome,
            'email': self.email,
            'pontos': int(self.pontuacao),
            'celular': self.telefone,
            'cpf': self.cpf
        }

    @staticmethod
    def pesquisa_cliente(codigo_cliente, codigo_empresa):
        configuracao = Configuracao()
        con = fdb.connect(
            dsn=configuracao.db_host + ':' + configuracao.db_path,
            user=configuracao.db_user, password=configuracao.db_password, fb_library_name=configuracao.db_lib)
        cur = con.cursor()
        qry_sync=("SELECT CODIGO_CLIENTE, CODIGO_EMPRESA, NOME, ID_WEB, PONTUACAO, EMAIL, CPF, TELEFONE1 "            
            "  FROM CLIENTES  "
            " WHERE CODIGO_CLIENTE = %s "
            "   AND CODIGO_EMPRESA = %s ")
        cur.execute(qry_sync % (codigo_cliente, codigo_empresa))
        columns = [column[0] for column in cur.description]
        results = []
        for row in cur.fetchall():
         results.append(dict(zip(columns, row)))
        return results

    @staticmethod
    def grava_id(codigo_cliente, codigo_empresa, id_web):
        configuracao = Configuracao()
        con = fdb.connect(
            dsn=configuracao.db_host + ':' + configuracao.db_path,
            user=configuracao.db_user, password=configuracao.db_password, fb_library_name=configuracao.db_lib)
        cur = con.cursor()
        qry_sync=("UPDATE CLIENTES SET ID_WEB = %s WHERE CODIGO_CLIENTE = %s AND CODIGO_EMPRESA = %s")
        cur.execute(qry_sync % (id_web, codigo_cliente,codigo_empresa))
        con.commit()
        cur.close()
        con.close()
