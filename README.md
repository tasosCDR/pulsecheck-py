# PulseCheck

> Unified health, liveness, and readiness checks for Python microservices.

PulseCheck is a framework-agnostic health check library designed for modern Python services.

It provides a pluggable health engine with adapters for FastAPI and Django, built with Kubernetes readiness/liveness semantics in mind.

---

## Features
- Framework-agnostic core
- FastAPI adapter
- Django adapter
- Pluggable dependency checks:
  - SQLAlchemy (async)
  - Django ORM
  - Redis (sync & async)
  - RabbitMQ (Kombu)
  - Celery worker inspection
  - HTTP dependency checks

- Configurable timeouts

- Degraded vs unhealthy states

- Optional dependency extras

- Zero forced framework pollution

- Production-ready JSON schema

- Kubernetes-compatible

---

## Installation

Install core only:

```bash
pip install pulsecheck-py
```
Install with FastAPI support:
```bash 
pip install pulsecheck-py[fastapi]
```
Install with Django support:

```bash
pip install pulsecheck-py[django]
```
Install with multiple dependency checks:

```bash 
pip install pulsecheck-py[fastapi,redis_async,sqlalchemy_async,rabbitmq,celery]
```
FastAPI Example
------------------

``` python
from fastapi import FastAPI 
from pulsecheck.core import HealthRegistry 
from pulsecheck.core.checks import SQLAlchemyAsyncCheck 
from pulsecheck.fastapi import make_health_router

app = FastAPI()

registry = HealthRegistry(environment="prod") 
registry.register(SQLAlchemyAsyncCheck(engine))

app.include_router(make_health_router(registry))
```

Endpoints:

```bash 
GET /health 
GET /health/live 
GET /health/ready
```

Django Example
------------------

```python 

from pulsecheck.core import HealthRegistry 
from pulsecheck.core.checks import DjangoDBCheck 
from pulsecheck.django import make_urlpatterns

registry = HealthRegistry(environment="prod") 
registry.register(DjangoDBCheck())

urlpatterns = [
    *make_urlpatterns(registry)
]
```

Health Response Format
-------------------------

```json
{
  "status": "HEALTHY",
  "timestamp": "2026-02-15T12:34:56Z",
  "environment": "prod",
  "checks": {
      "database": {
          "status": "HEALTHY",
          "response_time_ms": 4.3
      }
  }
}
```
States:

-   `HEALTHY`
-   `DEGRADED`
-   `UNHEALTHY`

Design Philosophy
------------------

PulseCheck separates:

-   Core health aggregation logic

-   Dependency checks

-   Framework adapters

This ensures:

-   No tight framework coupling

-   Optional extras per ecosystem

-   Clean dependency graphs

-   Compatibility across service architectures


Optional Dependencies (Extras)
---------------------------------

| Extra | Installs |
| --- | --- |
| fastapi | FastAPI adapter |
| django | Django adapter |
| redis_async | Async Redis check |
| redis_sync | Sync Redis check |
| rabbitmq | Kombu-based AMQP check |
| celery | Celery inspect check |
| sqlalchemy_async | Async SQLAlchemy check |
| http | HTTP dependency check |

Testing
----------

PulseCheck is tested against:

-   Python 3.10+

-   FastAPI

-   Django

-   Async and sync dependency scenarios

* * * * *

Intended Use
---------------

PulseCheck is designed for:

-   Microservices

-   Containerized applications

-   Kubernetes environments

-   Internal APIs

-   Distributed systems

It is **not** a monitoring system.\
It is a lightweight dependency availability indicator.

* * * * * 

Contributing
---------------

Issues and pull requests are welcome.