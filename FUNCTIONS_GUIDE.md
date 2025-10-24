# Andromeda Project - Complete Function Guide

## Overview
Andromeda is a comprehensive Django-based personal memory management system that allows users to create, organize, and analyze their life memories with AI-powered features.

## Core Architecture

### 1. Models (Data Structure)

#### **User Model** (`core.models.User`)
- **Purpose**: Extended Django user with avatar support
- **Fields**: username, email, password, avatar_url
- **Usage**: Authentication and user profile management

#### **Souvenir Model** (`core.models.Souvenir`)
- **Purpose**: Main memory storage with rich metadata
- **Key Fields**:
  - `titre`: Memory title (required)
  - `description`: Detailed description (required)
  - `date_evenement`: Event date (required, cannot be future)
  - `photo/video`: Media attachments (optional, size limits)
  - `emotion/theme`: Categorization (8 emotions, 10 themes)
  - `lieu/personnes_presentes`: Context information
  - `is_favorite/is_public`: User preferences
- **AI Features**: Auto-analysis, summaries, emotion detection, tags
- **Validation**: File size limits, date constraints, content requirements

#### **Supporting Models**:
- **AnalyseIASouvenir**: AI analysis results (emotions, keywords, objects)
- **AlbumSouvenir**: Memory collections with auto-generated covers
- **CapsuleTemporelle**: Time-locked memories (future opening)
- **PartageSouvenir**: Social sharing with privacy levels
- **EntreeJournal**: Journal entries linkable to memories
- **SuiviMotivationnel**: Gamification tracking (streaks, badges)
- **Badge/UserBadge**: Achievement system

### 2. Views (Business Logic)

#### **Authentication Views**
- `signup()`: User registration with custom form
- `login()`: Django built-in authentication

#### **Dashboard Views**
- `dashboard()`: Main dashboard with statistics and recent activity
- `index()`: Public homepage with sample notes

#### **Memory CRUD Views**
- `ajouter_souvenir()`: Create new memory with validation
- `liste_souvenirs()`: List user's memories with pagination
- `detail_souvenir()`: View memory details with media
- `modifier_souvenir()`: Edit existing memory
- `supprimer_souvenir()`: Delete memory with confirmation

#### **Advanced Memory Features**
- `filtrer_souvenirs()`: Filter by emotion, theme, date, favorites
- `toggle_favori()`: AJAX toggle favorite status
- `rechercher_souvenirs()`: Full-text search across memories

#### **AI-Powered Views**
- `analyser_souvenir_ia()`: Single memory AI analysis
- `galerie_ia()`: AI insights dashboard
- `analyser_tout_ia()`: Batch analysis of pending memories

#### **Time Capsule Views**
- `creer_capsule()`: Create future-locked memory
- `liste_capsules()`: View locked/opened capsules
- `ouvrir_capsule()`: Open ready capsules with reflection
- `detail_capsule()`: View opened capsule details

#### **Album Views**
- `liste_albums()`: Browse memory collections
- `creer_album()`: Create new album with memory selection
- `detail_album()`: View album contents

#### **Social Features**
- `partager_souvenir()`: Share memories with privacy controls
- `liste_partages()`: View shared memories

#### **Export & Analytics**
- `exporter_pdf()`: Generate PDF exports of memories
- `statistiques()`: User activity analytics
- `suivi_motivationnel()`: Gamification dashboard

### 3. Forms (Data Validation)

#### **SouvenirForm**
- **Purpose**: Memory creation/editing with comprehensive validation
- **Fields**: All Souvenir fields with custom widgets
- **Validation Methods**:
  - `clean_titre()`: Title length (3+ chars) and required
  - `clean_description()`: Description length (10+ chars) and required
  - `clean_photo()`: File type and size validation (10MB max)
  - `clean_video()`: File type and size validation (100MB max)
  - `clean_date_evenement()`: Prevents future dates

#### **Other Forms**
- `UserCreationForm`: Custom signup with email
- `CapsuleTemporelleForm`: Time capsule creation
- `RechercheForm`: Advanced search filters
- `PartageForm`: Memory sharing configuration

### 4. URL Routing (`core/urls.py`)

#### **URL Patterns**:
```
Dashboard: /dashboard/
Memories: /memories/ (CRUD operations)
AI Features: /ai-gallery/ (analysis tools)
Time Capsules: /capsules/ (future memories)
Albums: /albums/ (memory collections)
```

### 5. Key Workflows

#### **Memory Creation Process**:
1. User fills SouvenirForm
2. Form validation (title, description, date, files)
3. Memory saved with user association
4. Optional AI analysis triggered
5. Success message and redirect

#### **AI Analysis Workflow**:
1. Memory submitted for analysis
2. Text analysis (emotions, keywords, summary)
3. Image analysis (objects, colors, faces)
4. Results stored in AnalyseIASouvenir
5. Memory marked as analyzed

#### **Time Capsule Process**:
1. Memory created with future opening date
2. Capsule locked until opening date
3. User notified when ready to open
4. Opening requires reflection on current emotions
5. Growth metrics calculated (prediction accuracy)

#### **Gamification System**:
1. Track user activity (memories created, journals, shares)
2. Calculate streaks and achievements
3. Award badges based on milestones
4. Show motivational messages

### 6. File Upload Handling

#### **Media Storage**:
- Photos: `media/souvenirs/photos/YYYY/MM/`
- Videos: `media/souvenirs/videos/YYYY/MM/`
- Exports: `media/exports/pdf/`
- Albums: `media/albums/`

#### **File Validation**:
- **Photos**: JPG, PNG, GIF, WebP (max 10MB)
- **Videos**: MP4, AVI, MOV, WMV, MKV (max 100MB)
- **Security**: Extension checking, size limits

### 7. AI Integration

#### **AIAnalysisService**:
- `analyze_memory()`: Complete analysis pipeline
- `predict_future_emotion()`: Time capsule predictions
- `generate_album_suggestions()`: Smart album creation

#### **AIRecommendationService**:
- `get_memory_insights()`: User behavior insights
- `suggest_reflection_prompts()`: Journaling prompts

### 8. Security Features

#### **Authentication**: Django's auth system
#### **Authorization**: User ownership validation on all views
#### **File Security**: Type and size validation
#### **Data Privacy**: Public/private memory controls

### 9. Database Design

#### **Relationships**:
- User → Souvenirs (1:many)
- Souvenir → AnalyseIASouvenir (1:1)
- Souvenir ↔ AlbumSouvenir (many:many)
- Souvenir → CapsuleTemporelle (1:1)
- User → SuiviMotivationnel (1:1)

#### **Indexes**: Optimized for date-based queries and user filtering

### 10. Error Handling

#### **Form Validation**: Comprehensive field validation with user-friendly messages
#### **Exception Handling**: Try/catch blocks with logging
#### **User Feedback**: Success/error messages via Django messages framework

## How Functions Work Together

1. **User Journey**: Signup → Dashboard → Create Memory → AI Analysis → Organize in Albums → Share or Export

2. **Data Flow**: Form → Validation → Model Save → AI Processing → Template Rendering → User Display

3. **AI Integration**: Memories → Analysis Service → Database Storage → Enhanced Display

4. **Social Features**: Memory Creation → Sharing Configuration → Privacy Controls → Public Access

This system provides a complete personal memory management experience with modern features like AI analysis, time capsules, and gamification.