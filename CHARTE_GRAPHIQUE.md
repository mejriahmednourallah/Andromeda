# 🎨 Charte Graphique - Andromeda Journal

## 🌈 Palette de Couleurs

### Couleurs Principales

#### Violet Primaire (Brand)
- **Primary**: `#667eea` - Boutons, liens, accents
- **Primary Dark**: `#764ba2` - Hover states
- **Primary Light**: `#a78bfa` - Backgrounds légers

#### Rose/Magenta (Accent)
- **Accent Pink**: `#f093fb` - Highlights, badges
- **Accent Red**: `#f5576c` - Alertes importantes
- **Accent Coral**: `#ff6b9d` - Éléments interactifs

#### Cyan/Bleu (Secondaire)
- **Cyan**: `#4facfe` - Informations, données
- **Sky Blue**: `#00f2fe` - Backgrounds clairs
- **Ocean**: `#0ea5e9` - Links secondaires

#### Vert (Succès)
- **Success**: `#10b981` - Confirmations, validations
- **Success Light**: `#34d399` - Backgrounds de succès
- **Emerald**: `#059669` - États actifs

### Couleurs Neutres

#### Gris (Texte & Backgrounds)
- **Slate 900**: `#0f172a` - Texte principal
- **Slate 800**: `#1e293b` - Titres
- **Slate 700**: `#334155` - Texte secondaire
- **Slate 600**: `#475569` - Texte désactivé
- **Slate 500**: `#64748b` - Labels
- **Slate 400**: `#94a3b8` - Placeholders
- **Slate 300**: `#cbd5e1` - Bordures
- **Slate 200**: `#e2e8f0` - Dividers
- **Slate 100**: `#f1f5f9` - Backgrounds
- **Slate 50**: `#f8fafc` - Surfaces

#### Blanc & Noir
- **White**: `#ffffff` - Surfaces principales
- **Black**: `#000000` - Overlays (avec opacité)

---

## 🎭 Dégradés

### Dégradés Principaux

```css
/* Violet Dream */
background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);

/* Sunset */
background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);

/* Ocean Breeze */
background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);

/* Aurora */
background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);

/* Rainbow */
background: linear-gradient(135deg, #667eea 0%, #764ba2 30%, #f093fb 70%, #4facfe 100%);
```

### Dégradés de Fond

```css
/* Subtle Background */
background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);

/* Glass Effect */
background: linear-gradient(135deg, rgba(255,255,255,0.9) 0%, rgba(248,250,252,0.8) 100%);
```

---

## 📝 Typographie

### Famille de Polices

```css
/* Police Principale */
font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;

/* Police Monospace (Code) */
font-family: 'Fira Code', 'Courier New', monospace;
```

### Échelle Typographique

#### Titres
- **H1**: `2.5rem` (40px) - `font-weight: 900` - `letter-spacing: -0.5px`
- **H2**: `2rem` (32px) - `font-weight: 800` - `letter-spacing: -0.3px`
- **H3**: `1.75rem` (28px) - `font-weight: 700` - `letter-spacing: -0.2px`
- **H4**: `1.5rem` (24px) - `font-weight: 700`
- **H5**: `1.25rem` (20px) - `font-weight: 600`
- **H6**: `1.1rem` (18px) - `font-weight: 600`

#### Corps de Texte
- **Large**: `1.2rem` (19px) - `line-height: 1.8`
- **Normal**: `1rem` (16px) - `line-height: 1.6`
- **Small**: `0.9rem` (14px) - `line-height: 1.5`
- **Tiny**: `0.8rem` (13px) - `line-height: 1.4`

---

## 🎯 Composants UI

### Boutons

#### Bouton Primaire
```css
padding: 1.3rem 3rem;
border-radius: 60px;
font-size: 1.2rem;
font-weight: 800;
background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
color: white;
box-shadow: 0 12px 30px rgba(102,126,234,0.4);
transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
```

#### Bouton Secondaire
```css
padding: 1.3rem 3rem;
border-radius: 60px;
font-size: 1.2rem;
font-weight: 800;
background: linear-gradient(135deg, #f1f5f9 0%, #e2e8f0 100%);
color: #64748b;
box-shadow: 0 4px 12px rgba(0,0,0,0.08);
```

### Cartes (Cards)

#### Carte Standard
```css
background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
border-radius: 28px;
padding: 3rem;
box-shadow: 0 15px 40px rgba(0,0,0,0.08), 0 4px 12px rgba(0,0,0,0.04);
border: 2px solid rgba(102,126,234,0.1);
transition: all 0.4s ease;
```

#### Carte avec Glassmorphism
```css
background: rgba(255, 255, 255, 0.7);
backdrop-filter: blur(20px);
border-radius: 32px;
padding: 3rem;
box-shadow: 0 20px 60px rgba(0,0,0,0.1);
border: 2px solid rgba(255,255,255,0.5);
```

### Champs de Formulaire

```css
padding: 1.2rem 1.5rem;
border: 2px solid #e2e8f0;
border-radius: 20px;
font-size: 1.1rem;
background: white;
box-shadow: 0 2px 8px rgba(0,0,0,0.02);
transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);

/* Focus State */
border-color: #667eea;
box-shadow: 0 0 0 5px rgba(102,126,234,0.12), 0 10px 20px rgba(102,126,234,0.18);
transform: translateY(-3px);
```

---

## ✨ Effets & Animations

### Ombres (Shadows)

