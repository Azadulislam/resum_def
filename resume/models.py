import uuid

from django.db import models
from django.urls import reverse
from ckeditor.fields import RichTextField
from django.utils.text import slugify
from django.db.models import Max



class Profile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    title = models.CharField(max_length=255)
    description = RichTextField(blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    phone = models.CharField(max_length=255, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    github = models.URLField(blank=True, null=True)
    linkedin = models.URLField(blank=True, null=True)
    portfolio = models.URLField(blank=True, null=True)
    section = models.ManyToManyField("Section", related_name="profiles")
    variation = models.ManyToManyField("Variation", related_name="profiles")
    remote_ready = models.BooleanField(default=False)
    
    class Meta:
        db_table = "profile"
        verbose_name = "Profile"
        verbose_name_plural = "Profiles"

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("profile-detail", kwargs={"pk": self.pk})


class Section(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    description = RichTextField(blank=True, null=True)
    order = models.IntegerField(blank=True, null=True)
    key = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        db_table = "section"
        verbose_name = "Section"
        verbose_name_plural = "Sections"

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        is_new = self._state.adding
        if not self.key and self.title:
            self.key = slugify(self.title)

        super(Section, self).save(*args, **kwargs)

        # Auto-assign any newly created Section to every existing Profile
        # so it is immediately selectable in profile variation views.
        if is_new:
            for profile in Profile.objects.prefetch_related('section').all():
                try:
                    profile.section.add(self)
                except Exception:
                    pass

    def get_absolute_url(self):
        return reverse("section-detail", kwargs={"pk": self.pk})


class SectionItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    section = models.ForeignKey(Section, related_name="items", on_delete=models.CASCADE)
    title = models.CharField(max_length=255, blank=True, null=True)
    description = RichTextField(blank=True, null=True)
    link = models.URLField(blank=True, null=True)
    startdate = models.DateField(blank=True, null=True)
    enddate = models.DateField(blank=True, null=True)
    variation = models.ManyToManyField("Variation", related_name="section_items")
    order = models.IntegerField(null=True, blank=True)
    organization = models.CharField(max_length=255, null=True, blank=True)
    is_present = models.BooleanField(default=False)

    class Meta:
        db_table = "section_item"
        verbose_name = "Section Item"
        verbose_name_plural = "Section Items"

    def __str__(self):
        return f"{self.title}  {self.description}"

    def get_absolute_url(self):
        return reverse("section-item-detail", kwargs={"pk": self.pk})

    def save(self, *args, **kwargs):
        if self.order is None:
            max_value = self.__class__.objects.filter(section__id=self.section.id).aggregate(Max('order'))['order__max']
            self.order = (max_value or 0) + 1
        self.is_present = bool(self.is_present)
        if self.is_present:
            self.enddate = None
        super().save(*args, **kwargs)



class Variation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

    class Meta:
        db_table = "variation"
        verbose_name = "Variation"
        verbose_name_plural = "Variations"

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        is_new = self._state.adding
        super(Variation, self).save(*args, **kwargs)

        # Auto-assign any newly created Variation to every existing Profile
        # so it is immediately selectable as a profile resume variation.
        if is_new:
            for profile in Profile.objects.prefetch_related('variation').all():
                try:
                    profile.variation.add(self)
                except Exception:
                    pass

    def get_absolute_url(self):
        return reverse("variation-detail", kwargs={"pk": self.pk})
