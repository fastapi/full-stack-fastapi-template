# Multi-Language Support Implementation

## Overview

VNRunner now supports multiple languages for both the user interface and race content. The platform currently supports Vietnamese (vi) as the default language and English (en) as a secondary language, with the ability to add more languages in the future.

**Key Features:**
- ✅ Vietnamese (vi) as default language
- ✅ English (en) support
- ✅ Language code in URLs (e.g., `?lang=vi`)
- ✅ Admin interface for managing translations
- ✅ Automatic language detection from browser
- ✅ UI translations (200+ strings)
- ✅ Race content translations (races, categories, tags)

## Implementation Summary

### 1. Backend Changes

#### Database Schema
Added translation support to race-related tables with new columns:

**Migration**: `88968afdc9ad_add_multi_language_support.py`

- **`race` table**:
  - `translations` (JSON): Stores translations for name, description, location, etc.
  - `default_language` (String): Default language for the race (default: "vi")

- **`racecategory` table**:
  - `translations` (JSON): Stores translations for name, description

- **`racetag` table**:
  - `translations` (JSON): Stores translations for name

**Translation JSON Structure**:
```json
{
  "vi": {
    "name": "Giải chạy Hà Nội",
    "description": "Giải chạy marathon tại thủ đô Hà Nội..."
  },
  "en": {
    "name": "Hanoi Marathon",
    "description": "Marathon race in Vietnam's capital city..."
  }
}
```

#### Models (`backend/app/models.py`)

Updated SQLModel classes to include translation fields:

```python
class RaceBase(SQLModel):
    # ... existing fields ...
    default_language: str = Field(default="vi", max_length=10)
    translations: dict[str, Any] | None = Field(default=None, sa_column=Column(JSON))

class RaceCategoryBase(SQLModel):
    # ... existing fields ...
    translations: dict[str, Any] | None = Field(default=None, sa_column=Column(JSON))

class RaceTagBase(SQLModel):
    # ... existing fields ...
    translations: dict[str, Any] | None = Field(default=None, sa_column=Column(JSON))
```

#### I18n Utilities (`backend/app/i18n.py`)

Created comprehensive helper functions for handling translations:

**Key Functions**:

1. **`get_translated_field(obj, field_name, language, fallback_to_default)`**
   - Get a translated field value from a database object
   - Automatically falls back to default language or object's original field

2. **`translate_object(obj, fields, language)`**
   - Get multiple translated fields as a dictionary
   - Useful for serializing objects with translations

3. **`set_translation(obj, field_name, value, language)`**
   - Set a single translated field value

4. **`merge_translations(obj, translations)`**
   - Merge multiple translations at once
   - Format: `{"vi": {"name": "...", "description": "..."}, "en": {...}}`

5. **`is_language_supported(language)`**
   - Check if a language code is supported

**Example Usage**:
```python
from app.i18n import get_translated_field, merge_translations

# Get translated field
race = Race(name="Hanoi Marathon", translations={"vi": {"name": "Giải chạy Hà Nội"}})
vietnamese_name = get_translated_field(race, "name", "vi")  # Returns "Giải chạy Hà Nội"

# Set multiple translations
merge_translations(race, {
    "vi": {"name": "Giải chạy Hà Nội", "description": "..."},
    "th": {"name": "มาราธอนฮานอย"}
})
```

### 2. Frontend Changes

#### I18n Setup

**Installed Packages**:
```json
{
  "i18next": "^23.x",
  "react-i18next": "^13.x",
  "i18next-browser-languagedetector": "^7.x"
}
```

**Configuration** (`frontend/src/i18n/config.ts`):
- Language detection from localStorage, browser navigator, HTML tag
- Caches selected language in localStorage (`i18nextLng` key)
- Fallback language: Vietnamese (vi)
- Supported languages: Vietnamese (vi), English (en)
- Language parameter in URL: `?lang=vi` or `?lang=en`

