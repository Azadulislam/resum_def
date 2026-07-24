import uuid

from django.db import models
from django.urls import reverse
from ckeditor.fields import RichTextField
from django.utils.text import slugify



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
        if not self.key and self.title:
            self.key = slugify(self.title)

        super(Section, self).save(*args, **kwargs)

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

    class Meta:
        db_table = "section_item"
        verbose_name = "Section Item"
        verbose_name_plural = "Section Items"

    def __str__(self):
        return f"{self.title}  {self.description}"

    def get_absolute_url(self):
        return reverse("section-item-detail", kwargs={"pk": self.pk})


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

    def get_absolute_url(self):
        return reverse("variation-detail", kwargs={"pk": self.pk})
