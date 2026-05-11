from __future__ import annotations

from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand

from apps.training.models import TrainingMaterial, TrainingSlide


class Command(BaseCommand):
    help = (
        "Импортирует локальные PDF-курсы из "
        "'static/training/material/<КУРС>/*.pdf'. "
        "Каждая папка — отдельный курс (module_title), каждый PDF — материал."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--root",
            type=str,
            default="",
            help=(
                "Путь к папке с курсами. По умолчанию: "
                "<BASE_DIR>/static/training/material"
            ),
        )
        parser.add_argument(
            "--keep-existing",
            action="store_true",
            help="Не удалять существующие материалы перед импортом.",
        )

    def handle(self, *args, **options):
        root_opt = (options.get("root") or "").strip()
        keep_existing = bool(options.get("keep_existing"))

        root_dir = Path(root_opt) if root_opt else (settings.BASE_DIR / "static" / "training" / "material")
        if not root_dir.exists() or not root_dir.is_dir():
            self.stdout.write(self.style.ERROR(f"Папка не найдена: {root_dir}"))
            return

        if not keep_existing:
            deleted, _ = TrainingMaterial.objects.all().delete()
            self.stdout.write(self.style.WARNING(f"Удалены старые обучения: {deleted} объектов."))

        # Чистим слайды, чтобы не мешали PDF-вьюеру (не обязательно, но аккуратнее)
        TrainingSlide.objects.all().delete()

        total_materials = 0
        course_dirs = sorted([p for p in root_dir.iterdir() if p.is_dir()], key=lambda p: p.name.lower())
        for course_dir in course_dirs:
            module_title = course_dir.name
            pdf_files = sorted(course_dir.rglob("*.pdf"), key=lambda p: p.name.lower())
            if not pdf_files:
                continue

            self.stdout.write(self.style.MIGRATE_HEADING(f"Курс: {module_title}"))
            for idx, pdf_path in enumerate(pdf_files, start=1):
                rel = pdf_path.relative_to(settings.BASE_DIR / "static").as_posix()
                pdf_url = f"{settings.STATIC_URL.rstrip('/')}/{rel}"

                title = pdf_path.stem
                TrainingMaterial.objects.create(
                    module_title=module_title,
                    title=title[:255],
                    description="PDF-материал",
                    content=f"PDF_URL:{pdf_url}",
                    order=idx,
                )
                total_materials += 1
                self.stdout.write(self.style.HTTP_INFO(f"  + {title}"))

        self.stdout.write(self.style.SUCCESS(f"Импорт завершен. Материалов: {total_materials}"))

