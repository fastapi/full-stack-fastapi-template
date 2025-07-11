import React, { useEffect, useState } from "react"
import ReactECharts from 'echarts-for-react'
import { Text, Flex, Input } from "@chakra-ui/react"
import { Field } from '../ui/field'
import { RadioGroup, Radio } from '../ui/radio'
import { Button } from '../ui/button'

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
  const [mapLoaded, setMapLoaded] = useState(false)
  const [mapOption, setMapOption] = useState<any>(null)

  useEffect(() => {
    setLoading(true)
    fetch(`http://localhost:8000/api/v1/analysis/passenger-count-distribution?interval=${interval}`)
      .then(res => res.json())
      .then(data => setStatData(data))
      .catch(() => setStatData([]))
      .finally(() => setLoading(false))
  }, [interval])

  useEffect(() => {
    fetch('/370100_full.json')
      .then(res => res.json())
      .then(geoJson => {
        // 注册地图
        // @ts-ignore
        import('echarts').then(echarts => {
          echarts.registerMap('jinan', geoJson)
          setMapLoaded(true)
          setMapOption({
            title: { text: '济南市地图', left: 'center' },
            tooltip: { trigger: 'item' },
            visualMap: {
              min: 0,
              max: 100,
              left: 'left',
              top: 'bottom',
              text: ['高', '低'],
              inRange: { color: ['#e0ffff', '#006edd'] },
              show: true
            },
            series: [
              {
                name: '区域数据',
                type: 'map',
                map: 'jinan',
                roam: true,
                label: { show: true },
                data: [
                  { name: '历下区', value: 50 },
                  { name: '市中区', value: 80 },
                  { name: '槐荫区', value: 60 },
                  { name: '天桥区', value: 70 },
                  { name: '历城区', value: 90 },
                  { name: '长清区', value: 40 },
                  { name: '章丘区', value: 30 },
                  { name: '济阳区', value: 20 },
                  { name: '莱芜区', value: 10 },
                  { name: '钢城区', value: 15 },
                  { name: '平阴县', value: 25 },
                  { name: '商河县', value: 35 }
                ]
              }
            ]
          })
        })
      })
  }, [])

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
          <Input
            type="date"
            value={date}
            onChange={e => setDate(e.target.value)}
            height={8}
            borderRadius={4}
            border="1px solid #ccc"
            px={2}
            w={40}
          />
        </Field>
        <Field label="时间间隔">
          <RadioGroup value={interval} onValueChange={e => setInterval(e.value as '15min' | '1h')} direction="row">
            <Radio value="15min">15分钟</Radio>
            <Radio value="1h">1小时</Radio>
          </RadioGroup>
        </Field>
      </Flex>
      <Text mb={2} color="gray.500">下方为{interval === '15min' ? '15分钟' : '1小时'}乘客数量分布图：</Text>
      {loading ? (
        <Text mt={4}>加载中...</Text>
      ) : (
        <ReactECharts style={{height: 400}} option={statOption} notMerge={true} lazyUpdate={true} />
      )}
      {/* 新增济南市地图展示 */}
      <Text mt={8} mb={2} fontWeight="bold">济南市地图：</Text>
      {mapLoaded && mapOption ? (
        <ReactECharts style={{height: 500}} option={mapOption} notMerge={true} lazyUpdate={true} />
      ) : (
        <Text>地图加载中...</Text>
      )}
    </>
  )
} 