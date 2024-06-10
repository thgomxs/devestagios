from flask import Flask, render_template, request, session, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date
from openai import OpenAI
import json
import smtplib
import re
from dotenv import load_dotenv
import os
load_dotenv()

app = Flask(__name__)
client = OpenAI(api_key=os.getenv('CHATGPT_KEY'))
app.secret_key = os.getenv('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI')


class Database:
    _instance = None

    def __new__(classe):
        if Database._instance is None:
            Database._instance = super().__new__(classe)
        return Database._instance

    def init_app(self, app):
        self.db = SQLAlchemy(app)


# Inicializa o banco de dados utilizando o padrão de projeto criacional - SINGLETON
database = Database()
database.init_app(app)
db = database.db

candidato_vaga = db.Table('candidato_vaga',
                          db.Column('candidato_id', db.Integer, db.ForeignKey('candidatos.id'), primary_key=True),
                          db.Column('vaga_id', db.Integer, db.ForeignKey('vagas.id'), primary_key=True)
                          )


class Vaga(db.Model):
    __tablename__ = 'vagas'
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(100), nullable=False)
    concedente = db.Column(db.String(100), nullable=False)
    local = db.Column(db.String(100), nullable=False)
    bolsa = db.Column(db.Integer, nullable=False)
    beneficios = db.Column(db.String(50), nullable=False)
    turno = db.Column(db.String(10), nullable=False)
    requisitos = db.Column(db.Text, nullable=False)
    coordenador = db.Column(db.Integer, nullable=False)
    selecionado = db.Column(db.JSON, nullable=False)
    candidatos = db.relationship('Candidato', secondary=candidato_vaga, backref=db.backref('vagas', lazy='dynamic'))

    def __init__(self, titulo, concedente, local, bolsa, beneficios, turno, requisitos, coordenador, selecionado):
        self.titulo = titulo
        self.concedente = concedente
        self.local = local
        self.bolsa = bolsa
        self.beneficios = beneficios
        self.requisitos = requisitos
        self.turno = turno
        self.coordenador = coordenador
        self.selecionado = selecionado


class Candidato(db.Model):
    __tablename__ = 'candidatos'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(254), nullable=False, unique=True)
    nascimento = db.Column(db.Date, nullable=False)
    genero = db.Column(db.String(10), nullable=False)
    descricao = db.Column(db.Text, nullable=False)
    senha = db.Column(db.String(100), nullable=False)

    def __init__(self, nome, email, senha, nascimento, genero, descricao):
        self.nome = nome
        self.email = email
        self.senha = senha
        self.nascimento = nascimento
        self.genero = genero
        self.descricao = descricao

    def __str__(self):
        return f"Candidato(id={self.id},nome={self.nome}, descrição='{self.descricao}')"


class Coordenador(db.Model):
    __tablename__ = 'coordenadores'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(254), nullable=False, unique=True)
    senha = db.Column(db.String(100), nullable=False)

    def __init__(self, nome, email, senha):
        self.nome = nome
        self.email = email
        self.senha = senha


with app.app_context():
    db.create_all()
    if not Coordenador.query.filter_by(email='devestagios@gmail.com', senha='admin').first():
        coordenador = Coordenador(nome='admin', email='devestagios@gmail.com', senha='admin')
        db.session.add(coordenador)
        db.session.commit()


def verifica_caracteres(texto):
    padrao = re.compile("["
                        u"\U0001F600-\U0001F64F"
                        u"\U0001F300-\U0001F5FF"
                        u"\U0001F680-\U0001F6FF"
                        u"\U0001F1E0-\U0001F1FF"
                        u"\U00002500-\U00002BEF"
                        u"\U00002702-\U000027B0"
                        u"\U00002702-\U000027B0"
                        u"\U000024C2-\U0001F251"
                        u"\U0001f926-\U0001f937"
                        u"\U00010000-\U0010ffff"
                        u"\u2640-\u2642"
                        u"\u2600-\u2B55"
                        u"\u200d"
                        u"\u23cf"
                        u"\u23e9"
                        u"\u231a"
                        u"\ufe0f"
                        u"\u3030"
                        "]+", re.UNICODE)

    return bool(padrao.search(texto))


