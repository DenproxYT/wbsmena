import json
import os
import re
from html import unescape
from typing import Any, Dict, List, Optional, Set
from html.parser import HTMLParser
from urllib.error import HTTPError, URLError
from io import BytesIO
from urllib.parse import parse_qsl, unquote, urlencode, urljoin, urlparse
from urllib.request import Request, urlopen

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from apps.training.models import TrainingMaterial, TrainingSlide


def _load_dotenv_if_present():
    try:
        from dotenv import load_dotenv

        env_path = settings.BASE_DIR / ".env"
        if env_path.is_file():
            load_dotenv(env_path)
    except Exception:
        pass


def _get_x_auth_key(cli_value: Optional[str]) -> str:
    """
    Ключ для заголовка X-Auth-Key (как в DevTools после входа на edtech.rwb.ru).
    Не храните ключ в репозитории — только в .env или переменной окружения.
    """
    _load_dotenv_if_present()
    v = (cli_value or "").strip()
    if v:
        return v
    return (
        os.environ.get("RWB_EDTECH_X_AUTH_KEY", "").strip()
        or os.environ.get("EDTECH_X_AUTH_KEY", "").strip()
    )


def _get_cookie_header() -> str:
    _load_dotenv_if_present()
    return (
        os.environ.get("RWB_EDTECH_COOKIE", "").strip()
        or os.environ.get("EDTECH_COOKIE", "").strip()
    )


def _extract_wbaas_token(cookie_header: str) -> str:
    """Берёт последний x_wbaas_token из строки Cookie (в браузере иногда дублируется)."""
    if not cookie_header:
        return ""
    matches = re.findall(r"x_wbaas_token=([^;]+)", cookie_header, flags=re.IGNORECASE)
    if not matches:
        return ""
    return matches[-1].strip()


def _is_lms_block_url(url: str) -> bool:
    p = urlparse(url).path.lower()
    return "/lms/ru/block/" in p


def _headers_for_url(url: str, base_extra: Dict[str, str], cookie_header: str) -> Dict[str, str]:
    """
    Для /lms/ru/block/... нужны те же заголовки, что у XHR в браузере:
    Referer с courselist, X-Requested-With, x-wbaas-token из cookie.
    """
    h = dict(base_extra)
    if _is_lms_block_url(url):
        h["Referer"] = os.environ.get(
            "RWB_BLOCK_REFERER", "https://edtech.rwb.ru/lms/ru/courselist"
        ).strip()
        h["X-Requested-With"] = "XMLHttpRequest"
        wt = os.environ.get("RWB_WBAASS_TOKEN", "").strip() or _extract_wbaas_token(cookie_header)
        if wt:
            h["x-wbaas-token"] = wt
    return h


def _decompress_body(raw: bytes, content_encoding: str) -> bytes:
    enc = (content_encoding or "").lower()
    if "br" in enc:
        try:
            import brotli

            return brotli.decompress(raw)
        except ImportError:
            raise RuntimeError("Установите пакет brotli: pip install brotli") from None
    if "gzip" in enc:
        import gzip

        return gzip.decompress(raw)
    if "deflate" in enc:
        import zlib

        return zlib.decompress(raw)
    return raw


def _parse_embedded_json_scripts(html: str) -> List[dict]:
    """JSON из <script type="application/json"> и ld+json (часто данные без __NEXT_DATA__)."""
    out: List[dict] = []
    for m in re.finditer(
        r'<script[^>]*type=["\']application/json["\'][^>]*>(.*?)</script>',
        html,
        re.DOTALL | re.IGNORECASE,
    ):
        raw = m.group(1).strip()
        try:
            out.append(json.loads(raw))
        except json.JSONDecodeError:
            continue
    for m in re.finditer(
        r'<script[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
        html,
        re.DOTALL | re.IGNORECASE,
    ):
        raw = m.group(1).strip()
        try:
            data = json.loads(raw)
            if isinstance(data, list):
                for item in data:
                    if isinstance(item, dict):
                        out.append(item)
            elif isinstance(data, dict):
                out.append(data)
        except json.JSONDecodeError:
            continue
    return out


def _normalize_crawl_url(url: str) -> str:
    """
    Стабильный URL для очереди обхода.
    ВАЖНО: /lms/ru/course?publicationid=...&unitid=... — разные курсы;
    если отбросить query, все схлопнутся в один URL и запарсится только одна страница.
    """
    p = urlparse(url)
    path = p.path or "/"
    path_trim = path.rstrip("/") or "/"
    if path_trim == "/lms/ru/course" or path_trim.endswith("/course"):
        pairs = parse_qsl(p.query, keep_blank_values=True)
        pairs.sort(key=lambda x: (x[0], x[1]))
        q = urlencode(pairs)
        return f"{p.scheme}://{p.netloc}{path}" + (f"?{q}" if q else "")
    out = f"{p.scheme}://{p.netloc}{path_trim}"
    return out.rstrip("/") if path_trim != "/" else out


