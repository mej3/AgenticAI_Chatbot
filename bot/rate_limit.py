import asyncio
import logging

logger = logging.getLogger(__name__)

_FIB_DELAYS = [1, 1, 2, 3]  # seconds to wait before each retry attempt


def apply_rate_limit_retry(model):
    """Wraps generate_content_async on a model instance with Fibonacci retry on 429 errors."""
    original_generate = model.generate_content_async

    async def generate_with_retry(*args, **kwargs):
        for attempt, delay in enumerate(_FIB_DELAYS, start=1):
            try:
                async for response in original_generate(*args, **kwargs):
                    yield response
                return
            except Exception as e:
                if getattr(e, "code", None) != 429 or attempt == len(_FIB_DELAYS):
                    raise
                logger.warning(
                    f"Rate limit hit. Retrying {attempt}/{len(_FIB_DELAYS)} in {delay}s..."
                )
                await asyncio.sleep(delay)

    model.generate_content_async = generate_with_retry
    return model
