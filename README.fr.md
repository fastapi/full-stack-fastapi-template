# Modèle Full Stack FastAPI

<a href="https://github.com/fastapi/full-stack-fastapi-template/actions?query=workflow%3ATest" target="_blank"><img src="https://github.com/fastapi/full-stack-fastapi-template/workflows/Test/badge.svg" alt="Test"></a>
<a href="https://coverage-badge.samuelcolvin.workers.dev/redirect/fastapi/full-stack-fastapi-template" target="_blank"><img src="https://coverage-badge.samuelcolvin.workers.dev/fastapi/full-stack-fastapi-template.svg" alt="Coverage"></a>

## Technologies et fonctionnalités

- ⚡ [**FastAPI**](https://fastapi.tiangolo.com) pour l'API backend en Python.
  - 🧰 [SQLModel](https://sqlmodel.tiangolo.com) pour les interactions avec la base de données SQL en Python (ORM).
  - 🔍 [Pydantic](https://docs.pydantic.dev)utilisé par FastAPI, pour la validation des données et la gestion des paramètres.
  - 💾 [PostgreSQL](https://www.postgresql.org) comme base de données SQL.
- 🚀 [React](https://react.dev) pour le frontend.
  - 💃 Utilisation de TypeScript, hooks, Vite et d'autres outils modernes pour le frontend.
  - 🎨 [Chakra UI](https://chakra-ui.com) pour les composants frontend.
  - 🤖 Un client frontend généré automatiquement.
  - 🧪 [Playwright](https://playwright.dev) pour les tests End-to-End.
  - 🦇 Prise en charge du mode sombre.
- 🐋 [Docker Compose](https://www.docker.com) pour le développement et la production.
- 🔒 Hachage sécurisé des mots de passe par défaut.
- 🔑 Authentification par JWT (JSON Web Token).
- 📫 Récupération de mot de passe par email.
- ✅ Tests avec [Pytest](https://pytest.org).
- 📞 [Traefik](https://traefik.io) comme reverse proxy / load balancer.
- � Instructions de déploiement avec Docker Compose, incluant la configuration d'un proxy Traefik pour gérer les certificats HTTPS automatiques.

- 🏭 CI (intégration continue) et CD (déploiement continu) basés sur GitHub Actions.

### Connexion au Tableau de Bord

[![API docs](img/login.png)](https://github.com/fastapi/full-stack-fastapi-template)

### DashboaTableau de Bord - Admin

[![API docs](img/dashboard.png)](https://github.com/fastapi/full-stack-fastapi-template)

### Tableau de Bord - Créer un Utilisateur

[![API docs](img/dashboard-create.png)](https://github.com/fastapi/full-stack-fastapi-template)

### Dashboard - Articles

[![API docs](img/dashboard-items.png)](https://github.com/fastapi/full-stack-fastapi-template)

### Tableau de Bord - Paramètres Utilisateur

[![API docs](img/dashboard-user-settings.png)](https://github.com/fastapi/full-stack-fastapi-template)

### Tableau de Bord - Mode Sombre

[![API docs](img/dashboard-dark.png)](https://github.com/fastapi/full-stack-fastapi-template)

### Documentation Interactive de l'API

[![API docs](img/docs.png)](https://github.com/fastapi/full-stack-fastapi-template)

## Comment l'Utiliser

You can **just fork or clone** this repository and use it as is.

✨ It just works. ✨

### Comment Utiliser un Dépôt Privé

Si vous souhaitez avoir un dépôt privé, GitHub ne vous permettra pas de le forker directement, car il n'autorise pas la modification de la visibilité des forks.

Mais vous pouvez procéder comme suit :

- Créez un nouveau dépôt GitHub, par exemple my-full-stack.

- ce dépôt manuellement, en définissant le nom du projet que vous souhaitez utiliser, par exemple my-full-stack :

```bash
git clone git@github.com:fastapi/full-stack-fastapi-template.git my-full-stack
```

- Entrez dans le nouveau répertoire :

```bash
cd my-full-stack
```

- Définissez la nouvelle origine vers votre nouveau dépôt (copiez l'URL depuis l'interface GitHub), par exemple :

```bash
git remote set-url origin git@github.com:octocat/my-full-stack.git
```

- Ajoutez ce dépôt comme un autre "remote" pour pouvoir récupérer les mises à jour ultérieurement :

```bash
git remote add upstream git@github.com:fastapi/full-stack-fastapi-template.git
```

-Poussez le code vers votre nouveau dépôt :

```bash
git push -u origin master
```

### Mettre à Jour depuis le Modèle Original

Après avoir cloné le dépôt, et après avoir effectué des modifications, vous pourriez vouloir récupérer les dernières modifications depuis ce modèle original.

- Assurez-vous d'avoir ajouté le dépôt original comme un "remote", vous pouvez le vérifier avec :

```bash
git remote -v

origin    git@github.com:octocat/my-full-stack.git (fetch)
origin    git@github.com:octocat/my-full-stack.git (push)
upstream    git@github.com:fastapi/full-stack-fastapi-template.git (fetch)
upstream    git@github.com:fastapi/full-stack-fastapi-template.git (push)
```

- Récupérez les dernières modifications sans les fusionner :

```bash
git pull --no-commit upstream master
```

Cela téléchargera les dernières modifications de ce modèle sans les committer, vous permettant ainsi de vérifier que tout est correct avant de valider.

- S'il y a des conflits, résolvez-les dans votre éditeur.

- Une fois terminé, validez les modifications :

```bash
git merge --continue
```

### Configuration

Vous pouvez ensuite mettre à jour les configurations dans les fichiers `.env` pour personnaliser vos paramètres.

Avant de le déployer, assurez-vous de changer au moins les valeurs pour :

- `SECRET_KEY`
- `FIRST_SUPERUSER_PASSWORD`
- `POSTGRES_PASSWORD`

Vous pouvez (et devriez) passer ces variables comme des variables d'environnement depuis des secrets.

Lisez la documentation [deployment.md](./deployment.md) pour plus de details.

### Générer des Clés Secrètes

Certaines variables d'environnement dans le fichier `.env` ont une valeur par défaut de `changethis`.

Vous devez les remplacer par une clé secrète. Pour générer des clés secrètes, vous pouvez exécuter la commande suivante :

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

Copiez le résultat et utilisez-le comme mot de passe / clé secrète. Exécutez cette commande à nouveau pour générer une autre clé sécurisée.

## Comment l'Utiliser - Alternative avec Copier

Ce dépôt prend également en charge la génération d'un nouveau projet en utilisant[Copier](https://copier.readthedocs.io).

Il copiera tous les fichiers, vous posera des questions de configuration et mettra à jour les fichiers`.env` avec vos réponses.

### Installer Copier

Vous pouvez installer Copier avec :

```bash
pip install copier
```

Ou mieux, si vous avez [`pipx`](https://pipx.pypa.io/), vous pouvez l'exécuter avec :

```bash
pipx install copier
```

**Remarque**: Si vous avez `pipx`, l'installation de Copier est optionnelle, vous pouvez l'exécuter directement.

### Générer un Projet avec Copier

Décidez d'un nom pour le répertoire de votre nouveau projet, vous l'utiliserez ci-dessous. Par exemple `my-awesome-project`.

Allez dans le répertoire parent de votre projet et exécutez la commande avec le nom de votre projet :

```bash
copier copy https://github.com/fastapi/full-stack-fastapi-template my-awesome-project --trust
```

Si vous avez`pipx` et que vous n'avez pas installé `copier`,vous pouvez l'exécuter directement :

```bash
pipx run copier copy https://github.com/fastapi/full-stack-fastapi-template my-awesome-project --trust
```

**Remarque** l'option trust `--trust` est nécessaire pour pouvoir exécuter un [script post-création](https://github.com/fastapi/full-stack-fastapi-template/blob/master/.copier/update_dotenv.py) qui met à jour vos fichiers `.env` .

### Variables d'Entrée

Copier vous demandera certaines données, que vous pourriez vouloir préparer avant de générer le projet.

Mais ne vous inquiétez pas, vous pouvez simplement mettre à jour n'importe laquelle de ces valeurs dans les fichiers `.env` par la suite.

Les variables d'entrée, avec leurs valeurs par défaut (certaines générées automatiquement) sont :

- `project_name`: (par défaut: `"FastAPI Project"`) Le nom du projet, affiché aux utilisateurs de l'API (dans .env).
- `stack_name`: (par défaut: `"fastapi-project"`) Le nom de la stack utilisée pour les labels Docker Compose et le nom du projet (pas d'espaces, pas de points) (dans .env).
- `secret_key`: (par défaut: `"changethis"`) La clé secrète du projet, utilisée pour la sécurité, stockée dans .env. Vous pouvez en générer une avec la méthode ci-dessus.
- `first_superuser`: (par défaut: `"admin@example.com"`) L'email du premier superutilisateur (dans .env).
- `first_superuser_password`: (par défaut: `"changethis"`) Le mot de passe du premier superutilisateur (dans .env).
- `smtp_host`: (par défaut: "") L'hôte du serveur SMTP pour envoyer des emails, vous pouvez le définir plus tard dans .env.
- `smtp_user`: (par défaut: "") L'utilisateur du serveur SMTP pour envoyer des emails, vous pouvez le définir plus tard dans .env.
- `smtp_password`: (par défaut: "") Le mot de passe du serveur SMTP pour envoyer des emails, vous pouvez le définir plus tard dans .env.
- `emails_from_email`: (par défaut: `"info@example.com"`) Le compte email à partir duquel envoyer des emails, vous pouvez le définir plus tard dans .env.
- `postgres_password`: (par défaut: `"changethis"`) Le mot de passe pour la base de données PostgreSQL, stocké dans .env. Vous pouvez en générer un avec la méthode ci-dessus.
- `sentry_dsn`: (par défaut: "") Le DSN pour Sentry, si vous l'utilisez, vous pouvez le définir plus tard dans .env.

## Développement Backend

Documentation backend: [backend/README.md](./backend/README.md).

## Développement Frontend

Documentation frontend: [frontend/README.md](./frontend/README.md).

## Déploiement

Documentation de déploiement: [deployment.md](./deployment.md).

## Développement

Documentation générale de développement: [development.md](./development.md).

Cela inclut l'utilisation de Docker Compose, des domaines locaux personnalisés, des configurations `.env`,etc.

## Notes de Version

Consultez le fichier [release-notes.md](./release-notes.md).

## License

Le Modèle Full Stack FastAPI est sous licence MIT. Consultez le fichier LICENSE pour plus de détails.
