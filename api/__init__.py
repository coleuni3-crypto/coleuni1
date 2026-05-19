# =====================================================
# COLEUNI API PACKAGE (V4.5 PRODUCTION SAFE)
# =====================================================

"""
ColeUni API Routes Package - Global Education OS

⚠️ IMPORTANT:
- This file does NOT auto-load routers
- Router loading is handled ONLY in main.py
- This avoids duplicate imports + FastAPI conflicts
"""

import os
import pkgutil
import importlib
import logging

__version__ = "4.5.0"

# =====================================================
# 🔇 SAFE LOGGING SYSTEM
# =====================================================
logger = logging.getLogger("coleuni.api")

if os.getenv("ENV", "development") == "development":
    logger.setLevel(logging.INFO)
else:
    logger.setLevel(logging.WARNING)

# =====================================================
# 📦 EXPORTED MODULE LIST
# =====================================================
__all__ = []

# =====================================================
# 🔍 OPTIONAL MODULE DISCOVERY (DEBUG ONLY)
# =====================================================
def discover_modules(verbose: bool = False):
    """
    Only used for debugging.
    Does NOT auto-register routers.
    """

    package_name = __name__
    loaded = []

    try:
        for _, module_name, _ in pkgutil.iter_modules(__path__):
            full_module = f"{package_name}.{module_name}"

            try:
                importlib.import_module(full_module)
                loaded.append(module_name)

                if verbose:
                    logger.info(f"Loaded module: {full_module}")

            except Exception as e:
                logger.error(f"Failed loading {full_module}: {e}")

        return {
            "success": True,
            "modules": loaded,
            "count": len(loaded)
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

# =====================================================
# 🚫 AUTO-LOAD IS DISABLED BY DESIGN
# =====================================================
# Reason:
# - Prevents duplicate router registration
# - Keeps FastAPI startup deterministic
# - Ensures main.py controls system boot order