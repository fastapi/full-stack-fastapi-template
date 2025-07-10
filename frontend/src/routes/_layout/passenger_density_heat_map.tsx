import React, { useEffect, useRef, useState } from "react"
import { Box, Container, Heading, Text, Flex, IconButton, VStack, Input } from "@chakra-ui/react"
import { createFileRoute } from "@tanstack/react-router"
import { FiArrowLeft, FiMaximize2, FiMinimize2 } from "react-icons/fi"
import { useNavigate } from "@tanstack/react-router"

export const Route = createFileRoute("/_layout/passenger_density_heat_map")({
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
  // 新增：分析状态提示
  const [analyzing, setAnalyzing] = useState(false)
  // 新增：日期时间选择器状态
  const [selectedDateTime, setSelectedDateTime] = useState("2013-09-12T01:14:17")
  const [selectedEndDateTime, setSelectedEndDateTime] = useState("2013-09-12T04:28:35")

  // 新增：将日期时间转换为UTC时间戳
  const convertDateTimeToUtc = (dateTimeStr: string) => {
    try {
      const date = new Date(dateTimeStr)
      const year = date.getFullYear()
      const month = String(date.getMonth() + 1).padStart(2, '0')
      const day = String(date.getDate()).padStart(2, '0')
      const hours = String(date.getHours()).padStart(2, '0')
      const minutes = String(date.getMinutes()).padStart(2, '0')
      const seconds = String(date.getSeconds()).padStart(2, '0')
      return `${year}${month}${day}${hours}${minutes}${seconds}`
    } catch (e) {
      console.error('日期转换失败:', e)
      return startUtc
    }
  }

  // 新增：处理开始日期时间变化
  const handleStartDateTimeChange = (value: string) => {
    setSelectedDateTime(value)
    const utcTimestamp = convertDateTimeToUtc(value)
    setStartUtc(utcTimestamp)
  }

  // 新增：处理结束日期时间变化
  const handleEndDateTimeChange = (value: string) => {
    setSelectedEndDateTime(value)
    const utcTimestamp = convertDateTimeToUtc(value)
    setEndUtc(utcTimestamp)
  }

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
          "radius": 30,
          "visible": true,
          "opacity": 0.6
        })
        map.addOverlay(heatmapOverlay)
        heatmapOverlayRef.current = heatmapOverlay
        // 初始渲染示例数据
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
            <Heading size="lg" color="white">上客点密度分析</Heading>
            <Text color="gray.300" fontSize="sm">基于DBSCAN聚类的热门上客点分析</Text>
          </VStack>
        </Flex>
        {/* 新增：起止时间戳输入框 */}
        <Flex gap={2} alignItems="center">
          <Text color="white">起始时间戳</Text>
          <Input
            type="datetime-local"
            value={selectedDateTime}
            onChange={(e) => handleStartDateTimeChange(e.target.value)}
            style={{ padding: 4, borderRadius: 4, border: '1px solid #ccc', width: 140 }}
          />
          <Text color="white">结束时间戳</Text>
          <Input
            type="datetime-local"
            value={selectedEndDateTime}
            onChange={(e) => handleEndDateTimeChange(e.target.value)}
            style={{ padding: 4, borderRadius: 4, border: '1px solid #ccc', width: 140 }}
          />
          {/* 新增：开始分析按钮 */}
          <button
            style={{ 
              padding: '6px 16px', 
              borderRadius: 4, 
              background: analyzing ? '#666' : '#3182ce', 
              color: 'white', 
              border: 'none', 
              cursor: analyzing ? 'not-allowed' : 'pointer',
              opacity: analyzing ? 0.7 : 1
            }}
            disabled={analyzing}
            onClick={async () => {
              setAnalyzing(true)
              try {
                const res = await fetch(`http://localhost:8000/api/v1/analysis/dbscan-clustering?start_utc=${startUtc}&eps=0.03&min_samples=3`)
                const data = await res.json()
                // 使用热门上客点数据生成热力图
                const hotSpots = data.hot_spots || []
                const points = hotSpots.map((spot: any) => ({
                  lng: parseFloat(spot.lng),
                  lat: parseFloat(spot.lat),
                  count: parseInt(spot.count)+40
                })).filter((p: any) => !isNaN(p.lng) && !isNaN(p.lat))
                console.log('热门上客点数据:', points)
                // 动态更新热力图
                if (window.BMap && window.BMapLib && heatmapOverlayRef.current) {
                  heatmapOverlayRef.current.setDataSet({ data: [], max: 100 })
                  heatmapOverlayRef.current.setDataSet({
                    data: points,
                    max: 100
                  })
                }
              } catch (e) {
                console.error('聚类分析失败:', e)
              } finally {
                setAnalyzing(false)
              }
            }}
          >
            {analyzing ? "分析中..." : "开始分析"}
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

      {/* 分析中提示 */}
      {analyzing && (
        <Box 
          position="absolute" 
          top="80px" 
          left="50%" 
          transform="translateX(-50%)" 
          zIndex={2000} 
          bg="blue.500" 
          color="white" 
          px={6} 
          py={3} 
          borderRadius="md" 
          boxShadow="lg"
        >
          正在分析，请稍候...
        </Box>
      )}

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