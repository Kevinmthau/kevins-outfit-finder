#!/usr/bin/env python3
"""
Centralized configuration for Kevin's Outfit Finder.
All settings, paths, brand lists, and category definitions in one place.
"""

from pathlib import Path
from typing import Dict, List

# =============================================================================
# PATHS
# =============================================================================

# Base directory (project root)
BASE_DIR = Path(__file__).parent

# Tesseract OCR path (macOS Homebrew installation)
TESSERACT_PATH = "/opt/homebrew/bin/tesseract"

# Collection image directories
COLLECTION_PATHS: Dict[str, Path] = {
    "summer": BASE_DIR / "Kevin_Summer_Looks_Pages",
    "spring": BASE_DIR / "KEVIN_Spring_Looks_Images",
    "fw": BASE_DIR / "Fall_Winter_Looks_Images",
}

# Data file paths
DATA_FILES: Dict[str, Dict[str, Path]] = {
    "summer": {
        "clothing_index": BASE_DIR / "clothing_index.json",
        "page_items": BASE_DIR / "page_items.json",
        "category_stats": BASE_DIR / "category_stats_summer.json",
    },
    "spring": {
        "clothing_index": BASE_DIR / "clothing_index_spring.json",
        "page_items": BASE_DIR / "page_items_spring.json",
        "category_stats": BASE_DIR / "category_stats_spring.json",
    },
    "fw": {
        "clothing_index": BASE_DIR / "clothing_index_fw.json",
        "page_items": BASE_DIR / "page_items_fw.json",
        "category_stats": BASE_DIR / "category_stats_fw.json",
    },
    "fall": {
        "clothing_index": BASE_DIR / "clothing_index_fw.json",
        "page_items": BASE_DIR / "page_items_fw.json",
        "category_stats": BASE_DIR / "category_stats_fw.json",
        "page_seasons": BASE_DIR / "page_seasons_fw.json",
    },
    "winter": {
        "clothing_index": BASE_DIR / "clothing_index_fw.json",
        "page_items": BASE_DIR / "page_items_fw.json",
        "category_stats": BASE_DIR / "category_stats_fw.json",
        "page_seasons": BASE_DIR / "page_seasons_fw.json",
    },
}

# Page seasons file (for Fall/Winter split)
PAGE_SEASONS_FILE = BASE_DIR / "page_seasons_fw.json"

# Static site output
DIST_DIR = BASE_DIR / "dist"
DIST_IMAGE_FOLDERS: Dict[str, str] = {
    "summer": "images",
    "spring": "spring_images",
    "fw": "fw_images",
    "fall": "fw_images",
    "winter": "fw_images",
}

# =============================================================================
# CLOTHING CATEGORIES
# =============================================================================

# Summer collection categories (simpler, warm weather focus)
SUMMER_CATEGORIES: Dict[str, List[str]] = {
    "Outerwear": ["jacket", "blazer", "cardigan"],
    "Tops": ["polo", "shirt", "sweater", "tee", "t-shirt", "blouse", "henley"],
    "Bottoms": ["trouser", "pant", "short", "jean", "chino", "khaki", "5-pocket", "5 pocket", "corduroy"],
    "Footwear": ["loafer", "sandal", "espadrille", "shoe", "sneaker", "moccasin"],
    "Accessories": ["belt", "watch", "sunglasses", "hat", "tie"],
}

# Spring collection categories
SPRING_CATEGORIES: Dict[str, List[str]] = {
    "Outerwear": ["jacket", "coat", "blazer", "windbreaker", "bomber", "trench", "parka", "vest", "overcoat"],
    "Tops": ["shirt", "polo", "t-shirt", "tee", "blouse", "sweater", "pullover", "hoodie", "cardigan", "knit", "henley", "tank", "turtleneck", "sweatshirt"],
    "Bottoms": ["trouser", "pant", "jean", "chino", "short", "slack", "jogger", "corduroy", "5 pocket", "5-pocket"],
    "Footwear": ["shoe", "sneaker", "loafer", "boot", "sandal", "slipper", "oxford", "derby", "moccasin", "espadrille", "desert boot"],
    "Accessories": ["belt", "watch", "sunglasses", "hat", "cap", "scarf", "tie", "bag", "wallet", "bracelet", "necklace"],
    "Suits": ["suit", "tuxedo"],
    "Activewear": ["tracksuit", "sweatpant", "athletic", "gym", "running", "training"],
}

