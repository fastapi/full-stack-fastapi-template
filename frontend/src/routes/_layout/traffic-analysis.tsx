import React from "react"
import { Container, Heading, Tabs, Text } from "@chakra-ui/react"
import { createFileRoute, useNavigate } from "@tanstack/react-router"
import PassengerCountChart from '../../components/Traffic_analysis/PassengerCountChart'

export const Route = createFileRoute("/_layout/traffic-analysis")({
  component: TrafficAnalysis,
})

function TrafficAnalysis() {
  const navigate = useNavigate()

  return (
    <Container maxW="full">
      <Heading size="lg" pt={12}>交通数据分析</Heading>
      <Tabs.Root defaultValue="pickup-density" variant="subtle" mt={6}>
        <Tabs.List>
          <Tabs.Trigger value="pickup-density" onClick={() => navigate({ to: "/passenger_density_heat_map" })}>上客点密度分析</Tabs.Trigger>
          <Tabs.Trigger value="vehicle-trajectory">车辆轨迹可视化</Tabs.Trigger>
          <Tabs.Trigger value="static-heatmap">静态热力图</Tabs.Trigger>
          <Tabs.Trigger value="statistics">统计数据</Tabs.Trigger>
        </Tabs.List>
        <Tabs.Content value="pickup-density">
          <Container maxW="full" mt={4}>
            <Text>这里是上客点密度分析模块。</Text>
            <Text mt={2}>可以显示各个上客点的密度分布情况。</Text>
          </Container>
        </Tabs.Content>
        <Tabs.Content value="vehicle-trajectory">
          <Container maxW="full" mt={4}>
            <Text>这里是车辆轨迹可视化模块。</Text>
            <Text mt={2}>可以展示车辆的实时轨迹和历史路径。</Text>
          </Container>
        </Tabs.Content>
        <Tabs.Content value="statistics">
          <Container maxW="full" mt={4}>
            <PassengerCountChart />
          </Container>
        </Tabs.Content>
      </Tabs.Root>
    </Container>
  )
} 