from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from recython.config import RecythonConfig
from recython.filesystem import load_template


PROMPT_KEYS = ("classic_pyx", "classic_pxd", "pure")
PROFILE_NAMES = ("default", "safe", "performance", "minimal-diff", "maintenance")
PLACEHOLDERS = {
    "classic_pyx": ("XXXCODEXXX",),
    "classic_pxd": ("XXXRESULTXXX",),
    "pure": ("XXXCODEXXX",),
}
BUNDLED_FILES = {
    "classic_pyx": "cython_style_pyx.md",
    "classic_pxd": "cython_style_pxd.md",
    "pure": "cython_pure_python_style.md",
}
PROFILE_INSTRUCTIONS = {
    "default": "",
    "safe": (
        "\n\nAdditional guidance:\n"
        "Prefer correctness and readability over aggressive optimization."
    ),
    "performance": (
        "\n\nAdditional guidance:\n"
        "Prioritize meaningful Cython performance improvements when they are safe and justified."
    ),
    "minimal-diff": (
        "\n\nAdditional guidance:\n"
        "Make the smallest possible change set and preserve the source structure closely."
    ),
    "maintenance": (
        "\n\nAdditional guidance:\n"
        "Prefer minimal maintenance updates and preserve previously generated structure when possible."
    ),
}


@dataclass(slots=True)
class PromptTemplate:
    key: str
    text: str
    source: str


@dataclass(slots=True)
class PromptPack:
    profile: str
    templates: dict[str, PromptTemplate]


def list_prompt_profiles() -> list[str]:
    return list(PROFILE_NAMES)


def load_prompt_pack(config: RecythonConfig) -> PromptPack:
    if config.prompt_profile not in PROFILE_NAMES:
        raise ValueError(f"Unknown prompt profile '{config.prompt_profile}'.")

    templates: dict[str, PromptTemplate] = {}
    for key in PROMPT_KEYS:
        override_path = config.prompt_paths.get(key)
        if override_path:
            path = Path(override_path)
            if not path.is_absolute():
                path = (config.project_root / path).resolve()
            text = path.read_text(encoding="utf-8") + PROFILE_INSTRUCTIONS[config.prompt_profile]
            templates[key] = PromptTemplate(key=key, text=text, source=str(path))
        else:
            templates[key] = PromptTemplate(
                key=key,
                text=load_template(BUNDLED_FILES[key]) + PROFILE_INSTRUCTIONS[config.prompt_profile],
                source=BUNDLED_FILES[key],
            )

    pack = PromptPack(profile=config.prompt_profile, templates=templates)
    validate_prompt_pack(pack)
    return pack


def validate_prompt_pack(pack: PromptPack) -> None:
    missing = [key for key in PROMPT_KEYS if key not in pack.templates]
    if missing:
        raise ValueError(f"Prompt pack '{pack.profile}' is missing templates: {', '.join(missing)}")

    for key, required in PLACEHOLDERS.items():
        template = pack.templates[key]
        missing_placeholders = [placeholder for placeholder in required if placeholder not in template.text]
        if missing_placeholders:
            raise ValueError(
                f"Prompt template '{key}' from {template.source} is missing placeholders: "
                + ", ".join(missing_placeholders)
            )


def render_prompt(pack: PromptPack, template_key: str, **replacements: str) -> str:
    template = pack.templates[template_key].text
    rendered = template
    for placeholder, value in replacements.items():
        rendered = rendered.replace(placeholder, value)
    return rendered
