# =====================================================
# COLEUNI PACKAGE INITIALIZER (PRODUCTION READY)
# =====================================================

"""
ColeUni Backend Package
Enables structured imports like:
coleuni.api.auth_routes
coleuni.services.ai_service
"""

__version__ = "4.5.0"

import os
import logging

# =====================================================
# 🧠 LOGGER SETUP (SAFE FOR RENDER + LOCAL)
# =====================================================
logger = logging.getLogger("coleuni")

if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        "[ColeUni] %(levelname)s - %(message)s"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)


# =====================================================
# 🌍 ENV DETECTION (RENDER SAFE)
# =====================================================
ENV = os.getenv("ENV", "development")


# =====================================================
# 🚀 PACKAGE INITIALIZATION
# =====================================================
if ENV == "development":
    logger.info("ColeUni backend initialized (development mode)")
else:
    logger.info("ColeUni backend initialized (production mode)")