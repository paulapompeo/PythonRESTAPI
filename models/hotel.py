from sql_alchemy import banco

#classe modelo para representra os hoteis
class HotelModel(banco.Model):

    #mapeamento para o SQLAlchemy
    __tablename__ = 'hoteis'

    hotel_id = banco.Column(banco.String, primary_key=True)
    nome = banco.Column(banco.String(80))
    estrelas = banco.Column(banco.Float(precision=1))
    diaria = banco.Column(banco.Float(precision=2))
    cidade = banco.Column(banco.String(40))
    site_id = banco.Column(banco.Integer, banco.ForeignKey('sites.site_id'))

    def __init__(self, hotel_id, nome, estrelas, diaria, cidade, site_id):
        self.hotel_id = hotel_id
        self.nome = nome
        self.estrelas = estrelas
        self.diaria = diaria
        self.cidade = cidade
        self.site_id = site_id

    #classe para transformar o objeto para JSON
    def json(self):
        return {
            'hotel_id' : self.hotel_id,
            'nome' : self.nome,
            'estrelas' :self.estrelas,
            'diaria' : self.diaria,
            'cidade' : self.cidade,
            'site_id' : self.site_id
        }

    #é um metodo de classe pq nao vai usar nada relacionado a self, o hotel_id será passado via path
    #cls = HotelModel,       query vem do sql_alchemy
    @classmethod
    def find_hotel(cls, hotel_id):
        hotel = cls.query.filter_by(hotel_id = hotel_id).first()  # SELECT * FROM hoteis WHERE hotel_id = hotel_id(passado) LIMIT 1
        if hotel:
            return hotel
        return None


    def save_hotel(self):
        banco.session.add(self)
        banco.session.commit()

    def update_hotel(self, nome, estrelas, diaria, cidade, site_id): #desembrulha os dados
        self.nome = nome
        self.estrelas = estrelas
        self.diaria = diaria
        self.cidade = cidade
        self.site_id = site_id

    def delete_hotel(self):
        banco.session.delete(self)
        banco.session.commit()
