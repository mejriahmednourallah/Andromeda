"""
Test de la clé API Groq
"""
import os
from dotenv import load_dotenv
from groq import Groq

# Charger les variables d'environnement
load_dotenv()

# Récupérer la clé
api_key = os.getenv('GROQ_API_KEY')

print("=" * 50)
print("TEST DE LA CLÉ API GROQ")
print("=" * 50)

if not api_key:
    print("❌ ERREUR: Clé API Groq non trouvée dans .env")
    print("\nVérifiez que votre fichier .env contient:")
    print("GROQ_API_KEY=gsk_votre_cle_ici")
    exit(1)

if api_key.startswith('gsk-your') or api_key == 'gsk-your-groq-api-key-here':
    print("❌ ERREUR: Vous utilisez la clé d'exemple")
    print("\nVous devez:")
    print("1. Aller sur https://console.groq.com")
    print("2. Créer une nouvelle clé API")
    print("3. La mettre dans votre fichier .env")
    exit(1)

print(f"✅ Clé API trouvée: {api_key[:10]}...{api_key[-5:]}")
print("\nTest de connexion à Groq...")

try:
    client = Groq(api_key=api_key)
    
    # Test simple
    response = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": "Dis juste 'Bonjour' en français"
            }
        ],
        model="llama-3.3-70b-versatile",
        max_tokens=50,
    )
    
    result = response.choices[0].message.content
    print(f"✅ Connexion réussie!")
    print(f"✅ Réponse de l'IA: {result}")
    print("\n" + "=" * 50)
    print("✅ TOUT FONCTIONNE!")
    print("=" * 50)
    print("\nVotre clé API Groq est valide et fonctionnelle.")
    print("Le résumé automatique devrait maintenant fonctionner.")
    
except Exception as e:
    print(f"❌ ERREUR lors de la connexion:")
    print(f"   {str(e)}")
    print("\nPossibles causes:")
    print("1. Clé API invalide ou révoquée")
    print("2. Pas de connexion internet")
    print("3. Quota Groq dépassé")
    print("\nSolution:")
    print("1. Vérifiez votre clé sur https://console.groq.com")
    print("2. Créez une nouvelle clé si nécessaire")
    print("3. Mettez-la dans votre fichier .env")
