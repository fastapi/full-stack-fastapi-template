import React, { useEffect, useRef, useState } from "react"
import { Box, Container, Heading, Text, Flex, IconButton, VStack } from "@chakra-ui/react"
import { createFileRoute } from "@tanstack/react-router"
import { FiArrowLeft, FiMaximize2, FiMinimize2 } from "react-icons/fi"
import { useNavigate } from "@tanstack/react-router"

export const Route = createFileRoute("/_layout/static-heatmap")({
  component: StaticHeatmap,
})

function StaticHeatmap() {
  const mapRef = useRef<HTMLDivElement>(null)
  const navigate = useNavigate()
  const [startUtc, setStartUtc] = useState("20130912011417")
  const [endUtc, setEndUtc] = useState("20130912042835")
  // 新增：保存热力图实例
  const heatmapOverlayRef = useRef<any>(null)
  const mapInstanceRef = useRef<any>(null)

  useEffect(() => {
    // 百度地图API初始化
    const initMap = () => {
      if (typeof window !== 'undefined' && window.BMap) {
        const map = new window.BMap.Map(mapRef.current)
        mapInstanceRef.current = map
        // 设置济南市中心坐标
        const jinanCenter = new window.BMap.Point(117.000923, 36.675807)
        map.centerAndZoom(jinanCenter, 12)
        // 启用滚轮缩放
        map.enableScrollWheelZoom(true)
        // 添加地图控件
        map.addControl(new window.BMap.NavigationControl())
        map.addControl(new window.BMap.ScaleControl())
        map.addControl(new window.BMap.OverviewMapControl())
        map.addControl(new window.BMap.MapTypeControl())
        // 创建热力图实例并保存
        const heatmapOverlay = new window.BMapLib.HeatmapOverlay({
          "radius": 20,
          "visible": true,
          "opacity": 0.6
        })
        map.addOverlay(heatmapOverlay)
        heatmapOverlayRef.current = heatmapOverlay
        // 初始渲染示例数据
        const heatmapData = [
          { lng: 117.04324, lat: 36.66936, count: 100 },
          { lng: 117.020923, lat: 36.685807, count: 80 },
          { lng: 116.980923, lat: 36.665807, count: 60 },
          { lng: 117.010923, lat: 36.695807, count: 90 },
          { lng: 116.990923, lat: 36.685807, count: 70 },
        ]
        heatmapOverlay.setDataSet({
          data: heatmapData,
          max: 100
        })
      }
    }
    // 动态加载百度地图API
    const loadBaiduMap = () => {
      if (typeof window !== 'undefined' && !window.BMap) {
        const script = document.createElement('script')
        script.src = `https://api.map.baidu.com/api?v=3.0&ak=TtyedSKP6umaE86VQqLbcE1sHS0f65A8&callback=initBaiduMap`
        script.async = true
        document.head.appendChild(script)
        window.initBaiduMap = () => {
          // 加载热力图库
          const heatmapScript = document.createElement('script')
          heatmapScript.src = 'https://api.map.baidu.com/library/Heatmap/2.0/src/Heatmap_min.js'
          heatmapScript.onload = initMap
          document.head.appendChild(heatmapScript)
        }
      } else {
        initMap()
      }
    }
    loadBaiduMap()
  }, [])

  return (
    <Box 
      w="100vw" 
      h="100vh" 
      bg="linear-gradient(135deg, #1a202c 0%, #2d3748 100%)"
      position="relative"
      overflow="hidden"
    >
      {/* 顶部导航栏 */}
      <Flex 
        position="absolute" 
        top={0} 
        left={0} 
        right={0} 
        zIndex={1000}
        bg="rgba(0,0,0,0.8)" 
        backdropFilter="blur(10px)"
        p={4}
        alignItems="center"
        justifyContent="space-between"
      >
        <Flex alignItems="center" gap={4}>
          <IconButton
            aria-label="返回"
            variant="ghost"
            color="white"
            _hover={{ bg: "rgba(255,255,255,0.1)" }}
            onClick={() => navigate({ to: "/traffic-analysis" })}
          />
          <VStack align="start">
            <Heading size="lg" color="white">济南市交通热力图</Heading>
            <Text color="gray.300" fontSize="sm">实时交通流量分析大屏</Text>
          </VStack>
        </Flex>
        {/* 新增：起止时间戳输入框 */}
        <Flex gap={2} alignItems="center">
          <Text color="white">起始时间戳</Text>
          <input
            style={{ padding: 4, borderRadius: 4, border: '1px solid #ccc', width: 140 }}
            placeholder="20130912011417"
            value={startUtc}
            onChange={e => setStartUtc(e.target.value)}
          />
          <Text color="white">结束时间戳</Text>
          <input
            style={{ padding: 4, borderRadius: 4, border: '1px solid #ccc', width: 140 }}
            placeholder="20130912042835"
            value={endUtc}
            onChange={e => setEndUtc(e.target.value)}
          />
          {/* 新增：开始分析按钮 */}
          <button
            style={{ padding: '6px 16px', borderRadius: 4, background: '#3182ce', color: 'white', border: 'none', cursor: 'pointer' }}
            onClick={async () => {
              try {
                const res = await fetch(`http://localhost:8000/api/v1/data_analysis/get-data?start_utc=${startUtc}&end_utc=${endUtc}`)
                const data = await res.json()
                // 提取ONLAT和ONLON，count统一为100
                const points = (Array.isArray(data) ? data : []).map((item: any) => ({
                  lng: parseFloat(item.ONLON),
                  lat: parseFloat(item.ONLAT),
                  count: 100
                })).filter(p => !isNaN(p.lng) && !isNaN(p.lat))
                console.log('热力图数据:', points)
                // 动态更新热力图
                if (window.BMap && window.BMapLib && heatmapOverlayRef.current) {
                  heatmapOverlayRef.current.setDataSet({
                    data: points,
                    max: 100
                  })
                }
              } catch (e) {
                // 暂不处理错误
              }
            }}
          >
            开始分析
          </button>
        </Flex>
        <Flex gap={2}>
          <IconButton
            aria-label="全屏"
            variant="ghost"
            color="white"
            _hover={{ bg: "rgba(255,255,255,0.1)" }}
          />
        </Flex>
      </Flex>

      {/* 地图容器 */}
      <Box 
        ref={mapRef}
        w="100%" 
        h="100%" 
        position="absolute"
        top={0}
        left={0}
      />

      {/* 右下角信息面板 */}
      <Box
        position="absolute"
        bottom={6}
        right={6}
        bg="rgba(0,0,0,0.8)"
        backdropFilter="blur(10px)"
        borderRadius="lg"
        p={4}
        color="white"
        minW="200px"
      >
        <Text fontWeight="bold" mb={2}>热力图说明</Text>
        <Text fontSize="sm" color="gray.300">
          红色区域：交通流量密集<br/>
          黄色区域：交通流量中等<br/>
          绿色区域：交通流量较少
        </Text>
      </Box>
    </Box>
  )
}

// 声明全局变量
declare global {
  interface Window {
    BMap: any
    BMapLib: any
    initBaiduMap: () => void
  }
} 