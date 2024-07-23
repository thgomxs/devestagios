<p align="center"><a href="https://thgomxs.pythonanywhere.com/" target="_blank"><img src="https://github.com/thgomxs/devestagios/blob/main/static/images/logo_nome.png?raw=true" width="400" alt="DevEstagios logo"></a></p>

<p align="center">
   <img alt="MIT-LICENSE" src="https://img.shields.io/github/license/thgomxs/devestagios?color=%233880FF&logo=%1E65CF&logoColor=%1E65CF"/>
</p>


<p align="center">
 <a href="#tech">Tecnologias</a> • 
 <a href="#started">Começando...</a> • 
 <a href="#routes">Rotas da API</a>
</p>

<p align="center">
  Um website de estágios para a área de tecnologia utilizando padrões de projeto e com a API do ChatGPT integrado automatizando diversas funções. Desenvolvido para a matéria de Orientação a Objetos na Universidade de Brasília - FGA.
</p>

<h2 id="tech">💻 Tecnologias</h2>

- Python
- Flask
- JavaScript
- SQLite3

<h2 id="started">🚀 Começando... </h2>

Passo a passo para inicar o projeto localmente!

<h3>Pré-requisitos</h3>

Será necessário:

- Python
- Flask
- SQLAlchemy
- OpenAI

<h3>Clonando</h3>

```bash
git clone https://github.com/thgomxs/devestagios.git
```

<h3>Instalação</h3>

```bash
pip install flask
pip install flask_sqlalchemy 
pip install openai
```

<h3>Configurar variáveis .env</h2>

Use o trecho abaixo como referência para configurar o arquivo `.env` com suas credenciais

```yaml
CHATGPT_KEY={YOUR_CHATGPT_KEY}
SECRET_KEY={YOUR_SECRET_KEY}
DATABASE_URI={YOUR_DATABASE_URI}
```

<h3>Iniciando </h3>

Como inicar seu projeto

```bash
cd project-name
python app.py
```

<h2 id="routes">📍 Rotas da API </h2>

A API desta aplicação possui as seguintes rotas:
​
| ROTA               | DESCRIÇÃO                                          
|----------------------|-----------------------------------------------------
| <kbd>GET /</kbd>     | retorna página de login de usuário ou home caso usuário esteja logado
| <kbd>GET /coordenador</kbd>     | retorna página de login de coordenador ou home caso usuário esteja logado
| <kbd>POST /registrar/`<tipo>`</kbd>     | registra o usuário de acordo com o tipo (candidato ou coordenador)
| <kbd>POST /editar/`<tipo>`/`<id>`</kbd>     | edita o usuário de acordo com o tipo (candidato ou coordenador) e id
| <kbd>POST /logar/`<tipo>`</kbd>     | loga o usuário de acordo com o tipo (candidato ou coordenador)
| <kbd>POST /deslogar/`<tipo>`</kbd>     | desloga o usuário verificando o tipo (candidato ou coordenador)



<h2 >🚀 Licença </h2>

Este projeto possui uma licença do tipo MIT. Cheque o arquivo [LICENSE](https://github.com/thgomxs/devestagios/blob/main/LICENSE) para saber mais

