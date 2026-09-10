# Manual de Uso - AVA Educacional

## Sumário
1. [Visão Geral](#1-visão-geral)
2. [Primeiros Passos](#2-primeiros-passos)
3. [Autenticação](#3-autenticação)
4. [Dashboard](#4-dashboard)
5. [Gestão de Cursos](#5-gestão-de-cursos)
6. [Sistema de Avaliações](#6-sistema-de-avaliações)
7. [Notas e Boletim](#7-notas-e-boletim)
8. [API REST](#8-api-rest)
9. [Configuração do Supabase](#9-configuração-do-supabase)
10. [Solução de Problemas](#10-solução-de-problemas)

---

## 1. Visão Geral

O **AVA Educacional** é uma plataforma completa de Ambiente Virtual de Aprendizagem construída com Python, FastAPI e Supabase.

### Funcionalidades Principais
- Cadastro e login de usuários (aluno, professor, admin)
- Gestão completa de cursos
- Sistema de avaliações online
- Correção automática de questões
- Boletim com notas configuráveis
- Upload e organização de conteúdos

### Tecnologias
- **Backend**: Python 3.12+ / FastAPI
- **Banco de Dados**: PostgreSQL (Supabase)
- **Autenticação**: Supabase Auth (JWT)
- **Armazenamento**: Supabase Storage
- **Deploy**: Vercel

---

## 2. Primeiros Passos

### Acessar o Sistema
```
https://ecossistema-python-saas-educacional.vercel.app
```

### Criar sua Conta
1. Acesse a página inicial
2. Clique em **"Cadastre-se"**
3. Preencha:
   - Nome completo
   - Email
   - Senha (mínimo 6 caracteres)
4. Clique em **"Cadastrar"**

### Fazer Login
1. Acesse `/login`
2. Insira seu email e senha
3. Clique em **"Entrar"**
4. Será redirecionado para o Dashboard

---

## 3. Autenticação

### Tipos de Usuário

| Tipo | Permissões |
|------|-----------|
| **Student** | Ver cursos, fazer avaliações, consultar notas |
| **Teacher** | Criar cursos, gerenciar avaliações, lançar notas |
| **Admin** | Acesso total ao sistema |

### Fluxo de Cadastro
```
Preencher formulário → Enviar → Supabase cria conta → Email de confirmação → Login
```

### Fluxo de Login
```
Inserir credenciais → Supabase valida → Token JWT gerado → Cookie configurado → Dashboard
```

### Recuperar Senha
1. Acesse a página de login
2. Clique em "Esqueci minha senha"
3. Insira seu email
4. Verifique sua caixa de entrada
5. Crie uma nova senha

---

## 4. Dashboard

### Visão Geral
Ao fazer login, você acessa o painel principal com:

- **Cards de Estatísticas**: Cursos ativos, alunos matriculados, avaliações
- **Lista de Cursos**: Seus cursos matriculados ou criados
- **Navegação Rápida**: Links para todas as seções

### Navegação
```
Dashboard
├── Meus Cursos
├── Avaliações
└── Boletim
```

---

## 5. Gestão de Cursos

### Criar um Curso (Professor)

**Endpoint**: `POST /api/courses`

```json
{
  "title": "Matemática Básica",
  "description": "Curso introdutório de matemática",
  "teacher_id": "uuid-do-professor"
}
```

**Via Interface**:
1. Acesse Dashboard → Meus Cursos
2. Clique em "Novo Curso"
3. Preencha título e descrição
4. Confirme

### Listar Cursos

**Endpoint**: `GET /api/courses`

```bash
curl https://ecossistema-python-saas-educacional.vercel.app/api/courses
```

**Resposta**:
```json
{
  "courses": [
    {
      "id": "uuid",
      "title": "Matemática Básica",
      "description": "Curso introdutório",
      "teacher_id": "uuid-professor",
      "created_at": "2026-09-09T00:00:00Z"
    }
  ]
}
```

### Detalhes de um Curso

**Endpoint**: `GET /api/courses/{course_id}`

Retorna o curso com:
- Dados do professor
- Lista de matrículas
- Conteúdos vinculados

### Atualizar Curso

**Endpoint**: `PUT /api/courses/{course_id}`

```json
{
  "title": "Matemática Básica - Atualizado",
  "description": "Nova descrição"
}
```

### Excluir Curso

**Endpoint**: `DELETE /api/courses/{course_id}`

```bash
curl -X DELETE https://ecossistema-python-saas-educacional.vercel.app/api/courses/UUID_CURSO
```

---

## 6. Sistema de Avaliações

### Criar Avaliação

**Endpoint**: `POST /api/assessments`

```json
{
  "title": "Prova 1 - Álgebra",
  "course_id": "uuid-do-curso",
  "type": "online",
  "is_randomized": true,
  "start_date": "2026-09-10T09:00:00Z",
  "end_date": "2026-09-10T11:00:00Z",
  "duration_minutes": 120,
  "max_attempts": 1
}
```

### Configurações Disponíveis

| Campo | Descrição |
|-------|-----------|
| `type` | `online` ou `presential` |
| `is_randomized` | Embaralha as questões |
| `duration_minutes` | Tempo limite em minutos |
| `max_attempts` | Número máximo de tentativas |

### Adicionar Questões

**Endpoint**: `POST /api/questions`

```json
{
  "assessment_id": "uuid-avaliacao",
  "statement": "Qual é a raiz quadrada de 144?",
  "type": "multiple_choice",
  "points": 2.0,
  "options": [
    {"text": "10", "is_correct": false},
    {"text": "11", "is_correct": false},
    {"text": "12", "is_correct": true},
    {"text": "13", "is_correct": false}
  ]
}
```

### Tipos de Questão

| Tipo | Descrição |
|------|-----------|
| `multiple_choice` | Múltipla escolha (correção automática) |
| `open_ended` | Questão aberta (correção manual) |

### Submeter Resposta (Aluno)

**Endpoint**: `POST /api/attempts`

**Múltipla Escolha**:
```json
{
  "student_id": "uuid-aluno",
  "question_id": "uuid-questao",
  "selected_option": "uuid-opcao-correta"
}
```

**Questão Aberta**:
```json
{
  "student_id": "uuid-aluno",
  "question_id": "uuid-questao",
  "open_answer": "Resposta do aluno aqui"
}
```

### Randomização de Questões

**Endpoint**: `GET /api/random-questions`

```bash
curl "https://ecossistema-python-saas-educacional.vercel.app/api/random-questions?num=5&question_bank=[{\"text\":\"Q1\"},{\"text\":\"Q2\"},{\"text\":\"Q3\"},{\"text\":\"Q4\"},{\"text\":\"Q5\"}]"
```

Retorna 5 questões selecionadas aleatoriamente.

---

## 7. Notas e Boletim

### Configurar Pesos

**Endpoint**: `POST /api/grades/configure`

```json
{
  "course_id": "uuid-curso",
  "name": "Média Ponderada",
  "criteria": [
    {"category": "prova_presencial", "weight": 40},
    {"category": "prova_online", "weight": 40},
    {"category": "participacao", "weight": 20}
  ],
  "approval_threshold": 7.0
}
```

### Metodologias Suportadas

#### Nova EJA
| Categoria | Peso |
|-----------|------|
| Presencial | 40% |
| Online | 40% |
| Participação | 20% |
| **Aprovação** | **7.0** |

#### Ensino Médio
| Categoria | Peso |
|-----------|------|
| Prova Final | 60% |
| Trabalho | 30% |
| Participação | 10% |
| **Aprovação** | **6.0** |

#### Cursos Livres
| Categoria | Peso |
|-----------|------|
| Atividades | 50% |
| Projeto Final | 40% |
| Presença | 10% |
| **Aprovação** | **6.0** |

### Consultar Notas do Aluno

**Endpoint**: `GET /api/grades/{enrollment_id}`

```bash
curl https://ecossistema-python-saas-educacional.vercel.app/api/grades/UUID-MATRICULA
```

**Resposta**:
```json
{
  "grades": [
    {"category": "prova_presencial", "score": 8.5},
    {"category": "prova_online", "score": 7.0},
    {"category": "participacao", "score": 9.0}
  ],
  "configuration": {
    "name": "Média Ponderada",
    "approval_threshold": 7.0
  }
}
```

### Calcular Nota Final

**Endpoint**: `POST /api/grades/calculate`

```bash
curl -X POST -F "enrollment_id=UUID-MATRICULA" https://ecossistema-python-saas-educacional.vercel.app/api/grades/calculate
```

**Resposta**:
```json
{
  "final_score": 8.05,
  "status": "aprovado"
}
```

### Status Possíveis

| Status | Significado |
|--------|-------------|
| `aprovado` | Nota >= limite de aprovação |
| `em_processo` | Nota entre reprovado e aprovado |
| `reprovado` | Nota abaixo do mínimo |

---

## 8. API REST

### Endpoints Disponíveis

| Método | Rota | Descrição |
|--------|------|-----------|
| `POST` | `/api/auth/signup` | Cadastro de usuário |
| `POST` | `/api/auth/login` | Login |
| `GET` | `/api/courses` | Listar cursos |
| `POST` | `/api/courses` | Criar curso |
| `GET` | `/api/courses/{id}` | Detalhes do curso |
| `PUT` | `/api/courses/{id}` | Atualizar curso |
| `DELETE` | `/api/courses/{id}` | Excluir curso |
| `POST` | `/api/enrollments` | Matricular aluno |
| `GET` | `/api/assessments` | Listar avaliações |
| `POST` | `/api/assessments` | Criar avaliação |
| `GET` | `/api/assessments/{id}` | Detalhes da avaliação |
| `POST` | `/api/questions` | Criar questão |
| `POST` | `/api/attempts` | Submeter resposta |
| `GET` | `/api/grades/{id}` | Consultar notas |
| `POST` | `/api/grades/calculate` | Calcular nota final |
| `GET` | `/api/contents/{id}` | Listar conteúdos |
| `POST` | `/api/contents/upload` | Upload de arquivo |
| `GET` | `/health` | Status do sistema |

### Formato de Requisição

**Headers**:
```
Content-Type: application/json
```

**Corpo (Body)**:
```json
{
  "campo1": "valor1",
  "campo2": "valor2"
}
```

### Formato de Resposta

**Sucesso**:
```json
{
  "campo": "valor",
  "success": true
}
```

**Erro**:
```json
{
  "detail": "Mensagem de erro"
}
```

---

## 9. Configuração do Supabase

### Criar Projeto

1. Acesse https://supabase.com
2. Clique em "New project"
3. Nome: `ava-educacional`
4. Aguarde a criação

### Criar Tabelas

1. Vá em **SQL Editor**
2. Cole o conteúdo de `migrations/001_initial_schema.sql`
3. Clique em **Run**

### Obter Credenciais

1. Vá em **Settings** → **API**
2. Copie:
   - **Project URL**: `https://xxx.supabase.co`
   - **anon key**: `eyJ...`

### Configurar Variáveis de Ambiente

```env
SUPABASE_URL=https://seu-projeto.supabase.co
SUPABASE_KEY=sua-chave-anon
```

---

## 10. Solução de Problemas

### Erro: "Supabase não configurado"
- Verifique se as variáveis de ambiente estão preenchidas
- Reinicie o servidor após alterar o `.env`

### Erro: "Credenciais inválidas"
- Verifique email e senha
- Confirme se o email foi verificado

### Erro: "Curso não encontrado"
- Verifique se o UUID está correto
- Confirme se o curso existe no banco

### Erro: "Directory does not exist"
- Verifique se a pasta `static/` existe
- Adicione um arquivo `.gitkeep` na pasta

### Erro 500 no Vercel
- Verifique os logs: `vercel logs`
- Confirme as variáveis de ambiente no painel do Vercel

### Deploy falha no Vercel
- Verifique o `pyproject.toml`
- Confirme que `packages = []` está configurado

---

## Comandos Úteis

### Rodar Localmente
```bash
cd ecossistema-python-saas-educacional
pip install -r requirements.txt
cp .env.example .env
# Edite .env com suas credenciais
python app.py
```

### Deploy no Vercel
```bash
vercel --prod
```

### Ver Logs no Vercel
```bash
vercel logs https://ecossistema-python-saas-educacional.vercel.app
```

### Gerar Chave Secreta
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

---

## Links Úteis

| Recurso | URL |
|---------|-----|
| **Aplicação** | https://ecossistema-python-saas-educacional.vercel.app |
| **GitHub** | https://github.com/Lafabio/ava-educacional |
| **Supabase** | https://supabase.com |
| **Vercel** | https://vercel.com |
| **FastAPI Docs** | https://fastapi.tiangolo.com |

---

**Versão**: 1.0.0  
**Licença**: MIT  
**Autor**: AVA Python Studio
