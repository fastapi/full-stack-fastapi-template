import React from "react"
import { Container, Heading, Tabs, Text } from "@chakra-ui/react"
import { createFileRoute, useNavigate } from "@tanstack/react-router"
import PassengerCountChart from '../../components/Traffic_analysis/PassengerCountChart'
import VehicleTrajectory from '../../components/Traffic_analysis/VehicleTrajectory'
import PassengerDensityHeatMap from '../../components/Traffic_analysis/PassengerDensityHeatMap'

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
          <Tabs.Trigger value="pickup-density">上客点密度分析</Tabs.Trigger>
          <Tabs.Trigger value="vehicle-trajectory">车辆轨迹可视化</Tabs.Trigger>
          <Tabs.Trigger value="statistics">统计数据</Tabs.Trigger>
        </Tabs.List>
        <Tabs.Content value="pickup-density">
          <Container maxW="full" mt={4}>
            <PassengerDensityHeatMap />
          </Container>
        </Tabs.Content>
        <Tabs.Content value="vehicle-trajectory">
          <Container maxW="full" mt={4}>
            <VehicleTrajectory />
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