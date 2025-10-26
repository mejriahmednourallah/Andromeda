"""
Script pour régénérer les résumés des entrées existantes
"""
import os
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'andromeda.settings')
django.setup()

from core.models import EntreeJournal
from core.services.ai_service import get_ai_service

print("=" * 60)
print("RÉGÉNÉRATION DES RÉSUMÉS AUTOMATIQUES")
print("=" * 60)

# Récupérer toutes les entrées sans résumé
entrees = EntreeJournal.objects.filter(auto_summary='')
total = entrees.count()

if total == 0:
    print("\n✅ Toutes les entrées ont déjà un résumé!")
    exit(0)

print(f"\n📝 {total} entrée(s) sans résumé trouvée(s)")
print("\nGénération des résumés...")

ai_service = get_ai_service()
success = 0
errors = 0

for i, entree in enumerate(entrees, 1):
    print(f"\n[{i}/{total}] {entree.titre[:50]}...")
    
    try:
        # Générer le résumé
        resume = ai_service.generer_resume(entree.contenu_texte, longueur="court")
        
        if resume and resume != "Résumé non disponible":
            entree.auto_summary = resume
            entree.save()
            print(f"  ✅ Résumé généré: {resume[:80]}...")
            success += 1
        else:
            print(f"  ❌ Échec de la génération")
            errors += 1
            
    except Exception as e:
        print(f"  ❌ Erreur: {e}")
        errors += 1

print("\n" + "=" * 60)
print("RÉSUMÉ")
print("=" * 60)
print(f"✅ Succès: {success}")
print(f"❌ Erreurs: {errors}")
print(f"📊 Total: {total}")
print("\nTerminé!")
