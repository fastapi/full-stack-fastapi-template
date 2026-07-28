from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(protected_namespaces=(), extra="ignore")

    # ISO 639-1 codes, comma separated. Restricted to en+fr deliberately:
    # confidences are normalised across only these two, which makes the model
    # markedly more accurate on short segments than a wide language set
    # ("Open the door." is misread as Dutch once you add 5 more languages).
    #
    # The trade-off, accepted knowingly: with only two languages the detector
    # cannot say "this is Spanish". Non-EN/FR text is reported as whichever of
    # the two it resembles, and no confidence threshold separates it — German
    # scores 0.639 as English while a genuine "Yes." scores 0.634. This is safe
    # for an EN/FR bitext corpus and wrong for mixed-language input.
    LANGUAGES: str = "en,fr"

    # Reported only. lingua already returns no language when its own
    # minimum-relative-distance rule can't decide (numbers, symbols), so this
    # is a second, blunter gate — off by default.
    MIN_CONFIDENCE: float = 0.0

    MAX_TEXTS_PER_REQUEST: int = 8192

    # Trades accuracy for lower memory. Off: the accuracy on short segments is
    # the entire reason for choosing lingua.
    LOW_ACCURACY_MODE: bool = False

    # Load the n-gram models at startup rather than on first request, so
    # /ready means ready.
    PRELOAD: bool = True

    @property
    def language_codes(self) -> list[str]:
        return [c.strip().lower() for c in self.LANGUAGES.split(",") if c.strip()]


settings = Settings()
