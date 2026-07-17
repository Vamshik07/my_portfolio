import os
import logging
import mimetypes
import json

from django.shortcuts import render
from django.conf import settings
from django.http import FileResponse, Http404
from django.core.serializers.json import DjangoJSONEncoder

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _load_cert_metadata(media_dir: str) -> dict:
    """Load optional certificate metadata from a JSON sidecar file.

    Returns an empty dict on any failure so callers never crash.
    """
    meta_path = os.path.join(media_dir, 'metadata.json')
    if not os.path.isfile(meta_path):
        return {}
    try:
        with open(meta_path, 'r', encoding='utf-8') as fh:
            return json.load(fh)
    except Exception as exc:
        logger.warning("Failed to load certificate metadata from %s: %s", meta_path, exc)
        return {}

def _get_certificates() -> list:
    media_dir = os.path.join(settings.MEDIA_ROOT, 'certificates')

    # Build the certificate image URL from MEDIA_URL so the media path is always
    # consistent with the site configuration.
    media_url = f"{settings.MEDIA_URL.rstrip('/')}/certificates/"

    if not os.path.isdir(media_dir):
        return []

    metadata = _load_cert_metadata(media_dir)

    entries = []
    for fname in os.listdir(media_dir):
        if fname == 'metadata.json':
            continue
        fpath = os.path.join(media_dir, fname)
        if not os.path.isfile(fpath):
            continue
        ctype, _ = mimetypes.guess_type(fpath)
        if ctype and ctype.startswith('image'):
            entries.append((os.stat(fpath).st_mtime, fname))

    certs = []
    for _, fname in sorted(entries, reverse=True):
        info = metadata.get(fname, {})
        title = (
            info.get('title')
            or os.path.splitext(fname)[0].replace('_', ' ').title()
        )
        category = info.get('category', '').strip().lower()
        if not category:
            category = 'hackathon' if 'hackathon' in title.lower() else 'general'

        certs.append({
            'title': title,
            'issuer': info.get('issuer', ''),
            'issue_date': info.get('issue_date', ''),
            'credential_id': info.get('credential_id', ''),
            'verify_url': info.get('verify_url', ''),
            'image_url': media_url + fname,
            'category': category,
            'index': len(certs),
        })

    return certs


def _partition_certificates(certs: list) -> tuple[list, list]:
    hackathon = [cert for cert in certs if cert.get('category') == 'hackathon']
    other = [cert for cert in certs if cert.get('category') != 'hackathon']
    return hackathon, other


def _projects_data() -> list:
    """Return the static list of portfolio projects.

    Keeping this in one place means both the home view and any future
    API/projects-only view stay in sync without duplication.
    """
    return [
        {
            'title': 'Personalized Learning Coach Agent',
            'repo': 'https://github.com/Vamshik07/Personalized-learning-coach-Agent',
            'description': (
                'A modern, adaptive learning platform inspired by Duolingo-style personalized study. '
                'It features AI-generated quizzes with adaptive difficulty, smart spaced repetition revisions, '
                'automated flashcards, weakness detection, and chat-based AI tutoring.'
            ),
            'technologies': ['Next.js 15', 'React 19', 'TypeScript', 'Tailwind CSS', 'OpenAI API', 'Prisma ORM', 'PostgreSQL'],
        },
        {
            'title': 'Resume Evaluator',
            'repo': 'https://github.com/Vamshik07/Resume_evaluator',
            'description': (
                'An AI-powered resume evaluation system designed to automate resume screening against job '
                'requirements at scale. It provides relevance scores (0-100), identifies missing skills, '
                'and generates personalized improvement feedback.'
            ),
            'technologies': ['FastAPI', 'Streamlit', 'Google Gemini', 'LangChain', 'spaCy', 'Sentence Transformers', 'ChromaDB'],
        },
        {
            'title': 'Blood Donation Management System',
            'repo': 'https://github.com/Vamshik07/blood-donation-management-system',
            'description': (
                'A platform developed to connect blood donors with patients in need. '
                'The system helps manage donor data, track blood availability, and '
                'streamline the process of finding donors quickly during emergencies.'
            ),
            'technologies': ['Database systems', 'Web development', 'Backend logic'],
        },
        {
            'title': 'MarketMind AI',
            'repo': 'https://github.com/Vamshik07/marketmind',
            'description': (
                'AI-based market analysis platform that analyzes market trends and '
                'provides insights using data analytics and machine learning techniques '
                'to support better decision-making.'
            ),
            'technologies': ['Python', 'Data Analysis', 'AI models', 'Visualization'],
        },
        {
            'title': 'Intelli-Credit AI',
            'repo': 'https://github.com/Vamshik07/Intelli-Credit-AI',
            'description': (
                'An AI-powered corporate credit appraisal platform that analyzes '
                'financial documents, extracts insights, and generates risk scores '
                'and credit recommendations using AI agents.'
            ),
            'technologies': [
                'FastAPI', 'React', 'LangGraph', 'MongoDB',
                'Gemini AI', 'OCR', 'Python',
            ],
        },
    ]


