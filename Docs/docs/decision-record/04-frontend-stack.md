# Decision Record: Frontend Technology Stack Selection

**ID:** 04  
**Date:** 2024-06-07  
**Status:** Accepted  
**Author:** hoangpt  
**Reviewer:** lam

## Context

The project requires a modern, maintainable, and efficient frontend stack that supports rapid development, easy integration with backend APIs, and a smooth developer experience. The team is experienced with JavaScript/TypeScript and aims for a solution that is easy to onboard, scales with project needs, and fits well with the chosen backend and deployment approach.

## Options

| Technology                | Pros                                                                 | Cons                                      |
|---------------------------|----------------------------------------------------------------------|-------------------------------------------|
| **Monolithic (Vite + React)** | - Fast development and hot reload<br>- Simple setup and configuration<br>- Large ecosystem and community<br>- Fine-grained control over build and deployment<br>- Lightweight, easy to containerize | - No built-in SSR/SSG<br>- Manual routing and state management<br>- Less opinionated, requires more setup for advanced features |
| **Next.js**               | - Built-in SSR/SSG for SEO<br>- File-based routing<br>- API routes for simple backend needs<br>- Strong React integration<br>- Good for fullstack apps | - More complex build and deployment<br>- Some learning curve for advanced features<br>- May be overkill for simple SPAs |
| **NestJS (Frontend with SSR)** | - Unified backend/frontend with TypeScript<br>- Powerful DI and modularity<br>- Good for large, enterprise apps<br>- SSR support | - Primarily a backend framework<br>- Less frontend community support<br>- Heavier setup for pure frontend needs |

## Decision

- Select **Monolithic (Vite + React)** as the primary frontend technology stack for this project.

## Rationale

- Vite + React offers a fast, modern development experience with minimal configuration and excellent support for TypeScript.
- The team is already proficient in React, enabling rapid feature delivery and easier onboarding.
- The monolithic approach simplifies deployment and fits well with the current backend and infrastructure choices.
- For this project, SSR/SSG is not a strict requirement, so the simplicity and speed of Vite + React outweigh the benefits of Next.js or NestJS.
- The stack is lightweight, easy to containerize, and integrates smoothly with RESTful APIs provided by the backend.

## Consequences

- The team will need to set up routing, state management, and advanced features (e.g., authentication, code splitting) manually or with additional libraries.
- For future SEO or SSR needs, migration to Next.js or similar frameworks may be considered.
- Maintain clear documentation and code standards to ensure maintainability as the codebase grows.