```css
/* Petite */
box-shadow: 0 2px 8px rgba(0,0,0,0.04);

/* Moyenne */
box-shadow: 0 10px 30px rgba(0,0,0,0.08), 0 4px 12px rgba(0,0,0,0.04);

/* Grande */
box-shadow: 0 20px 60px rgba(0,0,0,0.12), 0 8px 20px rgba(0,0,0,0.06);

/* Colorée (Violet) */
box-shadow: 0 15px 40px rgba(102,126,234,0.3);

/* Colorée (Rose) */
box-shadow: 0 20px 50px rgba(245,87,108,0.3);
```

### Animations

```css
/* Fade In Up */
@keyframes fadeInUp {
    from {
        opacity: 0;
        transform: translateY(30px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

/* Float */
@keyframes float {
    0%, 100% { transform: translateY(0px); }
    50% { transform: translateY(-10px); }
}

/* Gradient Shift */
@keyframes gradientShift {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}

/* Rotate Glow */
@keyframes rotateGlow {
    from { transform: rotate(0deg); }
    to { transform: rotate(360deg); }
}
```

### Transitions

```css
/* Standard */
transition: all 0.3s ease;

/* Smooth */
transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);

/* Bounce */
transition: all 0.5s cubic-bezier(0.68, -0.55, 0.265, 1.55);
```

---

## 🎪 Espacement

### Système d'Espacement (basé sur 0.25rem = 4px)

- **xs**: `0.5rem` (8px)
- **sm**: `0.75rem` (12px)
- **md**: `1rem` (16px)
- **lg**: `1.5rem` (24px)
- **xl**: `2rem` (32px)
- **2xl**: `2.5rem` (40px)
- **3xl**: `3rem` (48px)
- **4xl**: `4rem` (64px)

### Marges & Paddings Standards

```css
/* Sections */
margin-bottom: 3rem;
padding: 3rem;

/* Cartes */
padding: 2.5rem 2rem;
gap: 2rem;

/* Formulaires */
margin-bottom: 2rem;
padding: 1.2rem 1.5rem;
```

---

## 🎨 Bordures & Coins Arrondis

### Radius

- **Small**: `12px` - Petits éléments
- **Medium**: `16px` - Éléments standards
- **Large**: `20px` - Champs de formulaire
- **XLarge**: `24px` - Cartes
- **2XLarge**: `28px` - Grandes cartes
- **3XLarge**: `32px` - Sections importantes
- **Pill**: `60px` - Boutons arrondis
- **Circle**: `50%` - Éléments circulaires

### Bordures

```css
/* Standard */
border: 2px solid #e2e8f0;

/* Accent */
border: 2px solid rgba(102,126,234,0.2);

/* Colorée */
border: 3px solid rgba(255,255,255,0.3);
```

---

## 🌟 Icônes & Emojis

### Emojis Recommandés

- **Journal**: ✍️ 📝 📖 📔 📓
- **Statistiques**: 📊 📈 📉 🎯 💯
- **Émotions**: 😊 😢 😡 😌 😴 🥳 😰
- **Actions**: ✓ ✗ ➕ ➖ 🔍 💾 📥 📤
- **Catégories**: 🏷️ 🎨 🎭 🎪 🎯 🏆
- **Temps**: ⏰ 📅 🕐 ⏳ 🔥
- **Succès**: ⭐ 🌟 ✨ 💫 🎉

---

## 📐 Grilles & Layouts

### Grid System

```css
/* 2 Colonnes */
display: grid;
grid-template-columns: 1fr 1fr;
gap: 1.5rem;

/* 3 Colonnes */
display: grid;
grid-template-columns: repeat(3, 1fr);
gap: 2rem;

/* Auto-fit (Responsive) */
display: grid;
grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
gap: 2rem;
```

### Flexbox

```css
/* Centrage */
display: flex;
justify-content: center;
align-items: center;

/* Espace entre */
display: flex;
justify-content: space-between;
align-items: center;

/* Colonne */
display: flex;
flex-direction: column;
gap: 1rem;
```

---

## 🎬 États Interactifs

### Hover

```css
transform: translateY(-5px) scale(1.05);
box-shadow: 0 20px 40px rgba(102,126,234,0.5);
```

### Active

```css
transform: scale(0.98);
```

### Focus

```css
outline: none;
border-color: #667eea;
box-shadow: 0 0 0 5px rgba(102,126,234,0.12);
```

### Disabled

```css
opacity: 0.5;
cursor: not-allowed;
filter: grayscale(50%);
```

---

## 🎯 Principes de Design

### 1. Hiérarchie Visuelle
- Utiliser la taille, le poids et la couleur pour créer une hiérarchie claire
- Les éléments importants doivent être plus grands et plus visibles

### 2. Espacement Généreux
- Laisser respirer les éléments avec des marges généreuses
- Éviter la surcharge visuelle

### 3. Cohérence
- Utiliser les mêmes styles pour les mêmes types d'éléments
- Maintenir un système de design cohérent

### 4. Feedback Visuel
- Toujours donner un retour visuel aux actions de l'utilisateur
- Animations et transitions pour améliorer l'UX

### 5. Accessibilité
- Contraste suffisant pour la lisibilité
- Tailles de texte adaptées
- Zones cliquables suffisamment grandes (minimum 44x44px)

---

## 🚀 Utilisation

Cette charte graphique doit être appliquée à tous les composants du projet Andromeda pour maintenir une cohérence visuelle et offrir une expérience utilisateur optimale.

**Dernière mise à jour**: Octobre 2025
