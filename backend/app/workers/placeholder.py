"""Worker placeholder — processo independente do frontend; lógica nas Fases 3/6."""

from __future__ import annotations

from app.core.config import get_settings
from app.core.logging import configure_logging, get_logger
from app.core.security import assert_paper_only


def main() -> None:
    settings = get_settings()
    configure_logging(settings.log_level)
    assert_paper_only(settings)
    logger = get_logger(__name__)
    logger.info(
        "Worker placeholder (Fase 1). Nenhuma ingestão ou trading ativo.",
        extra={"extra_fields": {"event": "worker_placeholder", "app_mode": "paper"}},
    )


if __name__ == "__main__":
    main()
