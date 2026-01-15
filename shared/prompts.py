# services/shared/prompts.py
EXTRACTOR_SYSTEM = """You are the FACTOR EXTRACTION agent.
Return ONLY valid JSON. No markdown. Schema: see instructions."""
# We'll dynamically compose the rest of prompts within services to inject PDF_TEXT, FACTOR, etc.
