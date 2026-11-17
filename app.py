import os
from datetime import datetime
from functools import wraps
from urllib.parse import urlparse, parse_qs

<<<<<<< HEAD
from flask import Flask, render_template, request, redirect, url_for, flash, session, abort, send_from_directory
=======
from flask import Flask, render_template, request, redirect, url_for, flash, session, abort
>>>>>>> c3516d7dcd18e8e0f38951830a33bac955f201c9
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey, inspect, or_
from sqlalchemy.orm import declarative_base, relationship, sessionmaker, scoped_session
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
UPLOAD_DIR = os.path.join(BASE_DIR, 'static', 'uploads')
os.makedirs(UPLOAD_DIR, exist_ok=True)

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'troque-esta-chave-em-producao-adaptedu')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(BASE_DIR, 'banco.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAX_CONTENT_LENGTH'] = 12 * 1024 * 1024
app.config['UPLOAD_FOLDER'] = UPLOAD_DIR

engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'], connect_args={'check_same_thread': False})
SessionLocal = sessionmaker(bind=engine)
db_session = scoped_session(SessionLocal)
Base = declarative_base()

class Usuario(Base):
    __tablename__ = 'usuarios'
    id = Column(Integer, primary_key=True)
    nome = Column(String(120), nullable=False)
    email = Column(String(180), nullable=False, index=True)
    senha = Column(String(255), nullable=False)
    materiais = relationship('Material', back_populates='autor')

class Material(Base):
    __tablename__ = 'materiais'
    id = Column(Integer, primary_key=True)
    titulo = Column(String(180), nullable=False)
    descricao = Column(Text, nullable=False)
    categoria = Column(String(60), nullable=False, default='Atividade')
    necessidade = Column(String(100), nullable=False, default='Todas')
    disciplina = Column(String(80), nullable=False, default='Geral')
    imagem = Column(String(500))
    video_url = Column(String(500))
    arquivo = Column(String(255))
    autor_id = Column(Integer, ForeignKey('usuarios.id'), nullable=True)
    criado_em = Column(DateTime, default=datetime.utcnow)
    autor = relationship('Usuario', back_populates='materiais')

