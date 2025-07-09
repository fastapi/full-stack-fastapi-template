import React from "react"
import { Container, Heading, Text } from "@chakra-ui/react"
import { createFileRoute } from "@tanstack/react-router"

export const Route = createFileRoute("/_layout/traffic-analysis")({
  component: TrafficAnalysis,
})

function TrafficAnalysis() {
  return (
    <Container maxW="full">
      <Heading size="lg" pt={12}>交通数据分析</Heading>
      <Text mt={4}>这里是交通数据分析模块页面。</Text>
    </Container>
  )
} 