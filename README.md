# AdaptEdu

Plataforma colaborativa para professores encontrarem e compartilharem atividades, estratégias, materiais visuais e tutoriais de educação inclusiva.

## Tecnologias

- Python + Flask
- SQLAlchemy ORM
- SQLite (`banco.db`)
- HTML, CSS e Jinja2

## Como executar no Windows

1. Abra a pasta do projeto no VS Code.
2. Abra o terminal nessa pasta.
3. Crie e ative um ambiente virtual:

```powershell
py -m venv venv
.\venv\Scripts\Activate.ps1
```

4. Instale as dependências:

```powershell
pip install -r requirements.txt
```

5. Inicie a aplicação:

```powershell
python app.py
```

6. Acesse o endereço exibido no terminal (normalmente `http://127.0.0.1:5000`).

O banco `banco.db` é mantido na pasta do projeto. Na primeira inicialização, o AdaptEdu cria a tabela de materiais, inclui alguns recursos demonstrativos e importa as atividades da tabela antiga para a biblioteca nova. Cadastros existentes são preservados. Senhas antigas em texto simples são convertidas para hash quando o respectivo usuário faz login.

## Funcionalidades

- Cadastro e login de professores.
- Senhas armazenadas com hash.
- Biblioteca com busca por palavra-chave, categoria e necessidade relacionada.
- Publicação de atividades, estratégias, materiais visuais e tutoriais.
- Links de imagem e vídeo, com incorporação de vídeos do YouTube.
- Anexo de PDF, imagens e documentos (limite de 12 MB).
- Edição e exclusão restritas ao autor da publicação.
- Página com as publicações de cada professor.

## Antes de publicar na internet

Defina uma `SECRET_KEY` forte por variável de ambiente, use HTTPS, configure proteção CSRF, política de privacidade e rotina de backup do banco. Revise os materiais e os links externos antes de disponibilizá-los publicamente. Não publique imagens ou dados que identifiquem estudantes sem autorização adequada.


## Aplicativo no celular (PWA)

O AdaptEdu agora possui os arquivos básicos para instalação como aplicativo:
- `static/manifest.json`: nome, cores e ícones.
- `static/service-worker.js`: cache de arquivos estáticos e tela simples quando estiver sem internet.
- `app.py`: disponibiliza o Service Worker na raiz do site.

Para testar no computador, execute o Flask e abra `http://127.0.0.1:5000`.
Para instalar em um celular, o aplicativo precisa estar publicado em um endereço HTTPS. No Android, abra o endereço no Chrome e escolha instalar/adicionar à tela inicial. No iPhone, abra no Safari, toque em Compartilhar e escolha Adicionar à Tela de Início.

Observação: o modo offline não mantém login, formulários ou dados pessoais em cache. É necessário estar conectado à internet para consultar e publicar materiais.
