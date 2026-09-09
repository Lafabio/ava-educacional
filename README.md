# AVA Educacional - SaaS 100% Python

## Visão Geral
Sistema completo de Ambiente Virtual de Aprendizagem construído com Python, Supabase e Vercel.

## Funcionalidades
- Autenticação completa (Supabase Auth)
- CRUD de cursos e turmas
- Sistema de avaliações com randomização
- Correção automática de questões
- Boletim com pesos configuráveis
- Chat e notificações (Realtime)
- Relatórios de aprendizagem

## Instalação

```bash
# Clonar repositório
git clone https://github.com/seu-usuario/ava-educacional
cd ava-educacional

# Criar ambiente virtual
python3 -m venv .venv
source .venv/bin/activate

# Instalar dependências
pip install -r requirements.txt

# Configurar variáveis de ambiente
cp .env.example .env
# Editar .env com suas credenciais do Supabase

# Rodar localmente
python app.py
```

## Deploy na Vercel

```bash
# Instalar Vercel CLI
npm i -g vercel

# Deploy
vercel --prod
```

## Estrutura do Projeto

```
ava-educacional/
├── app.py                 # FastAPI principal
├── models/                # SQLAlchemy models
├── services/              # Lógica de negócio
├── templates/             # Jinja2 templates
├── static/                # CSS/JS
├── requirements.txt       # Dependências
├── pyproject.toml         # Configuração
├── vercel.json            # Deploy config
└── .env                   # Variáveis de ambiente
```

## Tecnologias
- Python 3.12+
- FastAPI
- Supabase (PostgreSQL + Auth + Storage)
- Jinja2 + HTMX
- Vercel (deploy)

## Licença
MIT
