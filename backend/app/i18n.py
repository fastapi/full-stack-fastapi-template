"""
Internationalization (i18n) utilities for multi-language support.
"""
from typing import Any


SUPPORTED_LANGUAGES = ["vi", "en"]
DEFAULT_LANGUAGE = "vi"


def get_translated_field(
    obj: Any,
    field_name: str,
    language: str = DEFAULT_LANGUAGE,
    fallback_to_default: bool = True,
) -> str | None:
    """
    Get a translated field value from an object.
    
    Args:
        obj: The database object (Race, RaceCategory, RaceTag, etc.)
        field_name: The field to translate (e.g., "name", "description")
        language: The target language code (e.g., "en", "vi")
        fallback_to_default: If True, fallback to default field value if translation not found
    
    Returns:
        The translated value or None
    
    Example:
        race = Race(name="Hanoi Marathon", translations={"vi": {"name": "Giải chạy Hà Nội"}})
        get_translated_field(race, "name", "vi") # Returns "Giải chạy Hà Nội"
        get_translated_field(race, "name", "en") # Returns "Hanoi Marathon" (default)
    """
    # Normalize language code
    language = language.lower() if language else DEFAULT_LANGUAGE
    
    # Check if translations exist
    if hasattr(obj, "translations") and obj.translations:
        # Try to get translation for requested language
        if language in obj.translations:
            lang_translations = obj.translations[language]
            if isinstance(lang_translations, dict) and field_name in lang_translations:
                value = lang_translations[field_name]
                if value:  # Return if value is not None or empty
                    return value
        
        # Fallback to default language in translations
        if fallback_to_default and hasattr(obj, "default_language"):
            default_lang = obj.default_language or DEFAULT_LANGUAGE
            if default_lang in obj.translations:
                lang_translations = obj.translations[default_lang]
                if isinstance(lang_translations, dict) and field_name in lang_translations:
                    value = lang_translations[field_name]
                    if value:
                        return value
    
    # Fallback to object's default field value
    if fallback_to_default and hasattr(obj, field_name):
        return getattr(obj, field_name)
    
    return None


def translate_object(
    obj: Any,
    fields: list[str],
    language: str = DEFAULT_LANGUAGE,
) -> dict[str, Any]:
    """
    Get translated fields from an object as a dictionary.
    
    Args:
        obj: The database object
        fields: List of field names to translate
        language: Target language code
    
    Returns:
        Dictionary with translated field values
    
    Example:
        race = Race(name="Hanoi Marathon", description="...", translations={...})
        translate_object(race, ["name", "description"], "vi")
        # Returns {"name": "Giải chạy Hà Nội", "description": "..."}
    """
    result = {}
    for field in fields:
        value = get_translated_field(obj, field, language)
        if value is not None:
            result[field] = value
    return result


def set_translation(
    obj: Any,
    field_name: str,
    value: str,
    language: str,
) -> None:
    """
    Set a translated field value on an object.
    
    Args:
        obj: The database object to modify
        field_name: The field to translate
        value: The translated value
        language: The language code
    
    Example:
        race = Race(name="Hanoi Marathon")
        set_translation(race, "name", "Giải chạy Hà Nội", "vi")
    """
    # Normalize language code
    language = language.lower()
    
    # Initialize translations if needed - create a NEW dict to trigger SQLAlchemy change detection
    if not hasattr(obj, "translations") or obj.translations is None:
        obj.translations = {}
    else:
        # Create a copy to trigger SQLAlchemy change detection
        obj.translations = dict(obj.translations)
    
    # Ensure language key exists
    if language not in obj.translations:
        obj.translations[language] = {}
    else:
        # Create a copy of the language dict
        obj.translations[language] = dict(obj.translations[language])
    
    # Set the translation
    obj.translations[language][field_name] = value


def merge_translations(
    obj: Any,
    translations: dict[str, dict[str, str]],
) -> None:
    """
    Merge multiple translations into an object.
    
    Args:
        obj: The database object to modify
        translations: Nested dict of translations
            Format: {"vi": {"name": "...", "description": "..."}, "en": {...}}
    
    Example:
        race = Race(name="Hanoi Marathon")
        merge_translations(race, {
            "vi": {"name": "Giải chạy Hà Nội", "description": "..."},
            "th": {"name": "มาราธอนฮานอย"}
        })
    """
    if not translations:
        return
    
    # Initialize translations if needed - create a NEW dict to trigger SQLAlchemy change detection
    if not hasattr(obj, "translations") or obj.translations is None:
        obj.translations = {}
    else:
        # Create a copy to trigger SQLAlchemy change detection
        obj.translations = dict(obj.translations)
    
    # Merge each language
    for lang_code, lang_translations in translations.items():
        lang_code = lang_code.lower()
        
        if lang_code not in obj.translations:
            obj.translations[lang_code] = {}
        else:
            # Create a copy of the language dict
            obj.translations[lang_code] = dict(obj.translations[lang_code])
        
        # Merge fields
        obj.translations[lang_code].update(lang_translations)


def get_supported_languages() -> list[str]:
    """Get list of supported language codes."""
    return SUPPORTED_LANGUAGES.copy()


def is_language_supported(language: str) -> bool:
    """Check if a language is supported."""
    return language.lower() in SUPPORTED_LANGUAGES
