from typing import TYPE_CHECKING
from .base import HealthCheck, CheckConfig

if TYPE_CHECKING:
    from .sqlalchemy_async import SQLAlchemyAsyncCheck
    from .django_db import DjangoDBCheck
    from .redis_async import RedisAsyncCheck
    from .redis_sync import RedisSyncCheck
    from .rabbitmq_kombu import RabbitMQKombuCheck
    from .celery_inspect import CeleryInspectCheck
    from .http_dep import HttpDependencyCheck

__all__ = [
    "HealthCheck",
    "CheckConfig",
    "SQLAlchemyAsyncCheck",
    "DjangoDBCheck",
    "RedisAsyncCheck",
    "RedisSyncCheck",
    "RabbitMQKombuCheck",
    "CeleryInspectCheck",
    "HttpDependencyCheck",
]


def __getattr__(name: str):
    if name == "SQLAlchemyAsyncCheck":
        from .sqlalchemy_async import SQLAlchemyAsyncCheck
        return SQLAlchemyAsyncCheck

    if name == "DjangoDBCheck":
        from .django_db import DjangoDBCheck
        return DjangoDBCheck

    if name == "RedisAsyncCheck":
        from .redis_async import RedisAsyncCheck
        return RedisAsyncCheck

    if name == "RedisSyncCheck":
        from .redis_sync import RedisSyncCheck
        return RedisSyncCheck

    if name == "RabbitMQKombuCheck":
        from .rabbitmq_kombu import RabbitMQKombuCheck
        return RabbitMQKombuCheck

    if name == "CeleryInspectCheck":
        from .celery_inspect import CeleryInspectCheck
        return CeleryInspectCheck

    if name == "HttpDependencyCheck":
        from .http_dep import HttpDependencyCheck
        return HttpDependencyCheck

    raise AttributeError(f"module {__name__} has no attribute {name}")