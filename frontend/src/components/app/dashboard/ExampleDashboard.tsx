import React, { useState } from 'react';
import {Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle} from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Button } from '@/components/ui/button';
import { Activity, DollarSign, Users, TrendingUp, ArrowUpRight, ArrowDownRight, TrendingDown, MoveRight, Calendar } from 'lucide-react';
import { BrandAwarenessScore } from '@/components/app/dashboard/components/BrandAwarenessScore'

export default function ExampleDashboard() {

    const stats = [
        {
            title: 'Total Revenue',
            value: '$45,231.89',
            change: '+20.1%',
            changeType: 'positive',
            icon: DollarSign,
            description: 'from last month'
        },
        {
            title: 'Active Users',
            value: '2,350',
            change: '+180',
            changeType: 'positive',
            icon: Users,
            description: 'new this week'
        },
        {
            title: 'Conversions',
            value: '12.5%',
            change: '-2.3%',
            changeType: 'negative',
            icon: TrendingUp,
            description: 'vs last period'
        },
        {
            title: 'Engagement',
            value: '3.2m',
            change: '+12.5%',
            changeType: 'positive',
            icon: Activity,
            description: 'total interactions'
        }
    ];

    const recentActivity = [
        { user: 'Emma Thompson', action: 'Completed purchase', value: '$299.00', time: '2m ago' },
        { user: 'James Wilson', action: 'New signup', value: 'Pro Plan', time: '5m ago' },
        { user: 'Sarah Chen', action: 'Completed purchase', value: '$149.00', time: '12m ago' },
        { user: 'Michael Brown', action: 'Upgrade account', value: 'Enterprise', time: '18m ago' },
        { user: 'Lisa Garcia', action: 'Completed purchase', value: '$99.00', time: '23m ago' }
    ];

    {/* brand awareness score */}
    const [currentScore, setCurrentScore] = useState(7.8);
    const [previousScore, setPreviousScore] = useState(7.2);
    const [timeRange, setTimeRange] = useState('1month');
    const [chartType, setChartType] = useState('line');
    const [customDateRange, setCustomDateRange] = useState({
        start: '',
        end: ''
    });
    const [showCustomDate, setShowCustomDate] = useState(false);
    const [historicalData, setHistoricalData] = useState([]);

    // Mock data generator based on time range
    const generateMockData = (range) => {
        const dataPoints = {
            '1month': 4,
            '1quarter': 13,
            '1year': 52,
            'ytd': 8
        };

        const points = dataPoints[range] || 4;
        const data = [];
        const today = new Date();

        for (let i = points - 1; i >= 0; i--) {
            const date = new Date(today);
            date.setDate(date.getDate() - (i * 7));

            const weekLabel = `Week ${points - i}`;
            const dateStr = `${date.getMonth() + 1}/${date.getDate()}`;

            // Generate score with some variance
            const baseScore = 6.5 + (points - i) * 0.15 + (Math.random() - 0.5) * 0.4;
            const score = Math.min(10, Math.max(0, baseScore));

            // Calculate growth rate
            const growthRate = i === points - 1
                ? 0
                : ((score - data[data.length - 1]?.score) / data[data.length - 1]?.score * 100) || 0;

            data.push({
                week: weekLabel,
                date: dateStr,
                score: parseFloat(score.toFixed(2)),
                growthRate: parseFloat(growthRate.toFixed(2))
            });
        }

        return data;
    };

    /*
    // Simulate API call
    useEffect(() => {
        const fetchData = async () => {
            // Simulate network delay
            await new Promise(resolve => setTimeout(resolve, 300));
            const data = generateMockData(timeRange);
            setHistoricalData(data);

            // Update current score from latest data
            if (data.length > 0) {
                setCurrentScore(data[data.length - 1].score);
                if (data.length > 1) {
                    setPreviousScore(data[data.length - 2].score);
                }
            }
        };

        fetchData();
    }, [timeRange]); s
     */

    // Calculate trend
    const getTrend = () => {
        const diff = currentScore - previousScore;
        if (Math.abs(diff) < 0.05) return 'flat';
        return diff > 0 ? 'up' : 'down';
    };

    const getTrendIcon = () => {
        const trend = getTrend();
        const iconClass = "h-6 w-6";

        switch(trend) {
            case 'up':
                return <TrendingUp className={`${iconClass} text-green-600`} />;
            case 'down':
                return <TrendingDown className={`${iconClass} text-red-600`} />;
            default:
                return <Minus className={`${iconClass} text-gray-600`} />;
        }
    };

    const getTrendColor = () => {
        const trend = getTrend();
        switch(trend) {
            case 'up': return 'text-green-600';
            case 'down': return 'text-red-600';
            default: return 'text-gray-600';
        }
    };

    // Gauge component
    const GaugeChart = ({ value, max = 10 }) => {
        const percentage = (value / max) * 100;
        const rotation = (percentage / 100) * 180 - 90;

        // Calculate color based on value (green gradient)
        const getColor = (val) => {
            const ratio = val / max;
            if (ratio < 0.3) return '#ef4444'; // red
            if (ratio < 0.5) return '#f59e0b'; // orange
            if (ratio < 0.7) return '#eab308'; // yellow
            if (ratio < 0.85) return '#84cc16'; // light green
            return '#22c55e'; // green
        };

        return (
            <div className="relative w-64 h-32 mx-auto">
                <svg viewBox="0 0 200 100" className="w-full h-full">
                    {/* Background arc */}
                    <path
                        d="M 20 90 A 80 80 0 0 1 180 90"
                        fill="none"
                        stroke="#e5e7eb"
                        strokeWidth="20"
                        strokeLinecap="round"
                    />

                    {/* Gradient definition */}
                    <defs>
                        <linearGradient id="gaugeGradient" x1="0%" y1="0%" x2="100%" y2="0%">
                            <stop offset="0%" stopColor="#ef4444" />
                            <stop offset="25%" stopColor="#f59e0b" />
                            <stop offset="50%" stopColor="#eab308" />
                            <stop offset="75%" stopColor="#84cc16" />
                            <stop offset="100%" stopColor="#22c55e" />
                        </linearGradient>
                    </defs>

                    {/* Colored arc */}
                    <path
                        d="M 20 90 A 80 80 0 0 1 180 90"
                        fill="none"
                        stroke="url(#gaugeGradient)"
                        strokeWidth="20"
                        strokeLinecap="round"
                        strokeDasharray={`${percentage * 2.51}, 1000`}
                    />

                    {/* Indicator needle */}
                    <line
                        x1="100"
                        y1="90"
                        x2="100"
                        y2="30"
                        stroke={getColor(value)}
                        strokeWidth="3"
                        strokeLinecap="round"
                        transform={`rotate(${rotation} 100 90)`}
                    />

                    {/* Center circle */}
                    <circle cx="100" cy="90" r="8" fill={getColor(value)} />

                    {/* Scale markers */}
                    {[0, 2, 4, 6, 8, 10].map((num) => {
                        const angle = (num / max) * 180 - 90;
                        const rad = (angle * Math.PI) / 180;
                        const x = 100 + 75 * Math.cos(rad);
                        const y = 90 + 75 * Math.sin(rad);
                        return (
                            <text
                                key={num}
                                x={x}
                                y={y + 5}
                                textAnchor="middle"
                                className="text-xs fill-gray-600"
                            >
                                {num}
                            </text>
                        );
                    })}
                </svg>

                {/* Score display */}
                <div className="absolute bottom-0 left-1/2 transform -translate-x-1/2 text-center">
                    <div className="text-3xl font-bold" style={{ color: getColor(value) }}>
                        {value.toFixed(1)}
                    </div>
                    <div className="text-xs text-gray-500">Score</div>
                </div>
            </div>
        );
    };

    // Custom tooltip for charts
    const CustomTooltip = ({ active, payload }) => {
        if (active && payload && payload.length) {
            return (
                <div className="bg-white p-3 border border-gray-200 rounded-lg shadow-lg">
                    <p className="text-sm font-medium">{payload[0].payload.date}</p>
                    <p className="text-sm text-blue-600">
                        Score: <span className="font-bold">{payload[0].value}</span>
                    </p>
                    {payload[1] && (
                        <p className={`text-sm ${payload[1].value >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                            Growth: <span className="font-bold">{payload[1].value.toFixed(2)}%</span>
                        </p>
                    )}
                </div>
            );
        }
        return null;
    };

    return (
        <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 p-8">
            <div className="max-w-7xl mx-auto space-y-8">
                {/* Header */}
                <div className="flex items-center justify-between">
                    <div>
                        <h1 className="text-4xl font-bold text-slate-900">Brand Performance Dashboard</h1>
                        <p className="text-slate-600 mt-2">Welcome back! Here's what's happening today.</p>
                    </div>
                    <div className="flex gap-3">
                        <Button variant="outline">Download Report</Button>
                        <Button>
                            <Activity className="mr-2 h-4 w-4"/>
                            View Analytics
                        </Button>
                    </div>
                </div>

                {/* Main Brand Awareness Score Section */}
                <div className="w-full mx-auto">
                    <Card className="shadow-lg">
                        <CardHeader>
                            <CardTitle className="text-2xl font-bold">Brand AI Awareness Score</CardTitle>
                            <CardDescription>Track and analyze your brand's AI awareness performance</CardDescription>
                            <div className="h-px w-full bg-slate-200 shadow-[0_4px_6px_-1px_rgba(0,0,0,0.1)]"></div>
                        </CardHeader>

                        <CardContent className="space-y-8">
                            <BrandAwarenessScore/>
                        </CardContent>
                    </Card>
                </div>
            </div>
        </div>
    );
}