def _profile_data() -> dict:
    """Return static profile information for the portfolio owner."""
    return {
        'first_name': 'Vamshi Krishna',
        'last_name': 'Ambati',
        'headline': 'Vamshi Krishna Ambati',
        'skills': [
            'Python', 'Java', 'SQL', 'C', 'HTML5', 'CSS3', 'JavaScript',
            'TypeScript', 'Next.js', 'React', 'Tailwind CSS', 'Flutter',
            'Flask', 'FastAPI', 'REST APIs', 'MySQL', 'PostgreSQL', 'Prisma ORM',
            'Machine Learning', 'Pandas', 'NumPy', 'LLM APIs', 'OpenAI API',
            'Google Gemini', 'LangGraph', 'Streamlit', 'ChromaDB', 'Git',
            'GitHub', 'Postman', 'VS Code', 'Power BI', 'Excel',
        ],
        'contact': {
            'emails': ['ambativamshi743@gmail.com'],
            'linkedin': 'https://linkedin.com/in/VamshiKrishna',
        },
    }


# ---------------------------------------------------------------------------
# Views
# ---------------------------------------------------------------------------

def home(request):
    """Render the portfolio home page."""
    projects = _projects_data()
    certs = _get_certificates()
    hackathon_certs, other_certs = _partition_certificates(certs)

    context = {
        'profile_data': _profile_data(),
        'projects': projects,
        # Use DjangoJSONEncoder so dates / special objects serialise safely.
        # Embed with the {% json_script %} template tag on the template side
        # to prevent XSS, e.g.:
        #   {{ projects_json|json_script:"projects-data" }}
        'projects_json': json.dumps(projects, cls=DjangoJSONEncoder),
        'certificates': certs,
        'hackathon_certificates': hackathon_certs,
        'other_certificates': other_certs,
        'cert_count': len(certs),
        'certificates_json': json.dumps(certs, cls=DjangoJSONEncoder),
    }
    return render(request, 'portfolio/home.html', context)


def certificates(request):
    """Render the standalone certificates page."""
    certs = _get_certificates()
    hackathon_certs, other_certs = _partition_certificates(certs)

    context = {
        'certificates': certs,
        'hackathon_certificates': hackathon_certs,
        'other_certificates': other_certs,
        'cert_count': len(certs),
        'certificates_json': json.dumps(certs, cls=DjangoJSONEncoder),
    }
    return render(request, 'portfolio/certificates.html', context)


def resume(request):
    """Serve the resume file as a downloadable attachment.

    The file is expected at BASE_DIR/vamshiresume.docx.
    Returns HTTP 404 when the file is absent.
    """
    resume_path = os.path.join(settings.BASE_DIR, 'vamshiresume.docx')
    if not os.path.isfile(resume_path):
        logger.error("Resume file not found at expected path: %s", resume_path)
        raise Http404('Resume not found')

    # `open()` here is intentional — FileResponse takes ownership of the file
    # handle and closes it once the response is streamed, per Django docs.
    return FileResponse(
        open(resume_path, 'rb'),
        as_attachment=True,
        filename='Vamshi_Krishna_Ambati_Resume.docx',
    )