# Fall/Winter collection categories (cold weather focus)
FW_CATEGORIES: Dict[str, List[str]] = {
    "Outerwear": ["coat", "jacket", "blazer", "overcoat", "parka", "bomber", "windbreaker", "trench", "peacoat", "duffle", "topcoat", "raincoat", "anorak"],
    "Knitwear": ["sweater", "cardigan", "pullover", "jumper", "knit", "turtleneck", "rollneck", "v-neck", "crewneck", "cable knit", "merino", "cashmere", "wool"],
    "Tops": ["shirt", "polo", "blouse", "t-shirt", "tee", "henley", "oxford", "flannel"],
    "Bottoms": ["trouser", "pant", "jean", "chino", "corduroy", "slack", "wool pant", "flannel trouser", "5 pocket", "5-pocket"],
    "Footwear": ["boot", "shoe", "loafer", "oxford", "derby", "chelsea", "combat boot", "desert boot", "sneaker", "brogue", "monk strap", "chukka"],
    "Accessories": ["scarf", "glove", "hat", "beanie", "cap", "belt", "watch", "bag", "sunglasses", "tie", "pocket square", "muffler"],
    "Suits": ["suit", "tuxedo", "dinner jacket", "formal"],
    "Layering": ["vest", "gilet", "waistcoat", "liner", "thermal"],
}

# Category display order for each collection
CATEGORY_ORDER: Dict[str, List[str]] = {
    "summer": ["Bottoms", "Tops", "Footwear", "Outerwear", "Accessories", "Other"],
    "spring": ["Bottoms", "Tops", "Footwear", "Outerwear", "Accessories", "Suits", "Activewear", "Other"],
    "fw": ["Bottoms", "Tops", "Footwear", "Outerwear", "Knitwear", "Suits", "Layering", "Accessories", "Other"],
    "fall": ["Bottoms", "Tops", "Footwear", "Outerwear", "Knitwear", "Suits", "Layering", "Accessories", "Other"],
    "winter": ["Bottoms", "Tops", "Footwear", "Outerwear", "Knitwear", "Suits", "Layering", "Accessories", "Other"],
}

# Category icons for display
CATEGORY_ICONS: Dict[str, str] = {
    "Outerwear": "🧥",
    "Knitwear": "🧶",
    "Tops": "👔",
    "Bottoms": "👖",
    "Footwear": "👞",
    "Accessories": "🎩",
    "Suits": "🤵",
    "Layering": "🦺",
    "Activewear": "🏃",
    "Other": "📦",
}

# =============================================================================
# BRAND LISTS
# =============================================================================

# Core luxury brands (appear across all collections)
CORE_BRANDS: List[str] = [
    "Saint Laurent",
    "The Row",
    "Prada",
    "Tom Ford",
    "Brunello Cucinelli",
    "Loro Piana",
    "Zegna",
    "Hermès",
    "Hermes",
    "Bottega Veneta",
    "Gucci",
    "Valentino",
    "Burberry",
    "Ralph Lauren",
    "Polo Ralph Lauren",
]

# Italian tailoring brands
ITALIAN_BRANDS: List[str] = [
    "Boglioli",
    "Lardini",
    "Caruso",
    "Canali",
    "Kiton",
    "Isaia",
    "Brioni",
    "De Petrillo",
    "Ring Jacket",
]

# European designer brands
EUROPEAN_BRANDS: List[str] = [
    "Celine",
    "Dior",
    "Balenciaga",
    "Acne Studios",
    "Thom Browne",
    "Maison Margiela",
    "Lanvin",
    "Dries Van Noten",
    "Dries",
    "Jil Sander",
    "Marni",
    "Lemaire",
    "Margaret Howell",
    "Loewe",
]

