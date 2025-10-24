# Andromeda System Architecture

## Data Flow Diagram

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   User Browser  │───▶│  Django Views   │───▶│   Database      │
│                 │    │                 │    │   (Models)      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   HTML Forms    │    │  Form Validation│    │   AI Services   │
│                 │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Model Relationships

```
User (1) ────▶ (many) Souvenir
    │                    │
    │                    │
    ▼                    ▼
SuiviMotivationnel   AnalyseIASouvenir (AI analysis)
                       │
                       ▼
                   AlbumSouvenir (many-to-many)
                       │
                       ▼
                 CapsuleTemporelle (time-locked)
                       │
                       ▼
                 PartageSouvenir (sharing)
                       │
                       ▼
                 EntreeJournal (linked entries)
```

## Function Call Flow

### Memory Creation Process:
```
1. User visits /memories/add/
2. ajouter_souvenir() view loads SouvenirForm
3. User submits form with data
4. Form validation runs (clean_titre, clean_description, etc.)
5. If valid: Memory saved to database
6. Optional: AI analysis triggered
7. Success message shown, redirect to memory list
```

### AI Analysis Process:
```
1. analyser_souvenir_ia() called with memory ID
2. AIAnalysisService.analyze_memory() processes text + image
3. Results saved to AnalyseIASouvenir model
4. Memory marked as ai_analyzed = True
5. User redirected to memory detail with enhanced info
```

## Key Functions Explained

### Views (Business Logic):
- `dashboard()` → Shows stats, recent memories, activity
- `ajouter_souvenir()` → Creates new memory with validation
- `liste_souvenirs()` → Lists user's memories with pagination
- `detail_souvenir()` → Shows single memory with media
- `filtrer_souvenirs()` → Filters memories by criteria
- `analyser_souvenir_ia()` → Triggers AI analysis
- `creer_capsule()` → Creates time-locked memory
- `liste_albums()` → Shows memory collections

### Forms (Data Validation):
- `SouvenirForm.clean_titre()` → Validates title length
- `SouvenirForm.clean_description()` → Validates description
- `SouvenirForm.clean_photo()` → Checks file type/size
- `SouvenirForm.clean_date_evenement()` → Prevents future dates

### Models (Data Storage):
- `Souvenir` → Main memory with all metadata
- `AnalyseIASouvenir` → AI analysis results
- `AlbumSouvenir` → Memory collections
- `CapsuleTemporelle` → Time-locked memories
- `PartageSouvenir` → Sharing configuration

## URL Routing:
```
/dashboard/ → dashboard()
/memories/add/ → ajouter_souvenir()
/memories/<id>/ → detail_souvenir()
/ai-gallery/ → galerie_ia()
/capsules/create/ → creer_capsule()
/albums/ → liste_albums()
```

## File Structure:
```
core/
├── models.py (data definitions)
├── views.py (page logic)
├── forms.py (validation)
├── urls.py (routing)
├── admin.py (admin interface)
└── templates/ (HTML pages)
```

This architecture follows Django's MTV (Model-Template-View) pattern with additional AI services for enhanced functionality.