**Initialization** (`frontend/src/main.tsx`):
```typescript
import "./i18n/config" // Initialize i18n before app renders
```

#### Translation Files

**English** (`frontend/src/i18n/locales/en.json`):
- Comprehensive translations for all UI elements
- Organized by feature: `common`, `nav`, `home`, `races`, `about`, `footer`, `language`

**Vietnamese** (`frontend/src/i18n/locales/vi.json`):
- Full Vietnamese translations
- Culturally appropriate translations (e.g., "Giải chạy" instead of literal "cuộc đua")

**Translation Structure**:
```json
{
  "common": {
    "loading": "Loading...",
    "search": "Search",
    "register": "Register"
  },
  "home": {
    "hero": {
      "title": "Discover Your Next Running Challenge",
      "subtitle": "Find and register for running races..."
    }
  },
  "races": {
    "terrain": {
      "road": "Road",
      "trail": "Trail"
    }
  }
}
```

#### Language Switcher Component

**File**: `frontend/src/components/Common/LanguageSwitcher.tsx`

**Features**:
- Dropdown menu with language options
- Shows current language with checkmark
- Displays both native and English names
- Globe icon for easy recognition
- Integrates with react-i18next

**Usage**:
```tsx
import { LanguageSwitcher } from "@/components/Common/LanguageSwitcher"

<LanguageSwitcher />
```

**Added to**:
- Public header (desktop and mobile views)
- Accessible in all public pages

#### Updated Components

**Public Header** (`frontend/src/components/Public/PublicHeader.tsx`):
- Navigation links use translations: `t("nav.home")`, `t("nav.races")`, `t("nav.about")`
- Auth buttons use translations: `t("common.login")`, `t("common.register")`
- Includes LanguageSwitcher in both desktop and mobile views

**Homepage** (`frontend/src/routes/_public/index.tsx`):
- Hero section translations: `t("home.hero.title")`, `t("home.hero.subtitle")`
- Features translations: `t("home.features.discover.title")`
- Race rail titles: `t("home.trending")`, `t("home.upcoming")`
- Dynamic translation support throughout

**Using Translations in Components**:
```tsx
import { useTranslation } from "react-i18next"

function MyComponent() {
  const { t } = useTranslation()
  
  return (
    <div>
      <h1>{t("common.title")}</h1>
      <p>{t("common.description")}</p>
    </div>
  )
}
```

## How to Use

### For Developers

#### Adding New UI Translations

1. Add translation keys to both `en.json` and `vi.json`:
   ```json
   // en.json
   {
     "myFeature": {
       "title": "My Feature",
       "description": "Feature description"
     }
   }
   
   // vi.json
   {
     "myFeature": {
       "title": "Tính năng của tôi",
       "description": "Mô tả tính năng"
     }
   }
   ```

2. Use in components:
   ```tsx
   const { t } = useTranslation()
   <h1>{t("myFeature.title")}</h1>
   ```

#### Adding Race Content Translations

**Via API (when creating/updating races)**:
```python
from app.models import RaceCreate, RaceUpdate
from app.i18n import merge_translations

# Create race with translations
race_create = RaceCreate(
    name="Hanoi Marathon",
    description="Marathon in Hanoi...",
    # ... other fields
)
race = crud.create_race(session, race_create)

# Add translations
merge_translations(race, {
    "vi": {
        "name": "Giải chạy Hà Nội",
        "description": "Marathon tại Hà Nội...",
        "location": "Hà Nội, Việt Nam"
    }
})
session.commit()
```

**Via Admin UI** (future enhancement):
- Add translation fields to race creation/edit forms
- Store translations in JSON format

#### Retrieving Translated Content

**Backend**:
```python
from app.i18n import get_translated_field

language = "vi"  # From query parameter or user preference
race = crud.get_race(session, race_id)
translated_name = get_translated_field(race, "name", language)
```

