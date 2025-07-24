# FastAPI Project - Frontend (Next.js)

The frontend is built with [Next.js 15](https://nextjs.org/), [React](https://reactjs.org/), [TypeScript](https://www.typescriptlang.org/), [TanStack Query](https://tanstack.com/query), [Tailwind CSS](https://tailwindcss.com/), and [shadcn/ui](https://ui.shadcn.com/).

## Frontend development

Before you begin, ensure that you have either the Node Version Manager (nvm) or Fast Node Manager (fnm) installed on your system.

* To install fnm follow the [official fnm guide](https://github.com/Schniz/fnm#installation). If you prefer nvm, you can install it using the [official nvm guide](https://github.com/nvm-sh/nvm#installing-and-updating).

* After installing either nvm or fnm, proceed to the `frontend-nextjs` directory:

```bash
cd frontend-nextjs
```
* If the Node.js version specified in the `.nvmrc` file isn't installed on your system, you can install it using the appropriate command:

```bash
# If using fnm
fnm install

# If using nvm
nvm install
```

* Once the installation is complete, switch to the installed version:

```bash
# If using fnm
fnm use

# If using nvm
nvm use
```

* Within the `frontend-nextjs` directory, install the necessary NPM packages:

```bash
npm install
```

* And start the live server with the following `npm` script:

```bash
npm run dev
```

* Then open your browser at http://localhost:3000/.

Notice that this live server is not running inside Docker, it's for local development, and that is the recommended workflow. Once you are happy with your frontend, you can build the frontend Docker image and start it, to test it in a production-like environment. But building the image at every change will not be as productive as running the local development server with live reload.

Check the file `package.json` to see other available options.

### Technology Stack

This Next.js frontend uses:

- **Next.js 15** with App Router for the React framework
- **Tailwind CSS v4** for styling with modern CSS features
- **shadcn/ui** for beautiful, accessible UI components
- **Lucide React** for consistent iconography
- **TanStack Query** for server state management
- **TypeScript** for type safety
- **Generated API Client** for backend integration

### Removing the frontend

If you are developing an API-only app and want to remove the frontend, you can do it easily:

* Remove the `./frontend-nextjs` directory.

* In the `docker-compose.yml` file, remove the whole service / section `frontend-nextjs`.

* In the `docker-compose.override.yml` file, remove the whole service / section `frontend-nextjs`.

Done, you have a frontend-less (api-only) app. 🤓

---

If you want, you can also remove the `FRONTEND` environment variables from:

* `.env`
* `./scripts/*.sh`

But it would be only to clean them up, leaving them won't really have any effect either way.

## Generate Client

### Automatically

* Activate the backend virtual environment.
* From the top level project directory, run the script:

```bash
./scripts/generate-client.sh
```

* Commit the changes.

### Manually

* Start the Docker Compose stack.

* Download the OpenAPI JSON file from `http://localhost/api/v1/openapi.json` and copy it to a new file `openapi.json` at the root of the `frontend-nextjs` directory.

* To generate the frontend client, run:

```bash
npm run generate-client
```

* Commit the changes.

## Features

This Next.js frontend includes:

- **Authentication**: JWT-based authentication with login/logout functionality
- **Dashboard**: Modern dashboard with sidebar navigation
- **User Management**: User profile and settings management
- **Responsive Design**: Mobile-first responsive design with dark mode support
- **Type Safety**: Full TypeScript integration with generated API types
- **Modern UI**: Beautiful components built with shadcn/ui and Tailwind CSS

## Project Structure

```
frontend-nextjs/
├── app/                    # Next.js App Router pages
├── components/             # Reusable React components
│   └── ui/                # shadcn/ui components
├── lib/                   # Utility functions and configurations
├── hooks/                 # Custom React hooks
├── client/                # Generated API client
├── public/                # Static assets
└── styles/                # Global styles and Tailwind config
```

## Development

### Adding New Components

To add new shadcn/ui components:

```bash
npx shadcn@latest add [component-name]
```

### Building for Production

```bash
npm run build
```

### Running Tests

```bash
npm run test
```

## Docker

The frontend is containerized and can be run with Docker:

```bash
# Build the image
docker build -t frontend-nextjs .

# Run the container
docker run -p 3000:3000 frontend-nextjs
```

Or use the provided Docker Compose setup from the project root.