# Migração leve para preservar a tabela antiga de atividades e os cadastros existentes.
def preparar_banco():
    Base.metadata.create_all(engine)
    if db_session.query(Material).count() == 0:
        exemplos = [
            Material(titulo='Rotina visual para organizar a aula', descricao='Modelo de sequência visual para antecipar as etapas da aula. O professor pode substituir os cartões por imagens e símbolos familiares ao estudante, observando quais apoios funcionam melhor para cada pessoa.', categoria='Material visual', necessidade='TEA', disciplina='Interdisciplinar', imagem='https://images.unsplash.com/photo-1503676260728-1c00da094a0b?auto=format&fit=crop&w=1000&q=85', video_url='https://www.youtube.com/watch?v=x1oKpKBNH-I'),
            Material(titulo='Como adaptar enunciados e atividades', descricao='Sugestões para apresentar instruções objetivas, dividir tarefas longas em etapas e oferecer diferentes formas de resposta, sem reduzir a expectativa de aprendizagem.', categoria='Estratégia', necessidade='Deficiência intelectual', disciplina='Interdisciplinar', imagem='https://images.unsplash.com/photo-1509062522246-3755977927d7?auto=format&fit=crop&w=1000&q=85', video_url='https://www.youtube.com/watch?v=HsdxSz3bpqA'),
            Material(titulo='Recursos de acessibilidade para baixa visão', descricao='Ideias para melhorar a legibilidade: contraste adequado, fontes ampliadas, organização limpa da página e descrição textual de imagens. Ajuste os recursos conforme a orientação do estudante.', categoria='Tutorial', necessidade='Deficiência visual', disciplina='Interdisciplinar', imagem='https://images.unsplash.com/photo-1516321318423-f06f85e504b3?auto=format&fit=crop&w=1000&q=85', video_url='https://www.youtube.com/watch?v=pHc4FerJ7ml'),
            Material(titulo='Comunicação visual e cartões de apoio', descricao='Cartões com imagens, palavras ou símbolos podem apoiar a compreensão de instruções e escolhas. Combine os cartões com a comunicação que o estudante já utiliza.', categoria='Material visual', necessidade='Comunicação alternativa', disciplina='Interdisciplinar', imagem='https://images.unsplash.com/photo-1503454537195-1dcabb73ffb9?auto=format&fit=crop&w=1000&q=85', video_url='https://www.youtube.com/watch?v=pO2sm2oUdlw')
        ]
        db_session.add_all(exemplos)
        db_session.commit()
    videos_iniciais = {
        'Rotina visual para organizar a aula': 'https://www.youtube.com/watch?v=x1oKpKBNH-I',
        'Como adaptar enunciados e atividades': 'https://www.youtube.com/watch?v=HsdxSz3bpqA',
        'Recursos de acessibilidade para baixa visão': 'https://www.youtube.com/watch?v=pHc4FerJ7ml',
        'Comunicação visual e cartões de apoio': 'https://www.youtube.com/watch?v=pO2sm2oUdlw',
    }
    for titulo, link in videos_iniciais.items():
        item = db_session.query(Material).filter_by(titulo=titulo).first()
        if item and item.video_url and 'youtube.com/results?' in item.video_url:
            item.video_url = link
    db_session.commit()
    inspector = inspect(engine)
    if 'atividades' in inspector.get_table_names():
        existentes = {c['name'] for c in inspector.get_columns('atividades')}
        alteracoes = {
            'tipo': "ALTER TABLE atividades ADD COLUMN tipo VARCHAR(60) DEFAULT 'Atividade'",
            'imagem': 'ALTER TABLE atividades ADD COLUMN imagem VARCHAR(500)',
            'video': 'ALTER TABLE atividades ADD COLUMN video VARCHAR(500)',
            'origem': 'ALTER TABLE atividades ADD COLUMN origem VARCHAR(180)',
        }
        with engine.begin() as conn:
            for coluna, sql in alteracoes.items():
                if coluna not in existentes:
                    conn.exec_driver_sql(sql)
        with engine.connect() as conn:
            atividades_antigas = conn.exec_driver_sql(
                'SELECT titulo, disciplina, descricao, necessidade FROM atividades'
            ).mappings().all()
        titulos = {m.titulo for m in db_session.query(Material).all()}
        for atividade in atividades_antigas:
            if atividade['titulo'] not in titulos:
                db_session.add(Material(
                    titulo=atividade['titulo'], disciplina=atividade['disciplina'],
                    descricao=atividade['descricao'], necessidade=atividade['necessidade'] or 'Todas',
                    categoria='Atividade', autor_id=None
                ))
        db_session.commit()


def obter_material(material_id):
    material = db_session.get(Material, material_id)
    if material is None:
        abort(404)
    return material

@app.teardown_appcontext
def remover_sessao(_erro=None):
    db_session.remove()


def professor_logado():
    if 'usuario_id' not in session:
        return None
    return db_session.get(Usuario, session['usuario_id'])