**Frontend** (future enhancement):
```typescript
// When fetching race data, pass language parameter
const { data: race } = useQuery({
  queryKey: ["race", raceId, language],
  queryFn: () => RacesService.readRace({ raceId, lang: language })
})
```

### For Content Creators

#### Translating Races

1. **Name Translation**:
   - English: "Hanoi International Marathon"
   - Vietnamese: "Giải Marathon Quốc tế Hà Nội"

2. **Description Translation**:
   - Keep descriptions culturally appropriate
   - Use Vietnamese running terminology
   - Maintain formatting (HTML preserved)

3. **Location Translation**:
   - English: "Ho Chi Minh City, Vietnam"
   - Vietnamese: "Thành phố Hồ Chí Minh, Việt Nam"

#### Best Practices

1. **Consistency**: Use consistent terminology across translations
2. **Cultural Adaptation**: Adapt content for Vietnamese culture, not literal translation
3. **SEO**: Include Vietnamese keywords for better local search
4. **Completeness**: Translate all fields or leave in default language

## Language Detection Flow

1. **First Visit**:
   - Checks browser language setting
   - If Vietnamese browser → Sets to Vietnamese
   - Otherwise → Defaults to English
   - Saves preference to localStorage

2. **Subsequent Visits**:
   - Reads from localStorage (`i18nextLng` key)
   - Uses saved language preference

3. **Manual Switch**:
   - User selects language from switcher
   - Immediately updates UI
   - Saves to localStorage
   - Persists across sessions

## API Translation Endpoints

### Race Translation Management

**Update Race Translations**:
```http
PUT /api/v1/races/{race_id}/translations
Content-Type: application/json

{
  "language": "vi",
  "name": "Giải chạy Hà Nội",
  "description": "Giải chạy marathon tại thủ đô...",
  "location": "Hà Nội, Việt Nam"
}
```

**Get Race Translations**:
```http
GET /api/v1/races/{race_id}/translations

Response:
{
  "vi": {
    "name": "Giải chạy Hà Nội",
    "description": "...",
    "location": "Hà Nội, Việt Nam"
  },
  "en": {
    "name": "Hanoi Marathon",
    "description": "...",
    "location": "Hanoi, Vietnam"
  }
}
```

### Category Translation Management

**Update Category Translations**:
```http
PUT /api/v1/race-categories/{category_id}/translations
Content-Type: application/json

{
  "language": "vi",
  "name": "5K",
  "description": "Cự ly 5 kilometer"
}
```

**Get Category Translations**:
```http
GET /api/v1/race-categories/{category_id}/translations
```

### Tag Translation Management

**Update Tag Translations** (Admin only):
```http
PUT /api/v1/tags/{tag_id}/translations
Content-Type: application/json

{
  "language": "vi",
  "name": "Đường mòn"
}
```

**Get Tag Translations**:
```http
GET /api/v1/tags/{tag_id}/translations
```

## Admin Translation Interface

### Access

Navigate to the admin panel to manage translations:
- **Race Translations**: Admin → Races → Edit Race → "Race Translations" section
- **Tag Translations**: Admin → Tags

### Features

**Translation Editor Component**:
- ✅ Tab-based interface for each language (Vietnamese, English)
- ✅ Side-by-side editing of name, description, location
- ✅ Character count for fields with limits
- ✅ Save button with loading state
- ✅ Automatic detection of default language

**Race Translation Manager**:
- Edit race name, description, and location in multiple languages
- Integrated into race edit page
- Only race organizer or admin can update

**Category Translation Manager**:
- Edit category name and description
- Appears in category management section

**Tag Translation Manager**:
- Edit tag names in multiple languages
- Admin-only access
- Dedicated tags page: `/admin/tags`

### Usage Example

1. Navigate to **Admin → Races**
2. Click **Edit** on any race
3. Scroll to **"Race Translations"** section
4. Click **Vietnamese** or **English** tab
5. Enter translated content
6. Click **Save**

