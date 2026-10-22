from datetime import datetime, timezone

from repositories.material_repository import MaterialRepository
from services.previa_link_service import PreviaLinkService, validar_link


class ErroMaterial(ValueError):
    def __init__(self, mensagem, status=422):
        super().__init__(mensagem)
        self.status = status


class MaterialService:
    def __init__(self, repository=None, previa=None):
        self.repository = repository or MaterialRepository()
        self.previa = previa or PreviaLinkService()

    def _ator(self, repo, payload, usuario_id):
        ator = repo.usuario(payload.get("usuario_id"))
        if ator is None or ator.tipo_usuario != payload.get("tipo_usuario"):
            raise ErroMaterial("Sua sessão não é mais válida. Entre novamente.", 401)
        usuario = repo.usuario(usuario_id)
        if usuario is None or usuario.tipo_usuario != "usuario_tea":
            raise ErroMaterial("Perfil não encontrado.", 404)
        if ator.tipo_usuario == "usuario_tea" and ator.id == usuario_id:
            return ator, None
        if ator.tipo_usuario == "cuidador":
            vinculo = repo.vinculo(ator.id, usuario_id)
            if vinculo is not None:
                return ator, vinculo
        raise ErroMaterial("Você não tem permissão para acessar os materiais deste perfil.", 403)

    def _cuidador(self, repo, payload, usuario_id):
        ator, vinculo = self._ator(repo, payload, usuario_id)
        if vinculo is None:
            raise ErroMaterial("Somente cuidadores vinculados podem enviar materiais.", 403)
        return ator, vinculo

    def _dados(self, dados):
        resultado = {}
        for chave, limite, obrigatorio in [("titulo", 200, True), ("descricao", 2000, False), ("tipo", 100, True)]:
            valor = (dados.get(chave) or "").strip()
            if obrigatorio and not valor:
                raise ErroMaterial(f"Informe o {chave.replace('titulo', 'título')} do material.")
            if len(valor) > limite:
                raise ErroMaterial(f"O campo {chave} permite até {limite} caracteres.")
            resultado[chave] = valor
        try:
            resultado["link"] = validar_link(dados.get("link"))
            resultado["imagem_url"] = validar_link(dados["imagem_url"]) if dados.get("imagem_url") else None
        except ValueError as erro:
            raise ErroMaterial(str(erro)) from erro
        return resultado

    def _resumo(self, d, ator, vinculo):
        m = d.material
        cuidador = vinculo is not None
        autor = cuidador and m.autor_id == ator.id
        principal = cuidador and bool(vinculo.principal)
        dt = lambda data: data.isoformat() + "Z" if data else None
        return {
            "destinatario_id": d.id, "material_id": m.id, "usuario_id": d.usuario_id,
            "titulo": m.titulo, "descricao": m.descricao, "tipo": m.tipo,
            "link": m.link, "imagem_url": m.imagem_url, "autor_nome": m.autor_nome,
            "autor_id": m.autor_id, "criado_em": dt(d.criado_em), "situacao": d.situacao,
            "aprovado_em": dt(d.aprovado_em), "aprovado_por": d.aprovado_por,
            "aberto_em": dt(d.aberto_em), "visto_em": dt(d.visto_em), "removido_em": dt(d.removido_em),
            "acesso": "visto" if d.visto_em else "aberto" if d.aberto_em else "novo",
            "pode_editar": bool(autor), "pode_excluir": bool(autor or principal),
            "pode_aprovar": bool(principal and d.situacao == "pendente"),
        }

    def listar(self, payload, usuario_id, limite=50, inicio=0):
        with self.repository.transacao() as repo:
            ator, vinculo = self._ator(repo, payload, usuario_id)
            principal = bool(vinculo and vinculo.principal)
            cuidador_id = ator.id if vinculo is not None else None
            materiais, total = repo.listar(usuario_id, cuidador_id, principal, limite, inicio)
            return {"sucesso": True, "materiais": [self._resumo(d, ator, vinculo) for d in materiais],
                    "total": total, "inicio": inicio, "limite": limite,
                    "principal": principal, "tipos": repo.tipos(usuario_id, cuidador_id, principal)}

    def criar(self, payload, usuario_ids, dados):
        ids = list(dict.fromkeys(usuario_ids))
        if not ids or len(ids) > 20 or any(type(i) is not int or i < 1 for i in ids):
            raise ErroMaterial("Escolha de 1 a 20 perfis destinatários válidos.")
        valores = self._dados(dados)
        # Confere todos antes de consultar a prévia ou gravar qualquer coisa.
        with self.repository.transacao() as repo:
            for usuario_id in ids:
                self._cuidador(repo, payload, usuario_id)
        if not valores["imagem_url"]:
            valores["imagem_url"] = self.previa.obter(valores["link"])["imagem_url"]
        with self.repository.transacao() as repo:
            acessos = [(usuario_id, *self._cuidador(repo, payload, usuario_id)) for usuario_id in ids]
            ator = acessos[0][1]
            material = repo.novo_material(**valores, autor_id=ator.id, autor_nome=ator.nome)
            lista = []
            for usuario_id, ator, vinculo in acessos:
                direto = bool(vinculo.principal or vinculo.pode_enviar_materiais_sem_aprovacao)
                d = repo.novo_destinatario(material, usuario_id=usuario_id,
                    situacao="aprovado" if direto else "pendente",
                    aprovado_por=ator.id if direto else None, aprovado_em=datetime.now(timezone.utc).replace(tzinfo=None) if direto else None)
                lista.append(self._resumo(d, ator, vinculo))
            return {"sucesso": True, "mensagem": "Material enviado.", "materiais": lista}

    def editar(self, payload, usuario_id, destinatario_id, dados):
        valores = self._dados(dados)
        with self.repository.transacao() as repo:
            ator, vinculo = self._cuidador(repo, payload, usuario_id)
            d = repo.destinatario(destinatario_id, usuario_id, bloquear=True)
            if d is None:
                raise ErroMaterial("Material não encontrado.", 404)
            if d.material.autor_id != ator.id:
                raise ErroMaterial("Somente quem enviou pode editar este material.", 403)
            # Uma edição cria uma revisão apenas para este perfil e exige nova aprovação.
            direto = bool(vinculo.principal or vinculo.pode_enviar_materiais_sem_aprovacao)
            repo.substituir_material(d, **valores, autor_id=ator.id, autor_nome=ator.nome)
            d.situacao = "aprovado" if direto else "pendente"
            d.aprovado_por = ator.id if direto else None
            d.aprovado_em = datetime.now(timezone.utc).replace(tzinfo=None) if direto else None
            d.aberto_em = d.visto_em = None
            # Remover da lista é uma escolha do usuário; editar não desfaz essa escolha.
            return {"sucesso": True, "mensagem": "Material atualizado.", "material": self._resumo(d, ator, vinculo)}

    def decidir(self, payload, usuario_id, destinatario_id, aprovar):
        with self.repository.transacao() as repo:
            ator, vinculo = self._cuidador(repo, payload, usuario_id)
            if not vinculo.principal:
                raise ErroMaterial("Somente o cuidador principal pode aprovar ou recusar materiais.", 403)
            d = repo.destinatario(destinatario_id, usuario_id, bloquear=True)
            if d is None:
                raise ErroMaterial("Material não encontrado.", 404)
            if d.situacao != "pendente":
                raise ErroMaterial("Este material já foi analisado. Atualize a lista.", 409)
            d.situacao = "aprovado" if aprovar else "recusado"
            d.aprovado_por = ator.id if aprovar else None
            d.aprovado_em = datetime.now(timezone.utc).replace(tzinfo=None) if aprovar else None
            return {"sucesso": True, "mensagem": "Material aprovado." if aprovar else "Material recusado."}

    def registrar(self, payload, usuario_id, destinatario_id, acao):
        with self.repository.transacao() as repo:
            ator, vinculo = self._ator(repo, payload, usuario_id)
            if vinculo is not None:
                raise ErroMaterial("Entre no perfil TEA para registrar uma leitura ou remover da própria lista.", 403)
            d = repo.destinatario(destinatario_id, usuario_id, bloquear=True)
            if d is None or d.situacao != "aprovado" or d.removido_em is not None:
                raise ErroMaterial("Material não encontrado.", 404)
            agora = datetime.now(timezone.utc).replace(tzinfo=None)
            if acao == "abrir":
                d.aberto_em = d.aberto_em or agora
            elif acao == "visto":
                d.visto_em = d.visto_em or agora
            elif acao == "remover":
                d.removido_em = agora
            else:
                raise ErroMaterial("Operação inválida.")
            return {"sucesso": True, "material": self._resumo(d, ator, vinculo)}

    def excluir(self, payload, usuario_id, destinatario_id):
        with self.repository.transacao() as repo:
            ator, vinculo = self._cuidador(repo, payload, usuario_id)
            d = repo.destinatario(destinatario_id, usuario_id, bloquear=True)
            if d is None:
                raise ErroMaterial("Material não encontrado.", 404)
            if not vinculo.principal and d.material.autor_id != ator.id:
                raise ErroMaterial("Somente o autor ou o cuidador principal pode excluir este material.", 403)
            repo.excluir(d)
            return {"sucesso": True, "mensagem": "Material excluído deste perfil."}
