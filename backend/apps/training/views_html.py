from django.shortcuts import get_object_or_404, redirect, render
from django.views import View

from .models import TrainingMaterial
from .views import is_training_admin


class TrainingPageView(View):
    def get(self, request):
        if not request.user.is_authenticated:
            return redirect(f"/accounts/login/?next=/training/")

        materials = TrainingMaterial.objects.all()
        modules = {}
        for m in materials:
            modules.setdefault(m.module_title, []).append(m)

        return render(
            request,
            "training/list.html",
            {
                "is_training_admin": is_training_admin(request.user),
                "modules": modules,
            },
        )


class TrainingManagePageView(View):
    """
    Страница управления учебными материалами (без перехода в админку).
    Доступна только администратору/владельцу.
    """

    def get(self, request):
        if not request.user.is_authenticated:
            return redirect("/accounts/login/?next=/training/manage/")
        if not is_training_admin(request.user):
            return redirect("/training/")

        materials = TrainingMaterial.objects.all()
        return render(
            request,
            "training/manage.html",
            {
                "materials": materials,
            },
        )

    def post(self, request):
        if not request.user.is_authenticated:
            return redirect("/accounts/login/?next=/training/manage/")
        if not is_training_admin(request.user):
            return redirect("/training/")

        module_title = request.POST.get("module_title", "").strip() or "Как работать с программой WB PVZ"
        title = request.POST.get("title", "").strip()
        description = request.POST.get("description", "").strip()
        content = request.POST.get("content", "").strip()
        order_raw = request.POST.get("order", "").strip()
        pdf_file = request.FILES.get("pdf_file")

        try:
            order = int(order_raw) if order_raw else 0
        except ValueError:
            order = 0

        if title:
            TrainingMaterial.objects.create(
                module_title=module_title,
                title=title,
                description=description,
                content=content,
                pdf_file=pdf_file,
                order=order,
            )

        return redirect("/training/manage/")


class TrainingStatsPageView(View):
    """
    Страница «Статистика сотрудников по обучению» (только для администратора/владельца).
    """

    def get(self, request):
        if not request.user.is_authenticated:
            return redirect("/accounts/login/?next=/training/stats/")
        if not is_training_admin(request.user):
            return redirect("/training/")
        return render(request, "training/stats.html")


class TrainingMaterialDetailPageView(View):
    """
    Страница просмотра отдельного материала с поочередной сменой слайдов.
    """

    def get(self, request, pk: int):
        if not request.user.is_authenticated:
            return redirect(f"/accounts/login/?next=/training/material/{pk}/")

        material = get_object_or_404(
            TrainingMaterial.objects.prefetch_related("slides"),
            pk=pk,
        )
        slides = list(material.slides.all())
        total_slides = len(slides)
        pdf_url = ""
        if material.pdf_file:
            pdf_url = material.pdf_file.url
        content = (material.content or "").strip()
        if not pdf_url and content.startswith("PDF_URL:"):
            pdf_url = content[len("PDF_URL:") :].strip()

        return render(
            request,
            "training/material_detail.html",
            {
                "material": material,
                "slides": slides,
                "total_slides": total_slides,
                "pdf_url": pdf_url,
            },
        )
