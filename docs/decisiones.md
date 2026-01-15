# Decisiones técnicas

## 0001 - App base: template open-source (código secundario)
Se utiliza una aplicación open-source existente como base. 

**El foco del repositorio es la infraestructura, automatización y despliegue (prácticas DevOps).**

## 0002 - Kubernetes: kind en local, k3s en AWS EC2 (sin EKS)
Se eligen alternativas livianas para mantener el alcance terminable y ejecutable, evitando complejidad innecesaria.

## 0003 - CI/CD con GitHub Actions
Se utiliza GitHub Actions para:
- CI en Pull Requests (checks de calidad)
- CD al mergear a main (deploy automático)
