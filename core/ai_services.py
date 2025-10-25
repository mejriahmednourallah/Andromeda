"""
AI Services for Memory Analysis
Provides multi-modal AI analysis (text + image + video)
"""
import logging
import os
from django.conf import settings
from django.utils import timezone
from .models import Souvenir, AnalyseIASouvenir

logger = logging.getLogger(__name__)

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logger.warning("OpenAI package not installed. Using simulated analysis.")

try:
    from google.cloud import vision
    from google.oauth2 import service_account
    GOOGLE_VISION_AVAILABLE = True
except ImportError:
    GOOGLE_VISION_AVAILABLE = False
    logger.warning("Google Cloud Vision package not installed. Using simulated analysis.")


class AIAnalysisService:
    """
    Service for analyzing memories with AI
    Currently uses simulated analysis - replace with real AI APIs
    """
    
    @staticmethod
    def analyze_memory(souvenir):
        """
        Perform complete AI analysis on a memory
        Returns: AnalyseIASouvenir instance
        """
        try:
            # Check if already analyzed by querying the database
            from .models import AnalyseIASouvenir
            existing_analysis = AnalyseIASouvenir.objects.filter(souvenir=souvenir).first()
            if existing_analysis:
                logger.info(f"Memory {souvenir.id} already has AI analysis")
                return existing_analysis

            # Perform text analysis
            text_analysis = AIAnalysisService._analyze_text(souvenir.description, souvenir.titre)

            # Perform image analysis if photo exists
            image_analysis = {}
            if souvenir.photo:
                image_analysis = AIAnalysisService._analyze_image(souvenir.photo)

            # Create analysis record
            analyse = AnalyseIASouvenir.objects.create(
                souvenir=souvenir,
                resume_genere=text_analysis.get('summary', ''),
                mots_cles=text_analysis.get('keywords', []),
                emotion_texte=text_analysis.get('emotion', ''),
                score_emotion_texte=text_analysis.get('emotion_score', 0.0),
                objets_detectes=image_analysis.get('objects', []),
                lieu_detecte=image_analysis.get('location', ''),
                personnes_detectees=image_analysis.get('faces_count', 0),
                emotion_image=image_analysis.get('emotion', ''),
                couleurs_dominantes=image_analysis.get('colors', []),
                modele_utilise=settings.AI_TEXT_MODEL if OPENAI_AVAILABLE and settings.OPENAI_API_KEY else 'simulated',
                confiance_globale=text_analysis.get('confidence', 0.75)
            )

            # Update memory AI fields
            souvenir.ai_summary = text_analysis.get('summary', '')
            souvenir.ai_emotion_detected = text_analysis.get('emotion', '')
            souvenir.ai_tags = text_analysis.get('keywords', [])
            souvenir.ai_analyzed = True
            souvenir.ai_analysis_date = timezone.now()

            # Auto-suggest/override emotion if AI is confident
            ai_emotion = text_analysis.get('emotion', '')
            logger.info(f"AI emotion detected: '{ai_emotion}' for memory {souvenir.id}")
            if ai_emotion and ai_emotion in dict(Souvenir.EMOTION_CHOICES):
                old_emotion = souvenir.emotion
                souvenir.emotion = ai_emotion
                logger.info(f"Updated emotion from '{old_emotion}' to '{ai_emotion}' for memory {souvenir.id}")
            else:
                logger.warning(f"AI emotion '{ai_emotion}' not in valid choices or empty for memory {souvenir.id}")

            # Auto-suggest/override theme if AI can infer from keywords
            ai_theme = AIAnalysisService._suggest_theme_from_keywords(text_analysis.get('keywords', []))
            logger.info(f"AI theme suggested: '{ai_theme}' for memory {souvenir.id}")
            if ai_theme and ai_theme in dict(Souvenir.THEME_CHOICES):
                old_theme = souvenir.theme
                souvenir.theme = ai_theme
                logger.info(f"Updated theme from '{old_theme}' to '{ai_theme}' for memory {souvenir.id}")
            else:
                logger.warning(f"AI theme '{ai_theme}' not in valid choices or empty for memory {souvenir.id}")

            souvenir.save()
            logger.info(f"Souvenir {souvenir.id} saved with emotion='{souvenir.emotion}', theme='{souvenir.theme}'")

            logger.info(f"Successfully analyzed memory {souvenir.id}")
            return analyse

        except Exception as e:
            logger.error(f"Error analyzing memory {souvenir.id}: {str(e)}")
            raise

    @staticmethod
    def _suggest_theme_from_keywords(keywords):
        """
        Suggest a theme based on AI keywords (improved mapping)
        """
        if not keywords:
            return 'other'
        
        # Convert keywords to lowercase for matching
        keywords_lower = [kw.lower() for kw in keywords]
        
        theme_map = {
            'family': ['family', 'parent', 'child', 'children', 'mom', 'dad', 'sister', 'brother', 'cousin', 
                      'famille', 'père', 'mère', 'parents', 'enfants', 'fils', 'fille', 'frère', 'sœur'],
            'travel': ['travel', 'trip', 'journey', 'vacation', 'holiday', 'paris', 'city', 'country', 'beach', 'mountain', 'adventure',
                      'voyage', 'ville', 'pays', 'plage', 'montagne', 'rome', 'italie', 'italy', 'londres', 'london',
                      'tokyo', 'japan', 'japon', 'new york', 'amérique', 'america', 'chine', 'china', 'espagne', 'spain',
                      'destination', 'découverte', 'exploration', 'tourisme', 'tourist', 'étranger', 'foreign'],
            'work': ['work', 'job', 'office', 'project', 'meeting', 'colleague', 'boss', 'career', 'profession',
                    'travail', 'emploi', 'bureau', 'projet', 'réunion', 'collègue', 'patron', 'carrière', 'professionnel'],
            'friends': ['friend', 'friends', 'party', 'gathering', 'hangout', 'social', 'amis', 'soirée', 'fête',
                       'rencontre', 'social', 'groupe', 'communauté', 'relation', 'liens'],
            'achievement': ['achievement', 'award', 'win', 'success', 'goal', 'accomplishment', 'prize', 'victory',
                           'réussite', 'succès', 'prix', 'victoire', 'objectif', 'accomplissement', 'diplôme', 'certificat',
                           'promotion', 'récompense', 'mérite', 'excellence', 'réussir', 'accomplir', 'atteindre', 'obtenir'],
            'celebration': ['celebration', 'birthday', 'wedding', 'anniversary', 'festival', 'event', 'party',
                           'célébration', 'anniversaire', 'mariage', 'fête', 'événement', 'festival', 'commémoration',
                           'amusement', 'fun', 'entertainment', 'loisirs', 'divertissement', 'roller', 'coaster', 'attraction',
                           'parc', 'thrilling', 'exciting', 'adventure', 'aventure', 'amusant', 'distraction'],
            'nature': ['nature', 'forest', 'tree', 'river', 'mountain', 'beach', 'lake', 'outdoors', 'landscape',
                      'forêt', 'arbre', 'rivière', 'montagne', 'plage', 'lac', 'extérieur', 'paysage', 'campagne'],
            'learning': ['learning', 'study', 'school', 'university', 'class', 'lesson', 'teacher', 'exam', 'education',
                        'apprentissage', 'étude', 'école', 'université', 'cours', 'leçon', 'professeur', 'examen', 'éducation'],
        }
        
        # Score themes based on keyword matches
        theme_scores = {}
        for theme, words in theme_map.items():
            score = 0
            for keyword in keywords_lower:
                for word in words:
                    if word in keyword or keyword in word:  # Partial matching
                        score += 1
            if score > 0:
                theme_scores[theme] = score
        
        # Return theme with highest score, or 'other' if no matches
        if theme_scores:
            best_theme = max(theme_scores.items(), key=lambda x: x[1])
            return best_theme[0]
        
        return 'other'
    
    @staticmethod
    def _analyze_text(title, description):
        """
        Analyze text content (description + title)
        Uses OpenAI API if available, otherwise simulated analysis
        """
        text = f"{title}. {description}"

        if OPENAI_AVAILABLE and settings.OPENAI_API_KEY:
            try:
                client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)

                # Generate summary
                summary_prompt = f"""
                Summarize this memory in 2-3 sentences, capturing the essence and emotional impact:

                Title: {title}
                Description: {description}

                Summary:
                """

                summary_response = client.chat.completions.create(
                    model=settings.AI_TEXT_MODEL,
                    messages=[{"role": "user", "content": summary_prompt}],
                    max_tokens=150,
                    temperature=0.3
                )
                summary = summary_response.choices[0].message.content.strip()

                # Extract keywords
                keywords_prompt = f"""
                Extract 5-8 key themes, people, places, or emotions from this memory. Return as a comma-separated list:

                Title: {title}
                Description: {description}

                Keywords:
                """

                keywords_response = client.chat.completions.create(
                    model=settings.AI_TEXT_MODEL,
                    messages=[{"role": "user", "content": keywords_prompt}],
                    max_tokens=100,
                    temperature=0.2
                )
                keywords_text = keywords_response.choices[0].message.content.strip()
                keywords = [k.strip() for k in keywords_text.split(',') if k.strip()]


                # Detect emotion (improved extraction)
                emotion_prompt = f"""
                Analyze the emotional tone of this memory and return ONLY ONE WORD (no explanation), the primary emotion from this list: joy, sadness, nostalgia, gratitude, excitement, anger, fear, love, peace, neutral.

                Title: {title}
                Description: {description}

                Primary emotion:
                """

                emotion_response = client.chat.completions.create(
                    model=settings.AI_TEXT_MODEL,
                    messages=[{"role": "user", "content": emotion_prompt}],
                    max_tokens=5,
                    temperature=0.1
                )
                emotion_raw = emotion_response.choices[0].message.content.strip().lower()
                logger.info(f"OpenAI raw emotion response: '{emotion_raw}' for memory '{title}'")
                valid_emotions = ['joy', 'sadness', 'nostalgia', 'gratitude', 'excitement', 'anger', 'fear', 'love', 'peace', 'neutral']
                # Try exact match first
                if emotion_raw in valid_emotions:
                    emotion = emotion_raw
                else:
                    # Try to find a valid emotion in the response string
                    emotion = next((e for e in valid_emotions if e in emotion_raw), 'neutral')

                logger.info(f"Extracted emotion: '{emotion}' for memory '{title}'")
                return {
                    'summary': summary,
                    'keywords': keywords[:10],  # Limit to 10 keywords
                    'emotion': emotion,
                    'emotion_score': 0.9,
                    'confidence': 0.85
                }

            except Exception as e:
                logger.error(f"OpenAI API error: {str(e)}. Falling back to simulated analysis.")
        # Fallback to simulated analysis
        logger.warning("Using simulated text analysis (OpenAI unavailable or error)")
        
        # Improved simulated analysis
        full_text = f"{title}. {description}"
        
        # Generate better summary
        if len(description) > 100:
            # Try to create a meaningful summary
            sentences = description.split('.')
            if len(sentences) > 1:
                summary = f"{sentences[0].strip()}. {sentences[1].strip()}." if len(sentences) > 1 else sentences[0].strip()
            else:
                summary = description[:120] + "..."
        else:
            summary = description
        
        # Extract better keywords
        keywords = AIAnalysisService._extract_keywords_smart(full_text)
        
        # Detect emotion more intelligently
        emotion = AIAnalysisService._detect_emotion_smart(full_text)
        
        return {
            'summary': summary,
            'keywords': keywords,
            'emotion': emotion,
            'emotion_score': 0.85,
            'confidence': 0.82
        }
    
    @staticmethod
    def _analyze_image(photo):
        """
        Analyze image content
        Uses Google Vision API if available, otherwise simulated analysis
        """
        if GOOGLE_VISION_AVAILABLE and settings.GOOGLE_VISION_API_KEY:
            try:
                # Initialize Google Vision client
                client = vision.ImageAnnotatorClient()

                # Read image file
                with open(photo.path, 'rb') as image_file:
                    content = image_file.read()

                image = vision.Image(content=content)

                # Perform label detection (objects)
                label_response = client.label_detection(image=image)
                objects = [label.description.lower() for label in label_response.label_annotations[:5]]

                # Perform face detection
                face_response = client.face_detection(image=image)
                faces_count = len(face_response.face_annotations)

                # Perform text detection (for location hints)
                text_response = client.text_detection(image=image)
                detected_text = ' '.join([text.description for text in text_response.text_annotations[:3]])

                # Perform image properties (colors)
                properties_response = client.image_properties(image=image)
                colors = []
                if properties_response.image_properties_annotation:
                    dominant_colors = properties_response.image_properties_annotation.dominant_colors.colors[:3]
                    colors = [f"#{int(c.color.red):02x}{int(c.color.green):02x}{int(c.color.blue):02x}" for c in dominant_colors]

                # Try to detect location from landmarks
                landmark_response = client.landmark_detection(image=image)
                location = ""
                if landmark_response.landmark_annotations:
                    location = landmark_response.landmark_annotations[0].description

                # Estimate emotion from faces (if faces detected)
                emotion = 'neutral'
                if faces_count > 0 and face_response.face_annotations:
                    # Use the emotion of the most prominent face
                    face = face_response.face_annotations[0]
                    joy_likelihood = face.joy_likelihood
                    sorrow_likelihood = face.sorrow_likelihood
                    anger_likelihood = face.anger_likelihood
                    surprise_likelihood = face.surprise_likelihood

                    emotions = {
                        'joy': joy_likelihood,
                        'sadness': sorrow_likelihood,
                        'anger': anger_likelihood,
                        'surprise': surprise_likelihood
                    }

                    # Find emotion with highest likelihood
                    max_emotion = max(emotions.items(), key=lambda x: x[1])
                    if max_emotion[1] >= 3:  # LIKELY or VERY_LIKELY
                        emotion = max_emotion[0]

                return {
                    'objects': objects,
                    'location': location or 'Location not detected',
                    'faces_count': faces_count,
                    'emotion': emotion,
                    'colors': colors,
                    'detected_text': detected_text
                }

            except Exception as e:
                logger.error(f"Google Vision API error: {str(e)}. Falling back to simulated analysis.")

        # Fallback to simulated analysis
        logger.info("Using simulated image analysis")
        return {
            'objects': ['landscape', 'people', 'nature'],
            'location': 'Detected: outdoor scene',
            'faces_count': 2,
            'emotion': 'joy',
            'colors': ['#3498db', '#2ecc71', '#f39c12']
        }
    
    @staticmethod
    def _extract_keywords_smart(text):
        """
        Extract important keywords from text (improved version with French support and bigrams)
        """
        import re
        from collections import Counter
        
        # Comprehensive French stop words
        french_stop_words = {
            # Articles
            'le', 'la', 'les', 'l', 'un', 'une', 'des', 'du', 'de', 'd',
            # Pronouns
            'je', 'tu', 'il', 'elle', 'nous', 'vous', 'ils', 'elles', 'me', 'te', 'se', 'y',
            'en', 'ce', 'ça', 'cet', 'cette', 'ces', 'mon', 'ton', 'son', 'ma', 'ta', 'sa',
            'mes', 'tes', 'ses', 'notre', 'votre', 'leur', 'nos', 'vos', 'leurs',
            # Prepositions
            'à', 'au', 'aux', 'avec', 'chez', 'dans', 'de', 'des', 'du', 'en', 'par', 'pour',
            'sans', 'sous', 'sur', 'vers', 'dans', 'par', 'pour',
            # Conjunctions
            'et', 'ou', 'mais', 'donc', 'car', 'ni', 'que', 'qui', 'quoi', 'dont', 'où',
            # Adverbs
            'ne', 'pas', 'plus', 'tout', 'toute', 'tous', 'toutes', 'très', 'bien', 'mal',
            'peu', 'beaucoup', 'trop', 'assez', 'encore', 'déjà', 'jamais', 'toujours',
            # Common verbs
            'être', 'avoir', 'faire', 'aller', 'venir', 'voir', 'savoir', 'pouvoir', 'dire',
            'vouloir', 'venir', 'partir', 'prendre', 'mettre', 'donner', 'trouver', 'parler',
            'écouter', 'regarder', 'attendre', 'chercher', 'laisser', 'passer', 'tenir',
            # English stop words (for mixed content)
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with',
            'by', 'from', 'as', 'is', 'was', 'are', 'were', 'been', 'this', 'that', 'these',
            'those', 'i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'you', 'your', 'yours',
            'he', 'him', 'his', 'she', 'her', 'hers', 'it', 'its', 'they', 'them', 'their',
            'theirs', 'what', 'which', 'who', 'when', 'where', 'why', 'how', 'all', 'any',
            'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor',
            'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 'can', 'will',
            'just', 'don', 'should', 'now'
        }
        
        # Clean and normalize text
        text = text.lower()
        # Remove punctuation but keep spaces
        text = re.sub(r'[^\w\s]', ' ', text)
        # Normalize spaces
        text = re.sub(r'\s+', ' ', text).strip()
        
        words = text.split()
        
        # Extract unigrams (single words)
        unigrams = []
        for word in words:
            if (len(word) >= 3 and  # At least 3 characters
                word not in french_stop_words and  # Not a stop word
                not any(char.isdigit() for char in word) and  # No numbers
                not word.startswith(('http', 'www'))):  # No URLs
                unigrams.append(word)
        
        # Extract bigrams (two-word phrases)
        bigrams = []
        for i in range(len(words) - 1):
            bigram = f"{words[i]} {words[i+1]}"
            # Check if both words are meaningful
            if (len(words[i]) >= 3 and len(words[i+1]) >= 3 and
                words[i] not in french_stop_words and words[i+1] not in french_stop_words and
                not any(char.isdigit() for char in bigram)):
                bigrams.append(bigram)
        
        # Extract trigrams (three-word phrases) - for very specific phrases
        trigrams = []
        for i in range(len(words) - 2):
            trigram = f"{words[i]} {words[i+1]} {words[i+2]}"
            # Only keep trigrams that seem meaningful
            if (all(len(words[i+j]) >= 3 for j in range(3)) and
                all(words[i+j] not in french_stop_words for j in range(3)) and
                not any(char.isdigit() for char in trigram)):
                trigrams.append(trigram)
        
        # Score all candidates
        candidates = []
        
        # Score unigrams
        unigram_counts = Counter(unigrams)
        for word, count in unigram_counts.items():
            score = count * 2  # Base frequency score
            
            # Bonus for emotional words
            emotional_words = {
                'bonheur', 'joie', 'amour', 'passion', 'tristesse', 'peine', 'colère', 'peur',
                'heureux', 'content', 'satisfait', 'fier', 'proud', 'excité', 'enthousiaste',
                'nostalgique', 'gratitude', 'reconnaissant', 'chanceux', 'privilège'
            }
            if word in emotional_words:
                score += 3
            
            # Bonus for achievement words
            achievement_words = {
                'réussite', 'succès', 'accomplissement', 'objectif', 'projet', 'présentation',
                'travail', 'acharné', 'diplôme', 'promotion', 'victoire', 'récompense'
            }
            if word in achievement_words:
                score += 2
            
            candidates.append((word, score, 'unigram'))
        
        # Score bigrams
        bigram_counts = Counter(bigrams)
        for bigram, count in bigram_counts.items():
            score = count * 3  # Bigrams get higher base score
            
            # Bonus for meaningful bigrams
            meaningful_bigrams = {
                'projet universitaire', 'travail acharné', 'présenté succès', 'sentiment fier',
                'moment spécial', 'grande réussite', 'effort récompensé', 'objectif atteint'
            }
            if bigram in meaningful_bigrams:
                score += 5
            
            candidates.append((bigram, score, 'bigram'))
        
        # Score trigrams (rare but very specific)
        trigram_counts = Counter(trigrams)
        for trigram, count in trigram_counts.items():
            score = count * 4  # Trigrams get highest base score
            candidates.append((trigram, score, 'trigram'))
        
        # Sort by score and return top keywords
        sorted_candidates = sorted(candidates, key=lambda x: x[1], reverse=True)
        
        # Extract top keywords, preferring variety (mix of unigrams and bigrams)
        top_keywords = []
        unigram_count = 0
        bigram_count = 0
        
        for keyword, score, type_ in sorted_candidates:
            if len(top_keywords) >= 8:
                break
                
            # Balance between unigrams and bigrams
            if type_ == 'unigram' and unigram_count < 5:
                top_keywords.append(keyword)
                unigram_count += 1
            elif type_ == 'bigram' and bigram_count < 3:
                top_keywords.append(keyword)
                bigram_count += 1
            elif type_ == 'trigram' and len(keyword.split()) == 3:
                # Only add trigrams if they're really meaningful
                top_keywords.append(keyword)
        
        # If we don't have enough keywords, add context-aware ones
        if len(top_keywords) < 5:
            context_keywords = []
            text_lower = text.lower()
            
            # Academic/Work context
            if any(word in text_lower for word in ['universitaire', 'projet', 'présentation', 'diplôme', 'examen']):
                context_keywords.extend(['réussite académique', 'projet universitaire', 'travail intellectuel'])
            
            # Achievement context
            if any(word in text_lower for word in ['réussi', 'succès', 'accompli', 'fier', 'satisfait']):
                context_keywords.extend(['accomplissement personnel', 'succès obtenu', 'fierté personnelle'])
            
            # Time/Effort context
            if any(word in text_lower for word in ['mois', 'années', 'travail', 'effort', 'acharné']):
                context_keywords.extend(['effort soutenu', 'travail régulier', 'persévérance'])
            
            # Add context keywords if not already present
            for keyword in context_keywords[:3]:
                if keyword not in top_keywords:
                    top_keywords.append(keyword)
        
        return top_keywords[:8] if top_keywords else ['mémoire', 'souvenir', 'moment']
    
    @staticmethod
    def _detect_emotion_smart(text):
        """
        Detect emotion from text (improved version)
        """
        text_lower = text.lower()
        
        # Emotion patterns with weights
        emotion_patterns = {
            'joy': {
                'words': ['heureux', 'joyeux', 'content', 'super', 'génial', 'fantastique', 'merveilleux', 
                         'bonheur', 'plaisir', 'amusement', 'excité', 'enthousiaste', 'rires', 'sourire',
                         'happy', 'joy', 'great', 'wonderful', 'amazing', 'exciting', 'fun', 'love',
                         'satisfait', 'comblé', 'ravi', 'enchanté', 'jubilant'],
                'weight': 3
            },
            'sadness': {
                'words': ['triste', 'malheureux', 'déprimé', 'chagrin', 'peine', 'nostalgique', 'regret',
                         'manque', 'seul', 'abandonné', 'déçu', 'tristesse', 'larmes', 'pleurer',
                         'sad', 'unhappy', 'depressed', 'sorry', 'miss', 'alone', 'disappointed'],
                'weight': 3
            },
            'nostalgia': {
                'words': ['nostalgique', 'souvenir', 'rappelle', 'autrefois', 'jadis', 'passé', 'mémoire',
                         'revient', 'époque', 'temps', 'années', 'enfance', 'jeunesse', 'ancien',
                         'nostalgia', 'remember', 'memory', 'past', 'old', 'childhood', 'youth'],
                'weight': 2
            },
            'gratitude': {
                'words': ['remercié', 'reconnaissant', 'gratitude', 'chanceux', 'béni', 'merci', 'apprécié',
                         'reconnaissance', 'chance', 'privilège', 'félicité', 'satisfait',
                         'grateful', 'thankful', 'blessed', 'lucky', 'appreciate', 'fortunate',
                         'reconnaissant', 'gratitude', 'merci', 'remerciements'],
                'weight': 2
            },
            'excitement': {
                'words': ['excité', 'enthousiaste', 'impatient', 'passionné', 'énergie', 'vibrant', 'vivant',
                         'dynamique', 'fou', 'incroyable', 'extraordinaire', 'spectaculaire', 'époustouflant',
                         'excited', 'thrilled', 'passionate', 'amazing', 'incredible', 'spectacular',
                         'passionnant', 'stimulant', 'électrisant'],
                'weight': 2
            },
            'love': {
                'words': ['amour', 'aimé', 'tendresse', 'affection', 'chéri', 'adoré', 'passion', 'romantique',
                         'cœur', 'sentimental', 'intime', 'proche', 'union', 'lien', 'attachement',
                         'love', 'beloved', 'dear', 'darling', 'passion', 'romantic', 'heart', 'close'],
                'weight': 3
            },
            'peace': {
                'words': ['paix', 'calme', 'sérénité', 'tranquille', 'repos', 'détente', 'harmonie', 'équilibre',
                         'zen', 'méditation', 'contemplation', 'nature', 'océan', 'montagne', 'jardin',
                         'peace', 'calm', 'serene', 'quiet', 'relaxed', 'harmony', 'balance', 'nature'],
                'weight': 2
            },
            'anger': {
                'words': ['énervé', 'furieux', 'colère', 'rage', 'frustré', 'agacé', 'irrité', 'énervant',
                         'contrarié', 'dégoûté', 'mécontent', 'hostile', 'violent', 'agressif',
                         'angry', 'furious', 'mad', 'frustrated', 'annoyed', 'irritated', 'upset'],
                'weight': 2
            },
            'fear': {
                'words': ['peur', 'angoisse', 'inquiétude', 'stress', 'anxiété', 'terreur', 'panique',
                         'effrayé', 'horrifié', 'crainte', 'appréhension', 'nerveux', 'tendu',
                         'fear', 'anxiety', 'worry', 'stress', 'terror', 'panic', 'scared', 'afraid'],
                'weight': 2
            },
            'pride': {  # New emotion for achievements
                'words': ['fier', 'fierté', 'accompli', 'réussi', 'succès', 'réussite', 'accomplissement',
                         'objectif', 'atteint', 'proud', 'pride', 'achievement', 'accomplished',
                         'satisfait', 'content', 'diplôme', 'promotion', 'victoire', 'récompense',
                         'mérite', 'excellent', 'bravo', 'félicitations'],
                'weight': 4  # Higher weight for achievement-related emotions
            }
        }
        
        # Calculate emotion scores
        emotion_scores = {}
        for emotion, data in emotion_patterns.items():
            score = 0
            for word in data['words']:
                count = text_lower.count(word)
                score += count * data['weight']
            emotion_scores[emotion] = score
        
        # Find the emotion with the highest score
        if emotion_scores:
            best_emotion = max(emotion_scores.items(), key=lambda x: x[1])
            if best_emotion[1] > 0:
                # Special handling for pride - it should override neutral for achievement contexts
                if best_emotion[0] == 'pride':
                    return 'pride'
                # For other emotions, only return if score is significant
                elif best_emotion[1] >= 2:  # Minimum threshold
                    return best_emotion[0]
        
        # Default to neutral if no strong emotion detected
        return 'neutral'
    
    @staticmethod
    def generate_time_capsule_message(souvenir):
        """
        Generate an inspirational message for a time capsule based on the memory
        """
        from django.conf import settings
        import logging
        logger = logging.getLogger(__name__)

        # Compose prompt for generating a time capsule message
        prompt = f"""
        You are helping someone create a time capsule message to their future self. Based on this memory, write a short, inspirational message (2-3 sentences) that they can include in their time capsule. The message should be reflective, positive, and help them remember the significance of this moment.

        Memory Title: {souvenir.titre}
        Memory Description: {souvenir.description}
        Original Emotion: {getattr(souvenir, 'get_emotion_display', lambda: souvenir.emotion)()}

        Write a personal, meaningful message that captures the essence of this memory and encourages reflection:
        """

        if OPENAI_AVAILABLE and getattr(settings, 'OPENAI_API_KEY', None):
            try:
                client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
                response = client.chat.completions.create(
                    model=getattr(settings, 'AI_TEXT_MODEL', 'gpt-4o-mini'),
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=150,
                    temperature=0.7  # Higher temperature for more creative messages
                )
                message = response.choices[0].message.content.strip()
                return message
            except Exception as e:
                logger.error(f"OpenAI time capsule message generation failed: {str(e)}. Falling back to simulated.")

        # Simulated fallback messages based on emotion
        emotion_messages = {
            'joy': [
                "Remember this moment of pure joy and let it remind you that happiness is found in life's simple pleasures.",
                "Cherish this feeling of happiness. May it serve as a beacon of light on days when you need it most.",
                "This joy you felt - hold onto it. It's a reminder that beautiful moments are worth savoring."
            ],
            'nostalgia': [
                "As time passes, remember the warmth of this moment. It's a treasure worth revisiting.",
                "This memory holds a special place in your heart. May it bring you comfort and reflection in the future.",
                "Time may change many things, but the significance of this moment remains. Cherish it always."
            ],
            'gratitude': [
                "In this moment of gratitude, remember to always appreciate life's blessings, big and small.",
                "This feeling of thankfulness - may it stay with you and guide you to recognize goodness in your life.",
                "Gratitude is a gift you give yourself. Hold onto this feeling and let it grow with time."
            ],
            'love': [
                "Love, in all its forms, is life's greatest treasure. May this memory remind you of its power.",
                "This moment of love - let it be a reminder that connections with others enrich our lives immensely.",
                "Cherish this feeling of love. It's a beautiful reminder of what makes life meaningful."
            ],
            'peace': [
                "In this peaceful moment, remember that calm can always be found within you, even in stormy times.",
                "This serenity you feel - may it serve as an anchor when life becomes turbulent.",
                "Peace is not the absence of chaos, but the ability to find calm within it. Remember this feeling."
            ],
            'pride': [
                "This moment of pride in your accomplishment - let it fuel your future endeavors and remind you of your capabilities.",
                "Achievement brings its own special joy. May this memory inspire you to reach for new heights.",
                "Be proud of how far you've come. This moment is proof of your strength and determination."
            ]
        }

        # Get messages for the emotion, or use neutral messages
        messages = emotion_messages.get(souvenir.emotion, [
            "This moment in time holds special meaning for you. May revisiting it bring clarity and perspective.",
            "Life's moments, both big and small, shape who we are. Cherish this memory and let it guide you.",
            "Time capsules hold pieces of our journey. May this memory bring you wisdom and reflection in the future."
        ])

        # Return a random message from the appropriate category
        import random
        return random.choice(messages)
    
    @staticmethod
    def predict_future_emotion(souvenir, days_in_future=365):
        """
        Predict user's emotion when they reopen this memory in the future using OpenAI if available, otherwise fallback to simulated logic.
        """
        from django.conf import settings
        import logging
        logger = logging.getLogger(__name__)

        # Compose prompt for OpenAI
        prompt = f"""
        Imagine you are a psychologist and memory expert. Predict the primary emotion a person will feel when revisiting the following memory in {days_in_future} days. Choose ONE from: joy, sadness, nostalgia, gratitude, excitement, anger, fear, love, peace, neutral. Explain your reasoning in 1-2 sentences.

        Title: {souvenir.titre}
        Description: {souvenir.description}
        Original Emotion: {souvenir.get_emotion_display()}
        Event Date: {souvenir.date_evenement}

        Prediction:
        """

        if OPENAI_AVAILABLE and getattr(settings, 'OPENAI_API_KEY', None):
            try:
                client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
                response = client.chat.completions.create(
                    model=getattr(settings, 'AI_TEXT_MODEL', 'gpt-4o-mini'),
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=120,
                    temperature=0.3
                )
                content = response.choices[0].message.content.strip()
                # Try to extract emotion and explanation
                import re
                match = re.match(r"([a-zA-Z]+)[\s:,-]+(.+)?", content)
                if match:
                    emotion = match.group(1).strip().lower()
                    explanation = match.group(2).strip() if match.group(2) else ''
                else:
                    # Fallback: try to find emotion in content
                    valid_emotions = ['joy', 'sadness', 'nostalgia', 'gratitude', 'excitement', 'anger', 'fear', 'love', 'peace', 'neutral']
                    emotion = next((e for e in valid_emotions if e in content.lower()), 'neutral')
                    explanation = content
                # Validate emotion
                if emotion not in ['joy', 'sadness', 'nostalgia', 'gratitude', 'excitement', 'anger', 'fear', 'love', 'peace', 'neutral']:
                    emotion = 'neutral'
                return {
                    'emotion': emotion,
                    'confidence': 0.9,
                    'explanation': explanation or f"AI predicts you will feel {emotion} when revisiting this memory."
                }
            except Exception as e:
                logger.error(f"OpenAI future emotion prediction failed: {str(e)}. Falling back to simulated.")
                # fallback to simulated below

        # Simulated fallback
        current_emotion = souvenir.emotion
        emotion_map = {
            'sadness': ['peace', 'gratitude', 'nostalgia'],
            'joy': ['joy', 'nostalgia', 'gratitude'],
            'nostalgia': ['nostalgia', 'peace'],
            'excitement': ['nostalgia', 'joy'],
            'neutral': ['nostalgia', 'peace'],
        }
        predicted = emotion_map.get(current_emotion, ['peace'])[0]
        confidence = 0.73
        return {
            'emotion': predicted,
            'confidence': confidence,
            'explanation': f"Based on your past patterns, you'll likely feel {predicted} when revisiting this memory."
        }
    
    @staticmethod
    def generate_album_suggestions(user):
        """
        Generate smart album suggestions based on user's memories
        """
        from .models import Souvenir
        from collections import Counter
        
        souvenirs = Souvenir.objects.filter(utilisateur=user)
        
        suggestions = []
        
        # By theme (lowered threshold)
        theme_counts = Counter(s.theme for s in souvenirs if s.theme != 'other')
        for theme, count in theme_counts.most_common(3):
            if count >= 2:  # Changed from 3 to 2
                suggestions.append({
                    'type': 'theme',
                    'title': f"My {theme.replace('_', ' ').title()} Moments",
                    'theme': theme,
                    'count': count
                })
        
        # By year (lowered threshold)
        current_year = timezone.now().year
        year_counts = Counter(s.date_evenement.year for s in souvenirs)
        for year, count in year_counts.most_common(2):
            if count >= 3:  # Changed from 5 to 3
                suggestions.append({
                    'type': 'year',
                    'title': f"Memories from {year}",
                    'year': year,
                    'count': count
                })
        
        # Favorites (lowered threshold)
        favorites_count = souvenirs.filter(is_favorite=True).count()
        if favorites_count >= 2:  # Changed from 3 to 2
            suggestions.append({
                'type': 'favorite',
                'title': "My Favorite Memories",
                'count': favorites_count
            })
        
        # Recent memories (new suggestion type)
        recent_count = souvenirs.filter(date_evenement__year=current_year).count()
        if recent_count >= 1 and not any(s['type'] == 'year' and s['year'] == current_year for s in suggestions):
            suggestions.append({
                'type': 'recent',
                'title': f"This Year's Memories ({current_year})",
                'year': current_year,
                'count': recent_count
            })
        
        # AI analyzed memories (new suggestion type)
        analyzed_count = souvenirs.filter(ai_analyzed=True).count()
        if analyzed_count >= 2:
            suggestions.append({
                'type': 'ai_analyzed',
                'title': "AI-Enriched Memories",
                'count': analyzed_count
            })
        
        # Default suggestions if none generated
        if not suggestions and souvenirs.exists():
            total_count = souvenirs.count()
            suggestions.append({
                'type': 'all',
                'title': f"All My Memories ({total_count} total)",
                'count': total_count
            })
        
        return suggestions[:4]  # Limit to 4 suggestions
    
    @staticmethod
    def get_souvenir_ids_for_suggestion(user, suggestion_type, theme=None, year=None):
        """
        Get souvenir IDs that match a specific album suggestion
        """
        from .models import Souvenir
        
        souvenirs = Souvenir.objects.filter(utilisateur=user)
        
        if suggestion_type == 'theme' and theme:
            return list(souvenirs.filter(theme=theme).values_list('id', flat=True))
        elif suggestion_type == 'year' and year:
            return list(souvenirs.filter(date_evenement__year=year).values_list('id', flat=True))
        elif suggestion_type == 'favorite':
            return list(souvenirs.filter(is_favorite=True).values_list('id', flat=True))
        elif suggestion_type == 'recent':
            current_year = timezone.now().year
            return list(souvenirs.filter(date_evenement__year=current_year).values_list('id', flat=True))
        elif suggestion_type == 'ai_analyzed':
            return list(souvenirs.filter(ai_analyzed=True).values_list('id', flat=True))
        elif suggestion_type == 'all':
            return list(souvenirs.values_list('id', flat=True))
        
        return []


