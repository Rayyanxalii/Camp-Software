"""Routers package - API route handlers"""

from app.routers import auth, patients, visits, dental_visits, stock, lookup, analytics, uploads

__all__ = ["auth", "patients", "visits", "dental_visits", "stock", "lookup", "analytics", "uploads"]
