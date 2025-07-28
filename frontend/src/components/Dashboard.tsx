'use client'

import { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Progress } from '@/components/ui/progress'
import { Checkbox } from '@/components/ui/checkbox'
import { apiService, type HumanValue, type ChatbotRecommendation, type BotCompletionStats, type LeadershipChallenge } from '@/lib/api'

interface MetricCardProps {
  value: string
  label: string
}

interface BotCardProps {
  name: string
  users: number
  completion: number
}


interface ValueItemProps {
  name: string
  count: number
  maxCount: number
}

const MetricCard = ({ value, label }: MetricCardProps) => (
  <Card className="text-center border-l-4 border-l-blue-500 hover:shadow-lg transition-all duration-300 hover:-translate-y-1">
    <CardContent className="pt-6">
      <div className="text-4xl font-bold text-slate-800 mb-2">{value}</div>
      <div className="text-sm text-slate-600 uppercase tracking-wide">{label}</div>
    </CardContent>
  </Card>
)

const BotCard = ({ name, users, completion }: BotCardProps) => (
  <Card className="hover:border-blue-500 transition-all duration-300 hover:-translate-y-1">
    <CardContent className="pt-6">
      <h3 className="text-xl font-bold text-slate-800 mb-4">{name}</h3>
      <Progress value={completion} className="mb-2" />
      <div className="text-right font-bold text-green-600 text-lg">
        {completion}% Average Script Completion
      </div>
    </CardContent>
  </Card>
)


const ValueItem = ({ name, count, maxCount }: ValueItemProps) => {
  const percentage = (count / maxCount) * 100

  return (
    <div className="flex items-center gap-4 mb-5">
      <span className="font-semibold text-slate-800 min-w-[120px] text-sm">{name}</span>
      <div className="flex-1 h-5 bg-slate-200 rounded-full overflow-hidden">
        <div
          className="h-full bg-gradient-to-r from-purple-600 to-purple-700 rounded-full transition-all duration-700"
          style={{ width: `${percentage}%` }}
        />
      </div>
      <span className="font-bold text-slate-800 min-w-[30px] text-center">{count}</span>
    </div>
  )
}

const RecommendationItem = ({ name, count, maxCount }: ValueItemProps) => {
  const percentage = (count / maxCount) * 100

  return (
    <div className="flex items-center gap-4 mb-5">
      <span className="font-semibold text-slate-800 min-w-[120px] text-sm">{name}</span>
      <div className="flex-1 h-5 bg-slate-200 rounded-full overflow-hidden">
        <div
          className="h-full bg-gradient-to-r from-orange-600 to-orange-700 rounded-full transition-all duration-700"
          style={{ width: `${percentage}%` }}
        />
      </div>
      <span className="font-bold text-slate-800 min-w-[30px] text-center">{count}</span>
    </div>
  )
}

interface ChallengeCardProps {
  challenge: LeadershipChallenge
}

const ChallengeCard = ({ challenge }: ChallengeCardProps) => (
  <Card className="hover:border-blue-500 transition-all duration-300 hover:-translate-y-1 hover:shadow-lg h-fit">
    <CardContent className="pt-6">
      <div className="flex justify-between items-start gap-3 mb-4">
        <div className="flex flex-col gap-2 flex-1">
          <div className="bg-blue-500 text-white px-3 py-1 rounded-full text-xs font-semibold w-fit">
            [{challenge.category}]
          </div>
          <h3 className="text-lg font-bold text-slate-800 leading-tight">
            {challenge.challenge_name}
          </h3>
        </div>
        <div className="bg-red-500 text-white px-3 py-1 rounded-full text-xs font-bold flex-shrink-0">
          {challenge.count} conversations
        </div>
      </div>

      <div className="mt-4">
        <h5 className="text-slate-600 mb-3 font-semibold">What people are bringing to this challenge:</h5>
        <ul className="space-y-2">
          {challenge.summaries.map((summary, index) => (
            <li key={index} className="text-slate-700 text-sm leading-relaxed pl-4 relative">
              <span className="absolute left-0 top-2 w-1 h-1 bg-blue-500 rounded-full"></span>
              {summary}
            </li>
          ))}
        </ul>
      </div>
    </CardContent>
  </Card>
)

