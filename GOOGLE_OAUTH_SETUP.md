# Configuration de l'authentification Google OAuth

## Étapes pour configurer Google OAuth

### 1. Créer un projet Google Cloud

1. Allez sur [Google Cloud Console](https://console.cloud.google.com/)
2. Créez un nouveau projet ou sélectionnez un projet existant
3. Activez l'API Google+ (ou Google Identity)

### 2. Créer des identifiants OAuth 2.0

1. Dans le menu, allez à **APIs & Services** > **Credentials**
2. Cliquez sur **Create Credentials** > **OAuth client ID**
3. Choisissez **Web application**
4. Configurez les URIs autorisés :
   - **Authorized JavaScript origins** : `http://127.0.0.1:8000`
   - **Authorized redirect URIs** : `http://127.0.0.1:8000/accounts/google/login/callback/`
5. Notez le **Client ID** et le **Client Secret**

### 3. Configurer les variables d'environnement

Créez un fichier `.env` à la racine du projet :

```env
GOOGLE_CLIENT_ID=votre_client_id_ici
GOOGLE_CLIENT_SECRET=votre_client_secret_ici
```

### 4. Installer les dépendances et migrer

```bash
pip install -r requirements.txt
python manage.py migrate
```

### 5. Configurer le site Django

Lancez le serveur et allez dans l'admin Django :

```bash
python manage.py runserver
```

1. Allez sur `http://127.0.0.1:8000/admin/`
2. Connectez-vous avec un superuser (créez-en un si nécessaire : `python manage.py createsuperuser`)
3. Allez dans **Sites** et modifiez le site par défaut :
   - Domain name: `127.0.0.1:8000`
   - Display name: `Andromeda`

4. Allez dans **Social applications** et ajoutez une nouvelle application :
   - Provider: **Google**
   - Name: `Google OAuth`
   - Client id: Votre Client ID Google
   - Secret key: Votre Client Secret Google
   - Sites: Sélectionnez votre site (127.0.0.1:8000)

### 6. Tester l'authentification

1. Allez sur `http://127.0.0.1:8000/accounts/signup/`
2. Cliquez sur "Continue with Google"
3. Authentifiez-vous avec votre compte Google
4. Vous devriez être redirigé vers la page d'accueil

## Notes importantes

- Pour la production, ajoutez votre domaine de production dans les URIs autorisés de Google Cloud Console
- Gardez vos clés secrètes en sécurité et ne les commitez jamais dans Git
- Le fichier `.env` est déjà dans `.gitignore`

## Dépannage

### Erreur "redirect_uri_mismatch"
Vérifiez que l'URI de redirection dans Google Cloud Console correspond exactement à :
`http://127.0.0.1:8000/accounts/google/login/callback/`

### L'application sociale n'apparaît pas
Assurez-vous d'avoir bien configuré le site dans l'admin Django et d'avoir associé l'application Google à ce site.
