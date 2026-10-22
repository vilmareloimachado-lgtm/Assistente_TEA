"""Prévia opcional de links públicos, com limites de tempo, tamanho e redirecionamento."""

import http.client
import ipaddress
import socket
import ssl
import time
from html.parser import HTMLParser
from urllib.parse import urljoin, urlsplit


def validar_link(link):
    link = (link or "").strip()
    if not link or len(link) > 2048 or any(ord(c) < 33 for c in link) or "\\" in link:
        raise ValueError("Informe um link válido, com até 2048 caracteres e sem espaços.")
    try:
        url = urlsplit(link)
        porta = url.port
        host = (url.hostname or "").encode("idna").decode("ascii").lower().rstrip(".")
        if url.scheme not in ("http", "https") or not host or url.username is not None or url.password is not None:
            raise ValueError
        if porta not in (None, 80, 443) or host in ("localhost", "localhost.localdomain") or host.endswith((".localhost", ".local", ".internal")):
            raise ValueError
        try:
            ip = ipaddress.ip_address(host)
        except ValueError:
            if "." not in host or any(c not in "abcdefghijklmnopqrstuvwxyz0123456789-." for c in host):
                raise ValueError
        else:
            if not ip.is_global or (getattr(ip, "ipv4_mapped", None) and not ip.ipv4_mapped.is_global):
                raise ValueError
    except (ValueError, UnicodeError):
        raise ValueError("Use um link público começando com https:// ou http://.") from None
    return link


class _Metadados(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.meta = {}
        self.titulo = []
        self.em_titulo = False

    def handle_starttag(self, tag, attrs):
        dados = {k.lower(): v for k, v in attrs if v is not None}
        if tag == "meta":
            chave = (dados.get("property") or dados.get("name") or "").lower()
            self.meta.setdefault(chave, dados.get("content", ""))
        if tag == "title":
            self.em_titulo = True

    def handle_endtag(self, tag):
        if tag == "title":
            self.em_titulo = False

    def handle_data(self, data):
        if self.em_titulo:
            self.titulo.append(data)


class PreviaLinkService:
    LIMITE = 262144
    TIMEOUT = 3

    def _enderecos_publicos(self, host, porta):
        enderecos = socket.getaddrinfo(host, porta, type=socket.SOCK_STREAM)
        if not enderecos:
            raise ValueError("Endereço indisponível.")
        for item in enderecos:
            ip = ipaddress.ip_address(item[4][0])
            if not ip.is_global or (getattr(ip, "ipv4_mapped", None) and not ip.ipv4_mapped.is_global):
                raise ValueError("A prévia aceita apenas endereços públicos.")
        return enderecos[0][4][0]

    def _baixar(self, link):
        prazo = time.monotonic() + 8
        for _ in range(4):
            if time.monotonic() >= prazo:
                return None
            validar_link(link)
            url = urlsplit(link)
            host = url.hostname.encode("idna").decode("ascii")
            porta = url.port or (443 if url.scheme == "https" else 80)
            ip = self._enderecos_publicos(host, porta)
            if url.scheme == "https":
                conexao = http.client.HTTPSConnection(host, porta, timeout=self.TIMEOUT, context=ssl.create_default_context())
            else:
                conexao = http.client.HTTPConnection(host, porta, timeout=self.TIMEOUT)
            # Fixa o IP validado; o nome original continua sendo usado no TLS e no Host.
            conexao._create_connection = lambda addr, timeout, source_address=None, ip=ip, porta=porta: socket.create_connection((ip, porta), timeout, source_address)
            try:
                caminho = url.path or "/"
                if url.query:
                    caminho += "?" + url.query
                conexao.request("GET", caminho, headers={
                    "User-Agent": "doroTEA-LinkPreview/1.0", "Accept": "text/html", "Accept-Encoding": "identity"
                })
                resposta = conexao.getresponse()
                if resposta.status in (301, 302, 303, 307, 308):
                    local = resposta.getheader("Location")
                    if not local:
                        return None
                    link = urljoin(link, local)
                    continue
                if resposta.status != 200 or "text/html" not in (resposta.getheader("Content-Type") or "").lower():
                    return None
                partes, tamanho = [], 0
                while tamanho < self.LIMITE:
                    if time.monotonic() >= prazo:
                        return None
                    parte = resposta.read1(min(8192, self.LIMITE - tamanho))
                    if not parte:
                        break
                    partes.append(parte)
                    tamanho += len(parte)
                return link, b"".join(partes).decode("utf-8", errors="replace")
            finally:
                conexao.close()
        return None

    def obter(self, link):
        link = validar_link(link)
        resultado = {"link": link, "titulo": "", "descricao": "", "imagem_url": None}
        try:
            pagina = self._baixar(link)
            if pagina is None:
                return resultado
            url_final, html = pagina
            parser = _Metadados()
            parser.feed(html)
            resultado["titulo"] = (parser.meta.get("og:title") or "".join(parser.titulo)).strip()[:200]
            resultado["descricao"] = (parser.meta.get("og:description") or parser.meta.get("description") or "").strip()[:2000]
            imagem = parser.meta.get("og:image:secure_url") or parser.meta.get("og:image") or parser.meta.get("twitter:image")
            if imagem:
                imagem = validar_link(urljoin(url_final, imagem))
                url = urlsplit(imagem)
                self._enderecos_publicos(url.hostname, url.port or (443 if url.scheme == "https" else 80))
                resultado["imagem_url"] = imagem
        except (OSError, ValueError, http.client.HTTPException, UnicodeError):
            # Site sem prévia, bloqueio ou indisponibilidade nunca impedem o cadastro.
            pass
        return resultado