# Utilizando o padrão de projeto estrutural - FACHADA
class GerenciadorUsuarios:
    @staticmethod
    def login(tipo, request):
        global usuario

        if tipo == 'candidato':
            usuario = Candidato.query.filter_by(email=request.form['email']).first()
        elif tipo == 'coordenador':
            usuario = Coordenador.query.filter_by(email=request.form['email']).first()
        if usuario and usuario.senha == request.form['senha']:
            session[tipo] = usuario.id
            return redirect(url_for('index' if tipo == 'candidato' else 'coordenador'))
        else:
            flash(f'Dados incorretos!', 'warning')
            return redirect(url_for('index' if tipo == 'candidato' else 'coordenador'))

    @staticmethod
    def registrar(tipo, request):
        global usuario

        # Variaveis para registro de um candidato:
        global nome, email, senha, genero, descricao, nascimento, idade

        if tipo == 'candidato':
            usuario = Candidato.query.filter_by(email=request.form['email']).first()
        elif tipo == 'coordenador':
            usuario = Coordenador.query.filter_by(email=request.form['email']).first()

        if usuario:
            flash(f'Este e-mail já está em uso!', 'warning')
            return redirect(url_for('index' if tipo == 'candidato' else 'coordenador'))
        else:
            if tipo == 'candidato':
                if verifica_caracteres(request.form['descricao']) or verifica_caracteres(request.form['email']) or verifica_caracteres(request.form['nome']) or verifica_caracteres(request.form['senha']):
                    flash('Caracteres não permitidos detectados', 'warning')
                    return redirect(url_for('index' if tipo == 'candidato' else 'coordenador'))

                nome = request.form['nome']
                email = request.form['email']
                senha = request.form['senha']
                genero = request.form['genero']
                descricao = request.form['descricao']

                nascimento = request.form['nascimento']
                nascimento = datetime.fromisoformat(nascimento).date()
                hoje = date.today()
                idade = hoje.year - nascimento.year - ((hoje.month, hoje.day) < (nascimento.month, nascimento.day))

                if idade < 16:
                    flash('Você precisa ter pelo menos 16 anos para se cadastrar.', 'warning')
                    return redirect(url_for('index' if tipo == 'candidato' else 'coordenador'))

            candidato = Candidato(nome, email, senha, nascimento, genero, descricao)
            db.session.add(candidato)
            db.session.commit()
            flash('Candidato registrado com sucesso!', 'success')
            return redirect(url_for('index' if tipo == 'candidato' else 'coordenador'))

    @staticmethod
    def deslogar(tipo):
        session.pop(tipo, None)
        return redirect(url_for('index' if tipo == 'candidato' else 'coordenador'))

    @staticmethod
    def editar(tipo, id, request):
        global usuario

        if not tipo in session:
            flash(f'É necessário estar logado como {tipo} para executar esta ação!', 'warning')
            return redirect(url_for('index' if tipo == 'candidato' else 'coordenador'))

        if tipo == 'candidato':
            usuario = Candidato.query.get(id)
        elif tipo == 'coordenador':
            usuario = Coordenador.query.get(id)

        if usuario:
            if tipo == 'candidato':
                if verifica_caracteres(request.form['descricao']) or verifica_caracteres(request.form['email']):
                    flash('Caracteres não permitidos detectados', 'warning')
                    return redirect(url_for('index' if tipo == 'candidato' else 'coordenador'))

                usuario.descricao = request.form['descricao']
                usuario.email = request.form['email']

            if tipo == 'coordenador':
                if verifica_caracteres(request.form['nome']):
                    flash('Caracteres não permitidos detectados', 'warning')
                    return redirect(url_for('index' if tipo == 'candidato' else 'coordenador'))

                usuario.nome = request.form['nome']

            db.session.commit()
            flash('Perfil editado com sucesso!', 'success')
            return redirect(url_for('index' if tipo == 'candidato' else 'coordenador'))
        else:
            flash('Usuário não encontrado!', 'warning')
            return redirect(url_for('index' if tipo == 'candidato' else 'coordenador'))

    @staticmethod
    def carregar(tipo):
        if tipo == 'candidato':
            if tipo in session:
                vagas = Vaga.query.all()
                todasVagas = []
                minhasVagas = JuntarVagas()
                candidato = Candidato.query.get(session[tipo])
                if not candidato:
                    session.pop(tipo, None)
                    return redirect(url_for('index'))

                candidato.nascimentoFormatado = candidato.nascimento.strftime('%d/%m/%Y')

                for vaga in vagas:
                    vaga.candidatosID = [candidato.id for candidato in vaga.candidatos]
                    vaga.candidatosQtd = len(vaga.candidatos)
                    selecionado = json.loads(vaga.selecionado)
                    if not selecionado['id']:
                        todasVagas.append(vaga)

                if candidato.vagas:
                    for vaga in candidato.vagas:
                        selecionado = json.loads(vaga.selecionado)
                        if selecionado['id'] == session['candidato']:
                            vaga.selecionado = True
                            minhasVagas.addVagas(vaga)
                        elif selecionado['id'] != session[tipo] and selecionado['id'] == False:
                            vaga.selecionado = False
                            minhasVagas.addVagas(vaga)

                return render_template("index.html", vagas=todasVagas, candidato=candidato, minhasVagas=minhasVagas)
            else:
                return render_template("index.html")

        elif tipo == 'coordenador':
            if 'coordenador' in session:
                vagas = Vaga.query.all()
                vagasEncerradas = JuntarVagas()
                coordenador = Coordenador.query.get(session['coordenador'])
                if not coordenador:
                    session.pop('coordenador', None)
                    return redirect(url_for('index'))

                for vaga in vagas:
                    selecionado = json.loads(vaga.selecionado)
                    if selecionado['id']:
                        vaga.selecionado = True
                        vagasEncerradas.addVagas(vaga)
                    else:
                        vaga.selecionado = False

                    vaga.candidatosQtd = len(vaga.candidatos)

                    for candidato in vaga.candidatos:
                        candidato.nascimentoFormatado = candidato.nascimento.strftime('%d/%m/%Y')

                return render_template("coordenador.html", vagas=vagas, coordenador=coordenador,
                                       vagasEncerradas=vagasEncerradas)
            else:
                flash("EMAIL: devestagios@gmail.com | SENHA: admin", "warning")
                return render_template('coordenador.html')

    @staticmethod
    def verificar_permissao(tipo):
        if tipo in session:
            return True
        else:
            return False