def _harvest_urls_from_raw_html(
    html: str, base_origin: str, follow_prefix: str
) -> List[str]:
    """Ссылки из HTML, которые HTMLParser мог пропустить (SPA, кривая вёрстка)."""
    netloc = urlparse(base_origin).netloc
    found: List[str] = []
    seen: Set[str] = set()
    patterns = (
        r'href\s*=\s*["\']([^"\']+)["\']',
        r'src\s*=\s*["\']([^"\']+)["\']',
        r'["\'](/lms/[^"\']+)["\']',
        r'["\'](/api/[^"\']+)["\']',
    )
    for pattern in patterns:
        for m in re.finditer(pattern, html, re.IGNORECASE):
            href = m.group(1).strip()
            if not href or href.startswith("#") or href.lower().startswith("javascript"):
                continue
            if href.startswith("//"):
                href = "https:" + href
            full = urljoin(base_origin + "/", href)
            parsed = urlparse(full)
            if parsed.netloc != netloc:
                continue
            path_only = (parsed.path or "/").rstrip("/") or "/"
            fp = follow_prefix.rstrip("/")
            if not path_only.startswith(fp) and path_only != fp:
                continue
            clean = _normalize_crawl_url(full)
            if clean not in seen:
                seen.add(clean)
                found.append(clean)
    return found


def _looks_like_pdf_url(url: str) -> bool:
    u = url.lower()
    if ".pdf" in u.split("?", 1)[0]:
        return True
    if "format=pdf" in u or "type=pdf" in u:
        return True
    p = urlparse(url).path.lower()
    return p.endswith(".pdf") or "/pdf/" in p


def _harvest_pdf_urls_from_html(html: str, base_url: str) -> List[str]:
    found: List[str] = []
    seen: Set[str] = set()
    for m in re.finditer(r'href\s*=\s*["\']([^"\']+)["\']', html, re.I):
        href = m.group(1).strip()
        if not href or href.startswith("#") or "javascript:" in href.lower():
            continue
        full = urljoin(base_url, href)
        if _looks_like_pdf_url(full) and full not in seen:
            seen.add(full)
            found.append(full)
    for m in re.finditer(r'https?://[^\s"\'<>\)]+\.pdf[^\s"\'<>\)]*', html, re.I):
        u = m.group(0).rstrip(".,);")
        if u not in seen:
            seen.add(u)
            found.append(u)
    return found


def _collect_pdf_urls_from_json(
    obj: Any,
    out: List[str],
    base: str,
    seen: Set[str],
    seen_ids: Optional[Set[int]] = None,
    depth: int = 0,
) -> None:
    if depth > 40:
        return
    if seen_ids is None:
        seen_ids = set()
    oid = id(obj)
    if oid in seen_ids:
        return
    seen_ids.add(oid)

    if isinstance(obj, str):
        s = obj.strip()
        if s.startswith("http") and _looks_like_pdf_url(s) and s not in seen:
            seen.add(s)
            out.append(s)
        elif s.startswith("/") and _looks_like_pdf_url(s):
            full = urljoin(base, s)
            if full not in seen:
                seen.add(full)
                out.append(full)
    elif isinstance(obj, dict):
        for k, v in obj.items():
            lk = k.lower()
            if isinstance(v, str) and lk in (
                "fileurl",
                "pdfurl",
                "file",
                "url",
                "downloadurl",
                "src",
                "href",
                "attachmenturl",
                "documenturl",
            ):
                if _looks_like_pdf_url(v):
                    if v.startswith("http") and v not in seen:
                        seen.add(v)
                        out.append(v)
                    elif v.startswith("/"):
                        full = urljoin(base, v)
                        if full not in seen:
                            seen.add(full)
                            out.append(full)
            _collect_pdf_urls_from_json(v, out, base, seen, seen_ids, depth + 1)
    elif isinstance(obj, (list, tuple)):
        for item in obj:
            _collect_pdf_urls_from_json(item, out, base, seen, seen_ids, depth + 1)


def _pdf_bytes_to_page_texts(pdf_bytes: bytes) -> List[str]:
    from pypdf import PdfReader

    reader = PdfReader(BytesIO(pdf_bytes))
    pages: List[str] = []
    for page in reader.pages:
        t = page.extract_text() or ""
        pages.append(t)
    return pages


def _pdf_title_from_url(url: str, fallback: str) -> str:
    path = urlparse(url).path
    name = unquote(path.split("/")[-1] or "")
    if name.lower().endswith(".pdf"):
        return name[:-4][:255] or fallback[:255]
    return (fallback or "Документ PDF")[:255]


def _is_welcome_shell_material(title: str, content: str) -> bool:
    """Один экран «Добро пожаловать» без полезной базы — не материал для сохранения, если есть лучше."""
    t = (title or "").strip().lower()
    if t != "добро пожаловать":
        return False
    c = (content or "").lower()
    if len(content or "") > 8000:
        return False
    if "телефон" in c or "войти" in c or "вход" in c or "wildberries" in c:
        return True
    return len(content or "") < 400


def _extract_next_data(html: str) -> Optional[dict]:
    m = re.search(
        r'<script[^>]*\bid=["\']__NEXT_DATA__["\'][^>]*>(.*?)</script>',
        html,
        re.DOTALL | re.IGNORECASE,
    )
    if not m:
        return None
    try:
        return json.loads(m.group(1).strip())
    except json.JSONDecodeError:
        return None


def _collect_strings_from_json(
    obj: Any,
    out: List[str],
    seen_ids: Optional[Set[int]] = None,
    max_strings: int = 800,
) -> None:
    if seen_ids is None:
        seen_ids = set()
    oid = id(obj)
    if oid in seen_ids or len(out) >= max_strings:
        return
    seen_ids.add(oid)

    if isinstance(obj, str):
        t = " ".join(obj.split()).strip()
        if len(t) >= 3 and not t.startswith("http"):
            out.append(t)
    elif isinstance(obj, dict):
        for v in obj.values():
            _collect_strings_from_json(v, out, seen_ids, max_strings)
    elif isinstance(obj, (list, tuple)):
        for item in obj:
            _collect_strings_from_json(item, out, seen_ids, max_strings)


