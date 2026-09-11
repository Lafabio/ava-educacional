from fastapi import FastAPI, Request, Depends, HTTPException, UploadFile, File, Form
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse, RedirectResponse
from sqlalchemy import create_engine, Column, String, Integer, Float, Boolean, DateTime, ForeignKey, Enum, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import sessionmaker, relationship, declarative_base
from datetime import datetime, timedelta
import uuid, os, random, json, hashlib
from dotenv import load_dotenv
from supabase import create_client
from pydantic import BaseModel
from typing import Optional, List, Dict, Any

load_dotenv()

# ============================================================================
# CONFIGURAÇÃO
# ============================================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

SUPABASE_URL = os.environ.get('SUPABASE_URL')
SUPABASE_KEY = os.environ.get('SUPABASE_KEY')

app = FastAPI(title='AVA - Ambiente Virtual de Aprendizagem', version='1.0.0')

templates_dir = os.path.join(BASE_DIR, 'templates')
if os.path.isdir(templates_dir):
    templates = Jinja2Templates(directory=templates_dir)
else:
    templates = Jinja2Templates(directory='templates')

static_dir = os.path.join(BASE_DIR, 'static')
if os.path.isdir(static_dir):
    app.mount('/static', StaticFiles(directory=static_dir), name='static')

supabase = None
if SUPABASE_URL and SUPABASE_KEY and 'supabase.co' in SUPABASE_URL:
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception:
        supabase = None

# ============================================================================
# MODELOS DE DADOS
# ============================================================================

Base = declarative_base()

class User(Base):
    __tablename__ = 'profiles'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False)
    full_name = Column(String(255))
    role = Column(Enum('admin', 'teacher', 'student', name='user_roles'), default='student')
    avatar_url = Column(String(500))
    created_at = Column(DateTime, default=datetime.utcnow)

class Course(Base):
    __tablename__ = 'courses'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    teacher_id = Column(UUID(as_uuid=True), ForeignKey('profiles.id'))
    created_at = Column(DateTime, default=datetime.utcnow)
    teacher = relationship('User')
    enrollments = relationship('Enrollment', back_populates='course')
    contents = relationship('Content', back_populates='course')
    assessments = relationship('Assessment', back_populates='course')

class Enrollment(Base):
    __tablename__ = 'enrollments'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    student_id = Column(UUID(as_uuid=True), ForeignKey('profiles.id'))
    course_id = Column(UUID(as_uuid=True), ForeignKey('courses.id', ondelete='CASCADE'))
    status = Column(Enum('active', 'inactive', 'completed', name='enrollment_status'), default='active')
    enrolled_at = Column(DateTime, default=datetime.utcnow)
    student = relationship('User')
    course = relationship('Course', back_populates='enrollments')

class Content(Base):
    __tablename__ = 'contents'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    course_id = Column(UUID(as_uuid=True), ForeignKey('courses.id', ondelete='CASCADE'))
    title = Column(String(255), nullable=False)
    type = Column(Enum('pdf', 'video', 'quiz', 'assignment', name='content_types'))
    content_url = Column(String(500))
    order_index = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    course = relationship('Course', back_populates='contents')

class Assessment(Base):
    __tablename__ = 'assessments'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    course_id = Column(UUID(as_uuid=True), ForeignKey('courses.id', ondelete='CASCADE'))
    title = Column(String(255), nullable=False)
    type = Column(Enum('online', 'presential', name='assessment_types'))
    is_randomized = Column(Boolean, default=False)
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    duration_minutes = Column(Integer)
    max_attempts = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)
    course = relationship('Course', back_populates='assessments')
    questions = relationship('Question', back_populates='assessment')