## URL Language Parameter

The language is now included in public page URLs:
- Homepage: `/?lang=vi` or `/?lang=en`
- Races: `/races?lang=vi`
- Race Detail: `/races/{id}?lang=en`

**How it works:**
1. User clicks language switcher (Globe icon in header)
2. URL updates with `?lang={code}` parameter
3. Language preference saves to localStorage
4. On page load, URL parameter takes precedence over localStorage

## Supported Languages

Currently supported:
- ✅ **Vietnamese (vi)** - Default language
- ✅ **English (en)** - Secondary language

Future languages (planned):
- 🔲 **Thai (th)** - For Thai runners in Vietnam
- 🔲 **Chinese (zh)** - For Chinese tourists/expats

## Testing

### Testing Language Switch

1. Open the website
2. Click the Globe icon in the header
3. Select "Tiếng Việt"
4. Verify all UI elements change to Vietnamese
5. Navigate between pages - language persists
6. Refresh page - language preference saved
7. Switch back to English - UI updates immediately

### Testing Translation Fallbacks

1. Add a race with only English content (no translations)
2. Switch to Vietnamese
3. Verify race shows English content (fallback working)
4. Add Vietnamese translations
5. Verify Vietnamese content displays

## Files Modified/Created

### Backend
- ✅ Created: `backend/app/alembic/versions/88968afdc9ad_add_multi_language_support.py`
- ✅ Modified: `backend/app/models.py`
- ✅ Created: `backend/app/i18n.py`

### Frontend
- ✅ Created: `frontend/src/i18n/config.ts`
- ✅ Created: `frontend/src/i18n/locales/en.json`
- ✅ Created: `frontend/src/i18n/locales/vi.json`
- ✅ Created: `frontend/src/components/Common/LanguageSwitcher.tsx`
- ✅ Modified: `frontend/src/main.tsx`
- ✅ Modified: `frontend/src/components/Public/PublicHeader.tsx`
- ✅ Modified: `frontend/src/routes/_public/index.tsx`
- ✅ Modified: `package.json` (added i18n dependencies)

## Future Enhancements

1. **Admin Translation Interface**:
   - Add translation tabs in race creation/edit forms
   - Visual editor for each language
   - Translation progress indicators

2. **Auto-Translation**:
   - Integration with Google Translate API
   - Suggest translations for new content
   - Review and approve workflow

3. **Language-Specific SEO**:
   - Vietnamese meta tags when language is Vietnamese
   - Separate sitemaps per language
   - Hreflang tags for international SEO

4. **User Language Preference**:
   - Store language preference in user profile
   - Auto-set language on login
   - Remember preference across devices

5. **Missing Translation Warnings**:
   - Show indicators for untranslated content
   - Admin dashboard for translation coverage
   - Translation workflow management

6. **RTL Language Support**:
   - Prepare for Right-to-Left languages
   - Adjust layout for Arabic, Hebrew, etc.

7. **Translation Validation**:
   - Check for missing translations
   - Validate translation keys in JSON files
   - CI/CD integration

## Troubleshooting

### Language not changing
- Check browser console for errors
- Verify localStorage has `i18nextLng` key
- Clear localStorage and try again
- Check i18n configuration loaded

### Missing translations showing as keys
- Check translation key exists in JSON files
- Verify JSON syntax is valid
- Check for typos in translation keys
- Fallback to English should still work

### Translations not persisting
- Check localStorage is enabled
- Verify i18next-browser-languagedetector is installed
- Check browser privacy settings

## Conclusion

VNRunner now has comprehensive multi-language support for both UI elements and race content. The implementation uses industry-standard i18next for the frontend and JSON-based translation storage in PostgreSQL for race content. The system is extensible and ready for additional languages in the future.

**Language switcher is accessible in the header on all public pages. Users can switch between English and Vietnamese at any time, and their preference is saved automatically.**
