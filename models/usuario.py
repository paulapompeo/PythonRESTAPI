from sql_alchemy import banco
from flask import request, url_for
from requests import post

MAILGUN_DOMAIN = 'sandbox45d90e474c22400f96fceb38fe2aa26c.mailgun.org'
MAILGUN_API_KEY = 'df8a8456bfdf1ab7740405e9f2813218-ee13fadb-850ccd46'
FROM_TITLE = 'NO-REPLY'
FROM_EMAIL = 'no-reply@restapi.com'

#classe modelo para representra os usuarios
class UserModel(banco.Model):

    #mapeamento para o SQLAlchemy
    __tablename__ = 'usuarios'

    user_id = banco.Column(banco.Integer, primary_key=True)
    login = banco.Column(banco.String(40), nullable = False, unique = True)
    senha = banco.Column(banco.String(40), nullable = False)
    email = banco.Column(banco.String(100), nullable = False, unique = True)
    ativado = banco.Column(banco.Boolean, default = False)

    #ao ver que o user_id esta NULL o sqlalchemy altomaticamente incrementará
    def __init__(self, login, senha, email, ativado):
        self.login = login
        self.senha = senha
        self.email = email
        self.ativado = ativado


    #classe para transformar o objeto para JSON
    def json(self):
        return {
            'user_id' : self.user_id,
            'login' : self.login,
            'email' : self.email,
            'ativado' : self.ativado
        }

    def send_confirmation_email(self):
        #http://127.0.0.1.5000/confirmacao/1
        #para construir o link
        link = request.url_root[:-1] + url_for('userconfirm', user_id=self.user_id)
        return post('https://api.mailgun.net/v3/{}/messages'.format(MAILGUN_DOMAIN),
               auth=('api', MAILGUN_API_KEY),
               data={'from' : '{} <{}>'.format(FROM_TITLE, FROM_EMAIL),
                     'to' : self.email,
                     'subject' : 'Confirmação de Cadastro',
                     'text' : 'Confirme seu cadastro clicando no link a seguir: {}'.format(link),
                     'html' : '<html><p>\
                     Confirme seu cadastro clicando no link a seguir: <a href="{}">CONFIRMAR EMAIL</a>\
                     </p></html>'.format(link)})


    #é um metodo de classe pq nao vai usar nada relacionado a self, o user_id será passado via path
    #cls = UserModel,       query vem do sql_alchemy
    @classmethod
    def find_user(cls, user_id):
        user = cls.query.filter_by(user_id = user_id).first()  # SELECT * FROM hoteis WHERE hotel_id = hotel_id(passado) LIMIT 1
        if user:
            return user
        return None

    @classmethod
    def find_by_login(cls, login):
        user = cls.query.filter_by(login = login).first()  # SELECT * FROM hoteis WHERE hotel_id = hotel_id(passado) LIMIT 1
        if user:
            return user
        return None

    @classmethod
    def find_by_email(cls, email):
        user = cls.query.filter_by(email = email).first()  # SELECT * FROM hoteis WHERE hotel_id = hotel_id(passado) LIMIT 1
        if user:
            return user
        return None


    def save_user(self):
        banco.session.add(self)
        banco.session.commit()

    def delete_user(self):
        banco.session.delete(self)
        banco.session.commit()
