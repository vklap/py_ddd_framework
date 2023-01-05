# py_ddd_framework
Python Domain-Driven Design Framework

# A Domain-Driven Design (DDD) Framework for Python Developers :snake::snake::snake:

## What is this library good for?
This is a lightweight framework that provides a quick setup for
[Domain-Driven](https://en.wikipedia.org/wiki/Domain-driven_design) designed apps that
are easy to unit test - and is based on battle tested DDD Design Patterns, such as:

1. `Domain Layer` entities with domain events for handling side effects (or even support Event-Driven Architectures) 
2. `Application Service Layer` flow handlers that are being executed by units of work (to commit/rollback operations)
3. `Infrastructure/Adapters Layer` to external resources (such as: database repositories, web service clients, etc.)
4. `CQRS` (Command Query Responsibility Separation) with domain commands