"""Taxonomy manager: loads and validates the 30-category canonical issue taxonomy.

Maintains bidirectional mappings between canonical 30 issue types, their owning functions,
default severities, SLAs, and backward-compatible 9 generic categories.
"""

import json
import os
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class TaxonomyCategory(BaseModel):
    code: str
    slug: str
    name: str
    domain: str
    generic_category: str
    primary_owner: str
    secondary_owner: Optional[str] = None
    default_severity: str = "MEDIUM"
    sla_hours: int = 12
    escalation_policy: Optional[str] = None
    keywords: List[str] = Field(default_factory=list)

    @property
    def issue_type(self) -> str:
        return self.slug


class TaxonomyManager:
    """Loads, validates, and queries the retail issue taxonomy."""

    def __init__(self, taxonomy_file: Optional[str] = None):
        if not taxonomy_file:
            taxonomy_file = os.path.join(os.path.dirname(__file__), "taxonomy.json")
        self.taxonomy_file = taxonomy_file
        self.categories_by_name: Dict[str, TaxonomyCategory] = {}
        self.categories_by_slug: Dict[str, TaxonomyCategory] = {}
        self.categories_by_code: Dict[str, TaxonomyCategory] = {}
        self.domains: Dict[str, List[TaxonomyCategory]] = {}
        self.owner_mapping: Dict[str, str] = {}
        self.load()

    def load(self):
        if not os.path.exists(self.taxonomy_file):
            return
        with open(self.taxonomy_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        for item in data.get("categories", []):
            cat = TaxonomyCategory(**item)
            self.categories_by_name[cat.name] = cat
            self.categories_by_slug[cat.slug] = cat
            self.categories_by_code[cat.code] = cat
            self.owner_mapping[cat.slug] = cat.primary_owner
            self.owner_mapping[cat.name] = cat.primary_owner

            if cat.domain not in self.domains:
                self.domains[cat.domain] = []
            self.domains[cat.domain].append(cat)

    @property
    def categories(self) -> Dict[str, TaxonomyCategory]:
        """Backward-compatible mapping indexed by category name and slug."""
        merged = dict(self.categories_by_name)
        merged.update(self.categories_by_slug)
        return merged

    def get(self, query: str) -> Optional[TaxonomyCategory]:
        """Retrieve category by slug, name, or code."""
        if not query:
            return None
        q = query.strip()
        return (
            self.categories_by_slug.get(q)
            or self.categories_by_slug.get(q.lower())
            or self.categories_by_name.get(q)
            or self.categories_by_code.get(q)
            or self._fuzzy_find(q)
        )

    def _fuzzy_find(self, query: str) -> Optional[TaxonomyCategory]:
        q_lower = query.lower()
        for cat in self.categories_by_slug.values():
            if cat.slug.lower() == q_lower or cat.name.lower() == q_lower or cat.code.lower() == q_lower:
                return cat
            if q_lower in cat.slug.lower() or q_lower in cat.name.lower():
                return cat
        return None

    def get_owner(self, category_name_or_slug: str, default: str = "Store Ops") -> str:
        cat = self.get(category_name_or_slug)
        return cat.primary_owner if cat else default

    def to_generic_category(self, issue_type_or_category: str) -> str:
        """Map canonical 30 issue type or name to backward-compatible 9 generic categories."""
        cat = self.get(issue_type_or_category)
        if cat:
            return cat.generic_category
        return "Other or unknown"

    def list_all(self) -> List[TaxonomyCategory]:
        return list(self.categories_by_slug.values())

    def validate_category(self, category_name: str) -> bool:
        return self.get(category_name) is not None


# Global singleton instance
taxonomy_manager = TaxonomyManager()
