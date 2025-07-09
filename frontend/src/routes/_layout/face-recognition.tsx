import React from "react"
import { Container, Heading, Text } from "@chakra-ui/react"
import { createFileRoute } from "@tanstack/react-router"

export const Route = createFileRoute("/_layout/face-recognition")({
  component: FaceRecognition,
})

function FaceRecognition() {
  return (
    <Container maxW="full">
      <Heading size="lg" pt={12}>人脸识别</Heading>
      <Text mt={4}>这里是人脸识别模块页面。</Text>
    </Container>
  )
} 