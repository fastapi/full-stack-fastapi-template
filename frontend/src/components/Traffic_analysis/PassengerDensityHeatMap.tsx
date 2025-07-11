import React, { useEffect, useRef, useState } from "react"
import { Box, Container, Heading, Text, Flex, VStack, HStack } from "@chakra-ui/react"
import { Field } from '../ui/field'
import { Button } from '../ui/button'

export default function PassengerDensityHeatMap() {
  const mapRef = useRef<HTMLDivElement>(null)
  const [startUtc, setStartUtc] = useState("20130912011417")
  const [endUtc, setEndUtc] = useState("20130912042835")
  // 保存热力图实例
  const heatmapOverlayRef = useRef<any>(null)
  const mapInstanceRef = useRef<any>(null)
  // 分析状态提示
  const [analyzing, setAnalyzing] = useState(false)
  // 日期时间选择器状态
  const [selectedDateTime, setSelectedDateTime] = useState("2013-09-12T01:14:17")
  const [selectedEndDateTime, setSelectedEndDateTime] = useState("2013-09-12T04:28:35")

  // 将日期时间转换为UTC时间戳
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

  // 处理开始日期时间变化
  const handleStartDateTimeChange = (value: string) => {
    setSelectedDateTime(value)
    const utcTimestamp = convertDateTimeToUtc(value)
    setStartUtc(utcTimestamp)
  }

  // 处理结束日期时间变化
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

  const handleAnalyze = async () => {
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
  }

  return (
    <Container maxW="full">
      <Heading size="md" mb={4}>上客点密度分析</Heading>
      
      {/* 查询条件 */}
      <VStack gap={4} align="stretch" mb={6}>
        <HStack gap={4}>
          <Field label="起始时间">
            <input
              type="datetime-local"
              value={selectedDateTime}
              onChange={(e) => handleStartDateTimeChange(e.target.value)}
              style={{ 
                height: 32, 
                borderRadius: 4, 
                border: '1px solid #ccc', 
                padding: '0 8px',
                width: 200
              }}
            />
          </Field>
          
          <Field label="结束时间">
            <input
              type="datetime-local"
              value={selectedEndDateTime}
              onChange={(e) => handleEndDateTimeChange(e.target.value)}
              style={{ 
                height: 32, 
                borderRadius: 4, 
                border: '1px solid #ccc', 
                padding: '0 8px',
                width: 200
              }}
            />
          </Field>
        </HStack>
        
        {/* 分析参数说明 */}
        <Box border="1px solid" borderColor="gray.200" borderRadius="md" p={4}>
          <Text fontWeight="bold" mb={3}>分析参数</Text>
          <Text fontSize="sm" color="gray.600">
            使用DBSCAN聚类算法分析热门上客点，eps=0.03，min_samples=3
          </Text>
        </Box>
        
        <Button
          colorScheme="blue"
          onClick={handleAnalyze}
          loading={analyzing}
          loadingText="分析中..."
        >
          开始分析
        </Button>
      </VStack>

      {/* 地图容器 */}
      <Box 
        ref={mapRef}
        w="100%" 
        h="500px" 
        border="1px solid" 
        borderColor="gray.300" 
        borderRadius="md"
        mb={4}
      />

      {/* 热力图说明 */}
      <Box
        bg="blue.50"
        p={4}
        borderRadius="md"
        border="1px solid"
        borderColor="blue.200"
      >
        <Text fontWeight="bold" mb={2}>热力图说明</Text>
        <Text fontSize="sm" color="blue.700">
          <strong>红色区域：</strong>交通流量密集，乘客上下车频繁<br/>
          <strong>黄色区域：</strong>交通流量中等，有一定乘客活动<br/>
          <strong>绿色区域：</strong>交通流量较少，乘客活动稀疏
        </Text>
      </Box>
    </Container>
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