# Utilizando o padrão de projeto criacional - COMMAND
class CommandVagas:
    @staticmethod
    def adicionar(request):
        if Vaga.query.filter_by(titulo=request.form['titulo'].upper()).first():
            flash('Já existe uma vaga com este título!', 'warning')
            return redirect(url_for('coordenador'))
        else:
            beneficiosArray = request.form.getlist('beneficios')
            beneficios = ""
            if len(beneficiosArray) > 0:
                beneficios = ", ".join(beneficiosArray)
            else:
                beneficios = "Não"

            if verifica_caracteres(request.form['local']) or verifica_caracteres(
                    request.form['concedente']) or verifica_caracteres(
                    request.form['titulo'].upper()) or verifica_caracteres(request.form['requisitos']):
                flash('Caracteres não permitidos detectados', 'warning')
                return redirect(url_for('coordenador'))

            titulo = request.form['titulo'].upper()
            concedente = request.form['concedente']
            local = request.form['local']
            bolsa = request.form['bolsa']
            turno = request.form['turno']
            requisitos = request.form['requisitos']
            coordenador = session['coordenador']
            selecionado = json.dumps({"id": False})

            vaga = Vaga(titulo, concedente, local, bolsa, beneficios, turno, requisitos, coordenador, selecionado)
            db.session.add(vaga)
            db.session.commit()
            flash('Vaga adicionada com sucesso!', 'success')
            return redirect(url_for('coordenador'))

    @staticmethod
    def editar(vaga_id):
        if Vaga.query.filter_by(titulo=request.form['titulo'].upper()).first():
            flash('Já existe uma vaga com este título!', 'warning')
            return redirect(url_for('coordenador'))
        else:
            vaga = Vaga.query.get(vaga_id)
            if vaga:
                selecionado = json.loads(vaga.selecionado)

                if selecionado['id']:
                    flash('Vaga já foi encerrada e teve seu candidato escolhido!', 'warning')
                    return redirect(url_for('coordenador'))

                if verifica_caracteres(request.form['local']) or verifica_caracteres(
                        request.form['concedente']) or verifica_caracteres(
                        request.form['titulo'].upper()) or verifica_caracteres(request.form['requisitos']):
                    flash('Caracteres não permitidos detectados', 'warning')
                    return redirect(url_for('coordenador'))

                beneficiosArray = request.form.getlist('beneficios')
                beneficios = ""
                if len(beneficiosArray) > 0:
                    beneficios = ", ".join(beneficiosArray)
                else:
                    beneficios = "Não"
                vaga.beneficios = beneficios
                vaga.titulo = request.form['titulo'].upper()
                vaga.concedente = request.form['concedente']
                vaga.local = request.form['local']
                vaga.bolsa = request.form['bolsa']
                vaga.turno = request.form['turno']
                vaga.requisitos = request.form['requisitos']
                vaga.coordenador = session['coordenador']
                db.session.commit()
                flash('Vaga editada com sucesso!', 'success')
                return redirect(url_for('coordenador'))
            else:
                flash('Vaga não encontrada!', 'warning')
                return redirect(url_for('coordenador'))

    @staticmethod
    def remover(vaga_id):
        vaga = Vaga.query.get(vaga_id)
        if vaga:
            db.session.delete(vaga)
            db.session.commit()
            flash('Vaga removida com sucesso!', 'success')
            return redirect(url_for('coordenador'))
        else:
            flash('Vaga não encontrada!', 'warning')
            return redirect(url_for('coordenador'))

    @staticmethod
    def confirmar_candidato(vaga_id, candidato_id):
        vaga = Vaga.query.get(vaga_id)
        candidato = Candidato.query.get(candidato_id)

        if vaga and candidato:
            try:
                selecionado = json.loads(vaga.selecionado)

                if selecionado['id']:
                    flash('Vaga já foi encerrada e teve seu candidato escolhido!', 'warning')
                    return redirect(url_for('coordenador'))

                coordenador = Coordenador.query.get(session['coordenador'])

                coordenador_email = coordenador.email
                candidato_email = candidato.email

                corpo_email = f'''<p>{candidato.nome} você foi selecionado para <b>{vaga.titulo}</b>. Aguarde o agendamento da entrevista! Entraremos em contato! Parabéns!</p>'''
                subject = f"DevEstagios - Olá {candidato.nome}, você foi selecionado para entrevista!"
                msg = f"Subject: {subject}\nContent-Type: text/html\n\n{corpo_email}"

                with smtplib.SMTP('smtp.gmail.com', 587) as connection:
                    connection.starttls()
                    connection.login(coordenador_email, "asvtmsiyifamkgbc")
                    connection.sendmail(coordenador_email, candidato_email, msg.encode('utf-8'))
                    print('E-mail enviado com sucesso!')

                candidatoJSON = {"id": candidato.id}
                vaga.selecionado = json.dumps(candidatoJSON)
                db.session.commit()
                flash("Candidato selecionado com sucesso!", "success")
                return redirect(url_for('coordenador'))
            except Exception as e:
                flash("Ocorreu um erro!", "warning")
                return redirect(url_for('coordenador'))
        else:
            flash("Ocorreu um erro!", "warning")
            return redirect(url_for('coordenador'))

    @staticmethod
    def aplicar_candidato(vaga_id):
        candidato = Candidato.query.get(session['candidato'])
        vaga = Vaga.query.get(vaga_id)

        if vaga and candidato:
            selecionado = json.loads(vaga.selecionado)
            if selecionado['id']:
                flash('Vaga já foi encerrada e teve seu candidato escolhido!', 'warning')
                return redirect(url_for('index'))
            elif len(vaga.candidatos) == 5:
                flash('Limite de candidatos atingido!', 'warning')
                return redirect(url_for('index'))
            elif candidato in vaga.candidatos:
                flash('Você já esta candidatado!', 'warning')
                return redirect(url_for('index'))
            else:
                vaga.candidatos.append(candidato)
                db.session.commit()
                flash('Você foi aplicado na vaga com sucesso!', 'success')
                return redirect(url_for('index'))
        else:
            flash('Vaga ou candidato não encontrado(a)!', 'warning')
            return redirect(url_for('index'))

    @staticmethod
    def retirar_candidato(vaga_id):
        candidato = Candidato.query.get(session['candidato'])
        vaga = Vaga.query.get(vaga_id)

        if vaga and candidato:
            selecionado = json.loads(vaga.selecionado)

            if selecionado['id']:
                flash('Vaga já foi encerrada e teve seu candidato escolhido!', 'warning')
                return redirect(url_for('coordenador'))
            if not candidato in vaga.candidatos:
                flash('Você não está candidatado nesta vaga!', 'warning')
                return redirect(url_for('index'))

            vaga.candidatos.remove(candidato)
            db.session.commit()
            flash('Você foi retirado da vaga com sucesso!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Vaga ou candidato não encontrado(a)!', 'warning')
            return redirect(url_for('index'))


