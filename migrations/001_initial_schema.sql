-- ============================================================================
-- AVA Educacional - Migração inicial do banco de dados
-- Execute no SQL Editor do Supabase
-- ============================================================================

-- Habilitar extensões necessárias
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================================
-- TABELA: profiles (Usuários)
-- ============================================================================
CREATE TABLE IF NOT EXISTS profiles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    full_name VARCHAR(255),
    role VARCHAR(20) DEFAULT 'student' CHECK (role IN ('admin', 'teacher', 'student')),
    avatar_url VARCHAR(500),
    created_at TIMESTAMP DEFAULT NOW()
);

-- ============================================================================
-- TABELA: courses (Cursos)
-- ============================================================================
CREATE TABLE IF NOT EXISTS courses (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title VARCHAR(255) NOT NULL,
    description TEXT,
    teacher_id UUID REFERENCES profiles(id) ON DELETE SET NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- ============================================================================
-- TABELA: enrollments (Matrículas)
-- ============================================================================
CREATE TABLE IF NOT EXISTS enrollments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    student_id UUID REFERENCES profiles(id) ON DELETE CASCADE,
    course_id UUID REFERENCES courses(id) ON DELETE CASCADE,
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'inactive', 'completed')),
    enrolled_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(student_id, course_id)
);

-- ============================================================================
-- TABELA: contents (Conteúdos)
-- ============================================================================
CREATE TABLE IF NOT EXISTS contents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    course_id UUID REFERENCES courses(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    type VARCHAR(20) CHECK (type IN ('pdf', 'video', 'quiz', 'assignment')),
    content_url VARCHAR(500),
    order_index INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW()
);

-- ============================================================================
-- TABELA: assessments (Avaliações)
-- ============================================================================
CREATE TABLE IF NOT EXISTS assessments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    course_id UUID REFERENCES courses(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    type VARCHAR(20) CHECK (type IN ('online', 'presential')),
    is_randomized BOOLEAN DEFAULT FALSE,
    start_date TIMESTAMP,
    end_date TIMESTAMP,
    duration_minutes INTEGER,
    max_attempts INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT NOW()
);

-- ============================================================================
-- TABELA: questions (Questões)
-- ============================================================================
CREATE TABLE IF NOT EXISTS questions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    assessment_id UUID REFERENCES assessments(id) ON DELETE CASCADE,
    statement TEXT NOT NULL,
    type VARCHAR(20) CHECK (type IN ('multiple_choice', 'open_ended')),
    points FLOAT DEFAULT 1.0,
    created_at TIMESTAMP DEFAULT NOW()
);

-- ============================================================================
-- TABELA: question_options (Opções de questões)
-- ============================================================================
CREATE TABLE IF NOT EXISTS question_options (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    question_id UUID REFERENCES questions(id) ON DELETE CASCADE,
    option_text TEXT NOT NULL,
    is_correct BOOLEAN DEFAULT FALSE
);

-- ============================================================================
-- TABELA: attempts (Tentativas)
-- ============================================================================
CREATE TABLE IF NOT EXISTS attempts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    student_id UUID REFERENCES profiles(id) ON DELETE CASCADE,
    question_id UUID REFERENCES questions(id) ON DELETE CASCADE,
    selected_option UUID REFERENCES question_options(id) ON DELETE SET NULL,
    open_answer TEXT,
    is_correct BOOLEAN,
    score FLOAT,
    feedback TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- ============================================================================
-- TABELA: grade_configurations (Configurações de nota)
-- ============================================================================
CREATE TABLE IF NOT EXISTS grade_configurations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    course_id UUID REFERENCES courses(id) ON DELETE CASCADE,
    name VARCHAR(100),
    is_default BOOLEAN DEFAULT FALSE,
    approval_threshold FLOAT DEFAULT 7.0,
    created_at TIMESTAMP DEFAULT NOW()
);

-- ============================================================================
-- TABELA: grade_criteria (Critérios de avaliação)
-- ============================================================================
CREATE TABLE IF NOT EXISTS grade_criteria (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    config_id UUID REFERENCES grade_configurations(id) ON DELETE CASCADE,
    category VARCHAR(50),
    weight FLOAT,
    is_automatic BOOLEAN DEFAULT FALSE,
    is_mandatory BOOLEAN DEFAULT TRUE,
    sort_order INTEGER DEFAULT 0
);

