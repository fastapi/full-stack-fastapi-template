import React, { useEffect, useState } from "react"
import ReactECharts from 'echarts-for-react'
import { Text, Flex } from "@chakra-ui/react"
import { Field } from '../ui/field'
import { RadioGroup } from '../ui/radio'

function formatDate(date: Date) {
  const y = date.getFullYear()
  const m = String(date.getMonth() + 1).padStart(2, '0')
  const d = String(date.getDate()).padStart(2, '0')
  return `${y}-${m}-${d}`
}

export default function PassengerCountChart() {
  const [statData, setStatData] = useState<any[]>([])
  const [loading, setLoading] = useState(false)
  const [interval, setInterval] = useState<'15min' | '1h'>('15min')
  const [date, setDate] = useState(formatDate(new Date('2013-09-12')))

  useEffect(() => {
    setLoading(true)
    fetch(`http://localhost:8000/api/v1/analysis/passenger-count-distribution?interval=${interval}`)
      .then(res => res.json())
      .then(data => setStatData(data))
      .catch(() => setStatData([]))
      .finally(() => setLoading(false))
  }, [interval])

  const statOption = {
    title: { text: `${interval === '15min' ? '15分钟' : '1小时'}乘客数量分布`, left: 'center' },
    tooltip: { trigger: 'axis' },
    xAxis: {
      type: 'category',
      data: statData.map(item => {
        if (interval === '15min') {
          return item.interval_start.slice(8, 10) + ':' + item.interval_start.slice(10, 12)
        } else {
          return item.interval_start.slice(8, 10) + ':00'
        }
      }),
      name: '时间',
      axisLabel: { rotate: 45 }
    },
    yAxis: { type: 'value', name: '乘客数量' },
    series: [
      {
        data: statData.map(item => item.count),
        type: 'line',
        smooth: true,
        areaStyle: {},
        name: '乘客数'
      }
    ]
  }

  return (
    <>
      <Flex align="center" gap={4} mb={2}>
        <Field label="选择日期">
          <input
            type="date"
            value={date}
            onChange={e => setDate(e.target.value)}
            style={{ height: 32, borderRadius: 4, border: '1px solid #ccc', padding: '0 8px' }}
          />
        </Field>
        <Field label="时间间隔">
          <RadioGroup value={interval}>
            <label style={{marginRight: 12}}>
              <input type="radio" value="15min" checked={interval === '15min'} onChange={() => setInterval('15min')} /> 15分钟
            </label>
            <label>
              <input type="radio" value="1h" checked={interval === '1h'} onChange={() => setInterval('1h')} /> 1小时
            </label>
          </RadioGroup>
        </Field>
      </Flex>
      <Text mb={2} color="gray.500">下方为{interval === '15min' ? '15分钟' : '1小时'}乘客数量分布图：</Text>
      {loading ? (
        <Text mt={4}>加载中...</Text>
      ) : (
        <ReactECharts style={{height: 400}} option={statOption} notMerge={true} lazyUpdate={true} />
      )}
    </>
  )
} 