# Full Stack FastAPI Plantilla

<a href="https://github.com/fastapi/full-stack-fastapi-template/actions?query=workflow%3ATest" target="_blank"><img src="https://github.com/fastapi/full-stack-fastapi-template/workflows/Test/badge.svg" alt="Test"></a>
<a href="https://coverage-badge.samuelcolvin.workers.dev/redirect/fastapi/full-stack-fastapi-template" target="_blank"><img src="https://coverage-badge.samuelcolvin.workers.dev/fastapi/full-stack-fastapi-template.svg" alt="Coverage"></a>

## Pila de tecnología y características

- ⚡ [**FastAPI**](https://fastapi.tiangolo.com) para la API de backend de Python.
    - 🧰 [SQLModel](https://sqlmodel.tiangolo.com) para las interacciones de la base de datos SQL de Python (ORM).
    - 🔍 [Pydantic](https://docs.pydantic.dev),utilizado por FastAPI, para la validación de datos y la gestión de configuraciones.
    - 💾 [PostgreSQL](https://www.postgresql.org) como la base de datos SQL.
- 🚀 [React](https://react.dev) for the frontend.
    - 💃Usando TypeScript, ganchos, Vite y otras partes de una pila de frontend moderna.
    - 🎨 [Chakra UI](https://chakra-ui.com) para los componentes frontend.
    - 🤖Una cliente frontend generada automáticamente.
    - 🧪 [Playwright](https://playwright.dev) para pruebas de extremo a extremo.
    - 🦇 Soporte de modo oscuro.
- 🐋 [Docker Compose](https://www.docker.com) para desarrollo y producción.
- 🔒 Hashing de contraseña seguro de forma predeterminada.
- 🔑 JWT (JSON Web Token) autenticación.
- 📫 Recuperación de contraseña basada en correo electrónico.
- ✅ Pruebas con[Pytest](https://pytest.org).
- 📞 [Traefik](https://traefik.io) como proxy inverso / balanceador de carga.
- 🚢 Instrucciones de implementación mediante Docker Compose, incluido cómo configurar un proxy Traefik de interfaz para manejar certificados HTTPS automáticos.
- 🏭 CI (integración continua) y CD (implementación continua) basada en GitHub Actions.

### Iniciar sesión en el panel

[![API docs](img/login.png)](https://github.com/fastapi/full-stack-fastapi-template)

### Panel de control - Administrador

[![API docs](img/dashboard.png)](https://github.com/fastapi/full-stack-fastapi-template)

### Panel de control: crear usuario

[![API docs](img/dashboard-create.png)](https://github.com/fastapi/full-stack-fastapi-template)

### Panel de control - Artículos

[![API docs](img/dashboard-items.png)](https://github.com/fastapi/full-stack-fastapi-template)

### Panel de control: configuración de usuario

[![API docs](img/dashboard-user-settings.png)](https://github.com/fastapi/full-stack-fastapi-template)

### Panel de control: modo oscuro

[![API docs](img/dashboard-dark.png)](https://github.com/fastapi/full-stack-fastapi-template)

### Documentación API interactiva

[![API docs](img/docs.png)](https://github.com/fastapi/full-stack-fastapi-template)

## Cómo usarlo


Puedes **simplemente bifurcar o clonar** este repositorio y usarlo tal como está.

✨ simplemente funciona. ✨

### Cómo utilizar un repositorio privado

Si quieres tener un repositorio privado, GitHub no te permitirá simplemente bifurcarlo ya que no permite cambiar la visibilidad de las bifurcaciones.

Pero puedes hacer lo siguiente:

- Crea un nuevo repositorio de GitHub, por ejemplo
`my-full-stack`.
- Clona este repositorio manualmente, establece el nombre con el nombre del proyecto que quieres usar, por ejemplo
`my-full-stack`:

```bash
git clone git@github.com:fastapi/full-stack-fastapi-template.git my-full-stack
```

- Ingresa al nuevo directorio:


```bash
cd my-full-stack
```


- Establezca el nuevo origen en su nuevo repositorio, cópielo desde la interfaz de GitHub, por ejemplo

```bash
git remote set-url origin git@github.com:octocat/my-full-stack.git
```

- Agregue este repositorio como otro "remoto" para permitirle recibir actualizaciones más tarde:

```bash
git remote add upstream git@github.com:fastapi/full-stack-fastapi-template.git
```

- Envía el código a tu nuevo repositorio:

```bash
git push -u origin master
```

### Actualización de la plantilla original

Después de clonar el repositorio y realizar los cambios, es posible que desee obtener los últimos cambios de esta plantilla original.

- Asegúrate de haber agregado el repositorio original como remoto, puedes comprobarlo con:

```bash
git remote -v

origin    git@github.com:octocat/my-full-stack.git (fetch)
origin    git@github.com:octocat/my-full-stack.git (push)
upstream    git@github.com:fastapi/full-stack-fastapi-template.git (fetch)
upstream    git@github.com:fastapi/full-stack-fastapi-template.git (push)
```

- Extraer los últimos cambios sin fusionarlos:

```bash
git pull --no-commit upstream master
```

Esto descargará los últimos cambios de esta plantilla sin confirmarlos, de modo que puedas comprobar que todo esté correcto antes de confirmarlos.

- Si hay conflictos, resuélvelos en tu editor.

- Una vez que hayas terminado, confirma los cambios:

```bash
git merge --continue
```

### Configurar
Luego, puede actualizar las configuraciones en los archivos `.env` para personalizarlas.

Antes de implementarlo, asegúrese de cambiar al menos los valores de:

- `SECRET_KEY`
- `FIRST_SUPERUSER_PASSWORD`
- `POSTGRES_PASSWORD`

Puedes (y debes) pasarlos como variables de entorno desde secretos.

Lea el [deployment.md](./deployment.md) documentos para más detalles.

### Generar Secret Keys

Algunas variables de entorno del archivo `.env` tienen el valor predeterminado `changethis`.

Debes cambiarlas con una clave secreta. Para generarlas, puedes ejecutar el siguiente comando:

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

Copia el contenido y úsalo como contraseña o clave secreta. Ejecútalo de nuevo para generar otra clave segura

## Cómo usarlo - Alternativa con fotocopiadora


Este repositorio también admite la generación de un nuevo proyecto utilizando [Copier](https://copier.readthedocs.io).

Copiará todos los archivos, le hará preguntas de configuración y actualizará los archivos `.env` con sus respuestas

### Instalar copiadora

Puedes instalar Copier con:

```bash
pip install copier
```

O mejor, si tienes[`pipx`](https://pipx.pypa.io/), Puedes ejecutarlo con:

```bash
pipx install copier
```


**Nota**: Si tienes `pipx`, la instalación de Copier es opcional, puedes ejecutarlo directamente

### Generar un proyecto con Copier

Elige un nombre para el directorio de tu nuevo proyecto; lo usarás a continuación. Por ejemplo:, `my-awesome-project`.


Vaya al directorio que será el padre de su proyecto y ejecute el comando con el nombre de su proyecto:

```bash
copier copy https://github.com/fastapi/full-stack-fastapi-template my-awesome-project --trust
```


Si tienes `pipx` y no instalaste `copier`, puedes ejecutarlo directamente:

```bash
pipx run copier copy https://github.com/fastapi/full-stack-fastapi-template my-awesome-project --trust
```

**Nota** la opción `--trust` es necesaria para poder ejecutar un [post-creation script](https://github.com/fastapi/full-stack-fastapi-template/blob/master/.copier/update_dotenv.py) que actualiza tu `.env` archivos.

### Variables de entrada

Copier te solicitará algunos datos que quizás quieras tener a mano antes de generar el proyecto.

Pero no te preocupes, puedes actualizarlos en los archivos `.env` posteriormente.

Las variables de entrada, con sus valores predeterminados (algunos generados automáticamente), son:

- `project_name`: (predeterminado: `"FastAPI Project"`) El nombre del proyecto, mostrado a los usuarios de la API (en .env).

- `stack_name`: (predeterminado: `"fastapi-project"`) El nombre de la pila utilizada para las etiquetas de Docker Compose y el nombre del proyecto (sin espacios ni puntos) (en .env).

- `secret_key`: (predeterminado: `"changethis"`) La clave secreta del proyecto, utilizada por seguridad, almacenada en .env. Puedes generarla con el método anterior. - `first_superuser`: (predeterminado: `"admin@example.com"`) El correo electrónico del primer superusuario (en .env).
- `first_superuser_password`: (predeterminado: `"changethis"`) La contraseña del primer superusuario (en .env).
- `smtp_host`: (predeterminado: "") El host del servidor SMTP para enviar correos electrónicos. Puede configurarlo posteriormente en .env.
- `smtp_user`: (predeterminado: "") El usuario del servidor SMTP para enviar correos electrónicos. Puede configurarlo posteriormente en .env.
- `smtp_password`: (predeterminado: "") La contraseña del servidor SMTP para enviar correos electrónicos. Puede configurarla posteriormente en .env.
- `emails_from_email`: (predeterminado: `"info@example.com"`) La cuenta de correo electrónico desde la que se envían los correos. Puede configurarla posteriormente en .env.
- `postgres_password`: (predeterminado: `"changethis"`) La contraseña de la base de datos PostgreSQL, almacenada en .env. Puede generar una con el método descrito anteriormente.
- `sentry_dsn`: (predeterminado: "") El DSN de Sentry. Si lo usa, puede configurarlo posteriormente en .env.

## Desarrollo Backend

Documentación backend: [backend/README.md](./backend/README.md).

## Desarrollo Frontend

Documentación frontend: [frontend/README.md](./frontend/README.md).

## Implementación

Documentación de implementación: [deployment.md](./deployment.md).

## Desarrollo

Documentación general de desarrollo: [development.md](./development.md).

Esto incluye el uso de Docker Compose, dominios locales personalizados, configuraciones `.env`, etc.

## Notas de la versión

Consulta el archivo [release-notes.md](./release-notes.md).

## Licencia

La plantilla FastAPI Full Stack se rige por los términos de la licencia MIT.
