from instagram_agent.config import get_settings
from instagram_agent.db import create_schema, session_scope
from instagram_agent.models import Source

SOURCES = [
    ("Google AI Blog", "https://blog.google/technology/ai/rss/", 1),
    ("OpenAI News", "https://openai.com/news/rss.xml", 1),
    ("Anthropic News", "https://www.anthropic.com/rss.xml", 1),
]


def main() -> None:
    settings = get_settings()
    create_schema(settings)
    with session_scope(settings) as session:
        for name, feed_url, tier in SOURCES:
            if not session.query(Source).filter_by(feed_url=feed_url).first():
                session.add(
                    Source(
                        name=name,
                        source_type="rss",
                        feed_url=feed_url,
                        authority_tier=tier,
                    )
                )


if __name__ == "__main__":
    main()
