from app import app
import flask
from flask_sqlalchemy import SQLAlchemy
import cx_Oracle
from pandas import DataFrame

#conexão bd
connection = cx_Oracle.connect('PI/grupo10@localhost:1521/xepdb1')
cursor = connection.cursor()

#função pra printar a tabela
def printa_tabela():
    #pega todos os valores do bd
    amostras = DataFrame(cursor.execute("SELECT * FROM POLUICAO"))
    connection.commit()
    
    tabela = ''
    #trasnforma eles em uma grande string para facilitar na hora de printar no html 
    for i in range(0, len(amostras[0])):
        tabela += f'{amostras[0][i]} - MP10: {amostras[1][i]}   MP2,5: {amostras[2][i]}   O3: {amostras[3][i]}   CO: {amostras[4][i]}   NO2: {amostras[5][i]}   SO2: {amostras[6][i]}\n'
    return tabela

@app.route('/')

#rota do menu
@app.route('/index')
def index():
    return flask.render_template('index.html')

#rota para a pagina adicionar amostras
@app.route('/adicionar_amostra')
def adicionar_amostra():
    return flask.render_template('adicionar_amostra.html')

#rota para a pagia de alterar amostras
@app.route('/alterar_amostra')
def alterar_amostra():
    #chama a função para pegar os valores do bd
    tabela = printa_tabela()
    cursor.execute('UPDATE POLUICAO SET AMOSTRA = ROWNUM')
    connection.commit()
    return flask.render_template('alterar_amostra.html', tabela = tabela)

#rota para a pagina de excluir amostras
@app.route('/excluir_amostra')
def excluir_amostra():
    #chama a função para pegar os valores do bd
    tabela = printa_tabela()
    cursor.execute('UPDATE POLUICAO SET AMOSTRA = ROWNUM')
    connection.commit()
    return flask.render_template('excluir_amostra.html', tabela = tabela)

#rota para a pagina de classificação
@app.route('/classificacao')
def classificacao():
    return flask.render_template('classificacao.html')

#rota quando clica no botão classificar
@app.route('/classificar_ar', methods = ['POST'])
def classificar_amostras():
    
    #pega os valores médios do bd
    particulasInalaveis = DataFrame(cursor.execute('SELECT AVG (MP10) FROM poluicao'))
    particulasFinas = DataFrame(cursor.execute('SELECT AVG (MP25) FROM poluicao'))
    O3 = DataFrame(cursor.execute('SELECT AVG (O3) FROM poluicao'))
    CO = DataFrame(cursor.execute('SELECT AVG (CO) FROM poluicao'))
    NO2 = DataFrame(cursor.execute('SELECT AVG (NO2) FROM poluicao'))
    SO2 = DataFrame(cursor.execute('SELECT AVG (SO2) FROM poluicao'))
    connection.commit()
    
    #atribui os valores às variaveis
    particulasInalaveis = particulasInalaveis.to_dict()
    particulasInalaveis = particulasInalaveis[0][0]
    
    particulasFinas = particulasFinas.to_dict()
    particulasFinas = particulasFinas[0][0]
    
    O3 = O3.to_dict()
    O3 = O3[0][0]
    
    CO = CO.to_dict()
    CO = CO[0][0]
    
    
    NO2 = NO2.to_dict()
    NO2 = NO2[0][0]
    
    SO2 = SO2.to_dict()
    SO2 = SO2[0][0]
    
    #classifica o ar
    if particulasInalaveis <= 50 and particulasFinas <= 25 and O3 <= 100 and CO <= 9 and NO2 <= 200 and SO2 <= 20:
        mensagem = 'Qualidade do ar está BOA!'

    elif particulasInalaveis > 250 or particulasFinas > 125 or O3 > 200 or CO > 15 or NO2 > 1130 or SO2 > 800:
        mensagem = 'Qualidade do ar está PÉSSIMA. Toda a população pode apresentar sérios riscos de manifestações de doenças respiratórias e cardiovasculáres. Aumento de mortes prematórias do grupo sensível (crianças, idosos e pessoas com doenças respiratórias e cardíacas).'

    elif particulasInalaveis > 150 or particulasFinas > 75 or O3 > 160 or CO > 13 or NO2 > 320 or SO2 > 365:
       mensagem = 'Qualidade do ar está MUITO RUIM! Toda a população pode apresentar problemas como tosse seca, cansaço, arder nos olhos, nazir, garganta e ainda falta de ar e respiração ofegante. Efeitos ainda mais forte em grupos sensíveis (crianças, idosos e pessoas com doenças respiratórias e cardíacas).'

    elif particulasInalaveis > 100 or particulasFinas > 50 or O3 > 130 or CO > 11 or NO2 > 240 or SO2 > 40:
        mensagem = 'Qualidade do ar está RUIM! Toda a população pode apresentar problemas como tosse seca, cansaço, arder nos olhos, nazir e gargantas. Pessoas de grupos sensíveis (crianças, idosos e pessoas com doenças respiratórias e cardíacas) podema presentar efeitos mais sérios na saúde.'

    elif particulasInalaveis > 50 or particulasFinas > 25 or O3 > 100 or CO > 9 or NO2 > 200 or SO2 > 20:
        mensagem = 'Qualidade do ar está MODERADA! Pessoas do grupo sensível (crianças, idosos e pessoas com doenças respiratórias e cardíacas) podem apresentar tosse e cansaço. A população, em geral, não é afetada.'
        
    return flask.render_template('classificacao.html', mensagem=mensagem)

