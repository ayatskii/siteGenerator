# Russian Localization Setup

## Quick Start

### 1. Install Dependencies

```bash
cd frontend
npm install react-i18next i18next i18next-browser-languagedetector --legacy-peer-deps
```

### 2. Import i18n in main.jsx (or index.js)

```javascript
import "./i18n"; // Before importing App
import App from "./App";
```

### 3. Wrap App with I18nextProvider (if needed)

In `App.jsx`:

```javascript
import { I18nextProvider } from "react-i18next";
import i18n from "./i18n";

function App() {
  return (
    <I18nextProvider i18n={i18n}>{/* Your app content */}</I18nextProvider>
  );
}
```

### 4. Use translations in components

```javascript
import { useTranslation } from "react-i18next";

function MyComponent() {
  const { t } = useTranslation();

  return (
    <div>
      <h1>{t("nav.dashboard")}</h1>
      <button>{t("common.save")}</button>
    </div>
  );
}
```

### 5. Add Language Switcher

```javascript
import LanguageSwitcher from "./components/LanguageSwitcher";

//  In your header/navbar
<LanguageSwitcher />;
```

## Translation Files

- `src/locales/en/translation.json` - English translations
- `src/locales/ru/translation.json` - Russian translations

## Available Translation Keys

### Navigation

- `nav.dashboard`, `nav.sites`, `nav.pages`, `nav.media`, etc.

### Common

- `common.save`, `common.cancel`, `common.delete`, `common.edit`, etc.

### Auth

- `auth.login`, `auth.register`, `auth.email`, `auth.password`, etc.

### Sites

- `sites.title`, `sites.createNew`, `sites.domain`, etc.

### CreateSite

- `createSite.title`, `createSite.step1`, `createSite.brandName`, etc.

### Media

- `media.title`, `media.selectImage`, `media.noImages`, etc.

### Settings

- `settings.title`, `settings.general`, `settings.language`, etc.

### Prompts

- `prompts.title`, `prompts.textPrompts`, `prompts.createNew`, etc.

## Adding More Translations

1. Add key to both `en/translation.json` and `ru/translation.json`
2. Use `t('your.new.key')` in your component
3. Language will auto-switch based on user preference

## Backend (Django) Setup

### 1. Update settings.py

```python
LANGUAGE_CODE = 'en-us'
LANGUAGES = [
    ('en', 'English'),
    ('ru', 'Russian'),
]
LOCALE_PATHS = [BASE_DIR / 'locale']
USE_I18N = True
USE_L10N = True
```

### 2. Create locale files

```bash
python manage.py makemessages -l ru
```

### 3. Translate strings in locale/ru/LC_MESSAGES/django.po

### 4. Compile messages

```bash
python manage.py compilemessages
```

## Testing

1. Change language in UI using LanguageSwitcher
2. Verify all UI elements update
3. Check localStorage for saved preference
4. Reload page - language should persist
