"""Main CLI entry point for sitemap filter."""

from loguru import logger
import sys

# Configure loguru for the application
logger.remove()  # Remove default handler
logger.add(
    sys.stderr,
    format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level="INFO"
)


def main():
    """Main entry point for the sitemap filter CLI."""
    logger.info("Sitemap filter CLI starting...")
    # CLI implementation will be added in User Story phases
    pass


if __name__ == "__main__":
    main()
