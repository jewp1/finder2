import json

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from apps.projects.models import Project

User = get_user_model()

USERS = [
    {
        "email": "alice@example.com",
        "username": "alice",
        "password": "password123",
        "full_name": "Alice Johnson",
        "bio": "Full-stack developer with 5 years of experience. Love building products from scratch.",
        "skills": "Python, Django, React, PostgreSQL, Docker",
        "experience": "5 years in web development, worked at startups and mid-sized companies",
    },
    {
        "email": "bob@example.com",
        "username": "bob",
        "password": "password123",
        "full_name": "Bob Smith",
        "bio": "Mobile developer focused on cross-platform apps. Open to interesting projects.",
        "skills": "Flutter, Dart, Swift, Kotlin, Firebase",
        "experience": "3 years in mobile development",
    },
    {
        "email": "carol@example.com",
        "username": "carol",
        "password": "password123",
        "full_name": "Carol White",
        "bio": "UI/UX designer who codes. Passionate about accessible and beautiful interfaces.",
        "skills": "Figma, CSS, TypeScript, Vue.js, Tailwind",
        "experience": "4 years in product design and frontend development",
    },
    {
        "email": "david@example.com",
        "username": "david",
        "password": "password123",
        "full_name": "David Lee",
        "bio": "Backend engineer, love distributed systems and high-load architecture.",
        "skills": "Go, Rust, Kubernetes, Kafka, Redis",
        "experience": "7 years in backend and infrastructure",
    },
    {
        "email": "eva@example.com",
        "username": "eva",
        "password": "password123",
        "full_name": "Eva Martinez",
        "bio": "Data scientist and ML engineer. Looking for projects with real impact.",
        "skills": "Python, PyTorch, scikit-learn, SQL, Spark",
        "experience": "4 years in data science and machine learning",
    },
]

PROJECTS = [
    {
        "owner_username": "alice",
        "title": "Marketplace for Freelancers",
        "description": "Building a platform connecting freelancers with clients in design, development and marketing.",
        "requirements": json.dumps(["Flutter developer", "UI/UX designer", "Payment API experience"]),
        "budget": "$5,000–$10,000",
        "duration": "3–4 months",
        "status": "open",
    },
    {
        "owner_username": "bob",
        "title": "Fitness Tracking App",
        "description": "Cross-platform mobile app for tracking workouts, nutrition and sleep. Integration with wearables.",
        "requirements": json.dumps(["Python/Node backend", "Data analyst", "HealthKit/Google Fit"]),
        "budget": "$3,000–$6,000",
        "duration": "2–3 months",
        "status": "open",
    },
    {
        "owner_username": "david",
        "title": "Real-time Chat Platform",
        "description": "Scalable messenger with end-to-end encryption, channels and bots support.",
        "requirements": json.dumps(["React/Vue frontend", "Security specialist", "WebSocket experience"]),
        "budget": "$8,000–$15,000",
        "duration": "4–6 months",
        "status": "open",
    },
    {
        "owner_username": "eva",
        "title": "AI Content Moderation Tool",
        "description": "ML-based service for automatically detecting toxic content, spam and misinformation in social media.",
        "requirements": json.dumps(["NLP engineer", "Python backend", "Transformer models experience"]),
        "budget": "$10,000–$20,000",
        "duration": "5–6 months",
        "status": "open",
    },
    {
        "owner_username": "carol",
        "title": "Design System Library",
        "description": "Open-source UI component library with accessibility-first approach, supporting React and Vue.",
        "requirements": json.dumps(["React developer", "Vue developer", "Technical writer"]),
        "budget": "Equity / open source",
        "duration": "Ongoing",
        "status": "open",
    },
    {
        "owner_username": "alice",
        "title": "E-learning Platform MVP",
        "description": "Platform for online courses with video lessons, quizzes and progress tracking.",
        "requirements": json.dumps(["Mobile developer", "Video streaming specialist", "FFmpeg experience"]),
        "budget": "$7,000–$12,000",
        "duration": "4–5 months",
        "status": "in_progress",
    },
]


class Command(BaseCommand):
    help = "Seed database with test users and projects"

    def handle(self, *args, **options):
        created_users = 0
        created_projects = 0

        for data in USERS:
            if User.objects.filter(email=data["email"]).exists():
                continue
            password = data.pop("password")
            user = User(**data)
            user.set_password(password)
            user.save()
            data["password"] = password
            created_users += 1

        for data in PROJECTS:
            owner_username = data.pop("owner_username")
            try:
                owner = User.objects.get(username=owner_username)
            except User.DoesNotExist:
                data["owner_username"] = owner_username
                continue
            if Project.objects.filter(title=data["title"], owner=owner).exists():
                data["owner_username"] = owner_username
                continue
            Project.objects.create(owner=owner, **data)
            data["owner_username"] = owner_username
            created_projects += 1

        self.stdout.write(self.style.SUCCESS(f"Seeded {created_users} users and {created_projects} projects."))