# British brands
BRITISH_BRANDS: List[str] = [
    "Drake's",
    "Drakes",
    "Anderson & Sheppard",
    "Sunspel",
    "John Smedley",
    "Private White V.C.",
    "SEH Kelly",
    "Clarks",
    "Dunhill",
]

# Streetwear and contemporary brands
CONTEMPORARY_BRANDS: List[str] = [
    "Stone Island",
    "Moncler",
    "Off-White",
    "Fear of God",
    "Rick Owens",
    "Common Projects",
    "A.P.C.",
    "APC",
    "Norse Projects",
    "Our Legacy",
    "Auralee",
]

# Knitwear specialists
KNITWEAR_BRANDS: List[str] = [
    "Iris Von Arnim",
    "Le Kasha",
    "Fedeli",
    "Gran Sasso",
    "Zanone",
    "The Elder Statesman",
]

# Other notable brands
OTHER_BRANDS: List[str] = [
    "Altea",
    "Officine Generale",
    "Beams",
    "Lacoste",
    "Frame",
    "Frankie Shop",
    "Massimo Alba",
    "Berg & Berg",
    "Saman Amel",
    "Stoffa",
    "Canada Goose",
    "Derek Rose",
    "Castaner",
    "Ikiji",
]

# Combined brand lists by collection
SUMMER_BRANDS: List[str] = (
    CORE_BRANDS + ITALIAN_BRANDS + KNITWEAR_BRANDS +
    ["Altea", "Beams", "Lacoste", "Dries", "Loewe", "Fedeli", "Frame", "APC",
     "Frankie Shop", "Brioni", "Sunspel", "Massimo Alba", "Dunhill", "Derek Rose",
     "Castaner", "Ikiji", "Drakes", "Drake's"]
)

SPRING_BRANDS: List[str] = (
    CORE_BRANDS + ITALIAN_BRANDS + EUROPEAN_BRANDS + CONTEMPORARY_BRANDS +
    KNITWEAR_BRANDS + OTHER_BRANDS
)

FW_BRANDS: List[str] = (
    CORE_BRANDS + ITALIAN_BRANDS + EUROPEAN_BRANDS + BRITISH_BRANDS +
    CONTEMPORARY_BRANDS + KNITWEAR_BRANDS + OTHER_BRANDS
)

# All brands combined (for general use)
ALL_BRANDS: List[str] = list(set(
    CORE_BRANDS + ITALIAN_BRANDS + EUROPEAN_BRANDS + BRITISH_BRANDS +
    CONTEMPORARY_BRANDS + KNITWEAR_BRANDS + OTHER_BRANDS
))

# =============================================================================
# OCR SETTINGS
# =============================================================================

# Maximum item length before considering it might be multiple items combined
MAX_ITEM_LENGTH = 50

# Minimum item length to be considered valid
MIN_ITEM_LENGTH = 3

# OCR artifact patterns to clean
OCR_ARTIFACTS = [
    r"^i\s+",  # Leading "i "
    r"^of\s+",  # Leading "of "
    r"^\d+\s+",  # Leading numbers
    r"^[^\w]+",  # Leading non-word characters
]

# =============================================================================
# STATIC SITE SETTINGS
# =============================================================================

# Collection display names
COLLECTION_DISPLAY_NAMES: Dict[str, str] = {
    "summer": "Summer",
    "spring": "Spring",
    "fw": "Fall/Winter",
    "fall": "Fall",
    "winter": "Winter",
}

# Collection icons
COLLECTION_ICONS: Dict[str, str] = {
    "summer": "☀️",
    "spring": "🌸",
    "fw": "❄️",
    "fall": "🍂",
    "winter": "❄️",
}

# Default collection to show
DEFAULT_COLLECTION = "summer"

# Search settings
FUZZY_SEARCH_THRESHOLD = 0.6  # Minimum similarity score for fuzzy matching
