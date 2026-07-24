import io

from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Prefetch
from django.urls import reverse_lazy
from django.utils.text import slugify
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView
from reportlab.lib.enums import TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch, cm
from reportlab.platypus import HRFlowable, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import Profile, Section, SectionItem, Variation


class ProfileListView(ListView):
    model = Profile
    template_name = "resume/generic_list.html"
    context_object_name = "profiles"

    def get_queryset(self):
        query_set = super().get_queryset()

        query_set.prefetch_related(
            Prefetch('variation'),
            Prefetch('section_items')
        )
        # Replace 'user' with your actual ForeignKey field name on the Profile model
        return query_set

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["model_name"] = self.model.__name__
        # context["variations"] = Variation.objects.all()
        return context

class ProfileCreateView(LoginRequiredMixin, CreateView):
    model = Profile
    fields = ["name", "title", "description", "github", "linkedin", "portfolio"]
    template_name = "resume/generic_form.html"
    success_url = reverse_lazy("profile-list")


class ProfileDetailView(LoginRequiredMixin, DetailView):
    model = Profile
    template_name = "resume/generic_detail.html"
    context_object_name = "profile"


def _get_profile_variation_sections(profile, variation):
    sections = []
    if variation is None:
        return sections

    section_ids = profile.section.values_list("id", flat=True)
    related_sections = Section.objects.filter(id__in=section_ids).prefetch_related(
        Prefetch("items", queryset=SectionItem.objects.filter(variation=variation)),
    ).order_by("order")
    for section in related_sections:
        section_items = section.items.all()
        print(section.description)
        if section.description != "" or section_items.exists():
            sections.append({"section": section, "items": section_items})

    return sections

@login_required
def profile_variation_view(request, pk, variation_id=None):
    profile = get_object_or_404(Profile, pk=pk)
    variations = Variation.objects.all()
    selected_variation = None
    sections = []

    if variation_id:
        selected_variation = get_object_or_404(Variation, pk=variation_id)

    if selected_variation is None and variations.exists():
        selected_variation = variations.first()

    if selected_variation is not None:
        sections = _get_profile_variation_sections(profile, selected_variation)


    return render(
        request,
        "resume/profile_variation_view.html",
        {
            "profile": profile,
            "variations": variations,
            "selected_variation": selected_variation,
            "sections": sections,
        },
    )


def profile_variation_pdf(request, pk):
    profile = get_object_or_404(Profile, pk=pk)
    variation_id = request.GET.get("variation")
    variations = Variation.objects.all()
    selected_variation = None

    if variation_id:
        selected_variation = get_object_or_404(Variation, pk=variation_id)

    if selected_variation is None and variations.exists():
        selected_variation = variations.first()

    sections = _get_profile_variation_sections(profile, selected_variation)

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        title=f"{profile.name} Resume",
        leftMargin=cm,
        rightMargin=cm,
        topMargin=cm,
        bottomMargin=cm,
    )
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="ResumeTitle", parent=styles["Title"], fontSize=14, leading=10, spaceAfter=4))
    styles.add(ParagraphStyle(name="ResumeSubtitle", parent=styles["Heading2"], fontSize=12, textColor="#4b5563", spaceAfter=6, alignment=TA_LEFT))
    styles.add(ParagraphStyle(name="SectionHeading", parent=styles["Title"], fontWeight="bold", fontSize=11, leading=12, spaceAfter=5, alignment=TA_LEFT))
    styles["BodyText"].fontSize = 9
    styles["BodyText"].leading = 11
    styles["Heading4"].fontSize = 10
    story = []

    story.append(Paragraph(profile.name, styles["ResumeTitle"]))
    # story.append(Paragraph(profile.title, styles["ResumeSubtitle"]))
    if profile.description:
        story.append(Paragraph(profile.description, styles["BodyText"]))

    links = []
    if profile.github:
        links.append(f"GitHub: {profile.github}")
    if profile.linkedin:
        links.append(f"LinkedIn: {profile.linkedin}")
    if profile.portfolio:
        links.append(f"Portfolio: {profile.portfolio}")
    if links:
        story.append(Paragraph(" | ".join(links), styles["BodyText"]))

    for entry in sections:
        
        story.append(Paragraph(entry["section"].title, styles["SectionHeading"]))
        story.append(HRFlowable(width="100%", thickness=0.5, color=(0.2, 0.2, 0.2, 0.3), spaceBefore=0, spaceAfter=0.5))
        for item in entry["items"]:
            cells = []
            # Title cell (left-aligned)
            title_para = Paragraph(item.title, styles["Heading4"])
            cells.append(title_para)
            # Dates cell (right-aligned, if available)
            dates_para = None
            if item.startdate or item.enddate:
                dates = []
                if item.startdate:
                    dates.append(item.startdate.strftime("%b %Y"))
                if item.enddate:
                    dates.append(item.enddate.strftime("%b %Y"))
                dates_para = Paragraph(" - ".join(dates), styles["BodyText"])
            cells.append(dates_para if dates_para else "")
            # Create table with 2 columns
            table = Table([cells], colWidths=["50%", "50%"])
            table.setStyle(TableStyle([
                ("ALIGN", (0, 0), (0, 0), "LEFT"),
                ("ALIGN", (1, 0), (1, 0), "RIGHT"),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                ("TOPPADDING", (0, 0), (-1, -1), 0),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
                ("WIDTH", (0, 0), (-1, -1), "100%"),
            ]))
            story.append(table)
            if item.description:
                story.append(Paragraph(item.description.replace("\n", "<br />"), styles["BodyText"]))
            story.append(Spacer(1, 6))
        story.append(Spacer(1, 8))

    doc.build(story)
    pdf_value = buffer.getvalue()
    buffer.close()

    response = HttpResponse(pdf_value, content_type="application/pdf")
    filename = f"{slugify(profile.name)}-{slugify(selected_variation.title if selected_variation else 'resume')}.pdf"
    response["Content-Disposition"] = f"inline; filename={filename}"
    return response