class CommandChatGPT:
    @staticmethod
    def avaliar_descricao():
        candidato = Candidato.query.get(session['candidato'])

        if candidato:
            try:
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo-0125",
                    response_format={"type": "text"},
                    messages=[
                        {"role": "system",
                         "content": 'Se porte como um avaliador de descrição de um candidato para vagas de emprego na área da tecnologia, desenvolvedores e etc. Avalie o texto analisando coesão, coerência e etc. Sempre envie um JSON como resposta neste formato: { "nota": nota, "comentario": comentario }'},
                        {"role": "user",
                         "content": f'''Avalie esta decrição entre colchetes: [{candidato.descricao}] e dê uma nota de 0 a 10 e faça um comentário, caso os colchetes estejam vazios coloque nota 0 e explique o motivo no comentário.'''}
                    ]
                )
                resposta = response.choices[0].message.content
                resposta = resposta.replace("```json", "")
                resposta = resposta.replace("```", "")

                return jsonify(f'{resposta}')
            except Exception as e:
                print(e)
                erro = {'erro': 'Inteligência artificial não conseguiu obter uma resposta válida :('}
                return jsonify(json.dumps(erro))
        else:
            erro = {'erro': 'Inteligência artificial não conseguiu obter uma resposta válida :('}
            return jsonify(json.dumps(erro))

    @staticmethod
    def sugerir_candidato(vaga_id):
        vaga = Vaga.query.get(vaga_id)

        if vaga:
            candidatos_strings = [str(candidato) for candidato in vaga.candidatos]
            candidatos_strings = '\n'.join(candidatos_strings)

            try:
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo-0125",
                    response_format={"type": "text"},
                    messages=[
                        {"role": "system", "content": '''Se comporte como um avaliador de vagas de emprego na área da tecnologia, desenvolvedores e etc. Que irá comparar uma descrição de uma vaga
                                                         com um array de candidatos e verificar qual dos candidatos tem a descrição que possui maior 
                                                         compatibilidade com a vaga. Responda SEMPRE com um JSON no formato especificado.'''},
                        {"role": "user",
                         "content": f'''Verifique o usuário deste arrray entre colchetes [{candidatos_strings}] que possui maior compatibilidade com
                                                        a descrição desta vaga entre colchetes: [{vaga.requisitos}] e retorne qual o id do usuário mais compatível. Também faça um comentário falando o nome do candidato e o motivo que foi escolhido e não cite o id do usuário no comentário. Me
                                                        responda SEMPRE em um JSON e SEMPRE no formato "id": id, "comentario": comentario'''}
                    ]
                )
                resposta = response.choices[0].message.content
                resposta = resposta.replace("```json", "")
                resposta = resposta.replace("```", "")

                candidatoID = json.loads(f'{resposta}')
                candidatoSelecionado = Candidato.query.get(candidatoID['id'])

                candidatoDicionario = {'nascimentoFormatado': candidatoSelecionado.nascimento.strftime('%d/%m/%Y'),
                                       'email': candidatoSelecionado.email, 'nome': candidatoSelecionado.nome,
                                       'id': candidatoSelecionado.id, 'vaga_id': vaga.id,
                                       'comentario': candidatoID['comentario']}
                return jsonify(json.dumps(candidatoDicionario))
            except Exception as e:
                print(e)
                erro = {'erro': 'Inteligência artificial não conseguiu obter uma resposta válida :('}
                return jsonify(json.dumps(erro))

        else:
            erro = {'erro': 'Inteligência artificial não conseguiu obter uma resposta válida :('}
            return jsonify(json.dumps(erro))

    @staticmethod
    def verificar_compatibilidade(vaga_id):
        candidato = Candidato.query.get(session['candidato'])
        vaga = Vaga.query.get(vaga_id)

        if candidato and vaga:
            selecionado = json.loads(vaga.selecionado)
            if selecionado['id']:
                flash('Vaga já foi encerrada e teve seu candidato escolhido!', 'warning')
                return redirect(url_for('index'))
            try:
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo-0125",
                    response_format={"type": "text"},
                    messages=[
                        {"role": "system",
                         "content": f'''Se porte como um avaliador de descrição para vagas de emprego na área da tecnologia, desenvolvedores e etc. Verifique compatibilidade de uma descrição dessa vaga entre colchetes: [{vaga.requisitos}] com a descrição de um candidato. Sempre envie um JSON como resposta nesse formato: {{ "porcentagem": porcentagem, "comentario": comentario }}'''},
                        {"role": "user",
                         "content": f'''Verifique a compatiblidade com a descrição deste candidato entre colchetes: [{candidato.descricao}] e caso os colchetes da descrição do candidato estejam vazios, dê a porcentagem de 0% e explique o motivo no comentário.'''}
                    ]
                )

                resposta = response.choices[0].message.content
                resposta = resposta.replace("```json", "")
                resposta = resposta.replace("```", "")

                return jsonify(f'{resposta}')
            except Exception as e:
                print(e)
                erro = {'erro': 'Inteligência artificial não conseguiu obter uma resposta válida :('}
                return jsonify(json.dumps(erro))
        else:
            erro = {'erro': 'Inteligência artificial não conseguiu obter uma resposta válida :('}
            return jsonify(json.dumps(erro))



        # Utilizando o padrão de projeto criacional - COMMAND
