# Andromeda - Personal Memory Journal

Andromeda is a personal memory management application that helps you capture, organize, and reflect on your life's precious moments. Create memories, analyze them with AI, organize them in albums, and lock them in time capsules for future reflection.

## 🌟 Features

### Currently Implemented
- ✅ User authentication (registration/login)
- ✅ Complete memory management (Souvenirs)
- ✅ AI-powered analysis (text & image analysis)
- ✅ Memory albums and organization
- ✅ Time capsules for future memories
- ✅ Advanced filtering and search
- ✅ Modern, responsive UI
- ✅ Django admin configured

### AI Analysis Features
- **Text Analysis**: Emotion detection, keyword extraction, summarization
- **Image Analysis**: Object detection, face recognition, color analysis, location detection
- **Smart Organization**: Auto-generated album suggestions
- **Reflection Prompts**: Personalized prompts based on your memory patterns

## 🚀 Installation

### Prerequisites
- Python 3.10+
- pip

### Steps

1. **Clone the project**
```bash
git clone <repository-url>
cd Andromeda
```

2. **Create a virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables** (optional for AI features)
```bash
cp .env.example .env
# Edit .env with your API keys
```

5. **Apply migrations**
```bash
python manage.py migrate
```

6. **Create a superuser**
```bash
python manage.py createsuperuser
```

7. **Run the server**
```bash
python manage.py runserver
```

8. **Access the application**
- Application: http://127.0.0.1:8000/
- Admin: http://127.0.0.1:8000/admin/

## 🤖 AI Analysis Setup

To enable real AI analysis (instead of simulated), configure these environment variables:

### OpenAI (Text Analysis)
```bash
OPENAI_API_KEY=sk-your-openai-api-key-here
AI_TEXT_MODEL=gpt-4o-mini  # or gpt-4, gpt-3.5-turbo
```

### Google Vision (Image Analysis)
1. Create a Google Cloud project
2. Enable the Vision API
3. Create a service account and download the JSON key
4. Set the environment variable:
```bash
GOOGLE_VISION_API_KEY=path/to/your/service-account-key.json
```

If API keys are not provided, the app will use simulated analysis with realistic results.

## 📁 Project Structure

```
Andromeda/
├── andromeda/          # Django configuration
│   ├── settings.py     # Settings with AI API config
│   ├── urls.py         # Main URLs
│   └── wsgi.py         # WSGI
├── core/               # Main application
│   ├── models.py       # Models (Souvenir, Album, Capsule, etc.)
│   ├── views.py        # Views for all features
│   ├── forms.py        # Forms for memories and capsules
│   ├── urls.py         # App URLs
│   ├── admin.py        # Admin configuration
│   ├── ai_services.py  # AI analysis services
│   └── templates/      # HTML templates
├── static/             # Static files
│   ├── assets/         # Images, SVGs
│   ├── css/            # Styles
│   └── js/             # Scripts
├── media/              # User uploads
├── requirements.txt    # Python dependencies
├── .env.example        # Environment variables template
└── manage.py           # Django CLI
```

## 🎨 Design

Andromeda features a modern, warm design with:
- Color palette: Warm grays and accent colors
- Typography: Clean, readable fonts
- Responsive design for all devices
- Intuitive navigation and user experience

## 🔧 Technologies

- **Backend**: Django 5.2+
- **Frontend**: HTML, CSS, JavaScript
- **Database**: SQLite (dev) / PostgreSQL (prod)
- **AI Services**: OpenAI GPT, Google Vision API
- **Deployment**: Render, Gunicorn, WhiteNoise

## 📝 Data Models

- **Souvenir**: Memories with text, photos, videos, emotions, themes
- **AnalyseIASouvenir**: AI analysis results for each memory
- **AlbumSouvenir**: Collections of memories
- **CapsuleTemporelle**: Time-locked memories
- **PartageSouvenir**: Social sharing of memories

## 🧪 Testing

Andromeda includes comprehensive testing for all major components. You can test functions in several ways:

### Quick Test Runner

Use the interactive test runner:
```bash
python run_tests.py
```

This provides a menu with options to:
- Run smoke tests (basic functionality)
- Test AI analysis functions
- Test Django views
- Test model methods
- Run manual tests for specific features

### Test Specific Functions

