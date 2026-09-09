# Guia de Configuração do Supabase

## Passo 1: Criar conta no Supabase

1. Acesse https://supabase.com
2. Clique em "Start your project"
3. Faça login com GitHub ou email

## Passo 2: Criar novo projeto

1. Clique em "New project"
2. Preencha:
   - **Organization**: Selecione ou crie uma organização
   - **Project name**: `ava-educacional`
   - **Database Password**: Crie uma senha forte (guarde!)
   - **Region**: Escolha a mais próxima (Brazil se disponível)
3. Clique em "Create new project"
4. Aguarde 1-2 minutos para o projeto ser criado

## Passo 3: Criar as tabelas

1. No painel do projeto, vá em **SQL Editor**
2. Clique em "New query"
3. Cole todo o conteúdo do arquivo `migrations/001_initial_schema.sql`
4. Clique em "Run" (ícone de play)
5. Verifique se as tabelas foram criadas em **Table Editor**

## Passo 4: Pegar as credenciais

1. Vá em **Settings** (ícone de engrenagem)
2. Clique em **API**
3. Copie:
   - **Project URL** (ex: `https://xyzcompany.supabase.co`)
   - **anon public** key (chave pública)

## Passo 5: Configurar o .env

Edite o arquivo `.env` na raiz do projeto:

```env
# Substitua pelos seus dados reais
SUPABASE_URL=https://SEU-PROJETO.supabase.co
SUPABASE_KEY=sua_chave_anon_aqui
SUPABASE_SERVICE_KEY=sua_chave_service_aqui

# Configurações da app
SECRET_KEY=gerar_chave_secreta_aqui
DEBUG=true
```

### Gerar chave secreta

Execute no terminal:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

## Passo 6: Habilitar Auth (Opcional)

Se quiser usar autenticação de usuários:

1. Vá em **Authentication** > **Providers**
2. Habilitue "Email" (já vem habilitado)
3. Opcionalmente habilite Google, GitHub, etc.

## Passo 7: Configurar Storage (Opcional)

Para upload de arquivos:

1. Vá em **Storage**
2. Clique em "New bucket"
3. Nome: `contents`
4. Marque como "Public"
5. Clique em "Create bucket"

## Passo 8: Testar a aplicação

```bash
# No diretório do projeto
pip install -r requirements.txt
python app.py
```

Acesse http://localhost:8000

## Solução de Problemas

### Erro "Supabase não configurado"
- Verifique se o `.env` está preenchido corretamente
- Reinicie o servidor após alterar o `.env`

### Erro de conexão
- Verifique se o URL está correto (termina com `.supabase.co`)
- Verifique se a chave está completa

### Tabelas não existem
- Execute novamente o SQL no SQL Editor
- Verifique se não houve erro na execução

## Deploy na Vercel

```bash
# Instalar Vercel CLI
npm i -g vercel

# Fazer login
vercel login

# Deploy
vercel --prod

# Configurar variáveis de ambiente no Vercel
# Settings > Environment Variables
# Adicione SUPABASE_URL e SUPABASE_KEY
```
