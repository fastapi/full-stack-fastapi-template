# DevOps Portfolio — FastAPI Template (Docker + Kubernetes + CI/CD + AWS)

![CI](https://github.com/AlfreMu/devops-portfolio-fastapi/actions/workflows/ci.yml/badge.svg)

Este repositorio es un **portfolio personal DevOps/Cloud**. El objetivo es demostrar prácticas modernas de:
- Docker
- Kubernetes (kind en local / k3s en AWS EC2 — **sin EKS**)
- CI/CD con GitHub Actions
- Deploy automático al mergear Pull Requests

> La aplicación se utiliza como base open-source. El foco principal es infraestructura, automatización y despliegue.

## Qué vas a encontrar acá
- `docs/`: arquitectura, decisiones técnicas y guías de ejecución
- `k8s/portfolio/`: manifiestos Kubernetes creados como parte del portfolio
- `.github/workflows/`: pipelines del portfolio (CI y CD)

## Arquitectura (resumen)
- **Local (Docker):** ejecución reproducible con Docker/Compose
- **Local (Kubernetes):** cluster kind + manifests del portfolio
- **AWS:** instancia EC2 corriendo k3s + Nginx Ingress Controller
- **CI/CD:** GitHub Actions:
  - CI en Pull Requests
  - CD al mergear a `main`

## Cómo ejecutarlo
- Local con Docker: ver `docs/runbooks/local-docker.md`
- Kubernetes local (kind): ver `docs/runbooks/kind.md`
- AWS (EC2 + k3s): ver `docs/runbooks/aws-k3s.md`

## Skills DevOps demostradas
- Containerización y buenas prácticas Docker
- Deploy y troubleshooting en Kubernetes
- Automatización CI/CD con GitHub Actions
- Deploy automático a infraestructura en AWS (sin EKS)
- Documentación técnica orientada a entrevistas

## Roadmap
- [X] Phase 1: Docker baseline
- [X] Phase 2: Kubernetes local (kind)
- [ ] Phase 3: CI/CD
- [ ] Phase 4: AWS EC2 + k3s deploy

---

📌 Autor: AlfreMu