#rota quando clica no botao inserir
@app.route('/inserir_bd', methods = ['POST'])
def inserir_bd():
    
    #insere no bd os valores colocados no html
    MP10 = float(flask.request.form.get('MP10'))
    MP25 = float(flask.request.form.get('MP25'))
    O3 = float(flask.request.form.get('O3'))
    CO = float(flask.request.form.get('CO'))
    NO2 = float(flask.request.form.get('NO2'))
    SO2 = float(flask.request.form.get('SO2'))
    
    if MP10 >= 0 and MP25 >= 0 and O3 >= 0 and CO >= 0 and NO2 >= 0 and SO2 >= 0:
        cursor.execute(f"INSERT INTO POLUICAO (MP10, MP25, O3, CO, NO2, SO2) VALUES ({MP10}, {MP25}, {O3}, {CO}, {NO2}, {SO2})")
        cursor.execute('UPDATE POLUICAO SET AMOSTRA = ROWNUM')
        connection.commit()
        
    return flask.render_template('adicionar_amostra.html')

#rota quando clica botão de alterar
@app.route('/alterar_bd', methods = ['POST'])
def alterar_bd():
    #atualiza o bd com os valores colocados no html
    amostra = float(flask.request.form.get('amostra'))
    MP10 = float(flask.request.form.get('altera_MP10'))
    MP25 = float(flask.request.form.get('altera_MP25'))
    O3 = float(flask.request.form.get('altera_O3'))
    CO = float(flask.request.form.get('altera_CO'))
    NO2 = float(flask.request.form.get('altera_NO2'))
    SO2 = float(flask.request.form.get('altera_SO2'))
    
    if MP10 >= 0 and MP25 >= 0 and O3 >= 0 and CO >= 0 and NO2 >= 0 and SO2 >= 0:
        cursor.execute(f"UPDATE POLUICAO SET MP10 = {MP10}, MP25 = {MP25}, O3 = {O3}, CO = {CO}, NO2 = {NO2}, SO2 = {SO2} WHERE AMOSTRA = {amostra}")
        cursor.execute('UPDATE POLUICAO SET AMOSTRA = ROWNUM')
        connection.commit()
    
    tabela = printa_tabela()
    return flask.render_template('alterar_amostra.html', tabela = tabela)

#rota quando clica no botão de excluir
@app.route('/excluir_bd', methods = ['POST'])
def excluir_bd():
    #exclui o valor selecionado do bd
    cursor.execute(f"DELETE FROM POLUICAO WHERE AMOSTRA = {float(flask.request.form.get('excluir_amostra'))}")
    cursor.execute('UPDATE POLUICAO SET AMOSTRA = ROWNUM')
    connection.commit()
    
    tabela = printa_tabela()
    return flask.render_template('excluir_amostra.html', tabela = tabela)

#rota quando clica no botão de excluir todas as amostras
@app.route('/excluir_tudo')
def excluir_tudo():
    #exclui tudo do bd
    cursor.execute('DELETE FROM POLUICAO')
    connection.commit()
    return flask.render_template('excluir_amostra.html')