class JuntarVagas:
    def __init__(self):
        self.vagas = []
        self.indice = 0

    def addVagas(self, vaga):
        self.vagas.append(vaga)

    def __iter__(self):
        return self

    def __next__(self):
        if self.indice < len(self.vagas):
            vaga = self.vagas[self.indice]
            self.indice += 1
            return vaga
        else:
            self.indice = 0
            raise StopIteration


@app.route('/coordenador_adicionar_vaga', methods=['POST'])
def coordenador_adicionar_vaga():
    if GerenciadorUsuarios.verificar_permissao('coordenador'):
        return CommandVagas.adicionar(request)
    else:
        return redirect(url_for('coordenador'))


@app.route('/coordenador_editar_vaga/<vaga_id>', methods=['POST'])
def coordenador_editar_vaga(vaga_id):
    if GerenciadorUsuarios.verificar_permissao('coordenador'):
        return CommandVagas.editar(vaga_id)
    else:
        return redirect(url_for('coordenador'))


@app.route('/coordenador_remover_vaga/<vaga_id>', methods=['POST'])
def coordenador_remover_vaga(vaga_id):
    if GerenciadorUsuarios.verificar_permissao('coordenador'):
        return CommandVagas.remover(vaga_id)
    else:
        return redirect(url_for('coordenador'))