def _collect_urls_from_json(
    obj: Any, base: str, out: List[str], seen_ids: Optional[Set[int]] = None
) -> None:
    if seen_ids is None:
        seen_ids = set()
    oid = id(obj)
    if oid in seen_ids:
        return
    seen_ids.add(oid)

    if isinstance(obj, str):
        if obj.startswith("/lms/"):
            out.append(urljoin(base, obj.split("?", 1)[0]).rstrip("/"))
        elif "edtech.rwb.ru" in obj:
            out.append(obj.split("?", 1)[0].rstrip("/"))
    elif isinstance(obj, dict):
        for k, v in obj.items():
            if k.lower() in ("href", "url", "path", "slug", "link", "permalink") and isinstance(v, str):
                if v.startswith("/"):
                    out.append(urljoin(base, v.split("?", 1)[0]).rstrip("/"))
                elif "edtech.rwb.ru" in v:
                    out.append(v.split("?", 1)[0].rstrip("/"))
            _collect_urls_from_json(v, base, out, seen_ids)
    elif isinstance(obj, (list, tuple)):
        for item in obj:
            _collect_urls_from_json(item, base, out, seen_ids)


def _collect_api_url_strings(obj: Any, out: List[str], seen_ids: Optional[Set[int]] = None) -> None:
    """Ищет в JSON строки-URL вида /api/... для запросов с теми же заголовками."""
    if seen_ids is None:
        seen_ids = set()
    oid = id(obj)
    if oid in seen_ids:
        return
    seen_ids.add(oid)

    if isinstance(obj, str):
        s = obj.strip()
        if "/api/" in s and s.startswith("/") and " " not in s and len(s) < 500:
            out.append(s.split("?", 1)[0])
        elif "edtech.rwb.ru" in s and "/api/" in s:
            out.append(s.split("?", 1)[0])
    elif isinstance(obj, dict):
        for v in obj.values():
            _collect_api_url_strings(v, out, seen_ids)
    elif isinstance(obj, (list, tuple)):
        for item in obj:
            _collect_api_url_strings(item, out, seen_ids)


def _extract_article_like_blocks(
    obj: Any,
    out: List[Dict[str, str]],
    seen_ids: Optional[Set[int]] = None,
    depth: int = 0,
) -> None:
    """
    Ищет в дереве JSON объекты похожие на статьи (title + текст).
    Используется для данных React Query в __NEXT_DATA__.
    """
    if depth > 40:
        return
    if seen_ids is None:
        seen_ids = set()
    oid = id(obj)
    if oid in seen_ids:
        return
    seen_ids.add(oid)

    if isinstance(obj, dict):
        lower = {k.lower(): k for k in obj.keys()}
        title_key = lower.get("title") or lower.get("name") or lower.get("heading")
        body_key = (
            lower.get("content")
            or lower.get("body")
            or lower.get("text")
            or lower.get("html")
            or lower.get("markdown")
            or lower.get("description")
            or lower.get("preview")
            or lower.get("abstract")
        )
        if title_key and body_key:
            raw_title = obj.get(title_key)
            raw_body = obj.get(body_key)
            if isinstance(raw_title, str) and isinstance(raw_body, str):
                t = " ".join(raw_title.split()).strip()
                b = raw_body.strip()
                if len(t) >= 3 and len(b) >= 15:
                    if t.lower() in ("учебный центр rwb",):
                        pass
                    elif t.lower() == "добро пожаловать" and len(b) < 80:
                        pass
                    else:
                        out.append({"title": t[:255], "content": b})

        for v in obj.values():
            _extract_article_like_blocks(v, out, seen_ids, depth + 1)

    elif isinstance(obj, (list, tuple)):
        for item in obj:
            _extract_article_like_blocks(item, out, seen_ids, depth + 1)


def _merge_api_materials(
    pages_data: List[Dict[str, Any]], api_items: List[Dict[str, str]]
) -> List[Dict[str, Any]]:
    """Добавляет материалы из API, не дублируя по title."""
    existing = {p["title"].strip().lower() for p in pages_data}
    for item in api_items:
        key = item["title"].strip().lower()
        if key and key not in existing:
            existing.add(key)
            pages_data.append(
                {
                    "url": "https://edtech.rwb.ru/lms/ru/knowledge-base",
                    "title": item["title"],
                    "description": "",
                    "content": item["content"],
                }
            )
    return pages_data


class PlainTextHTMLParser(HTMLParser):
    """Видимый текст страницы (если контент в div без h1/p)."""

    def __init__(self):
        super().__init__()
        self._skip_depth = 0
        self.chunks: List[str] = []

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style", "noscript", "svg"):
            self._skip_depth += 1

    def handle_endtag(self, tag):
        if tag in ("script", "style", "noscript", "svg"):
            self._skip_depth = max(0, self._skip_depth - 1)

    def handle_data(self, data):
        if self._skip_depth:
            return
        t = " ".join(data.split()).strip()
        if len(t) >= 2:
            self.chunks.append(t)

    def plain_text(self) -> str:
        lines: List[str] = []
        seen: Set[str] = set()
        for c in self.chunks:
            if c not in seen:
                seen.add(c)
                lines.append(c)
        return "\n\n".join(lines)


