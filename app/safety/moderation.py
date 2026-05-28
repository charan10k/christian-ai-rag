import re

# Patterns that must be blocked outright — hate, incitement, fabrication, injection
BLOCKED_PATTERNS = [
    # Rewrite / fabricate scripture to support ideology
    r"rewrite\b.{0,60}\bbible\b",
    r"rewrite\b.{0,60}\bverse",
    r"rewrite\b.{0,60}\bscripture",
    r"change\b.{0,60}\bbible\b.{0,40}\bsay",
    r"make (the )?bible (say|support|justify)",
    r"edit\b.{0,40}\bverse\b.{0,40}\bto (say|support|justify)",

    # White supremacy / racial hatred
    r"white supremac",
    r"racial (superiority|supremacy|purity|cleansing)",
    r"(blacks?|jews?|muslims?|hispanics?|asians?)\b.{0,40}(inferior|subhuman|evil race|should die)",

    # Explicit incitement
    r"\bkill (all )?(christians?|jews?|muslims?|infidels?|unbelievers?)",
    r"\b(murder|kill|exterminate|genocide)\b.{0,30}\b(religion|faith|christians?|jews?|muslims?)",
    r"use (the )?bible to (justify|support|endorse) (violence|killing|murder|genocide|rape|slavery)",
    r"justify\b.{0,40}(terrorism|jihad|crusade killings?|ethnic cleansing)",

    # Hate toward religion / God
    r"\bhate (god|jesus|christianity|islam|judaism|religion)\b",
    r"\b(destroy|abolish|eradicate)\b.{0,20}\b(christianity|religion|church)\b",

    # Explicit sexual content
    r"\b(sexual|erotic|porn|nude|naked)\b.{0,30}\b(jesus|mary|god|bible|church|saint)\b",

    # Prompt injection attempts
    r"ignore (your|all|previous) instructions",
    r"disregard (your|all|previous) (instructions|rules|guidelines)",
    r"you are now\b.{0,40}\b(evil|unrestricted|jailbreak|dan|unfiltered)",
    r"pretend (you are|to be)\b.{0,40}\b(evil|unrestricted|no (rules|restrictions))",
    r"act as if (you have no|you don't have|without) (restrictions|guidelines|safety|ethics)",
    r"new (persona|mode|system prompt|instructions):",
    r"\[system\]",
    r"bypass (your|safety|content|moderation)",

    # Scripture manipulation
    r"write a (fake|false|new|made.?up) (bible )?verse",
    r"invent\b.{0,30}\b(verse|scripture|passage)",
    r"fabricate\b.{0,30}\b(verse|scripture|passage)",
    r"create\b.{0,40}\bverse\b.{0,30}\b(that says|to support|justifying)",

    # Extremist theology
    r"extremist",
    r"terrorist\b.{0,20}\b(christian|islamic|jewish)",
    r"religious (war|cleansing|purification) (is|should be) (good|right|necessary)",
]

_COMPILED = [re.compile(p, re.IGNORECASE) for p in BLOCKED_PATTERNS]


def moderate_prompt(prompt: str) -> dict:
    for pattern in _COMPILED:
        if pattern.search(prompt):
            return {
                "blocked": True,
                "message": (
                    "This request has been blocked. It appears to contain content "
                    "that promotes hatred, scripture manipulation, or unsafe theology. "
                    "Please ask a sincere question about Christian faith."
                )
            }
    return {"blocked": False}