@app.route('/coordenador_confirmar_candidato/<vaga_id>/<candidato_id>', methods=['POST'])
def coordenador_confirmar_candidato(vaga_id, candidato_id):
    if GerenciadorUsuarios.verificar_permissao('coordenador'):
        return CommandVagas.confirmar_candidato(vaga_id, candidato_id)
    else:
        return redirect(url_for('coordenador'))


@app.route('/coordenador_sugerir_candidato/<vaga_id>', methods=['POST'])
def coordenador_sugerir_candidato(vaga_id):
    if GerenciadorUsuarios.verificar_permissao('coordenador'):
        return CommandChatGPT.sugerir_candidato(vaga_id)
    else:
        return redirect(url_for('coordenador'))


@app.route('/candidato_retirar/<vaga_id>', methods=['POST'])
def candidato_retirar(vaga_id):
    if GerenciadorUsuarios.verificar_permissao('candidato'):
        return CommandVagas.retirar_candidato(vaga_id)
    else:
        return redirect(url_for('candidato'))


@app.route('/candidato_aplicar/<vaga_id>', methods=['POST'])
def candidato_aplicar(vaga_id):
    if GerenciadorUsuarios.verificar_permissao('candidato'):
        return CommandVagas.aplicar_candidato(vaga_id)
    else:
        return redirect(url_for('candidato'))