class Question(Base):
    __tablename__ = 'questions'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    assessment_id = Column(UUID(as_uuid=True), ForeignKey('assessments.id', ondelete='CASCADE'))
    statement = Column(Text, nullable=False)
    type = Column(Enum('multiple_choice', 'open_ended', name='question_types'))
    points = Column(Float, default=1.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    assessment = relationship('Assessment', back_populates='questions')
    options = relationship('QuestionOption', back_populates='question')

class QuestionOption(Base):
    __tablename__ = 'question_options'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    question_id = Column(UUID(as_uuid=True), ForeignKey('questions.id', ondelete='CASCADE'))
    option_text = Column(Text, nullable=False)
    is_correct = Column(Boolean, default=False)
    question = relationship('Question', back_populates='options')

class Attempt(Base):
    __tablename__ = 'attempts'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    student_id = Column(UUID(as_uuid=True), ForeignKey('profiles.id'))
    question_id = Column(UUID(as_uuid=True), ForeignKey('questions.id'))
    selected_option = Column(UUID(as_uuid=True), ForeignKey('question_options.id'), nullable=True)
    open_answer = Column(Text, nullable=True)
    is_correct = Column(Boolean, nullable=True)
    score = Column(Float, nullable=True)
    feedback = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class GradeConfiguration(Base):
    __tablename__ = 'grade_configurations'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    course_id = Column(UUID(as_uuid=True), ForeignKey('courses.id'))
    name = Column(String(100))
    is_default = Column(Boolean, default=False)
    approval_threshold = Column(Float, default=7.0)
    created_at = Column(DateTime, default=datetime.utcnow)

class GradeCriteria(Base):
    __tablename__ = 'grade_criteria'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    config_id = Column(UUID(as_uuid=True), ForeignKey('grade_configurations.id', ondelete='CASCADE'))
    category = Column(String(50))
    weight = Column(Float)
    is_automatic = Column(Boolean, default=False)
    is_mandatory = Column(Boolean, default=True)
    sort_order = Column(Integer, default=0)

class StudentGrade(Base):
    __tablename__ = 'student_grades'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    enrollment_id = Column(UUID(as_uuid=True), ForeignKey('enrollments.id'))
    category = Column(String(50))
    score = Column(Float)
    manual_entry = Column(Boolean, default=True)
    assessment_id = Column(UUID(as_uuid=True), ForeignKey('assessments.id'), nullable=True)
    entered_by = Column(UUID(as_uuid=True), ForeignKey('profiles.id'))
    entered_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# ============================================================================
# SCHEMAS PYDANTIC
# ============================================================================

class CreateCourseRequest(BaseModel):
    title: str
    description: Optional[str] = None
    teacher_id: Optional[str] = None

class UpdateCourseRequest(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None

class CreateAssessmentRequest(BaseModel):
    title: str
    course_id: str
    type: str
    is_randomized: bool = False
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    duration_minutes: Optional[int] = None
    max_attempts: int = 1

class CreateQuestionRequest(BaseModel):
    assessment_id: str
    statement: str
    type: str
    points: float = 1.0
    options: Optional[List[Dict[str, Any]]] = None

class SubmitAnswerRequest(BaseModel):
    student_id: str
    question_id: str
    selected_option: Optional[str] = None
    open_answer: Optional[str] = None

class GradeConfigRequest(BaseModel):
    course_id: str
    name: str
    criteria: List[Dict[str, Any]]
    approval_threshold: float = 7.0

# ============================================================================
# FUNÇÕES DE NEGÓCIO
# ============================================================================

def calculate_final_grade(grades: Dict[str, float], criteria: List[Dict]) -> Dict[str, Any]:
    """Calcula nota final baseada nos pesos configurados"""
    total_weight = sum(c['weight'] for c in criteria)
    weighted_sum = sum(grades.get(c['category'], 0) * c['weight'] for c in criteria)
    final_score = (weighted_sum / total_weight / 10) * 10 if total_weight > 0 else 0
    
    # Determina status
    if final_score >= 7.0:
        status = 'aprovado'
    elif final_score >= 4.0:
        status = 'em_processo'
    else:
        status = 'reprovado'
    
    return {'final_score': round(final_score, 2), 'status': status}

def randomize_questions(question_bank: List[Dict], num_questions: int) -> List[Dict]:
    """Seleciona questões aleatoriamente"""
    if len(question_bank) <= num_questions:
        return question_bank
    return random.sample(question_bank, num_questions)

def check_dependencies(student_id: str, assessment_id: str, min_score: float = 7.0) -> bool:
    """Verifica se aluno atendeu pré-requisitos"""
    # Simulação: consulta ao banco
    return True

def get_user_from_token(token: str) -> Optional[Dict]:
    """Obtém usuário a partir do token JWT do Supabase"""
    if not supabase:
        return None
    try:
        user = supabase.auth.get_user(token)
        return user
    except Exception:
        return None

# ============================================================================
# ROTAS PÚBLICAS (HTML)
# ============================================================================

@app.get('/')
def home(request: Request):
    return templates.TemplateResponse(request, 'index.html')

@app.get('/login')
def login_page(request: Request):
    return templates.TemplateResponse(request, 'login.html')

@app.get('/register')
def register_page(request: Request):
    return templates.TemplateResponse(request, 'register.html')

@app.get('/forgot-password')
def forgot_password_page(request: Request):
    return templates.TemplateResponse(request, 'forgot_password.html')

@app.get('/courses')
def courses_page(request: Request):
    return templates.TemplateResponse(request, 'courses.html')

@app.get('/ebook/genetica')
def ebook_genetica(request: Request):
    return templates.TemplateResponse(request, 'ebook_genetica.html')

@app.get('/catalog')
def catalog_page(request: Request):
    return templates.TemplateResponse(request, 'catalog.html')

@app.get('/my-courses')
def my_enrollments_page(request: Request):
    return templates.TemplateResponse(request, 'my_enrollments.html')

@app.get('/dashboard')
async def dashboard(request: Request):
    access_token = request.cookies.get('access_token')
    if not access_token:
        return RedirectResponse(url='/login', status_code=302)
    if supabase:
        try:
            user = supabase.auth.get_user(access_token)
            if not user or not user.user:
                return RedirectResponse(url='/login', status_code=302)
        except Exception:
            return RedirectResponse(url='/login', status_code=302)
    user_email = request.cookies.get('user_email', 'Usuário')
    return templates.TemplateResponse(request, 'dashboard.html', {'user_email': user_email})

# ============================================================================
# ROTAS API (REST)
# ============================================================================

# --- Autenticação (Supabase) ---

@app.post('/api/auth/signup')
async def auth_signup(email: str = Form(...), password: str = Form(...), full_name: str = Form(...)):
    if not supabase:
        raise HTTPException(500, 'Supabase não configurado')
    try:
        user = supabase.auth.sign_up({'email': email, 'password': password})
        supabase.table('profiles').insert({
            'id': user.user.id,
            'email': email,
            'full_name': full_name,
            'role': 'student'
        }).execute()
        return RedirectResponse(url='/login?msg=cadastro_ok', status_code=302)
    except Exception as e:
        if 'already registered' in str(e).lower():
            return RedirectResponse(url='/login?msg=email_ja_cadastrado', status_code=302)
        raise HTTPException(400, str(e))

@app.post('/api/auth/login')
async def auth_login(request: Request, email: str = Form(...), password: str = Form(...)):
    if not supabase:
        raise HTTPException(500, 'Supabase não configurado')
    try:
        session = supabase.auth.sign_in_with_password({'email': email, 'password': password})
        response = RedirectResponse(url='/dashboard', status_code=302)
        response.set_cookie('access_token', session.session.access_token, httponly=True)
        response.set_cookie('user_email', email, httponly=True)
        return response
    except Exception as e:
        return RedirectResponse(url='/login?error=1', status_code=302)

@app.post('/api/auth/forgot-password')
async def auth_forgot_password(request: Request, email: str = Form(...)):
    if not supabase:
        raise HTTPException(500, 'Supabase não configurado')
    try:
        # Obtém a URL base do request para redirecionamento correto
        base_url = str(request.base_url).rstrip('/')
        redirect_to = f'{base_url}/login?msg=senha_redefinida'

        supabase.auth.reset_password_for_email(email, {'redirect_to': redirect_to})
        return RedirectResponse(url='/login?msg=email_enviado', status_code=302)
    except Exception as e:
        return RedirectResponse(url='/forgot-password?error=1', status_code=302)

# --- Cursos ---

@app.get('/api/courses')
def list_courses():
    if not supabase:
        return {'courses': []}
    data = supabase.table('courses').select('*, profiles(full_name)').execute()
    return {'courses': data.data}

@app.post('/api/courses')
async def create_course(request: Request, title: str = Form(...), description: str = Form('')):
    if not supabase:
        raise HTTPException(500, 'Supabase não configurado')
    access_token = request.cookies.get('access_token')
    if not access_token:
        raise HTTPException(401, 'Não autenticado')
    try:
        user = supabase.auth.get_user(access_token)
        teacher_id = user.user.id
    except Exception:
        raise HTTPException(401, 'Token inválido')
    data = supabase.table('courses').insert({
        'title': title,
        'description': description,
        'teacher_id': teacher_id
    }).execute()
    return RedirectResponse(url='/courses', status_code=302)

@app.get('/api/courses/{course_id}')
def get_course(course_id: str):
    if not supabase:
        raise HTTPException(500, 'Supabase não configurado')
    data = supabase.table('courses').select('*, profiles(full_name), enrollments(student_id)').eq('id', course_id).execute()
    if not data.data:
        raise HTTPException(404, 'Curso não encontrado')
    return {'course': data.data[0]}

@app.put('/api/courses/{course_id}')
async def update_course(course_id: str, request: UpdateCourseRequest):
    if not supabase:
        raise HTTPException(500, 'Supabase não configurado')
    data = supabase.table('courses').update(request.dict(exclude_none=True)).eq('id', course_id).execute()
    if not data.data:
        raise HTTPException(404, 'Curso não encontrado')
    return {'course': data.data[0]}

@app.delete('/api/courses/{course_id}')
def delete_course(course_id: str):
    if not supabase:
        raise HTTPException(500, 'Supabase não configurado')
    supabase.table('courses').delete().eq('id', course_id).execute()
    return {'success': True}

# --- Matrículas ---

@app.post('/api/enrollments')
async def enroll_student(request: Request, course_id: str = Form(...)):
    if not supabase:
        raise HTTPException(500, 'Supabase não configurado')
    access_token = request.cookies.get('access_token')
    if not access_token:
        raise HTTPException(401, 'Não autenticado')
    try:
        user = supabase.auth.get_user(access_token)
        student_id = user.user.id
    except Exception:
        raise HTTPException(401, 'Token inválido')
    existing = supabase.table('enrollments').select('*').eq('student_id', student_id).eq('course_id', course_id).execute()
    if existing.data:
        return {'enrollment': existing.data[0], 'message': 'Já matriculado'}
    data = supabase.table('enrollments').insert({'course_id': course_id, 'student_id': student_id}).execute()
    return {'enrollment': data.data[0]}

@app.get('/api/my-enrollments')
def my_enrollments(request: Request):
    if not supabase:
        return {'enrollments': []}
    access_token = request.cookies.get('access_token')
    if not access_token:
        return {'enrollments': []}
    try:
        user = supabase.auth.get_user(access_token)
        student_id = user.user.id
    except Exception:
        return {'enrollments': []}
    data = supabase.table('enrollments').select('*, courses(*)').eq('student_id', student_id).execute()
    return {'enrollments': data.data}

# --- Avaliações ---

@app.get('/api/assessments')
def list_assessments(course_id: Optional[str] = None):
    if not supabase:
        return {'assessments': []}
    query = supabase.table('assessments').select('*, courses(title)')
    if course_id:
        query = query.eq('course_id', course_id)
    data = query.execute()
    return {'assessments': data.data}

@app.post('/api/assessments')
async def create_assessment(request: CreateAssessmentRequest):
    if not supabase:
        raise HTTPException(500, 'Supabase não configurado')
    data = supabase.table('assessments').insert(request.dict()).execute()
    return {'assessment': data.data[0]}

@app.get('/api/assessments/{assessment_id}')
def get_assessment(assessment_id: str):
    if not supabase:
        raise HTTPException(500, 'Supabase não configurado')
    data = supabase.table('assessments').select('*, questions(*, question_options(*))').eq('id', assessment_id).execute()
    if not data.data:
        raise HTTPException(404, 'Avaliação não encontrada')
    return {'assessment': data.data[0]}

# --- Questões ---

@app.post('/api/questions')
async def create_question(request: CreateQuestionRequest):
    if not supabase:
        raise HTTPException(500, 'Supabase não configurado')
    
    question_data = request.dict()
    options = question_data.pop('options', [])
    
    question = supabase.table('questions').insert(question_data).execute()
    question_id = question.data[0]['id']
    
    for opt in options:
        supabase.table('question_options').insert({
            'question_id': question_id,
            'option_text': opt['text'],
            'is_correct': opt.get('is_correct', False)
        }).execute()
    
    return {'question': question.data[0]}

# --- Submissão de Respostas ---

@app.post('/api/attempts')
async def submit_answer(request: SubmitAnswerRequest):
    if not supabase:
        raise HTTPException(500, 'Supabase não configurado')
    
    # Busca questão para verificar resposta
    question = supabase.table('questions').select('*, question_options(*)').eq('id', request.question_id).execute()
    if not question.data:
        raise HTTPException(404, 'Questão não encontrada')
    
    is_correct = None
    score = None
    
    if request.selected_option:
        # Múltipla escolha: verifica se a opção selecionada é correta
        option = supabase.table('question_options').select('is_correct').eq('id', request.selected_option).execute()
        if option.data:
            is_correct = option.data[0]['is_correct']
            score = 1.0 if is_correct else 0.0
    
    # Registra tentativa
    attempt_data = request.dict()
    attempt_data['is_correct'] = is_correct
    attempt_data['score'] = score
    
    data = supabase.table('attempts').insert(attempt_data).execute()
    return {'attempt': data.data[0], 'is_correct': is_correct, 'score': score}

# --- Boletim / Notas ---

@app.get('/api/grades/{enrollment_id}')
def get_student_grades(enrollment_id: str):
    if not supabase:
        raise HTTPException(500, 'Supabase não configurado')
    
    # Busca notas do aluno
    grades = supabase.table('student_grades').select('*').eq('enrollment_id', enrollment_id).execute()
    
    # Busca configuração de pesos do curso
    course = supabase.table('enrollments').select('course_id').eq('id', enrollment_id).execute()
    if course.data:
        config = supabase.table('grade_configurations').select('*, grade_criteria(*)').eq('course_id', course.data[0]['course_id']).execute()
    else:
        config = {'data': []}
    
    return {'grades': grades.data, 'configuration': config.data[0] if config.data else None}

@app.post('/api/grades/calculate')
async def calculate_grades(enrollment_id: str = Form(...)):
    if not supabase:
        raise HTTPException(500, 'Supabase não configurado')
    
    # Busca configuração
    course = supabase.table('enrollments').select('course_id').eq('id', enrollment_id).execute()
    if not course.data:
        raise HTTPException(404, 'Matrícula não encontrada')
    
    config = supabase.table('grade_configurations').select('*, grade_criteria(*)').eq('course_id', course.data[0]['course_id']).execute()
    if not config.data:
        raise HTTPException(400, 'Nenhuma configuração de notas encontrada')
    
    # Busca notas do aluno
    grades_data = supabase.table('student_grades').select('*').eq('enrollment_id', enrollment_id).execute()
    grades_map = {g['category']: g['score'] for g in grades_data.data}
    
    # Calcula nota final
    criteria = config.data[0].get('grade_criteria', [])
    result = calculate_final_grade(grades_map, criteria)
    
    # Salva histórico
    supabase.table('student_status_history').insert({
        'enrollment_id': enrollment_id,
        'status': result['status'],
        'final_score': result['final_score']
    }).execute()
    
    return result

# --- Conteúdos ---

@app.get('/api/contents/{course_id}')
def list_contents(course_id: str):
    if not supabase:
        return {'contents': []}
    data = supabase.table('contents').select('*').eq('course_id', course_id).order('order_index').execute()
    return {'contents': data.data}

@app.post('/api/contents/upload')
async def upload_content(
    course_id: str = Form(...),
    title: str = Form(...),
    content_type: str = Form(...),
    file: UploadFile = File(...)
):
    if not supabase:
        raise HTTPException(500, 'Supabase não configurado')
    
    # Upload para Supabase Storage
    content = await file.read()
    file_name = f"{uuid.uuid4()}_{file.filename}"
    
    try:
        supabase.storage.from_('contents').upload(file_name, content)
        url = supabase.storage.from_('contents').get_public_url(file_name)
    except Exception as e:
        raise HTTPException(500, f'Erro no upload: {str(e)}')
    
    # Registra no banco
    data = supabase.table('contents').insert({
        'course_id': course_id,
        'title': title,
        'type': content_type,
        'content_url': url
    }).execute()
    
    return RedirectResponse(url=f'/course/{course_id}', status_code=302)

@app.delete('/api/contents/{content_id}')
def delete_content(content_id: str):
    if not supabase:
        raise HTTPException(500, 'Supabase não configurado')
    supabase.table('contents').delete().eq('id', content_id).execute()
    return {'success': True}

@app.post('/api/contents/update')
async def update_content(
    content_id: str = Form(...),
    course_id: str = Form(...),
    title: str = Form(...),
    content_type: str = Form(...),
    file: UploadFile = File(None)
):
    if not supabase:
        raise HTTPException(500, 'Supabase não configurado')
    
    update_data = {'title': title, 'type': content_type}
    
    if file and file.filename:
        content = await file.read()
        file_name = f"{uuid.uuid4()}_{file.filename}"
        try:
            supabase.storage.from_('contents').upload(file_name, content)
            url = supabase.storage.from_('contents').get_public_url(file_name)
            update_data['content_url'] = url
        except Exception as e:
            raise HTTPException(500, f'Erro no upload: {str(e)}')
    
    supabase.table('contents').update(update_data).eq('id', content_id).execute()
    return RedirectResponse(url=f'/course/{course_id}', status_code=302)

# ============================================================================
# ROTAS (HTML com templates)
# ============================================================================

@app.get('/course/{course_id}')
def course_detail(request: Request, course_id: str):
    if not supabase:
        return templates.TemplateResponse(request, 'error.html', {'message': 'Supabase não configurado'})
    
    # Busca curso
    course = supabase.table('courses').select('*, profiles(full_name)').eq('id', course_id).execute()
    if not course.data:
        return templates.TemplateResponse(request, 'error.html', {'message': 'Curso não encontrado'})
    
    # Busca conteúdos
    contents = supabase.table('contents').select('*').eq('course_id', course_id).order('order_index').execute()
    
    return templates.TemplateResponse(request, 'course_detail.html', {
        'course': course.data[0],
        'contents': contents.data
    })

@app.get('/assessment/{assessment_id}')
def assessment_detail(request: Request, assessment_id: str):
    if not supabase:
        return templates.TemplateResponse(request, 'error.html', {'message': 'Supabase não configurado'})
    
    assessment = supabase.table('assessments').select('*, questions(*, question_options(*))').eq('id', assessment_id).execute()
    if not assessment.data:
        return templates.TemplateResponse(request, 'error.html', {'message': 'Avaliação não encontrada'})
    
    return templates.TemplateResponse(request, 'assessment_detail.html', {
        'assessment': assessment.data[0]
    })

# ============================================================================
# INICIALIZAÇÃO
# ============================================================================

@app.get('/health')
def health_check():
    return {'status': 'healthy', 'supabase': 'connected' if supabase else 'disconnected'}

@app.get('/api/random-questions')
def get_random_questions(question_bank: str, num: int = 5):
    """Endpoint para testar randomização"""
    try:
        questions = json.loads(question_bank)
        result = randomize_questions(questions, num)
        return {'selected': result}
    except Exception as e:
        raise HTTPException(400, str(e))

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8000)
