// src/components/app/Projects.tsx
export default function Projects() {
  const projects = [
    { name: "Website Redesign", status: "Active", progress: 75, team: 5 },
    { name: "Mobile App", status: "Active", progress: 45, team: 8 },
    { name: "API Integration", status: "Planning", progress: 20, team: 3 },
    { name: "Marketing Campaign", status: "Completed", progress: 100, team: 4 },
  ]

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
          Projects
        </h1>
        <button className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition">
          New Project
        </button>
      </div>

      <div className="grid gap-6">
        {projects.map((project, idx) => (
          <div
            key={idx}
            className="bg-white dark:bg-gray-800 p-6 rounded-lg border border-gray-200 dark:border-gray-700"
          >
            <div className="flex justify-between items-start mb-4">
              <div>
                <h3 className="text-xl font-bold text-gray-900 dark:text-white">
                  {project.name}
                </h3>
                <span
                  className={`inline-block mt-2 px-3 py-1 text-xs rounded-full ${
                    project.status === "Active"
                      ? "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200"
                      : project.status === "Planning"
                        ? "bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200"
                        : "bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200"
                  }`}
                >
                  {project.status}
                </span>
              </div>
              <div className="text-right">
                <div className="text-sm text-gray-600 dark:text-gray-400">
                  Team Size
                </div>
                <div className="text-2xl font-bold text-gray-900 dark:text-white">
                  {project.team}
                </div>
              </div>
            </div>

            <div>
              <div className="flex justify-between text-sm mb-2">
                <span className="text-gray-600 dark:text-gray-400">
                  Progress
                </span>
                <span className="font-semibold text-gray-900 dark:text-white">
                  {project.progress}%
                </span>
              </div>
              <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                <div
                  className="bg-blue-600 h-2 rounded-full"
                  style={{ width: `${project.progress}%` }}
                />
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