@app.route('/candidato_compatibilidade/<vaga_id>', methods=['POST'])
def candidato_compatibilidade(vaga_id):
    if GerenciadorUsuarios.verificar_permissao('candidato'):
        return CommandChatGPT.verificar_compatibilidade(vaga_id)
    else:
        return redirect(url_for('candidato'))


@app.route('/candidato_avaliar')
def candidato_avaliar():
    if GerenciadorUsuarios.verificar_permissao('candidato'):
        return CommandChatGPT.avaliar_descricao()
    else:
        return redirect(url_for('candidato'))


# Rotas de usuário (candidato e coordenador) gerenciadas pela classse GerenciadorUsuarios
@app.route('/editar/<tipo>/<id>', methods=['POST'])
def editar(tipo, id):
    return GerenciadorUsuarios.editar(tipo, id, request)


@app.route('/deslogar/<tipo>', methods=['POST'])
def deslogar(tipo):
    return GerenciadorUsuarios.deslogar(tipo)


@app.route('/logar/<tipo>', methods=['POST'])
def logar(tipo):
    return GerenciadorUsuarios.login(tipo, request)


@app.route('/registrar/<tipo>', methods=['POST'])
def registrar(tipo):
    return GerenciadorUsuarios.registrar(tipo, request)


# Carrega as informações na página do coordenador
@app.route('/coordenador', methods=['POST', 'GET'])
def coordenador():
    return GerenciadorUsuarios.carregar('coordenador')


# Carrega as informações na página do candidato
@app.route('/')
def index():
    return GerenciadorUsuarios.carregar('candidato')


if __name__ == '__main__':
    app.run()
