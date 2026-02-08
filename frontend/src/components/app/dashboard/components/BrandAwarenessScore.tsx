import React from 'react'
import { BrandAwarenessScoreCurrentScore } from '@/components/app/dashboard/components/BrandAwarnessScoreCurrentScore'
import { BrandAwarenessScoreGaugeView } from '@/components/app/dashboard/components/BrandAwarenessScoreGaugeView'
import { BrandAwarenessScoreHistoricalView } from '@/components/app/dashboard/components/BrandAwarenessScoreHistoricalView'

export function BrandAwarenessScore() {

    return (
        /* Main Brand Awareness Score Section */
        <div className="grid grid-cols-12 md:grid-cols-12 gap-8 border-b pb-6 items-stretch">
            <div className="col-span-6 flex">
                <BrandAwarenessScoreCurrentScore/>
            </div>
            <div className="col-span-6 flex">
                <BrandAwarenessScoreGaugeView />
            </div>

            <div className="col-span-12">
                {/* Brand Score historic view */}
                <BrandAwarenessScoreHistoricalView/>
            </div>
        </div>

    );
}