-- ============================================================================
-- TABELA: student_grades (Notas dos alunos)
-- ============================================================================
CREATE TABLE IF NOT EXISTS student_grades (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    enrollment_id UUID REFERENCES enrollments(id) ON DELETE CASCADE,
    category VARCHAR(50),
    score FLOAT,
    manual_entry BOOLEAN DEFAULT TRUE,
    assessment_id UUID REFERENCES assessments(id) ON DELETE SET NULL,
    entered_by UUID REFERENCES profiles(id) ON DELETE SET NULL,
    entered_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- ============================================================================
-- TABELA: student_status_history (Histórico de status)
-- ============================================================================
CREATE TABLE IF NOT EXISTS student_status_history (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    enrollment_id UUID REFERENCES enrollments(id) ON DELETE CASCADE,
    status VARCHAR(20),
    final_score FLOAT,
    changed_at TIMESTAMP DEFAULT NOW()
);

-- ============================================================================
-- ÍNDICES para performance
-- ============================================================================
CREATE INDEX IF NOT EXISTS idx_courses_teacher ON courses(teacher_id);
CREATE INDEX IF NOT EXISTS idx_enrollments_student ON enrollments(student_id);
CREATE INDEX IF NOT EXISTS idx_enrollments_course ON enrollments(course_id);
CREATE INDEX IF NOT EXISTS idx_contents_course ON contents(course_id);
CREATE INDEX IF NOT EXISTS idx_assessments_course ON assessments(course_id);
CREATE INDEX IF NOT EXISTS idx_questions_assessment ON questions(assessment_id);
CREATE INDEX IF NOT EXISTS idx_question_options_question ON question_options(question_id);
CREATE INDEX IF NOT EXISTS idx_attempts_student ON attempts(student_id);
CREATE INDEX IF NOT EXISTS idx_attempts_question ON attempts(question_id);
CREATE INDEX IF NOT EXISTS idx_student_grades_enrollment ON student_grades(enrollment_id);

-- ============================================================================
-- RLS (Row Level Security) - Opcional mas recomendado
-- ============================================================================
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE courses ENABLE ROW LEVEL SECURITY;
ALTER TABLE enrollments ENABLE ROW LEVEL SECURITY;
ALTER TABLE contents ENABLE ROW LEVEL SECURITY;
ALTER TABLE assessments ENABLE ROW LEVEL SECURITY;
ALTER TABLE questions ENABLE ROW LEVEL SECURITY;
ALTER TABLE question_options ENABLE ROW LEVEL SECURITY;
ALTER TABLE attempts ENABLE ROW LEVEL SECURITY;
ALTER TABLE grade_configurations ENABLE ROW LEVEL SECURITY;
ALTER TABLE grade_criteria ENABLE ROW LEVEL SECURITY;
ALTER TABLE student_grades ENABLE ROW LEVEL SECURITY;
ALTER TABLE student_status_history ENABLE ROW LEVEL SECURITY;

-- Políticas básicas (permitir leitura para todos autenticados)
CREATE POLICY "Authenticated users can view profiles" ON profiles FOR SELECT USING (auth.role() = 'authenticated');
CREATE POLICY "Users can update own profile" ON profiles FOR UPDATE USING (auth.uid() = id);

CREATE POLICY "Authenticated users can view courses" ON courses FOR SELECT USING (auth.role() = 'authenticated');
CREATE POLICY "Teachers can manage courses" ON courses FOR ALL USING (auth.uid() = teacher_id);

CREATE POLICY "Authenticated users can view enrollments" ON enrollments FOR SELECT USING (auth.role() = 'authenticated');
CREATE POLICY "Students can enroll themselves" ON enrollments FOR INSERT WITH CHECK (auth.uid() = student_id);

-- ============================================================================
-- DADOS INICIAIS (opcional - admin padrão)
-- ============================================================================
-- Descomente para criar um admin inicial (substitua pelo UUID do seu usuário Supabase)
-- INSERT INTO profiles (id, email, full_name, role) VALUES 
-- ('SEU_UUID_AQUI', 'admin@ava.com', 'Administrador', 'admin');