def login_obrigatorio(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not professor_logado():
            flash('Entre na sua conta para acessar a área do professor.', 'info')
            return redirect(url_for('login'))
        return func(*args, **kwargs)
    return wrapper


def video_embed(url):
    if not url:
        return None
    parsed = urlparse(url)
    if parsed.netloc not in ('youtube.com', 'www.youtube.com', 'm.youtube.com', 'youtu.be'):
        return None
    video_id = parsed.path.strip('/').split('/')[-1] if parsed.netloc == 'youtu.be' else parse_qs(parsed.query).get('v', [None])[0]
    if not video_id or not all(ch.isalnum() or ch in '-_' for ch in video_id):
        return None
    return 'https://www.youtube-nocookie.com/embed/' + video_id

def url_segura(url):
    if not url:
        return True
    parsed = urlparse(url)
    return parsed.scheme in ('http', 'https') and bool(parsed.netloc)

@app.context_processor
def contexto_global():
    return {'usuario_atual': professor_logado(), 'video_embed': video_embed}

<<<<<<< HEAD


@app.route('/service-worker.js')
def service_worker():
    resposta = send_from_directory(app.static_folder, 'service-worker.js', mimetype='application/javascript')
    resposta.headers['Service-Worker-Allowed'] = '/'
    resposta.headers['Cache-Control'] = 'no-cache'
    return resposta

=======
>>>>>>> c3516d7dcd18e8e0f38951830a33bac955f201c9
@app.route('/')
def inicio():
    destaques = db_session.query(Material).order_by(Material.criado_em.desc()).limit(3).all()
    return render_template('index.html', destaques=destaques)

@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        nome = request.form.get('nome', '').strip()
        email = request.form.get('email', '').strip().lower()
        senha = request.form.get('senha', '')
        if not nome or not email or len(senha) < 6:
            flash('Preencha todos os campos. A senha deve ter pelo menos 6 caracteres.', 'error')
            return render_template('cadastro.html')
        if db_session.query(Usuario).filter_by(email=email).first():
            flash('Já existe uma conta com esse e-mail. Faça login.', 'error')
            return render_template('cadastro.html')
        usuario = Usuario(nome=nome, email=email, senha=generate_password_hash(senha))
        db_session.add(usuario)
        db_session.commit()
        flash('Cadastro realizado! Agora entre para acessar a plataforma.', 'success')
        return redirect(url_for('login'))
    return render_template('cadastro.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        senha = request.form.get('senha', '')
        usuario = db_session.query(Usuario).filter_by(email=email).order_by(Usuario.id.desc()).first()
        if usuario:
            senha_valida = check_password_hash(usuario.senha, senha) if usuario.senha.startswith(('scrypt:', 'pbkdf2:')) else usuario.senha == senha
            if senha_valida:
                if not usuario.senha.startswith(('scrypt:', 'pbkdf2:')):
                    usuario.senha = generate_password_hash(senha)
                    db_session.commit()
                session.clear()
                session['usuario_id'] = usuario.id
                flash(f'Bem-vindo(a), {usuario.nome.split()[0]}!', 'success')
                return redirect(url_for('painel'))
        flash('E-mail ou senha incorretos.', 'error')
    return render_template('login.html')

@app.route('/sair')
def sair():
    session.clear()
    flash('Você saiu da sua conta.', 'info')
    return redirect(url_for('inicio'))

@app.route('/painel')
@login_obrigatorio
def painel():
    busca = request.args.get('q', '').strip()
    categoria = request.args.get('categoria', '').strip()
    necessidade = request.args.get('necessidade', '').strip()
    consulta = db_session.query(Material)
    if busca:
        termo = f'%{busca}%'
        consulta = consulta.filter(or_(Material.titulo.ilike(termo), Material.descricao.ilike(termo), Material.disciplina.ilike(termo)))
    if categoria:
        consulta = consulta.filter_by(categoria=categoria)
    if necessidade:
        consulta = consulta.filter_by(necessidade=necessidade)
    materiais = consulta.order_by(Material.criado_em.desc()).all()
    total = db_session.query(Material).count()
    meus = db_session.query(Material).filter_by(autor_id=session['usuario_id']).count()
    return render_template('painel.html', materiais=materiais, total=total, meus=meus, busca=busca, categoria=categoria, necessidade=necessidade)

@app.route('/materiais/novo', methods=['GET', 'POST'])
@login_obrigatorio
def novo_material():
    if request.method == 'POST':
        titulo = request.form.get('titulo', '').strip()
        descricao = request.form.get('descricao', '').strip()
        categoria = request.form.get('categoria', 'Atividade')
        necessidade = request.form.get('necessidade', 'Todas')
        disciplina = request.form.get('disciplina', 'Geral').strip()
        imagem = request.form.get('imagem', '').strip()
        video_url = request.form.get('video_url', '').strip()
        if not titulo or not descricao:
            flash('Informe o título e a descrição do material.', 'error')
            return render_template('material_form.html', material=None)
        if imagem and not url_segura(imagem):
            flash('O endereço da imagem precisa começar com http:// ou https://.', 'error')
            return render_template('material_form.html', material=None)
        if video_url and not url_segura(video_url):
            flash('Informe um link válido para o vídeo.', 'error')
            return render_template('material_form.html', material=None)
        arquivo_nome = None
        arquivo = request.files.get('arquivo')
        if arquivo and arquivo.filename:
            nome_seguro = secure_filename(arquivo.filename)
            extensao = nome_seguro.rsplit('.', 1)[-1].lower() if '.' in nome_seguro else ''
            if extensao not in {'pdf', 'png', 'jpg', 'jpeg', 'webp', 'doc', 'docx', 'ppt', 'pptx'}:
                flash('Formato não permitido. Envie PDF, imagem ou documento.', 'error')
                return render_template('material_form.html', material=None)
            arquivo_nome = f"{datetime.utcnow().strftime('%Y%m%d%H%M%S%f')}_{nome_seguro}"
            arquivo.save(os.path.join(app.config['UPLOAD_FOLDER'], arquivo_nome))
        material = Material(titulo=titulo, descricao=descricao, categoria=categoria, necessidade=necessidade,
                            disciplina=disciplina or 'Geral', imagem=imagem or None, video_url=video_url or None,
                            arquivo=arquivo_nome, autor_id=session['usuario_id'])
        db_session.add(material)
        db_session.commit()
        flash('Material publicado na comunidade de professores!', 'success')
        return redirect(url_for('detalhe_material', material_id=material.id))
    return render_template('material_form.html', material=None)

@app.route('/materiais/<int:material_id>')
@login_obrigatorio
def detalhe_material(material_id):
    material = obter_material(material_id)
    return render_template('material_detalhe.html', material=material)

@app.route('/materiais/<int:material_id>/editar', methods=['GET', 'POST'])
@login_obrigatorio
def editar_material(material_id):
    material = obter_material(material_id)
    if material.autor_id != session['usuario_id']:
        abort(403)
    if request.method == 'POST':
        material.titulo = request.form.get('titulo', '').strip()
        material.descricao = request.form.get('descricao', '').strip()
        material.categoria = request.form.get('categoria', 'Atividade')
        material.necessidade = request.form.get('necessidade', 'Todas')
        material.disciplina = request.form.get('disciplina', 'Geral').strip()
        material.imagem = request.form.get('imagem', '').strip() or None
        material.video_url = request.form.get('video_url', '').strip() or None
        if not material.titulo or not material.descricao or (material.imagem and not url_segura(material.imagem)) or (material.video_url and not url_segura(material.video_url)):
            flash('Revise os campos e os links informados.', 'error')
            return render_template('material_form.html', material=material)
        db_session.commit()
        flash('Material atualizado.', 'success')
        return redirect(url_for('detalhe_material', material_id=material.id))
    return render_template('material_form.html', material=material)

@app.route('/materiais/<int:material_id>/excluir', methods=['POST'])
@login_obrigatorio
def excluir_material(material_id):
    material = obter_material(material_id)
    if material.autor_id != session['usuario_id']:
        abort(403)
    if material.arquivo:
        caminho = os.path.join(app.config['UPLOAD_FOLDER'], material.arquivo)
        if os.path.isfile(caminho):
            os.remove(caminho)
    db_session.delete(material)
    db_session.commit()
    flash('Material removido.', 'success')
    return redirect(url_for('meus_materiais'))

@app.route('/meus-materiais')
@login_obrigatorio
def meus_materiais():
    materiais = db_session.query(Material).filter_by(autor_id=session['usuario_id']).order_by(Material.criado_em.desc()).all()
    return render_template('meus_materiais.html', materiais=materiais)

@app.route('/buscar')
@login_obrigatorio
def buscar():
    return redirect(url_for('painel', **request.args))

@app.route('/atividades')
def atividades_antigas():
    return redirect(url_for('painel', categoria='Atividade'))

@app.route('/atividades/cadastrar')
def cadastrar_atividade_antiga():
    return redirect(url_for('novo_material'))

@app.route('/ajuda')
def ajuda():
    return render_template('ajuda.html')

# Rotas antigas continuam válidas, mas agora levam ao catálogo unificado.
@app.route('/estrategias')
@app.route('/materiais-visuais')
def estrategias():
    return redirect(url_for('painel', categoria='Estratégia'))

@app.route('/videos')
def videos():
    return redirect(url_for('painel', categoria='Vídeo'))

@app.route('/praticas')
def praticas():
    return redirect(url_for('painel', categoria='Atividade'))

@app.route('/metodos')
def metodos():
    return render_template('ajuda.html')

@app.errorhandler(413)
def arquivo_grande(_erro):
    flash('O arquivo ultrapassa o limite de 12 MB.', 'error')
    return redirect(url_for('novo_material'))

@app.errorhandler(403)
def proibido(_erro):
    return render_template('erro.html', codigo=403, mensagem='Você só pode editar ou excluir os materiais que publicou.'), 403

@app.errorhandler(404)
def nao_encontrado(_erro):
    return render_template('erro.html', codigo=404, mensagem='Não encontramos essa página ou material.'), 404

with app.app_context():
    preparar_banco()

if __name__ == '__main__':
    app.run(debug=True)