export default function Dashboard() {
  const [botFilters, setBotFilters] = useState({
    playerMindset: true,
    actionPlan: true,
    assessmentDebrief: true
  })

  // State for API data
  const [totalSessions, setTotalSessions] = useState<number>(0)
  const [activeUsers, setActiveUsers] = useState<number>(0)
  const [botCompletionStats, setBotCompletionStats] = useState<Record<string, BotCompletionStats>>({})
  const [humanValues, setHumanValues] = useState<HumanValue[]>([])
  const [chatbotRecommendations, setChatbotRecommendations] = useState<ChatbotRecommendation[]>([])
  const [leadershipChallenges, setLeadershipChallenges] = useState<LeadershipChallenge[]>([])
  const [loading, setLoading] = useState<boolean>(true)
  const [error, setError] = useState<string | null>(null)

  // Fetch data on component mount
  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true)
        setError(null)

        const [
          totalSessionsData,
          activeUsersData,
          botCompletionData,
          humanValuesData,
          recommendationsData,
          leadershipChallengesData
        ] = await Promise.all([
          apiService.getTotalSessions(),
          apiService.getActiveUsers(),
          apiService.getBotCompletion(),
          apiService.getTopHumanValues(5),
          apiService.getTopChatbotRecommendations(5),
          apiService.getTopLeadershipChallenges(6)
        ])

        setTotalSessions(totalSessionsData.total_sessions)
        setActiveUsers(activeUsersData.active_users)
        setBotCompletionStats(botCompletionData.bot_completion_stats)
        setHumanValues(humanValuesData.top_human_values)
        setChatbotRecommendations(recommendationsData.top_chatbot_recommendations)
        setLeadershipChallenges(leadershipChallengesData.top_leadership_challenges)
      } catch (err) {
        setError(err instanceof Error ? err.message : 'An error occurred while fetching data')
        console.error('Error fetching dashboard data:', err)
      } finally {
        setLoading(false)
      }
    }

    fetchData()
  }, [])

  // Calculate metrics from API data
  const averageCompletion = Object.keys(botCompletionStats).length > 0
    ? Math.round(
        Object.values(botCompletionStats).reduce((sum, bot) => sum + bot.completion_percentage, 0) /
        Object.keys(botCompletionStats).length * 100
      )
    : 0

  const avgSessionsPerUser = activeUsers > 0 ? (totalSessions / activeUsers).toFixed(1) : '0'

  const metrics = [
    { value: activeUsers.toString(), label: 'Active Users' },
    { value: totalSessions.toString(), label: 'Total Sessions' },
    { value: `${averageCompletion}%`, label: 'Average Script Completion' },
    { value: avgSessionsPerUser, label: 'Avg Sessions per User' }
  ]

  // Map bot names from API to display names
  const botNameMapping: Record<string, string> = {
    'player_mindset_en': 'Player Mindset Coach',
    'assessment_actionplan_en': 'Action Plan Coach',
    'assessment_debrief_en': 'Assessment Debrief'
  }

  const bots = Object.entries(botCompletionStats).map(([botKey, stats]) => ({
    name: botNameMapping[botKey] || botKey,
    users: 0, // This data is not available from the current API
    completion: Math.round(stats.completion_percentage * 100)
  }))

  const maxValueCount = humanValues.length > 0 ? Math.max(...humanValues.map(v => v.count)) : 1
  const maxRecommendationCount = chatbotRecommendations.length > 0 ? Math.max(...chatbotRecommendations.map(r => r.count)) : 1

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-indigo-500 via-purple-500 to-purple-700 p-5 flex items-center justify-center">
        <div className="bg-white rounded-3xl shadow-2xl p-8">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
            <p className="text-slate-600">Loading dashboard data...</p>
          </div>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-indigo-500 via-purple-500 to-purple-700 p-5 flex items-center justify-center">
        <div className="bg-white rounded-3xl shadow-2xl p-8">
          <div className="text-center">
            <div className="text-red-600 text-xl mb-4">Error Loading Dashboard</div>
            <p className="text-slate-600 mb-4">{error}</p>
            <button
              onClick={() => window.location.reload()}
              className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
            >
              Retry
            </button>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-500 via-purple-500 to-purple-700 p-5">
      <div className="max-w-7xl mx-auto bg-white rounded-3xl shadow-2xl overflow-hidden">
        {/* Header */}
        <div className="bg-gradient-to-r from-slate-800 to-blue-600 text-white p-8 text-center">
          <h1 className="text-4xl font-light mb-3">Leadership Development Analytics</h1>
          <p className="text-xl opacity-90">Insights from ConsciousInsights AI Coaching Sessions</p>
        </div>

        <div className="p-10">
          {/* Key Metrics */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8 mb-12">
            {metrics.map((metric, index) => (
              <MetricCard key={index} value={metric.value} label={metric.label} />
            ))}
          </div>

          {/* Bot Usage Section */}
          <div className="mb-12">
            <h2 className="text-3xl font-light text-slate-800 mb-8 border-b-4 border-blue-500 pb-3">
              Bot Usage & Script Completion
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {bots.map((bot, index) => (
                <BotCard key={index} name={bot.name} users={bot.users} completion={bot.completion} />
              ))}
            </div>
          </div>

          {/* Challenge Analysis Section */}
          <div className="mb-12">
            <h2 className="text-3xl font-light text-slate-800 mb-8 border-b-4 border-blue-500 pb-3">
              Leadership Challenges & Coaching Insights
            </h2>

            {/* Bot Filter */}
            <Card className="mb-8 bg-slate-50">
              <CardContent className="pt-6">
                <h4 className="mb-4 text-slate-800 font-semibold">Filter All Analytics by Coaching Bot:</h4>
                <div className="flex flex-wrap gap-6">
                  <div className="flex items-center space-x-2">
                    <Checkbox
                      id="playerMindset"
                      checked={botFilters.playerMindset}
                      onCheckedChange={(checked) =>
                        setBotFilters(prev => ({ ...prev, playerMindset: checked as boolean }))
                      }
                    />
                    <label htmlFor="playerMindset" className="cursor-pointer">Player Mindset Coach</label>
                  </div>
                  <div className="flex items-center space-x-2">
                    <Checkbox
                      id="actionPlan"
                      checked={botFilters.actionPlan}
                      onCheckedChange={(checked) =>
                        setBotFilters(prev => ({ ...prev, actionPlan: checked as boolean }))
                      }
                    />
                    <label htmlFor="actionPlan" className="cursor-pointer">Action Plan Coach</label>
                  </div>
                  <div className="flex items-center space-x-2">
                    <Checkbox
                      id="assessmentDebrief"
                      checked={botFilters.assessmentDebrief}
                      onCheckedChange={(checked) =>
                        setBotFilters(prev => ({ ...prev, assessmentDebrief: checked as boolean }))
                      }
                    />
                    <label htmlFor="assessmentDebrief" className="cursor-pointer">Assessment Debrief</label>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Top 5 Leadership Challenges */}
            <h3 className="text-2xl font-semibold text-slate-800 mb-6">Top 5 Leadership Challenges</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-10">
              {leadershipChallenges.map((challenge, index) => (
                <ChallengeCard key={index} challenge={challenge} />
              ))}
            </div>

            {/* Values & Coaching Patterns */}
            <h3 className="text-2xl font-semibold text-slate-800 mb-6">Values & Coaching Patterns</h3>
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-10">
              {/* Human Values */}
              <Card className="bg-slate-50">
                <CardHeader>
                  <CardTitle className="text-center text-slate-800">Top Human Values</CardTitle>
                </CardHeader>
                <CardContent>
                  {humanValues.map((value, index) => (
                    <ValueItem
                      key={index}
                      name={value.value}
                      count={value.count}
                      maxCount={maxValueCount}
                    />
                  ))}
                </CardContent>
              </Card>

              {/* AI Coaching Areas */}
              <Card className="bg-slate-50">
                <CardHeader>
                  <CardTitle className="text-center text-slate-800">Top AI Coaching Areas</CardTitle>
                </CardHeader>
                <CardContent>
                  {chatbotRecommendations.map((recommendation, index) => (
                    <RecommendationItem
                      key={index}
                      name={recommendation.recommendation}
                      count={recommendation.count}
                      maxCount={maxRecommendationCount}
                    />
                  ))}
                </CardContent>
              </Card>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