class AIRecommendationService:
    """Service for AI-powered recommendations and insights"""
    
    @staticmethod
    def get_memory_insights(user):
        """
        Generate insights about user's memories
        """
        from .models import Souvenir
        from collections import Counter
        
        souvenirs = Souvenir.objects.filter(utilisateur=user)
        
        if not souvenirs.exists():
            return None
        
        # Emotion distribution
        emotions = [s.emotion for s in souvenirs]
        emotion_counts = Counter(emotions)
        dominant_emotion = emotion_counts.most_common(1)[0][0] if emotion_counts else 'neutral'
        
        # Themes
        themes = [s.theme for s in souvenirs if s.theme != 'other']
        theme_counts = Counter(themes)
        
        # Time analysis
        dates = [s.date_evenement for s in souvenirs]
        oldest = min(dates) if dates else None
        newest = max(dates) if dates else None
        
        insights = {
            'total_memories': souvenirs.count(),
            'dominant_emotion': dominant_emotion,
            'emotion_distribution': dict(emotion_counts),
            'most_common_themes': dict(theme_counts.most_common(3)),
            'time_span': {
                'oldest': oldest,
                'newest': newest,
                'span_days': (newest - oldest).days if oldest and newest else 0
            },
            'favorites_count': souvenirs.filter(is_favorite=True).count(),
            'analyzed_count': souvenirs.filter(ai_analyzed=True).count(),
            'with_media': souvenirs.filter(photo__isnull=False).count()
        }
        
        return insights
    
    @staticmethod
    def suggest_reflection_prompts(user):
        """
        Generate personalized reflection prompts based on user's patterns
        """
        insights = AIRecommendationService.get_memory_insights(user)
        
        if not insights:
            return []
        
        prompts = []
        
        # Based on dominant emotion
        if insights['dominant_emotion'] == 'joy':
            prompts.append("What brings you the most joy in your life?")
        elif insights['dominant_emotion'] == 'nostalgia':
            prompts.append("Which memory would you like to relive and why?")
        
        # Based on themes
        themes = insights['most_common_themes']
        if 'family' in themes:
            prompts.append("Describe a family tradition that means a lot to you.")
        if 'travel' in themes:
            prompts.append("What's the most transformative place you've visited?")
        
        # General prompts
        prompts.extend([
            "What lesson have you learned this year?",
            "Describe your relationship with your best friend.",
            "What are you grateful for today?"
        ])
        
        return prompts[:5]  # Return top 5
    
    @staticmethod
    def generate_inspirational_story(reflexion_text):
        """
        Generate an inspirational story based on a celebrity who overcame similar challenges
        Returns a story in plain text format (150-250 words)
        """
        if not reflexion_text or not reflexion_text.strip():
            return {
                'story': "Parfois, il suffit d'un petit pas pour tout changer. Michael Jordan a été rejeté de l'équipe de basket de son lycée. Mais au lieu d'abandonner, il s'est entraîné chaque jour avec encore plus de détermination.\n\nCette déception est devenue son moteur. Il a transformé la frustration en force. Des années plus tard, il devenait l'un des plus grands joueurs de tous les temps.\n\nSon secret ? Ne jamais laisser un échec définir qui il était. Chaque obstacle était une opportunité d'apprendre, de grandir, de devenir plus fort.\n\nTu as en toi cette même force. Celle qui transforme les doutes en défis, et les défis en victoires. Crois en toi, même quand c'est difficile. Surtout quand c'est difficile.",
                'celebrity': 'Michael Jordan',
                'simulated': True
            }
        
        if OPENAI_AVAILABLE and settings.OPENAI_API_KEY:
            try:
                client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
                
                prompt = f"""Tu es un assistant d'inspiration et de bien-être intégré à une plateforme web moderne.
L'utilisateur vient d'écrire une réflexion personnelle exprimant une émotion, un doute ou une difficulté.

🎯 Ton rôle :
Créer une **courte histoire inspirante** mettant en scène une **star ou personnalité réelle** 
ayant traversé une situation similaire, pour lui montrer que tout le monde peut surmonter ses épreuves.

💡 Objectif :
- Donner espoir et motivation.
- Relier l'histoire à l'émotion exprimée.
- Conclure par une phrase positive, apaisante et mémorable.

🎨 Style à respecter :
- Ton bienveillant, sincère et motivant.
- Style fluide, simple et naturel (langage humain, pas de jargon IA).
- Structure claire :
  1️⃣ Contexte rapide de la star.  
  2️⃣ Son épreuve / difficulté.  
  3️⃣ Comment elle s'en est sortie.  
  4️⃣ Morale ou conseil final.  

🧭 Format attendu :
- Environ 150 à 250 mots.
- Paragraphes courts (max 4 lignes chacun).
- Pas de listes, pas de hashtags.
- Aucune mention de "IA" ou "intelligence artificielle".
- Aucune phrase d'introduction comme "Voici l'histoire…" — commence directement.
- Sortie en texte brut (sans HTML).

🌈 Contexte visuel :
Le texte sera affiché dans une **carte de dashboard moderne**, avec un fond clair et des bordures arrondies.  
Le style général de la plateforme est **calme, épuré et inspirant**, avec des nuances de bleu et de violet.  
Évite les mots négatifs ou dramatiques, reste optimiste et léger.

👤 Entrée de l'utilisateur :
"{reflexion_text}"

✍️ Ta tâche :
Génère une histoire adaptée à ce texte en suivant parfaitement le style ci-dessus.
Ne mentionne jamais le nom de l'utilisateur. 
Termine toujours par une phrase motivante qui incite à croire en soi.
Réponds uniquement avec l'histoire, rien d'autre."""

                response = client.chat.completions.create(
                    model=settings.AI_TEXT_MODEL,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=500,
                    temperature=0.8
                )
                
                story = response.choices[0].message.content.strip()
                
                # Try to extract celebrity name from the story (basic heuristic)
                celebrity = "Une personnalité inspirante"
                
                return {
                    'story': story,
                    'celebrity': celebrity,
                    'simulated': False
                }
                
            except Exception as e:
                logger.error(f"Error generating inspirational story: {str(e)}")
                # Fallback to simulated story
        
        # Simulated stories based on common themes
        simulated_stories = [
            {
                'celebrity': 'J.K. Rowling',
                'story': "J.K. Rowling vivait des moments très difficiles. Mère célibataire, elle touchait le chômage et devait élever sa fille seule dans un petit appartement.\n\nElle écrivait le premier tome d'Harry Potter dans des cafés, pour économiser le chauffage. Douze éditeurs ont refusé son manuscrit. Douze fois, elle a essuyé un \"non\".\n\nMais elle n'a jamais abandonné. Elle croyait en son histoire, en sa plume, en elle-même. Le treizième éditeur a dit oui.\n\nAujourd'hui, elle inspire des millions de personnes à travers le monde. Son parcours nous rappelle que chaque refus nous rapproche du \"oui\" qui changera tout. Continue d'avancer. Ton histoire mérite d'être racontée."
            },
            {
                'celebrity': 'Oprah Winfrey',
                'story': "Oprah Winfrey a grandi dans la pauvreté extrême. Elle a connu l'abandon, les abus, le rejet. À 17 ans, tout semblait perdu.\n\nMais elle avait une voix. Une histoire. Une force intérieure qu'elle refusait de laisser se briser. Elle a transformé sa douleur en pouvoir.\n\nElle a commencé à parler, à partager, à inspirer. Petit à petit, elle est devenue l'une des femmes les plus influentes au monde.\n\nSa force ? Elle n'a jamais laissé son passé définir son futur. Tu as cette même force. Tes épreuves ne te définissent pas. Elles te façonnent. Et tu es plus fort que tu ne le penses."
            },
            {
                'celebrity': 'Nelson Mandela',
                'story': "Nelson Mandela a passé 27 ans en prison. Vingt-sept années d'isolement, d'injustice, de douleur.\n\nMais il n'a jamais perdu espoir. Chaque jour, il choisissait de croire en un avenir meilleur. Il lisait, méditait, grandissait.\n\nÀ sa libération, il n'avait pas de rancœur. Seulement de la sagesse, de la compassion et une vision claire. Il est devenu président et a changé l'histoire de son pays.\n\nSon parcours nous enseigne que la résilience n'est pas l'absence de souffrance, mais le choix de transformer cette souffrance en lumière. Tu portes cette lumière en toi. Laisse-la briller."
            },
            {
                'celebrity': 'Walt Disney',
                'story': "Walt Disney a été licencié d'un journal parce qu'on lui disait qu'il manquait d'imagination et de bonnes idées.\n\nSa première entreprise a fait faillite. Il a été rejeté plus de 300 fois avant de trouver un financement pour Disneyland.\n\nMais il continuait de dessiner, de rêver, de créer. Il croyait en sa vision même quand personne d'autre n'y croyait.\n\nAujourd'hui, son nom évoque la magie, l'enfance et les rêves qui se réalisent. Il nous rappelle que les échecs ne sont que des détours vers le succès. Continue de croire en tes rêves. Ils méritent de prendre vie."
            },
            {
                'celebrity': 'Lady Gaga',
                'story': "Lady Gaga a été harcelée à l'école pour sa différence. On se moquait d'elle, on la rejetait. Elle se sentait seule et incomprise.\n\nMais elle a transformé sa différence en force. Elle a embrassé qui elle était vraiment, sans s'excuser.\n\nElle a créé sa propre voie, son propre style, sa propre musique. Aujourd'hui, elle inspire des millions de personnes à être authentiques.\n\nSon message est clair : ta différence n'est pas une faiblesse, c'est ta plus grande force. Ose être toi-même. Le monde a besoin de ta lumière unique."
            }
        ]
        
        import random
        selected_story = random.choice(simulated_stories)
        
        return {
            'story': selected_story['story'],
            'celebrity': selected_story['celebrity'],
            'simulated': True
        }
