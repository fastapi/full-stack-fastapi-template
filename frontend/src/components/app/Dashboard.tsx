// src/components/app/Dashboard.tsx
export default function Dashboard() {
  const stats = [
    { label: 'Total Users', value: '2,543', change: '+12%', color: 'blue' },
    { label: 'Active Projects', value: '127', change: '+8%', color: 'green' },
    { label: 'Revenue', value: '$45,231', change: '+23%', color: 'purple' },
    { label: 'Conversion Rate', value: '3.24%', change: '+5%', color: 'orange' },
  ]

  return (
    <div>
      <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-6">Dashboard</h1>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        {stats.map((stat, idx) => (
          <div key={idx} className="bg-white dark:bg-gray-800 p-6 rounded-lg border border-gray-200 dark:border-gray-700">
            <div className="text-sm text-gray-600 dark:text-gray-400 mb-1">{stat.label}</div>
            <div className="text-3xl font-bold text-gray-900 dark:text-white mb-2">{stat.value}</div>
            <div className="text-sm text-green-600 dark:text-green-400">{stat.change} from last month</div>
          </div>
        ))}
      </div>

      {/* Recent Activity */}
      <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
        <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-4">Recent Activity</h2>
        <div className="space-y-4">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="flex items-center space-x-4 p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
              <div className="w-10 h-10 bg-blue-100 dark:bg-blue-900 rounded-full flex items-center justify-center">
                <span className="text-blue-600 dark:text-blue-400 font-bold">U</span>
              </div>
              <div className="flex-1">
                <div className="text-sm font-medium text-gray-900 dark:text-white">User Activity {i}</div>
                <div className="text-xs text-gray-500 dark:text-gray-400">2 hours ago</div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}