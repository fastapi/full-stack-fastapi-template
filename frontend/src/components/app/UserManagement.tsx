import { tableClasses } from "@/components/app/dashboard/components/tableTheme"

// src/components/app/UserManagement.tsx
export default function UserManagement() {
  const users = [
    {
      name: "John Doe",
      email: "john@example.com",
      role: "Admin",
      status: "Active",
    },
    {
      name: "Jane Smith",
      email: "jane@example.com",
      role: "Member",
      status: "Active",
    },
    {
      name: "Bob Wilson",
      email: "bob@example.com",
      role: "Member",
      status: "Inactive",
    },
    {
      name: "Alice Brown",
      email: "alice@example.com",
      role: "Manager",
      status: "Active",
    },
  ]

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold text-slate-900 dark:text-white">
          User Management
        </h1>
        <button
          type="button"
          className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition"
        >
          Add User
        </button>
      </div>

      <div className={tableClasses.wrapper}>
        <table className={tableClasses.table}>
          <thead className={tableClasses.headerRow}>
            <tr>
              <th className={`${tableClasses.head} px-6 py-3 text-left`}>
                Name
              </th>
              <th className={`${tableClasses.head} px-6 py-3 text-left`}>
                Email
              </th>
              <th className={`${tableClasses.head} px-6 py-3 text-left`}>
                Role
              </th>
              <th className={`${tableClasses.head} px-6 py-3 text-left`}>
                Status
              </th>
              <th className={`${tableClasses.head} px-6 py-3 text-left`}>
                Actions
              </th>
            </tr>
          </thead>
          <tbody>
            {users.map((user, idx) => (
              <tr key={idx} className={tableClasses.row}>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="flex items-center">
                    <div className="w-10 h-10 bg-gradient-to-br from-blue-600 to-sky-500 rounded-full flex items-center justify-center text-white font-bold mr-3">
                      {user.name.charAt(0)}
                    </div>
                    <div className="text-sm font-medium text-slate-900">
                      {user.name}
                    </div>
                  </div>
                </td>
                <td
                  className={`px-6 py-4 whitespace-nowrap text-sm ${tableClasses.cellMuted}`}
                >
                  {user.email}
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span className="px-2 py-1 text-xs rounded-full bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200">
                    {user.role}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span
                    className={`px-2 py-1 text-xs rounded-full ${
                      user.status === "Active"
                        ? "bg-green-100 text-green-800"
                        : "bg-slate-100 text-slate-700"
                    }`}
                  >
                    {user.status}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm">
                  <button
                    type="button"
                    className="text-blue-600 hover:text-blue-800 mr-4"
                  >
                    Edit
                  </button>
                  <button
                    type="button"
                    className="text-red-600 hover:text-red-800"
                  >
                    Delete
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
