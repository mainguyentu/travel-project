from __future__ import annotations

from app.core.config import settings
from app.core.errors import AppError


class RepositoryBoundaryMixin:
    owner_domain = "unknown"
    allowed_service_profiles: set[str] = set()

    def _assert_service_boundary(self, repository_name: str) -> None:
        profile = settings.service_profile
        if profile == "monolith":
            return
        if not self.allowed_service_profiles:
            return
        if profile in self.allowed_service_profiles:
            return

        raise AppError(
            "BOUNDARY_VIOLATION",
            f"{repository_name} is not allowed in service profile '{profile}'",
            status_code=500,
            details=[
                {
                    "repository": repository_name,
                    "owner_domain": self.owner_domain,
                    "service_profile": profile,
                    "allowed_service_profiles": sorted(self.allowed_service_profiles),
                }
            ],
        )
