-- ============================================================
-- BANCO DE DADOS DO SISTEMA TEA
-- Execute este arquivo no MySQL Workbench antes de rodar o Python.
-- ============================================================

CREATE DATABASE IF NOT EXISTS tea_db
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;

USE tea_db;

-- Remove as tabelas antigas, caso você esteja recriando o banco.
DROP TABLE IF EXISTS passos;
DROP TABLE IF EXISTS tarefas;
DROP TABLE IF EXISTS usuarios;

-- ============================================================
-- TABELA DE USUÁRIOS
-- Guarda o perfil principal do usuário.
-- ============================================================
CREATE TABLE usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL UNIQUE,
    estilo_instrucao ENUM('direto', 'detalhado') NOT NULL DEFAULT 'direto',
    nivel_suporte ENUM('Leve', 'Moderado', 'Severo') NOT NULL DEFAULT 'Leve',
    data_nascimento DATE NOT NULL,
    senha_login VARCHAR(255) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    tipo_usuario VARCHAR(20) NOT NULL DEFAULT 'cuidador',
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- TABELA DE TAREFAS
-- Guarda as atividades diárias e educacionais.
-- ============================================================
CREATE TABLE tarefas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    usuario_id INT NOT NULL,
    tipo ENUM('tarefas_diarias', 'tarefas_educacionais') NOT NULL,
    titulo VARCHAR(200) NOT NULL,
    descricao TEXT NULL, 
    prioridade ENUM('baixa', 'media', 'alta') NOT NULL DEFAULT 'media', 
    prazo DATE NULL,
    concluida BOOLEAN NOT NULL DEFAULT FALSE,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_tarefas_usuario
        FOREIGN KEY (usuario_id)
        REFERENCES usuarios(id)
        ON DELETE CASCADE
);

-- ============================================================
-- TABELA DE PASSOS
-- Guarda os passos gerados pela IA para cada tarefa.
-- ============================================================
CREATE TABLE passos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    tarefa_id INT NOT NULL,
    texto TEXT NOT NULL,
    concluido BOOLEAN NOT NULL DEFAULT FALSE,
    ordem INT NOT NULL DEFAULT 1,

    CONSTRAINT fk_passos_tarefa
        FOREIGN KEY (tarefa_id)
        REFERENCES tarefas(id)
        ON DELETE CASCADE
);

-- ============================================================
-- DADOS DE EXEMPLO
-- Pode apagar esta parte depois que testar.
-- ============================================================
INSERT INTO usuarios (
    nome, 
    estilo_instrucao,
    nivel_suporte,
    data_nascimento,
    senha_login,
    email
) VALUES (
    'Matheus', 
    'direto',
    'Leve',
    '1990-01-01',
    'senha_criptografada_aqui',
    'matheus@exemplo.com'
);

INSERT INTO tarefas (usuario_id, tipo, titulo, descricao, prioridade, prazo, concluida) VALUES 
(1, 'tarefas_diarias', 'Organizar mochila', 'Separar material por disciplina antes da aula.', 'media', '2026-06-10', FALSE), 
(1, 'tarefas_educacionais', 'Revisar lógica de programação', 'Rever variáveis, condições e repetição.', 'alta', '2026-06-12', FALSE);
