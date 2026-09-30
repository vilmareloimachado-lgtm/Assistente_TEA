-- ============================================================
-- BANCO DE DADOS DO SISTEMA TEA
-- Execute este arquivo no MySQL Workbench antes de rodar o Python.
--
-- ATENCAO: este script APAGA as tabelas antigas e cria tudo do zero.
-- Todos os dados que estiverem nelas serao perdidos.
-- ============================================================

CREATE DATABASE IF NOT EXISTS tea_db
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;

USE tea_db;

-- Remove as tabelas antigas, caso voce esteja recriando o banco.
-- A ordem importa: primeiro as tabelas que dependem das outras.
DROP TABLE IF EXISTS passos;
DROP TABLE IF EXISTS tarefas;
DROP TABLE IF EXISTS vinculos;
DROP TABLE IF EXISTS usuarios;

-- ============================================================
-- TABELA DE USUARIOS
-- Guarda os dois tipos de usuario:
--   cuidador    -> entra com email e senha
--   usuario_tea -> nao usa email nem senha; o cuidador escolhe o
--                  perfil dele e, se houver PIN, ele e pedido.
-- ============================================================
CREATE TABLE usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    estilo_instrucao ENUM('direto', 'detalhado') NOT NULL DEFAULT 'direto',
    nivel_suporte ENUM('Leve', 'Moderado', 'Severo') NOT NULL DEFAULT 'Leve',
    data_nascimento DATE NOT NULL,
    senha_login VARCHAR(255) NULL,
    email VARCHAR(150) NULL UNIQUE,
    pin_hash VARCHAR(255) NULL,
    tipo_usuario VARCHAR(20) NOT NULL DEFAULT 'cuidador',
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT ck_usuarios_tipo
        CHECK (tipo_usuario IN ('cuidador', 'usuario_tea')),

    -- Todo cuidador precisa de email e senha para conseguir entrar.
    CONSTRAINT ck_cuidador_com_login
        CHECK (tipo_usuario <> 'cuidador'
               OR (email IS NOT NULL AND senha_login IS NOT NULL))
);

-- ============================================================
-- TABELA DE VINCULOS
-- Liga cada cuidador aos usuarios TEA que ele acompanha.
-- Um usuario TEA pode ter varios cuidadores (pai, mae, terapeuta...)
-- e um cuidador pode acompanhar varios usuarios TEA.
--   principal = TRUE  -> cuidador responsavel (quem criou o perfil)
--   principal = FALSE -> cuidador adicional
-- Regras como "so um principal por usuario TEA" ficam no service.
-- ============================================================
CREATE TABLE vinculos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    cuidador_id INT NOT NULL,
    usuario_id INT NOT NULL,
    principal BOOLEAN NOT NULL DEFAULT FALSE,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Impede repetir o mesmo par cuidador + usuario TEA.
    CONSTRAINT uq_vinculos_cuidador_usuario
        UNIQUE (cuidador_id, usuario_id),

    CONSTRAINT fk_vinculos_cuidador
        FOREIGN KEY (cuidador_id)
        REFERENCES usuarios(id)
        ON DELETE CASCADE,

    CONSTRAINT fk_vinculos_usuario
        FOREIGN KEY (usuario_id)
        REFERENCES usuarios(id)
        ON DELETE CASCADE
);

-- ============================================================
-- TABELA DE TAREFAS
-- Guarda as atividades diarias e educacionais.
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
