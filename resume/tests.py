from django.test import TestCase
from django.urls import reverse

from .models import Profile, Section, SectionItem, Variation


class ProfileModelTests(TestCase):
    def test_profile_can_be_created_with_required_fields(self):
        profile = Profile.objects.create(
            name="Ada Lovelace",
            title="Software Engineer",
            description="Pioneer in computing.",
        )

        self.assertEqual(profile.name, "Ada Lovelace")
        self.assertEqual(profile.title, "Software Engineer")
        self.assertTrue(profile.pk)

    def test_profile_variation_pdf_view_returns_pdf_response(self):
        profile = Profile.objects.create(
            name="Ada Lovelace",
            title="Software Engineer",
            description="Pioneer in computing.",
        )
        variation = Variation.objects.create(title="Technical")
        section = Section.objects.create(title="Experience")
        profile.section.add(section)
        item = SectionItem.objects.create(
            section=section,
            title="Engineer",
            description="Built software.",
        )
        item.variation.add(variation)

        response = self.client.get(
            reverse("profile-variation-pdf", kwargs={"pk": profile.pk}) + f"?variation={variation.pk}"
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/pdf")
