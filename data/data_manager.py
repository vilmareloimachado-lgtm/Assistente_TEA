import os
from typing import Dict, Any

import mysql.connector
from dotenv import load_dotenv

load_dotenv()

def conectar():
    """
    Abre uma conexão com o banco MySQL.

    Antes de executar o sistema, confira o arquivo .env:
    DB_HOST=localhost
    DB_USER=root
    DB_PASSWORD=sua_senha
    DB_NAME=tea_db
    """
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", ""),
        database=os.getenv("DB_NAME", "tea_db"),
        port=int(os.getenv("DB_PORT", "3306"))
    )


def carregar_dados() -> Dict[str, Any]:
    """
    Busca os usuários, tarefas e passos no MySQL e monta a mesma estrutura
    que antes era lida do arquivo tea_users.json.

    Estrutura retornada:
    {
        "Nome": {
            "preferencias": {"estilo_instrucao": "direto"},
            "nivel_suporte": "Leve",
            "data_nascimento": "2000-01-01"
            "senha_login": "..."
            "tarefas_diarias": [...],
            "tarefas_educacionais": [...]
        }
    }
    """
    dados = {}

    conexao = conectar()
    cursor = conexao.cursor(dictionary=True)

    cursor.execute("""
        SELECT id, nome, estilo_instrucao, nivel_suporte, data_nascimento, senha_login
        FROM usuarios
        ORDER BY nome
    """)
    usuarios = cursor.fetchall()

    for usuario in usuarios:
        nome = usuario["nome"]

        data_nasc = usuario["data_nascimento"].strftime("%Y-%m-%d") if usuario["data_nascimento"] else ""

        dados[nome] = {
            "preferencias": {
                "estilo_instrucao": usuario["estilo_instrucao"]
            },
            "nivel_suporte": usuario["nivel_suporte"],
            "data_nascimento": data_nasc,
            "senha_login": usuario["senha_login"],
            "tarefas_diarias": [],
            "tarefas_educacionais": []
        }

        cursor.execute("""
            SELECT id, titulo, descricao, prioridade, prazo, concluida, tipo 
            FROM tarefas 
            WHERE usuario_id = %s 
            ORDER BY id
        """, (usuario["id"],))
        tarefas = cursor.fetchall()

        for tarefa in tarefas:
            prazo = tarefa["prazo"].strftime("%Y-%m-%d") if tarefa["prazo"] else ""
            tarefa_dict = {
                "titulo": tarefa["titulo"],
                "descricao": tarefa.get("descricao") or "", 
                "prioridade": tarefa.get("prioridade") or "media", 
                "prazo": prazo,
                "concluida": bool(tarefa["concluida"]),
                "passos": []
            }

            cursor.execute("""
                SELECT texto, concluido
                FROM passos
                WHERE tarefa_id = %s
                ORDER BY ordem
            """, (tarefa["id"],))
            passos = cursor.fetchall()

            for passo in passos:
                tarefa_dict["passos"].append({
                    "texto": passo["texto"],
                    "concluido": bool(passo["concluido"])
                })

            dados[nome][tarefa["tipo"]].append(tarefa_dict)

    cursor.close()
    conexao.close()

    return dados


def salvar_dados(dados: Dict[str, Any]) -> None:
    """
    Salva no MySQL a estrutura completa do sistema.

    Para manter o código simples e didático para os alunos, esta função:
    1. apaga os dados antigos;
    2. recria usuários, tarefas e passos com base no dicionário recebido.

    Em sistemas profissionais, normalmente usaríamos INSERT, UPDATE e DELETE
    específicos para cada ação.
    """
    conexao = conectar()
    cursor = conexao.cursor()

    try:
        cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
        cursor.execute("TRUNCATE TABLE passos")
        cursor.execute("TRUNCATE TABLE tarefas")
        cursor.execute("TRUNCATE TABLE usuarios")
        cursor.execute("SET FOREIGN_KEY_CHECKS = 1")

        for nome, info_usuario in dados.items():
            estilo = info_usuario.get("preferencias", {}).get("estilo_instrucao", "direto")
            nivel_suporte = info_usuario.get("nivel_suporte", "Leve")
            data_nascimento = info_usuario.get("data_nascimento") if info_usuario.get("data_nascimento") else None
            senha_login = info_usuario.get("senha_login", "")
            cursor.execute("""
                INSERT INTO usuarios (nome, estilo_instrucao,nivel_suporte, data_nascimento, senha_login)
                VALUES (%s, %s, %s, %s, %s)
            """, (nome, estilo, nivel_suporte, data_nascimento, senha_login))

            usuario_id = cursor.lastrowid

            for tipo in ["tarefas_diarias", "tarefas_educacionais"]:
                for tarefa in info_usuario.get(tipo, []):
                    cursor.execute("""
                        INSERT INTO tarefas (usuario_id, tipo, titulo, descricao, prioridade, prazo, concluida)
                        VALUES (%s, %s, %s, %s, %s, NULLIF(%s, ''), %s)
                    """, (
                        usuario_id,
                        tipo,
                        tarefa.get("titulo", ""),
                        tarefa.get("descricao", ""), 
                        tarefa.get("prioridade", "media"), 
                        tarefa.get("prazo", ""),
                        bool(tarefa.get("concluida", False))
                    ))

                    tarefa_id = cursor.lastrowid

                    for ordem, passo in enumerate(tarefa.get("passos", []), start=1):
                        cursor.execute("""
                            INSERT INTO passos (tarefa_id, texto, concluido, ordem)
                            VALUES (%s, %s, %s, %s)
                        """, (
                            tarefa_id,
                            passo.get("texto", ""),
                            bool(passo.get("concluido", False)),
                            ordem
                        ))

        conexao.commit()

    except Exception:
        conexao.rollback()
        raise

    finally:
        cursor.close()
        conexao.close()