class KnowledgeBaseHTMLParser(HTMLParser):
    """
    Lightweight parser for extracting readable sections from KB pages.
    """

    def __init__(self):
        super().__init__()
        self.page_title = ""
        self.heading = ""
        self.description = ""
        self.blocks = []
        self.links = []
        self._tag_stack = []
        self._text_buffer = []
        self._active_link = None
        self._active_link_text = []
        self._seen_links = set()

    def handle_starttag(self, tag, attrs):
        self._tag_stack.append(tag)
        attrs_dict = dict(attrs)
        if tag == "a":
            href = (attrs_dict.get("href") or "").strip()
            self._active_link = href or None
            self._active_link_text = []

    def handle_endtag(self, tag):
        if tag in {"title", "h1", "h2", "h3", "h4", "p", "li"}:
            text = self._normalize("".join(self._text_buffer))
            if text:
                if tag == "title" and not self.page_title:
                    self.page_title = text
                elif tag == "h1" and not self.heading:
                    self.heading = text
                    self.blocks.append(f"# {text}")
                elif tag in {"h2", "h3", "h4"}:
                    self.blocks.append(f"## {text}")
                elif tag == "p":
                    if not self.description:
                        self.description = text
                    self.blocks.append(text)
                elif tag == "li":
                    self.blocks.append(f"- {text}")
            self._text_buffer = []

        if tag == "a":
            link_text = self._normalize("".join(self._active_link_text))
            self.record_link_text(link_text)
            self._active_link = None
            self._active_link_text = []

        if self._tag_stack and self._tag_stack[-1] == tag:
            self._tag_stack.pop()
        elif tag in self._tag_stack:
            self._tag_stack.remove(tag)

    def handle_data(self, data):
        if any(t in {"title", "h1", "h2", "h3", "h4", "p", "li", "a"} for t in self._tag_stack):
            self._text_buffer.append(data)
        if self._active_link is not None:
            self._active_link_text.append(data)

    def handle_entityref(self, name):
        self._text_buffer.append(unescape(f"&{name};"))

    def handle_charref(self, name):
        self._text_buffer.append(unescape(f"&#{name};"))

    def _normalize(self, value: str) -> str:
        text = " ".join(value.split())
        return text.strip()

    def record_link_text(self, text: str):
        href = self._active_link or ""
        text = self._normalize(text)
        if not href or not text:
            return
        key = (href, text)
        if key in self._seen_links:
            return
        self._seen_links.add(key)
        self.links.append((href, text))