class ProfileUpdateView(UpdateView):
    model = Profile
    fields = ["name", "title", "description", "github", "linkedin", "portfolio"]
    template_name = "resume/generic_form.html"
    success_url = reverse_lazy("profile-list")


class ProfileDeleteView(DeleteView):
    model = Profile
    template_name = "resume/generic_confirm_delete.html"
    success_url = reverse_lazy("profile-list")
    context_object_name = "profile"


class SectionListView(ListView):
    model = Section
    template_name = "resume/generic_list.html"
    context_object_name = "sections"


class SectionCreateView(CreateView):
    model = Section
    fields = ["title", "description"]
    template_name = "resume/generic_form.html"
    success_url = reverse_lazy("section-list")


class SectionDetailView(DetailView):
    model = Section
    template_name = "resume/generic_detail.html"
    context_object_name = "section"


class SectionUpdateView(UpdateView):
    model = Section
    fields = ["title", "description"]
    template_name = "resume/generic_form.html"
    success_url = reverse_lazy("section-list")


class SectionDeleteView(DeleteView):
    model = Section
    template_name = "resume/generic_confirm_delete.html"
    success_url = reverse_lazy("section-list")
    context_object_name = "section"


class SectionItemListView(ListView):
    model = SectionItem
    template_name = "resume/generic_list.html"
    context_object_name = "section_items"


class SectionItemCreateView(CreateView):
    model = SectionItem
    fields = ["section", "title", "description", "link", "startdate", "enddate"]
    template_name = "resume/generic_form.html"
    success_url = reverse_lazy("section-item-list")


class SectionItemDetailView(DetailView):
    model = SectionItem
    template_name = "resume/generic_detail.html"
    context_object_name = "section_item"


class SectionItemUpdateView(UpdateView):
    model = SectionItem
    fields = ["section", "title", "description", "link", "startdate", "enddate"]
    template_name = "resume/generic_form.html"
    success_url = reverse_lazy("section-item-list")


class SectionItemDeleteView(DeleteView):
    model = SectionItem
    template_name = "resume/generic_confirm_delete.html"
    success_url = reverse_lazy("section-item-list")
    context_object_name = "section_item"


class VariationListView(ListView):
    model = Variation
    template_name = "resume/generic_list.html"
    context_object_name = "variations"


class VariationCreateView(CreateView):
    model = Variation
    fields = ["title", "description"]
    template_name = "resume/generic_form.html"
    success_url = reverse_lazy("variation-list")


class VariationDetailView(DetailView):
    model = Variation
    template_name = "resume/generic_detail.html"
    context_object_name = "variation"


class VariationUpdateView(UpdateView):
    model = Variation
    fields = ["title", "description"]
    template_name = "resume/generic_form.html"
    success_url = reverse_lazy("variation-list")


class VariationDeleteView(DeleteView):
    model = Variation
    template_name = "resume/generic_confirm_delete.html"
    success_url = reverse_lazy("variation-list")
    context_object_name = "variation"
