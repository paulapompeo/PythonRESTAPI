from flask_restful import Resource, reqparse
from models.hotel import HotelModel
from resources.filtros import normalize_path_params, consulta_sem_cidade, consulta_com_cidade
from models.site import SiteModel
from flask_jwt_extended import jwt_required   #para funcoes que precisam estar logadas para serem realizadas
import sqlite3


# path /hoteis?cidade=Rio de janeiro&estrelas_min=4&diaria_max=400
path_params = reqparse.RequestParser()  #instanciando um objeto da classe RequestParser
 #construtor do path_params
path_params.add_argument('cidade', type=str)
path_params.add_argument('estrelas_min', type=float)
path_params.add_argument('estrelas_max', type=float)
path_params.add_argument('diaria_min', type=float)
path_params.add_argument('diaria_max', type=float)
path_params.add_argument('limit', type=float)  #quantidade de itens que queremos exibir por pagina
path_params.add_argument('offset', type=float) #quantidade de elementos que queremos pular


#extendemos a classe Resource -> Hoteis será nosso primeiro recurso
class Hoteis(Resource):
    def get(self):
        connection = sqlite3.connect('banco.db')
        cursor = connection.cursor()

        dados = path_params.parse_args()
        dados_validos =  {chave:dados[chave] for chave in dados if dados[chave] is not None}

        parametros = normalize_path_params(**dados_validos) #retorna um json com ou sem cidade

        if not parametros.get('cidade'):     #get -> usado para não quebrar o codigo caso a chave não exista
            #so queremos os valores do dicionario - sem as chaves
            tupla = tuple([parametros[chave] for chave in parametros])
            resultado = cursor.execute(consulta_sem_cidade, tupla)
        else:
            tupla = tuple([parametros[chave] for chave in parametros])
            resultado = cursor.execute(consulta_com_cidade, tupla)

        hoteis = []
        for linha in resultado:
            hoteis.append({
            'hotel_id' : linha[0],
            'nome' : linha[1],
            'estrelas' : linha[2],
            'diaria' : linha[3],
            'cidade' : linha[4],
            'site_id' : linha[5]})

        #list comprehension   hotel.json()-> transforma objeto em json
        return{'hoteis' : hoteis} #select * from hoteis

class Hotel(Resource):
    argumentos = reqparse.RequestParser() #chama o reqparse e instancia um RequestParser
    #com isso nossos argumentos sao uma instancia do RequestParser, e podemos adicionar os
    #argumentos que queremos pegar do JSON que a pessoa enviar
    argumentos.add_argument('nome', type=str, required=True, help="The field 'nome' cannot be left blank")
    argumentos.add_argument('estrelas', type=float,required=True, help="The field 'estrelas' cannot be left blank")
    argumentos.add_argument('diaria')
    argumentos.add_argument('cidade')
    argumentos.add_argument('site_id', type=int, required= True, help="Every hotel needs to be linked with a site")
    # sempre adiocionar os elemento que queremos pegar, pois a pessoa pode enviar mais coisas

#Passamos o find_hotel para o hotel.py-models
    # def find_hotel(hotel_id):
    #     #hoteis é o nome da lista de hoteis
    #     for hotel in hoteis:
    #         #se o hotel_id for igual ao hotel_id passado para a gente
    #         if hotel['hotel_id'] == hotel_id:
    #             return hotel
    #     return None  #essa funcao retornará ou o hotel, ou None

    def get(self, hotel_id):
        hotel = HotelModel.find_hotel(hotel_id)  #Hotel é a classe
        if hotel:
            return hotel.json()
        return {'message' :  'Hotel not found.'}, 404 #status code http not found

    @jwt_required
    def post(self, hotel_id):
        #restringir a chave primaria
        if HotelModel.find_hotel(hotel_id):
            return {"message" : "Hotel id '{}' alredy exists.".format(hotel_id)}, 400 #bad request

        #criar um construtor
        #dados-> corresponde a chave e valor de todos os argumentos que foram passados
        dados = Hotel.argumentos.parse_args()
        #construir o novo hotel
        hotel = HotelModel(hotel_id, **dados) #objeto do tipo hotel

        if not SiteModel.find_by_id(dados.get('site_id')):
            return {'message' : 'The hotel must be associated to a valid site id.'}, 400

        try:
            #funcao para salvar o hotel no banco de dados
            hotel.save_hotel()
        except:
            return {'message', 'An internal error ocurred trying to save hotel.'}, 500 # internal server error
        return hotel.json()

    @jwt_required
    def put(self, hotel_id):
        #momento que colhe os dados
        dados = Hotel.argumentos.parse_args()

        #primeiro temos que verificar se o hotel ja existe -> atualizar
        # se o hotel nao existe, ele vai ser criado
        hotel_encontrado = HotelModel.find_hotel(hotel_id)
        if hotel_encontrado:
            hotel_encontrado.update_hotel(**dados) #update -> funcao built in do python   **dados -> embrulha os dados
            hotel_encontrado.save_hotel()
            return hotel_encontrado.json(), 200

        #construir o novo hotel, caso nao seja encontrado
        hotel = HotelModel(hotel_id, **dados) #objeto do tipo hotel    # **dados é um kwargs
        try:
            #funcao para salvar o hotel no banco de dados
            hotel.save_hotel()
        except:
            return {'message', 'An internal error ocurred trying to save hotel.'}, 500 # internal server error
        return hotel.json(), 201 #Codigo para criado

    @jwt_required
    def delete(self, hotel_id):
        hotel = HotelModel.find_hotel(hotel_id)
        if hotel:
            try:
                hotel.delete_hotel()
            except :
                return {'message', 'An internal error ocurred trying to delete hotel.'}, 500 # internal server error
            return {'message' : 'Hotel deleted'}
        return {'message' : 'Hotel not found'}, 404
