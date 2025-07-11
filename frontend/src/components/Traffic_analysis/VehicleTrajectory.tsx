import React, { useState, useEffect, useRef } from "react"
import { Box, Container, Heading, Text, Flex, Input, Button, VStack, HStack } from "@chakra-ui/react"
import { Field } from '../ui/field'

export default function VehicleTrajectory() {
  const [commaddr, setCommaddr] = useState("")
  const [startUtc, setStartUtc] = useState("20130912010000")
  const [endUtc, setEndUtc] = useState("20130912020000")
  const [loading, setLoading] = useState(false)
  const [trajectoryData, setTrajectoryData] = useState<any[]>([])
  const mapRef = useRef<HTMLDivElement>(null)
  const mapInstanceRef = useRef<any>(null)
  const markersRef = useRef<any[]>([])
  const polylineRef = useRef<any>(null)
  
  // 矫正功能状态
  const [useCorrectedData, setUseCorrectedData] = useState(false)
  const [coordinateSystem, setCoordinateSystem] = useState("BD09")
  const [correctionInfo, setCorrectionInfo] = useState<any>(null)

  // 初始化百度地图
  useEffect(() => {
    const initMap = () => {
      if (typeof window !== 'undefined' && window.BMap && mapRef.current) {
        const map = new window.BMap.Map(mapRef.current)
        mapInstanceRef.current = map
        // 设置济南市中心坐标
        const jinanCenter = new window.BMap.Point(117.000923, 36.675807)
        map.centerAndZoom(jinanCenter, 12)
        map.enableScrollWheelZoom(true)
        map.addControl(new window.BMap.NavigationControl())
        map.addControl(new window.BMap.ScaleControl())
      }
    }

    const loadBaiduMap = () => {
      if (typeof window !== 'undefined' && !window.BMap) {
        const script = document.createElement('script')
        script.src = `https://api.map.baidu.com/api?v=3.0&ak=TtyedSKP6umaE86VQqLbcE1sHS0f65A8&callback=initBaiduMap`
        script.async = true
        document.head.appendChild(script)
        window.initBaiduMap = initMap
      } else {
        initMap()
      }
    }
    loadBaiduMap()
  }, [])

  // 清空地图上的所有覆盖物
  const clearMap = () => {
    if (!mapInstanceRef.current) return
    
    // 清除之前的轨迹线
    if (polylineRef.current) {
      mapInstanceRef.current.removeOverlay(polylineRef.current)
      polylineRef.current = null
    }
    
    // 清除之前的标记
    markersRef.current.forEach(marker => {
      mapInstanceRef.current.removeOverlay(marker)
    })
    markersRef.current = []
  }

  // 在地图上绘制轨迹
  const drawTrajectoryOnMap = (data: any[]) => {
    console.log('开始绘制轨迹，数据:', data)
    
    if (!mapInstanceRef.current) {
      console.error('地图实例未初始化')
      return
    }
    
    if (!window.BMap) {
      console.error('百度地图API未加载')
      return
    }

    // 清空地图
    clearMap()

    if (data.length === 0) {
      console.log('没有轨迹数据')
      return
    }

    // 检查数据格式
    console.log('第一条数据:', data[0])
    console.log('最后一条数据:', data[data.length - 1])

    // 创建轨迹点数组
    const points = data.map(record => {
      const point = new window.BMap.Point(record.lon, record.lat)
      console.log(`创建点: (${record.lon}, ${record.lat})`)
      return point
    })
    
    console.log('轨迹点数量:', points.length)
    
    // 绘制轨迹线
    const polyline = new window.BMap.Polyline(points, {
      strokeColor: "#FF0000",
      strokeWeight: 3,
      strokeOpacity: 0.8
    })
    mapInstanceRef.current.addOverlay(polyline)
    polylineRef.current = polyline
    console.log('轨迹线已添加')

    // 添加起点和终点标记
    if (data.length > 0) {
      const startPoint = new window.BMap.Point(data[0].lon, data[0].lat)
      const endPoint = new window.BMap.Point(data[data.length - 1].lon, data[data.length - 1].lat)
      
      // 使用百度地图内置的默认图标
      const startMarker = new window.BMap.Marker(startPoint)
      const endMarker = new window.BMap.Marker(endPoint)
      
      // 设置不同的图标样式来区分起点和终点
      startMarker.setLabel(new window.BMap.Label("起点", { offset: new window.BMap.Size(20, -10) }))
      endMarker.setLabel(new window.BMap.Label("终点", { offset: new window.BMap.Size(20, -10) }))
      
      mapInstanceRef.current.addOverlay(startMarker)
      mapInstanceRef.current.addOverlay(endMarker)
      markersRef.current.push(startMarker, endMarker)
      console.log('起点和终点标记已添加')

      // 转换速度单位：cm/s -> m/s -> km/h
      const startSpeedMs = (data[0].speed / 100).toFixed(1)
      const startSpeedKmh = (data[0].speed * 0.036).toFixed(1)
      const endSpeedMs = (data[data.length - 1].speed / 100).toFixed(1)
      const endSpeedKmh = (data[data.length - 1].speed * 0.036).toFixed(1)

      // 添加信息窗口
      const startInfo = new window.BMap.InfoWindow(`起点<br/>时间: ${data[0].utc}<br/>速度: ${startSpeedMs}m/s (${startSpeedKmh}km/h)`)
      const endInfo = new window.BMap.InfoWindow(`终点<br/>时间: ${data[data.length - 1].utc}<br/>速度: ${endSpeedMs}m/s (${endSpeedKmh}km/h)`)
      
      startMarker.addEventListener("click", () => {
        mapInstanceRef.current.openInfoWindow(startInfo, startPoint)
      })
      endMarker.addEventListener("click", () => {
        mapInstanceRef.current.openInfoWindow(endInfo, endPoint)
      })
    }

    // 调整地图视野以包含所有轨迹点
    mapInstanceRef.current.setViewport(points)
    console.log('地图视野已调整')
  }

  const fetchTrajectoryData = async () => {
    if (!commaddr.trim()) {
      alert("请输入车牌号")
      return
    }

    setLoading(true)
    // 清空地图和轨迹数据
    clearMap()
    setTrajectoryData([])
    setCorrectionInfo(null)
    
    try {
      console.log('开始查询轨迹数据...')
      
      // 根据是否使用矫正数据选择不同的API
      const apiUrl = useCorrectedData 
        ? `http://localhost:8000/api/v1/analysis/gps-records-corrected?commaddr=${commaddr}&start_utc=${startUtc}&end_utc=${endUtc}&coordinate_system=${coordinateSystem}`
        : `http://localhost:8000/api/v1/analysis/gps-records?commaddr=${commaddr}&start_utc=${startUtc}&end_utc=${endUtc}`
      
      const response = await fetch(apiUrl)
      const data = await response.json()
      
      console.log('API响应:', data)
      
      if (data.error) {
        alert(`查询失败: ${data.error}`)
        return
      }
      
      const records = data.records || []
      console.log('轨迹记录数量:', records.length)
      
      setTrajectoryData(records)
      
      // 保存矫正信息
      if (useCorrectedData && data.correction_info) {
        setCorrectionInfo(data.correction_info)
      }
      
      // 确保地图已初始化后再绘制轨迹
      if (mapInstanceRef.current && window.BMap) {
        // 延迟一点时间确保地图完全加载
        setTimeout(() => {
          drawTrajectoryOnMap(records)
        }, 100)
      } else {
        console.error('地图未初始化，无法绘制轨迹')
      }
    } catch (error) {
      console.error('获取轨迹数据失败:', error)
      alert('获取轨迹数据失败')
    } finally {
      setLoading(false)
    }
  }

  return (
    <Container maxW="full">
      <Heading size="md" mb={4}>车辆轨迹可视化</Heading>
      
      {/* 查询条件 */}
      <VStack gap={4} align="stretch" mb={6}>
        <Field label="车牌号">
          <Input
            value={commaddr}
            onChange={(e) => setCommaddr(e.target.value)}
            placeholder="请输入车牌号"
          />
        </Field>
        
        <HStack gap={4}>
          <Field label="起始时间">
            <Input
              value={startUtc}
              onChange={(e) => setStartUtc(e.target.value)}
              placeholder="YYYYMMDDHHMMSS"
            />
          </Field>
          <Field label="结束时间">
            <Input
              value={endUtc}
              onChange={(e) => setEndUtc(e.target.value)}
              placeholder="YYYYMMDDHHMMSS"
            />
          </Field>
        </HStack>
        
        {/* 坐标系转换选项 */}
        <Box border="1px solid" borderColor="gray.200" borderRadius="md" p={4}>
          <Text fontWeight="bold" mb={3}>坐标系转换</Text>
          
          <HStack gap={4}>
            <Field label="使用BD09坐标系">
              <input
                type="checkbox"
                checked={useCorrectedData}
                onChange={(e) => setUseCorrectedData(e.target.checked)}
              />
            </Field>
            
            {useCorrectedData && (
              <Field label="目标坐标系">
                <select
                  value={coordinateSystem}
                  onChange={(e) => setCoordinateSystem(e.target.value)}
                  style={{ padding: '4px', borderRadius: '4px' }}
                >
                  <option value="WGS84">WGS84</option>
                  <option value="GCJ02">GCJ02</option>
                  <option value="BD09">BD09 (百度地图)</option>
                </select>
              </Field>
            )}
          </HStack>
          
          {useCorrectedData && (
            <Text fontSize="sm" color="gray.600" mt={2}>
              推荐使用BD09坐标系，这样GPS数据就能与百度地图路网完美匹配
            </Text>
          )}
        </Box>
        
        <Button
          colorScheme="blue"
          onClick={fetchTrajectoryData}
          disabled={loading}
        >
          {loading ? "查询中..." : "查询轨迹"}
        </Button>
      </VStack>

      {/* 矫正信息显示 */}
      {correctionInfo && (
        <Box bg="blue.50" p={3} borderRadius="md" mb={4}>
          <Text fontWeight="bold" mb={2}>坐标系转换信息：</Text>
          <Text fontSize="sm">
            原始数据点：{correctionInfo.original_count} | 
            坐标系：{correctionInfo.coordinate_system}
          </Text>
        </Box>
      )}

      {/* 地图容器 */}
      <Box 
        ref={mapRef}
        w="100%" 
        h="400px" 
        border="1px solid" 
        borderColor="gray.300" 
        borderRadius="md"
        mb={4}
      />

      {/* 轨迹数据展示 */}
      {trajectoryData.length > 0 && (
        <Box>
          <Text fontWeight="bold" mb={2}>
            查询结果：共找到 {trajectoryData.length} 条轨迹记录
          </Text>
          
          {/* 轨迹点列表 */}
          <Box maxH="300px" overflowY="auto" border="1px solid" borderColor="gray.200" borderRadius="md" p={4}>
            {trajectoryData.map((record, index) => {
              // 转换速度单位：cm/s -> m/s -> km/h
              const speedMs = (record.speed / 100).toFixed(1)
              const speedKmh = (record.speed * 0.036).toFixed(1)
              
              return (
                <Box key={index} p={2} borderBottom="1px solid" borderColor="gray.100">
                  <Text fontSize="sm">
                    <strong>时间:</strong> {record.utc} | 
                    <strong>位置:</strong> ({record.lat}, {record.lon}) | 
                    <strong>速度:</strong> {speedMs}m/s ({speedKmh}km/h) | 
                    <strong>方向:</strong> {record.head}° | 
                    <strong>状态:</strong> {record.tflag === 1 ? '载客' : '空载'}
                  </Text>
                </Box>
              )
            })}
          </Box>
        </Box>
      )}

      {/* 空状态 */}
      {!loading && trajectoryData.length === 0 && commaddr && (
        <Text color="gray.500" textAlign="center">
          未找到该车辆在指定时间范围内的轨迹数据
        </Text>
      )}
    </Container>
  )
}

// 声明全局变量
declare global {
  interface Window {
    BMap: any
    initBaiduMap: () => void
  }
} 