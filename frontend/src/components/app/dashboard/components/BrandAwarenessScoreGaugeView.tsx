import React, { useState } from 'react';
import { Activity, DollarSign, Users, TrendingUp } from 'lucide-react';


export function BrandAwarenessScoreGaugeView() {
    /* brand awareness score */
    const [currentScore, setCurrentScore] = useState(7.8);

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
        /* Section 2: Gauge Chart */
        <div className="rounded-md bg-gradient-to-b p-6 border border-gray-200 h-full w-full">
            <h3 className="text-md font-semibold mb-4">Score Health</h3>
            <GaugeChart value={currentScore} max={10}/>
            <div className="flex justify-center gap-8 mt-4 text-xs">
                <div className="flex items-center gap-2">
                    <div className="w-4 h-4 rounded-full bg-red-500"></div>
                    <span>Poor (0-3)</span>
                </div>
                <div className="flex items-center gap-2">
                    <div className="w-4 h-4 rounded-full bg-yellow-500"></div>
                    <span>Fair (3-5)</span>
                </div>
                <div className="flex items-center gap-2">
                    <div className="w-4 h-4 rounded-full bg-lime-500"></div>
                    <span>Good (5-7)</span>
                </div>
                <div className="flex items-center gap-2">
                    <div className="w-4 h-4 rounded-full bg-green-500"></div>
                    <span>Excellent (7-10)</span>
                </div>
            </div>
        </div>
    );
}