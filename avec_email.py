import smtplib
from email.message import EmailMessage


class Email:
    def __init__(self, configuracao, rotina, msg, title):
        self.user = configuracao.email_user
        self.password = configuracao.email_password
        self.to = configuracao.email_to
        self.msg = msg
        self.title = title
        self.rotina = rotina
        self.app_nome = configuracao.app_nome
        self.app_acesso = configuracao.app_acesso
        self.app_telefone = configuracao.app_telefone

    def send_mail(self):
        try:
            msg = EmailMessage()
            msg['From'] = self.user
            msg['To'] = self.to
            msg['Subject'] = self.title

            f = open("avec.error.html" , 'r')
            f_content = f.read().replace('\n', '')
            css = "<style>*{font-family:'Quicksand',sans-serif}table{margin:0 auto;padding:0;font-size:14px}body{background-color:#eaeaea}img{border:none}p{font-family:Verdana,Geneva,sans-serif;font-size:11px;line-height:150%;color:#404042}</style>"

            mensagem = f_content.format(css=css, method_name=self.rotina, lista_erros=self.msg, salao_nome=self.app_nome, salao_acesso=self.app_acesso, salao_telefone=self.app_telefone)


            msg.add_header('Content-Type','text/html')
            msg.set_payload(mensagem.encode('utf-8').strip())

            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(self.user, self.password)
            server.send_message(msg)
        except Exception as e:
            print('email exception: ' + e)
