from sql_alchemy import banco

#classe modelo para representra os hoteis
class SiteModel(banco.Model):

    #mapeamento para o SQLAlchemy
    __tablename__ = 'sites'

    site_id = banco.Column(banco.Integer, primary_key=True)
    url = banco.Column(banco.String(80))
    hoteis = banco.relationship('HotelModel')  #relacionamento entre as classes -> tabelas, rcebemos uma lista de objeto hoteis

    #construtor   -> o id é criado automaticamente
    def __init__(self, url):
        self.url = url

    #classe para transformar o objeto para JSON
    def json(self):
        return {
            'site_id' : self.site_id,
            'url' : self.url,
            'hoteis' : [hotel.json() for hotel in self.hoteis]
        }

    #é um metodo de classe pq nao vai usar nada relacionado a self, o hotel_id será passado via path
    #cls = HotelModel,       query vem do sql_alchemy
    @classmethod
    def find_site(cls, url):   #procuramos pela URL pq nao temos conhecimento do id
        site = cls.query.filter_by(url = url).first()  # SELECT * FROM hoteis WHERE hotel_id = hotel_id(passado) LIMIT 1
        if site:
            return site
        return None

    @classmethod
    def find_by_id(cls, site_id):   #procuramos pela URL pq nao temos conhecimento do id
        site = cls.query.filter_by(site_id = site_id).first()  # SELECT * FROM hoteis WHERE hotel_id = hotel_id(passado) LIMIT 1
        if site:
            return site
        return None


    def save_site(self):
        banco.session.add(self)
        banco.session.commit()

    def delete_site(self):
        #deleta os hoteis associados ao site em questao
        [hotel.delete_hotel() for hotel in self.hoteis]
        #deleta o site
        banco.session.delete(self)
        banco.session.commit()
