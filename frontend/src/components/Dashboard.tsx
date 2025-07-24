'use client'

import { useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Progress } from '@/components/ui/progress'
import { Checkbox } from '@/components/ui/checkbox'

interface MetricCardProps {
  value: string
  label: string
}

interface BotCardProps {
  name: string
  users: number
  completion: number
}

interface ChallengeCardProps {
  category: string
  name: string
  count: number
  details: string[]
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
      <div className="flex justify-between mb-3">
        <span className="text-slate-600">Unique Users:</span>
        <span className="font-bold text-slate-800">{users}</span>
      </div>
      <Progress value={completion} className="mb-2" />
      <div className="text-right font-bold text-green-600 text-lg">
        {completion}% Average Script Completion
      </div>
    </CardContent>
  </Card>
)

const ChallengeCard = ({ category, name, count, details }: ChallengeCardProps) => (
  <Card className="hover:border-blue-500 transition-all duration-300 hover:-translate-y-1 hover:shadow-lg">
    <CardContent className="pt-6">
      <div className="flex justify-between items-start gap-3 mb-4">
        <div className="flex flex-col gap-2 flex-1">
          <div className="bg-blue-500 text-white px-3 py-1 rounded-full text-xs font-semibold w-fit">
            [{category}]
          </div>
          <h4 className="font-bold text-slate-800 text-lg leading-tight">{name}</h4>
        </div>
        <div className="bg-red-500 text-white px-3 py-1 rounded-full text-xs font-bold whitespace-nowrap">
          {count} conversations
        </div>
      </div>
      <div>
        <h5 className="text-slate-600 mb-3 font-semibold">What people are bringing to this challenge:</h5>
        <ul className="space-y-2">
          {details.map((detail, index) => (
            <li key={index} className="text-slate-700 text-sm leading-relaxed pl-4 relative">
              <span className="absolute left-0 top-1 text-blue-500 text-lg">•</span>
              {detail}
            </li>
          ))}
        </ul>
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

export default function Dashboard() {
  const [botFilters, setBotFilters] = useState({
    playerMindset: true,
    actionPlan: true,
    assessmentDebrief: true
  })

  const metrics = [
    { value: '191', label: 'Active Users' },
    { value: '365', label: 'Total Sessions' },
    { value: '72%', label: 'Average Script Completion' },
    { value: '2.2', label: 'Avg Sessions per User' }
  ]

  const bots = [
    { name: 'Player Mindset Coach', users: 100, completion: 65 },
    { name: 'Action Plan Coach', users: 127, completion: 78 },
    { name: 'Assessment Debrief', users: 138, completion: 82 }
  ]

  const challenges = [
    {
      category: 'Communication and Collaboration',
      name: 'Miscommunication / Lack of Clarity',
      count: 16,
      details: [
        'Unclear expectations from managers leading to repeated work and frustration',
        'Difficulty communicating complex technical concepts to non-technical stakeholders',
        'Inconsistent messaging across different teams causing confusion in projects',
        'Lack of clear communication channels for urgent vs. non-urgent matters',
        'Assumptions made in email communications that lead to misunderstandings'
      ]
    },
    {
      category: 'Task and Workload Management',
      name: 'Overload / Time Pressure',
      count: 16,
      details: [
        'Competing priorities from multiple stakeholders with no clear prioritization framework',
        'Unrealistic deadlines that compromise quality and increase stress levels',
        'Inability to say no to additional requests, leading to overcommitment',
        'Lack of time for strategic thinking due to constant firefighting',
        'Difficulty delegating tasks effectively to reduce personal workload'
      ]
    },
    {
      category: 'Communication and Collaboration',
      name: 'Cross-functional Misalignment',
      count: 7,
      details: [
        'Different departments working with conflicting goals and metrics',
        'Lack of visibility into other teams\' processes and timelines',
        'Stakeholders not understanding the impact of their decisions on other areas',
        'Insufficient collaboration tools for cross-functional project management'
      ]
    },
    {
      category: 'Task and Workload Management',
      name: 'Unclear Goals / Priorities',
      count: 5,
      details: [
        'Shifting priorities from leadership without clear communication about changes',
        'Lack of connection between individual tasks and organizational strategy',
        'Difficulty determining which projects should take precedence',
        'Vague objectives that make it hard to measure success',
        'Conflicting direction from different managers or stakeholders'
      ]
    },
    {
      category: 'Management and Leadership',
      name: 'Inconsistent or Absent Direction',
      count: 4,
      details: [
        'Managers who change direction frequently without explanation',
        'Lack of regular check-ins and guidance from supervisors',
        'Inconsistent feedback that makes it difficult to improve performance',
        'Absence of clear leadership during critical project phases'
      ]
    }
  ]

  const values = [
    { name: 'Responsibility', count: 22 },
    { name: 'Collaboration', count: 12 },
    { name: 'Accountability', count: 11 },
    { name: 'Honesty', count: 8 },
    { name: 'Proactivity', count: 6 }
  ]

  const recommendations = [
    { name: 'Reflect on Personal Contribution', count: 5 },
    { name: 'Focus on Controllable Actions', count: 3 },
    { name: 'Set Clear Expectations', count: 3 },
    { name: 'Proactive Planning', count: 2 },
    { name: 'Consider Alternative Approaches', count: 2 }
  ]

  const maxValueCount = Math.max(...values.map(v => v.count))
  const maxRecommendationCount = Math.max(...recommendations.map(r => r.count))

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

            {/* Top 5 Challenges */}
            <h3 className="text-2xl font-semibold text-slate-800 mb-6">Top 5 Leadership Challenges</h3>
            <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6 mb-12">
              {challenges.map((challenge, index) => (
                <ChallengeCard
                  key={index}
                  category={challenge.category}
                  name={challenge.name}
                  count={challenge.count}
                  details={challenge.details}
                />
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
                  {values.map((value, index) => (
                    <ValueItem
                      key={index}
                      name={value.name}
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
                  {recommendations.map((recommendation, index) => (
                    <RecommendationItem
                      key={index}
                      name={recommendation.name}
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
