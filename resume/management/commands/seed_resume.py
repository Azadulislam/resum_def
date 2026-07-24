from django.core.management.base import BaseCommand

from resume.models import Profile, Section, SectionItem, Variation


class Command(BaseCommand):
    help = "Seed the resume database with sample profile, sections, items, and variations"

    def handle(self, *args, **options):
        profile_data = {
            "name": "Azadul Islam",
            "title": "Backend Developer",
            "description": '',
            "location": "Binodpur, Rajshahi, Bangladesh",
            "phone": "+8801601026191",
            "email": "azadkh92558@gmail.com",
            "github": "https://github.com/Azadulislam",
            "linkedin": "https://www.linkedin.com/in/azadul-islam-ai/",
            "portfolio": "https://azadulislam.top/",
        }

        profile, created = Profile.objects.get_or_create(
            name=profile_data["name"],
            defaults=profile_data,
        )

        if created:
            self.stdout.write(self.style.SUCCESS(f"Created profile: {profile.name}"))
        else:
            self.stdout.write(f"Profile already exists: {profile.name}")

        variation_titles = ["Django Developer", "Laravel Developer", "Backend Developer"]
        variations = []
        for title in variation_titles:
            variation, _ = Variation.objects.get_or_create(title=title)
            variations.append(variation)

        section_titles = [
            ["Summery", "summary", 1, '<p><strong>Full Stack Engineer</strong> with 4.5+ years of professional experience building <strong>REST APIs</strong>, multi-tenant applications, payment integrations, and database-driven systems. Experienced in <strong>PHP, Laravel, Python, Django, Django REST Framework, PostgreSQL, MySQL</strong>, <strong>authentication systems</strong>, and <strong>performance optimization</strong>. Passionate about designing scalable backend architectures and delivering reliable, production-ready applications.</p>'],
            ["Tools and Technology", "tools_technology", 2, ''],
            ["Key Achievements", "technical_highlights", 3, """<ul>
	<li>Reduced database query response time from <strong>13s to 2s on 200K+</strong> records.</li>
	<li>Integrated <strong>Stripe recurring subscriptions</strong> with automated billing workflows.</li>
	<li>Built scalable REST APIs using <strong>Django REST Framework </strong>and Laravel.</li>
	<li>Implemented Progressive<strong> Web App (PWA) </strong>offline support using Service Workers to enhance user experience</li>
	<li>Developed real-time chat functionality using <strong>WebSockets,&nbsp;</strong><strong>Laravel Reverb&nbsp;</strong>and<strong>&nbsp;Redis</strong>.</li>
	<li>Automated recurring tasks using <strong>Laravel Scheduler</strong>.</li>
	<li>Designed role-based access control (<strong>RBAC</strong>) and multi-tenant architectures.</li>
</ul>"""],
            ["Experience", "experience", 4, ''],
            ["Projects", "projects", 5, ''],
            ["Certification", "certification", 6, ''],
            ["Education", "education", 6, ''],
            ["Language", "language", 7, ''],
            ["References", "references", 8, ''],
        ]
        sections = []
        for title, key, order, description in section_titles:
            section, _ = Section.objects.get_or_create(title=title, key=key, order=order, description=description)
            sections.append(section)

        section_items = [
            {
                "section": 'experience',
                "title": "Full Stack PHP Software Developer, Fitlynk",
                "description": (
                    "Developed and maintained REST APIs powering e-commerce and booking platforms.\n"
                    "Reduced database response time from 13s to 2s through query optimization, indexing across 200K+ records.\n"
                    "Integrated Stripe subscription billing with secure webhook processing and automated payment workflows.\n"
                    "Designed backend business logic for booking workflows and user account systems."
                ),
            },
            {
                "section": 'projects',
                "title": "MedibazarBD – Full-Stack E-commerce Platform (Laravel, MySQL, VueJS )",
                "description": ("""                    <ul>
                        <li>Built a scalable e-commerce platform using Laravel, Vue.js, and REST APIs.</li>
                        <li>Optimized backend performance by reducing database queries from 175 to 18 (~90%) and improving response time from 973ms to 480&ndash;580ms (~50% faster).</li>
                        <li>Eliminated N+1 queries using eager loading, implemented cursor pagination, and optimized database queries for scalability.</li>
                        <li>Implemented Laravel Queue for image processing and email automation, improving application responsiveness.</li>
                        <li>Optimized product images for SEO and developed responsive user/admin interfaces with Tailwind CSS.</li>
                    </ul>"""
                ),
            },
            {
                "section": 'tools_technology',
                "title": "Backend",
                "description": "Python, Django, DRF, FastAPI, PHP, Laravel",
            },
            {
                "section": 'tools_technology',
                "title": "Database",
                "description": "MySQL, Redis, PostgreSQL",
            },
            {
                "section": 'tools_technology',
                "title": "Frontend",
                "description": "Vue.js, JavaScript, TailwindCSS",
            },
            {
                "section": 'tools_technology',
                "title": "Tools",
                "description": "Git, Postman, DigitalOcean, WebSockets",
            },
            {
                "section": 'certification',
                "title": "LEDP - Learning and Earning Development Project",
                "description": "ICT",
            },
            {
                "section": 'education',
                "title": "Diploma in Computer Technology",
                "description": "Rajshahi Polytechnic Institute, 2018 - 2023",
            },
        ]

        created_items = []
        for item_data in section_items:
            item, _ = SectionItem.objects.get_or_create(
                section=Section.objects.get(key=item_data["section"]),
                title=item_data["title"],
                defaults={"description": item_data.get("description", "")},
            )
            created_items.append(item)

        profile.section.add(*sections)
        profile.variation.add(*variations)

        for item in created_items:
            item.variation.add(*variations)

        self.stdout.write(self.style.SUCCESS("Resume seed data completed successfully."))