class Command(BaseCommand):
    help = (
        "Полностью пересобирает обучение: удаляет текущие материалы и парсит "
        "все доступные страницы раздела knowledge-base с edtech.rwb.ru."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--url",
            type=str,
            default="https://edtech.rwb.ru/lms/ru/knowledge-base",
            help="Стартовая ссылка для парсинга.",
        )
        parser.add_argument(
            "--module-title",
            type=str,
            default="База знаний RWB",
            help="Название модуля, в который будут записаны материалы.",
        )
        parser.add_argument(
            "--keep-existing",
            action="store_true",
            help="Не удалять старые материалы перед импортом.",
        )
        parser.add_argument(
            "--limit",
            type=int,
            default=150,
            help="Лимит страниц для обхода, чтобы избежать бесконечного сканирования.",
        )
        parser.add_argument(
            "--x-auth-key",
            type=str,
            default="",
            help=(
                "Значение заголовка X-Auth-Key (как в Network после входа на edtech.rwb.ru). "
                "Безопаснее задать переменную окружения RWB_EDTECH_X_AUTH_KEY или строку в .env."
            ),
        )
        parser.add_argument(
            "--cookie",
            type=str,
            default="",
            help=(
                "Заголовок Cookie целиком (как в DevTools → Network → Cookie). "
                "Или переменная окружения RWB_EDTECH_COOKIE в .env."
            ),
        )
        parser.add_argument(
            "--follow-prefix",
            type=str,
            default="/lms/ru",
            help=(
                "Обходить только ссылки на тот же домен с путём, начинающимся с этого префикса "
                "(по умолчанию /lms/ru — шире, чем только knowledge-base)."
            ),
        )
        parser.add_argument(
            "--pvz-knowledge-block",
            action="store_true",
            dest="pvz_knowledge_block",
            help=(
                "Старт с HTML-блока базы знаний ПВЗ: "
                "/lms/ru/block/lms2_pvz_knowledge-base_v1 (см. RWB_PVZ_BLOCK_URL в .env)."
            ),
        )
        parser.add_argument(
            "--dump-first-html",
            type=str,
            default="",
            dest="dump_first_html",
            metavar="PATH",
            help="Сохранить HTML первой успешно загруженной страницы в файл (для отладки).",
        )
        parser.add_argument(
            "--urls-file",
            type=str,
            default="",
            dest="urls_file",
            metavar="PATH",
            help=(
                "Текстовый файл: по одному полному URL страницы курса в строке "
                "(с publicationid и unitid), чтобы обойти ссылки, которые не попали в HTML."
            ),
        )
        parser.add_argument(
            "--no-pdf",
            action="store_true",
            dest="no_pdf",
            help="Не скачивать и не разбирать PDF (только HTML/JSON).",
        )
        parser.add_argument(
            "--max-pdfs",
            type=int,
            default=300,
            dest="max_pdfs",
            help="Максимум PDF-файлов за один импорт.",
        )

    def handle(self, *args, **options):
        start_url = options["url"].strip()
        if options.get("pvz_knowledge_block"):
            start_url = os.environ.get(
                "RWB_PVZ_BLOCK_URL",
                "https://edtech.rwb.ru/lms/ru/block/lms2_pvz_knowledge-base_v1",
            ).strip()
            self.stdout.write(
                self.style.HTTP_INFO(f"Режим блока ПВЗ: стартовый URL = {start_url}")
            )
        start_url = _normalize_crawl_url(start_url)
        module_title = options["module_title"].strip() or "База знаний RWB"
        keep_existing = bool(options["keep_existing"])
        limit = max(1, int(options.get("limit") or 150))
        x_auth_key = _get_x_auth_key(options.get("x_auth_key") or None)
        cookie_header = (options.get("cookie") or "").strip() or _get_cookie_header()
        follow_prefix = (options.get("follow_prefix") or "/lms/ru").strip() or "/lms/ru"

        extra_headers: Dict[str, str] = {}
        if x_auth_key:
            extra_headers["X-Auth-Key"] = x_auth_key
            self.stdout.write(self.style.HTTP_INFO("Используется заголовок X-Auth-Key (авторизованные запросы)."))
        if cookie_header:
            extra_headers["Cookie"] = cookie_header
            self.stdout.write(self.style.HTTP_INFO("Используется заголовок Cookie (сессия браузера)."))

        parsed_start = urlparse(start_url)
        if not parsed_start.scheme or not parsed_start.netloc:
            raise CommandError("Некорректный URL для парсинга.")

        base_origin = f"{parsed_start.scheme}://{parsed_start.netloc}"

        if not keep_existing:
            deleted_count, _ = TrainingMaterial.objects.all().delete()
            self.stdout.write(self.style.WARNING(f"Удалены все текущие обучения: {deleted_count} объектов."))

        self.stdout.write(self.style.MIGRATE_HEADING(f"Парсинг материалов из: {start_url}"))

        queue = [start_url]
        if options.get("pvz_knowledge_block"):
            for extra in (
                f"{base_origin}/lms/ru/knowledge-base",
                f"{base_origin}/lms/ru/courselist",
            ):
                eu = _normalize_crawl_url(extra)
                if eu.rstrip("/") != start_url.rstrip("/") and eu not in queue:
                    queue.append(eu)
            self.stdout.write(
                self.style.HTTP_INFO(
                    "В очередь добавлены страницы knowledge-base и courselist для обхода ссылок."
                )
            )

        urls_file = (options.get("urls_file") or "").strip()
        if urls_file:
            from pathlib import Path

            path = Path(urls_file)
            if not path.is_file():
                raise CommandError(f"Файл со списком URL не найден: {urls_file}")
            added = 0
            for line in path.read_text(encoding="utf-8").splitlines():
                u = line.strip()
                if not u or u.startswith("#"):
                    continue
                if u.startswith("http"):
                    nu = _normalize_crawl_url(u)
                    if nu not in queue:
                        queue.append(nu)
                        added += 1
            self.stdout.write(
                self.style.HTTP_INFO(f"Из файла добавлено URL в очередь: {added} ({urls_file})")
            )

        visited = set()
        pages_data = []
        api_url_queue: Set[str] = set()
        articles_from_json: List[Dict[str, str]] = []
        dump_first_html = (options.get("dump_first_html") or "").strip()
        dumped_first = False

        import_pdfs = not bool(options.get("no_pdf"))
        max_pdfs = max(1, int(options.get("max_pdfs") or 300))
        pdf_seen: Set[str] = set()
        pdf_materials_queue: List[Dict[str, Any]] = []

        if import_pdfs:
            self.stdout.write(
                self.style.HTTP_INFO(
                    "Импорт PDF включён: текст со страниц PDF → слайды (нужны Cookie + доступ к файлам)."
                )
            )

        while queue and len(visited) < limit:
            current_url = queue.pop(0)
            if current_url in visited:
                continue
            visited.add(current_url)

            req_headers = _headers_for_url(current_url, extra_headers, cookie_header)
            html, fetch_err = self._fetch_url(
                current_url,
                extra_headers=req_headers,
                accept="text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            )
            if not html:
                msg = f"  Пропущено (не удалось получить HTML): {current_url}"
                if fetch_err:
                    msg += f" — {fetch_err}"
                self.stdout.write(self.style.WARNING(msg))
                continue

            if dump_first_html and not dumped_first:
                try:
                    from pathlib import Path

                    Path(dump_first_html).write_text(html, encoding="utf-8")
                    dumped_first = True
                    self.stdout.write(
                        self.style.HTTP_INFO(f"Первый HTML сохранён в {dump_first_html} (для отладки).")
                    )
                except OSError as e:
                    self.stdout.write(self.style.WARNING(f"Не удалось сохранить HTML: {e}"))

            parser = KnowledgeBaseHTMLParser()
            parser.feed(html)

            page_title = parser.heading or parser.page_title or "Материал"
            page_description = parser.description
            content = "\n\n".join(parser.blocks).strip()

            next_data = _extract_next_data(html)
            json_urls: List[str] = []
            if next_data:
                nd_strings: List[str] = []
                _collect_strings_from_json(next_data, nd_strings)
                nd_text = "\n\n".join(dict.fromkeys(nd_strings))
                if len(nd_text) > len(content):
                    content = nd_text
                elif not content.strip() and nd_text.strip():
                    content = nd_text.strip()
                _collect_urls_from_json(next_data, base_origin, json_urls)

                blocks: List[Dict[str, str]] = []
                _extract_article_like_blocks(next_data, blocks)
                for b in blocks:
                    articles_from_json.append(b)

                api_strings: List[str] = []
                _collect_api_url_strings(next_data, api_strings)
                for s in api_strings:
                    full = urljoin(base_origin, s) if s.startswith("/") else s
                    if full.startswith(base_origin) and full not in visited:
                        api_url_queue.add(full.split("?", 1)[0])

            for emb in _parse_embedded_json_scripts(html):
                nd_strings_emb: List[str] = []
                _collect_strings_from_json(emb, nd_strings_emb)
                nd_text_emb = "\n\n".join(dict.fromkeys(nd_strings_emb))
                if len(nd_text_emb) > len(content):
                    content = nd_text_emb
                elif not content.strip() and nd_text_emb.strip():
                    content = nd_text_emb.strip()
                ej_urls: List[str] = []
                _collect_urls_from_json(emb, base_origin, ej_urls)
                json_urls.extend(ej_urls)
                blocks_emb: List[Dict[str, str]] = []
                _extract_article_like_blocks(emb, blocks_emb)
                for b in blocks_emb:
                    articles_from_json.append(b)
                api_emb: List[str] = []
                _collect_api_url_strings(emb, api_emb)
                for s in api_emb:
                    full = urljoin(base_origin, s) if s.startswith("/") else s
                    if full.startswith(base_origin) and full not in visited:
                        api_url_queue.add(full.split("?", 1)[0])

            if not content.strip():
                ptp = PlainTextHTMLParser()
                ptp.feed(html)
                content = ptp.plain_text().strip()

            if content.strip():
                if page_title in ("", "Материал") and content:
                    first_line = content.split("\n", 1)[0].strip()
                    if len(first_line) >= 3:
                        page_title = first_line[:255]
                pages_data.append(
                    {
                        "url": current_url,
                        "title": page_title[:255],
                        "description": page_description,
                        "content": content,
                    }
                )

            seen_urls = set()
            for href, text in parser.links:
                next_url = urljoin(current_url, href)
                parsed = urlparse(next_url)
                if parsed.netloc != parsed_start.netloc:
                    continue
                if not parsed.path.startswith(follow_prefix):
                    continue
                clean_url = _normalize_crawl_url(next_url)
                if clean_url not in visited and clean_url not in queue and clean_url not in seen_urls:
                    seen_urls.add(clean_url)
                    queue.append(clean_url)

            for ju in json_urls:
                parsed = urlparse(ju)
                if parsed.netloc != parsed_start.netloc:
                    continue
                if not parsed.path.startswith(follow_prefix):
                    continue
                clean_url = _normalize_crawl_url(ju)
                if clean_url not in visited and clean_url not in queue and clean_url not in seen_urls:
                    seen_urls.add(clean_url)
                    queue.append(clean_url)

            for hu in _harvest_urls_from_raw_html(html, base_origin, follow_prefix):
                parsed = urlparse(hu)
                if parsed.netloc != parsed_start.netloc:
                    continue
                path = parsed.path.split("?", 1)[0]
                if path.startswith("/api/"):
                    api_url_queue.add(hu.split("?", 1)[0].rstrip("/"))
                    continue
                if not path.startswith(follow_prefix):
                    continue
                clean_url = _normalize_crawl_url(hu)
                if clean_url not in visited and clean_url not in queue and clean_url not in seen_urls:
                    seen_urls.add(clean_url)
                    queue.append(clean_url)

            if import_pdfs and len(pdf_materials_queue) < max_pdfs:
                pdf_candidates: List[str] = []
                sj1: Set[str] = set()
                sj2: Set[str] = set()
                pdf_candidates.extend(_harvest_pdf_urls_from_html(html, current_url))
                if next_data:
                    _collect_pdf_urls_from_json(next_data, pdf_candidates, base_origin, sj1)
                for emb in _parse_embedded_json_scripts(html):
                    _collect_pdf_urls_from_json(emb, pdf_candidates, base_origin, sj2)

                for pdf_u in pdf_candidates:
                    if len(pdf_materials_queue) >= max_pdfs:
                        break
                    pdf_full = pdf_u if pdf_u.startswith("http") else urljoin(base_origin, pdf_u)
                    self._append_pdf_material(
                        pdf_full=pdf_full,
                        referer=current_url,
                        page_title=page_title,
                        course_url=current_url,
                        extra_headers=extra_headers,
                        cookie_header=cookie_header,
                        pdf_seen=pdf_seen,
                        pdf_materials_queue=pdf_materials_queue,
                        max_pdfs=max_pdfs,
                    )

        # Доп. запросы к API, найденным в __NEXT_DATA__ (контент часто только там)
        for api_u in list(api_url_queue)[:80]:
            raw, err = self._fetch_url(
                api_u,
                extra_headers=_headers_for_url(api_u, extra_headers, cookie_header),
                accept="application/json, */*;q=0.8",
            )
            if not raw or err:
                continue
            try:
                data = json.loads(raw)
            except json.JSONDecodeError:
                continue
            _extract_article_like_blocks(data, articles_from_json)
            if import_pdfs and len(pdf_materials_queue) < max_pdfs:
                pdf_api: List[str] = []
                sjx: Set[str] = set()
                _collect_pdf_urls_from_json(data, pdf_api, base_origin, sjx)
                for purl in pdf_api:
                    if len(pdf_materials_queue) >= max_pdfs:
                        break
                    pfull = purl if purl.startswith("http") else urljoin(base_origin, purl)
                    self._append_pdf_material(
                        pdf_full=pfull,
                        referer=f"{base_origin}/lms/ru/courselist",
                        page_title="API",
                        course_url=api_u,
                        extra_headers=extra_headers,
                        cookie_header=cookie_header,
                        pdf_seen=pdf_seen,
                        pdf_materials_queue=pdf_materials_queue,
                        max_pdfs=max_pdfs,
                    )

        # Пробуем ту же страницу как JSON (иногда отдаёт данные)
        raw_json, _ = self._fetch_url(
            start_url,
            extra_headers=_headers_for_url(start_url, extra_headers, cookie_header),
            accept="application/json",
        )
        if raw_json:
            try:
                j = json.loads(raw_json)
                _extract_article_like_blocks(j, articles_from_json)
            except json.JSONDecodeError:
                pass

        if articles_from_json:
            seen_titles: Set[str] = set()
            deduped: List[Dict[str, str]] = []
            for a in articles_from_json:
                k = a["title"].strip().lower()
                if k and k not in seen_titles:
                    seen_titles.add(k)
                    deduped.append(a)
            articles_from_json = deduped
            pages_data = _merge_api_materials(pages_data, articles_from_json)
            pages_data = [
                p
                for p in pages_data
                if not (
                    p["title"].strip().lower() == "учебный центр rwb"
                    and len(p.get("content", "")) < 400
                    and len(articles_from_json) > 0
                )
            ]

        if len(pages_data) > 1:
            pages_data = [
                p
                for p in pages_data
                if not _is_welcome_shell_material(p["title"], p.get("content", ""))
            ]

        if not pages_data and not pdf_materials_queue:
            self.stdout.write(
                self.style.WARNING(
                    "Не удалось извлечь текст ни с одной страницы и ни одного PDF.\n"
                    "  • Добавьте в .env строку Cookie: скопируйте поле «Cookie» из запроса в DevTools "
                    "(Network → любой запрос к edtech.rwb.ru после входа) в переменную RWB_EDTECH_COOKIE.\n"
                    "  • Оставьте RWB_EDTECH_X_AUTH_KEY — часто нужны оба заголовка.\n"
                    "  • Для курсов используйте --urls-file со списком URL вида course?publicationid=...&unitid=...\n"
                    "  • Увеличьте --limit и проверьте, что импорт PDF не отключён (--no-pdf не указан)."
                )
            )
            return

        created = 0
        order_idx = 0
        for item in pages_data:
            order_idx += 1
            material = TrainingMaterial.objects.create(
                module_title=module_title,
                title=item["title"],
                description=(item["description"] or "")[:2000],
                content=f"Источник: {item['url']}\n\n{item['content']}",
                order=order_idx,
            )
            self._create_text_slides(material, item["content"])
            created += 1
            self.stdout.write(self.style.HTTP_INFO(f"  Добавлен материал: {item['title']}"))

        for pm in pdf_materials_queue:
            order_idx += 1
            full_text = "\n\n".join(s for s in pm["pages"] if s and s.strip())
            material = TrainingMaterial.objects.create(
                module_title=module_title,
                title=pm["title"],
                description=(f"PDF: {pm['pdf_url']}\nКурс: {pm['course_url']}")[:2000],
                content=f"Источник PDF: {pm['pdf_url']}\n\n{full_text}"[:500000],
                order=order_idx,
            )
            self._create_slides_from_pdf_pages(material, pm["pages"])
            created += 1
            self.stdout.write(self.style.HTTP_INFO(f"  Добавлен материал (PDF): {pm['title']}"))

        self.stdout.write(
            self.style.SUCCESS(
                f"Импорт завершен: материалов {created} (в т.ч. PDF: {len(pdf_materials_queue)}), "
                f"страниц сайта просмотрено: {len(visited)}."
            )
        )

        if (
            created == 1
            and not pdf_materials_queue
            and pages_data
            and len((pages_data[0].get("content") or "")) < 500
        ):
            self.stdout.write(
                self.style.WARNING(
                    "Похоже, что подтянулась только «оболочка» страницы без статей базы знаний.\n"
                    "  1) Добавьте в .env RWB_EDTECH_COOKIE (целиком из DevTools → Network → Cookie после входа).\n"
                    "  2) В браузере откройте базу знаний → Network → фильтр Fetch/XHR → скопируйте URL запроса "
                    "со списком материалов и запустите: python manage.py import_wb_pvz_materials --url \"<этот URL>\"\n"
                    "  3) Для PDF: откройте курс в браузере → Network → найдите запрос .pdf → убедитесь, что Cookie "
                    "в .env совпадает с сессией, где файл открывается."
                )
            )

    def _append_pdf_material(
        self,
        pdf_full: str,
        referer: str,
        page_title: str,
        course_url: str,
        extra_headers: Dict[str, str],
        cookie_header: str,
        pdf_seen: Set[str],
        pdf_materials_queue: List[Dict[str, Any]],
        max_pdfs: int,
    ) -> None:
        if len(pdf_materials_queue) >= max_pdfs:
            return
        if not _looks_like_pdf_url(pdf_full):
            return
        if pdf_full in pdf_seen:
            return
        pdf_seen.add(pdf_full)
        pdf_headers = dict(_headers_for_url(pdf_full, extra_headers, cookie_header))
        pdf_headers["Referer"] = referer
        raw_pdf, err_pdf = self._fetch_binary(pdf_full, pdf_headers)
        if not raw_pdf or err_pdf:
            self.stdout.write(
                self.style.WARNING(f"  PDF не загружен ({err_pdf}): {pdf_full[:100]}")
            )
            return
        if not raw_pdf.startswith(b"%PDF"):
            self.stdout.write(
                self.style.WARNING(f"  Ответ не PDF (нужна сессия?): {pdf_full[:100]}")
            )
            return
        try:
            page_texts = _pdf_bytes_to_page_texts(raw_pdf)
        except Exception as exc:
            self.stdout.write(self.style.WARNING(f"  Ошибка чтения PDF: {exc} ({pdf_full[:80]})"))
            return
        non_empty = [p.strip() for p in page_texts if p and p.strip()]
        if not non_empty:
            self.stdout.write(
                self.style.WARNING(
                    f"  PDF без текстового слоя (скан): {_pdf_title_from_url(pdf_full, page_title)}"
                )
            )
            return
        pdf_title = _pdf_title_from_url(pdf_full, page_title)
        pdf_materials_queue.append(
            {
                "title": pdf_title,
                "pdf_url": pdf_full,
                "course_url": course_url,
                "pages": page_texts,
            }
        )
        self.stdout.write(
            self.style.HTTP_INFO(f"  PDF готов: «{pdf_title}» ({len(page_texts)} стр.)")
        )

    def _fetch_url(
        self,
        url: str,
        extra_headers: Optional[Dict[str, str]] = None,
        accept: str = "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    ) -> tuple:
        try:
            headers = {
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/122.0.0.0 Safari/537.36"
                ),
                "Accept": accept,
                "Accept-Language": "ru-RU,ru;q=0.9,en;q=0.8",
                "Referer": "https://edtech.rwb.ru/lms/ru/knowledge-base",
            }
            if extra_headers:
                headers.update(extra_headers)
            req = Request(url, headers=headers)
            with urlopen(req, timeout=45) as response:
                raw = response.read()
                enc = (response.headers.get("Content-Encoding") or "").lower()
                ctype = response.headers.get("Content-Type") or ""
                charset = "utf-8"
                cm = re.search(r"charset=([\w-]+)", ctype, re.IGNORECASE)
                if cm:
                    charset = cm.group(1).strip()

                if enc:
                    try:
                        raw = _decompress_body(raw, enc)
                    except RuntimeError as decomp_err:
                        return "", str(decomp_err)

                body = raw.decode(charset, errors="replace")
                return body, ""
        except HTTPError as e:
            return "", f"HTTP {e.code}"
        except URLError as e:
            return "", f"URL error: {e.reason!s}"
        except Exception as e:
            return "", str(e)

    def _fetch_binary(
        self,
        url: str,
        extra_headers: Optional[Dict[str, str]] = None,
    ) -> tuple:
        """Скачивает бинарные ответы (PDF); те же заголовки авторизации, что и у HTML."""
        try:
            headers = {
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/122.0.0.0 Safari/537.36"
                ),
                "Accept": "application/pdf,application/octet-stream,*/*;q=0.8",
                "Accept-Language": "ru-RU,ru;q=0.9,en;q=0.8",
                "Referer": "https://edtech.rwb.ru/lms/ru/knowledge-base",
            }
            if extra_headers:
                headers.update(extra_headers)
            req = Request(url, headers=headers)
            with urlopen(req, timeout=120) as response:
                raw = response.read()
                enc = (response.headers.get("Content-Encoding") or "").lower()
                if enc:
                    try:
                        raw = _decompress_body(raw, enc)
                    except RuntimeError as decomp_err:
                        return b"", str(decomp_err)
                return raw, ""
        except HTTPError as e:
            return b"", f"HTTP {e.code}"
        except URLError as e:
            return b"", f"URL error: {e.reason!s}"
        except Exception as e:
            return b"", str(e)

    def _create_slides_from_pdf_pages(self, material: TrainingMaterial, pages: List[str]):
        """Один слайд = одна страница PDF."""
        for order, page_text in enumerate(pages, start=1):
            text = (page_text or "").strip()
            if not text:
                text = f"(Страница {order}: текст не извлечён — возможно, сканированное изображение)"
            TrainingSlide.objects.create(
                material=material,
                order=order,
                image_url="",
                text=text,
            )

    def _create_text_slides(self, material: TrainingMaterial, content: str):
        """
        Turn long text into readable chunks for the existing slide UI.
        """
        lines = [line.strip() for line in content.splitlines() if line.strip()]
        if not lines:
            return

        chunks = []
        chunk_size = 8
        for i in range(0, len(lines), chunk_size):
            chunk = "\n".join(lines[i : i + chunk_size]).strip()
            if chunk:
                chunks.append(chunk)

        for order, text_chunk in enumerate(chunks, start=1):
            TrainingSlide.objects.create(
                material=material,
                order=order,
                image_url="",
                text=text_chunk,
            )