#### AI Analysis Functions
```bash
# Test all AI functions
python test_suite.py AIAnalysisServiceTest

# Test specific AI function
python test_suite.py AIAnalysisServiceTest test_analyze_memory
python test_suite.py AIAnalysisServiceTest test_analyze_text_function
python test_suite.py AIAnalysisServiceTest test_predict_future_emotion
```

#### Django Views
```bash
# Test all view functions
python test_suite.py ViewTest

# Test souvenir creation
python test_suite.py ViewTest test_souvenir_creation
```

#### Model Methods
```bash
# Test all model methods
python test_suite.py ModelTest

# Test time capsule functionality
python test_suite.py ModelTest test_capsule_temporelle_methods
```

### Manual Testing

#### Test AI Analysis Manually
```bash
python -c "
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'andromeda.settings')
django.setup()

from django.contrib.auth.models import User
from core.models import Souvenir
from core.ai_services import AIAnalysisService

user = User.objects.create_user('test', 'test@example.com', 'pass')
souvenir = Souvenir.objects.create(
    utilisateur=user, titre='Test', description='Test memory',
    emotion='joy', theme='personal', date_evenement='2024-01-01'
)
analysis = AIAnalysisService.analyze_memory(souvenir)
print('Analysis:', analysis.resume_genere)
"
```

#### Test Souvenir Creation
```bash
python -c "
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'andromeda.settings')
django.setup()

from django.contrib.auth.models import User
from core.models import Souvenir

user = User.objects.create_user('test', 'test@example.com', 'pass')
souvenir = Souvenir.objects.create(
    utilisateur=user, titre='Test Memory', description='Description',
    emotion='joy', theme='personal', date_evenement='2024-01-01'
)
print('Created souvenir:', souvenir.titre)
"
```

### Test Coverage

The test suite covers:

**AI Services (`core/ai_services.py`)**:
- `analyze_memory()` - Complete memory analysis
- `_analyze_text()` - Text analysis (OpenAI/simulated)
- `_analyze_image()` - Image analysis (Google Vision/simulated)
- `predict_future_emotion()` - Future emotion prediction
- `generate_album_suggestions()` - Smart album suggestions
- `get_memory_insights()` - User memory insights
- `suggest_reflection_prompts()` - Reflection prompts

**Django Views (`core/views.py`)**:
- `dashboard()` - Main dashboard
- `ajouter_souvenir()` - Add memory
- `analyser_souvenir_ia()` - AI analysis view
- `liste_souvenirs()` - Memory list
- `creer_capsule()` - Create time capsule

**Models (`core/models.py`)**:
- `Souvenir` methods: `has_media()`, `needs_ai_analysis()`
- `CapsuleTemporelle` methods: `jours_restants()`, `pourcentage_progression()`, `is_expired()`
- `AlbumSouvenir` methods: `souvenirs_count()`

### Running Tests in Development

1. **Basic smoke test**:
```bash
python smoke_test.py
```

2. **Interactive test menu**:
```bash
python run_tests.py
```

3. **Run all tests**:
```bash
python test_suite.py
```

4. **Run with Django's test runner**:
```bash
python manage.py test
```

### Testing AI Features

To test AI features with real APIs:

1. **Set up API keys** in `.env`:
```bash
OPENAI_API_KEY=sk-your-key-here
GOOGLE_VISION_API_KEY=path/to/service-account.json
```

2. **Test AI analysis**:
```bash
python run_tests.py
# Choose option 7: Test AI analysis manually
```

Without API keys, tests will use simulated analysis with realistic results.

## 📚 Documentation

- `BUILD_SPEC.md`: Detailed project specifications
- `GUIDE_UTILISATION.md`: User guide
- `SOUVENIRS_API.md`: API documentation

## 🔐 Security

For production:
- Set `SECRET_KEY` in environment variables
- Set `DEBUG=False`
- Configure `ALLOWED_HOSTS`
- Use HTTPS
- Secure API keys

## 🤝 Contributing

Contributions are welcome! Feel free to open an issue or pull request.

## 📄 License

[To be defined]

## 👤 Author

[Your name]

## 🗺️ Roadmap

### Phase 1 (Current)
- [x] Memory CRUD with AI analysis
- [x] Album organization
- [x] Time capsules
- [x] Advanced filtering
- [x] Modern UI

### Phase 2
- [ ] Social sharing features
- [ ] PDF export
- [ ] Journal integration
- [ ] Gamification (badges)

### Phase 3
- [ ] Mobile app
- [ ] Advanced AI features
- [ ] Team collaboration
- [ ] Offline sync
