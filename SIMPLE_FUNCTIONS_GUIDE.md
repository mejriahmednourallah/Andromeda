# Andromeda Memory System - Simple Function Overview

## What is Andromeda?
Andromeda is a Django web application that helps people save and organize their personal memories (called "souvenirs" in French). It's like a digital photo album + journal with AI features.

## Main Parts of the System

### 🗄️ **Data Models (What gets stored)**

#### **Souvenir (Memory)**
```
What it stores:
- Title and description of the memory
- Date when it happened
- Photo or video (optional)
- Emotions (joy, sadness, nostalgia, etc.)
- Theme (family, travel, work, etc.)
- Location and people present
- Favorite status and privacy settings
- AI analysis results
```

#### **Other Important Data**:
- **User**: People who use the app
- **Album**: Collections of memories
- **Time Capsule**: Memories locked until future date
- **Journal Entries**: Text entries that can link to memories
- **AI Analysis**: Smart analysis of photos and text

### 🎯 **Main Functions (What users can do)**

#### **1. Create Memories** (`ajouter_souvenir`)
```
User fills a form → System validates → Saves to database → Shows success message
```

#### **2. View Memories** (`liste_souvenirs`, `detail_souvenir`)
```
Gets memories from database → Shows in list or detail view → User can see photos/videos
```

#### **3. Edit/Delete Memories** (`modifier_souvenir`, `supprimer_souvenir`)
```
Finds memory → Shows edit form → Saves changes → Or deletes with confirmation
```

#### **4. Search & Filter** (`filtrer_souvenirs`)
```
User chooses filters → System queries database → Shows matching memories
```

#### **5. AI Analysis** (`analyser_souvenir_ia`)
```
Takes memory → Sends to AI → Gets emotions/keywords → Saves results → Shows enhanced memory
```

#### **6. Time Capsules** (`creer_capsule`, `ouvrir_capsule`)
```
Create memory with future date → Locks it → User gets notified when ready → Can open with reflection
```

#### **7. Albums** (`creer_album`, `liste_albums`)
```
User selects memories → Creates collection → Can view album with all memories
```

### 🔧 **How Forms Work**

#### **SouvenirForm** (Memory Creation Form)
```python
# What it does:
def clean_titre(self):  # Checks title is not empty and long enough
def clean_description(self):  # Checks description meets requirements
def clean_photo(self):  # Validates photo file type and size
def clean_date_evenement(self):  # Prevents future dates
```

### 🛣️ **URL System (How pages connect)**

```
/dashboard/          → Main dashboard
/memories/           → List all memories
/memories/add/       → Create new memory
/memories/<id>/      → View specific memory
/ai-gallery/         → AI analysis tools
/capsules/           → Time capsule features
/albums/             → Memory collections
```

### 🤖 **AI Features**

#### **What AI Does**:
- **Text Analysis**: Finds emotions, creates summaries, extracts keywords
- **Image Analysis**: Detects objects, colors, faces, locations
- **Predictions**: Guesses future emotions for time capsules
- **Suggestions**: Recommends album themes, reflection prompts

### 🔒 **Security & Validation**

#### **User Permissions**:
- Users can only see/edit their own memories
- File uploads are checked for safety
- Dates can't be in the future

#### **Data Validation**:
- Titles must be 3+ characters
- Descriptions must be 10+ characters
- Photos max 10MB, videos max 100MB
- Only allowed file types

### 📊 **Dashboard & Statistics**

#### **What it shows**:
- Total number of memories
- Recent activity
- Favorite memories
- AI analysis progress
- Achievement progress

## Simple Workflow Example

1. **User signs up** → Account created
2. **User goes to dashboard** → Sees overview
3. **User clicks "Add Memory"** → Fills form
4. **System validates form** → Saves if valid
5. **AI analyzes memory** → Adds smart tags
6. **User can organize in albums** → Creates collections
7. **User can share memories** → Sets privacy levels

## Key Files & Their Jobs

- **`models.py`**: Defines what data looks like
- **`views.py`**: Contains the logic for each page
- **`forms.py`**: Handles form validation and user input
- **`urls.py`**: Connects URLs to view functions
- **`templates/`**: HTML files that show the pages
- **`admin.py`**: Admin interface for managing data

This system combines traditional journaling with modern AI features to create a comprehensive personal memory management tool.