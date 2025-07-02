import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Button, Flex } from '@chakra-ui/react'
import { FiHome, FiBarChart2, FiUsers, FiTrendingUp, FiSettings } from 'react-icons/fi'
import { RoleDashboard } from '../Common/RoleDashboard'
import { PropertyCRM } from './PropertyCRM'

interface DashboardData {
  status: string
  data: {
    summary: {
      total_users: number
      active_users: number
      total_properties: number
      total_revenue: number
      active_branches: number
      monthly_growth: number
      active_agents: number
    }
    current_user: {
      id: string
      email: string
      full_name: string
      role: string
      is_superuser: boolean
    }
  }
}

const fetchCEODashboard = async (): Promise<DashboardData> => {
  const response = await fetch('http://localhost:8000/api/v1/ceo/dashboard', {
    headers: {
      'Authorization': `Bearer ${localStorage.getItem('token')}`,
      'Content-Type': 'application/json',
    },
  })
  
  if (!response.ok) {
    throw new Error('Failed to fetch dashboard data')
  }
  
  return response.json()
}

export const CEODashboard = () => {
  const [activeTab, setActiveTab] = useState('dashboard')
  
  const tabs = [
    { id: 'dashboard', label: 'Dashboard Ejecutivo', icon: FiBarChart2 },
    { id: 'properties', label: 'Propiedades', icon: FiHome },
    { id: 'analytics', label: 'Analytics', icon: FiTrendingUp },
    { id: 'organization', label: 'Organización', icon: FiUsers },
    { id: 'settings', label: 'Configuración', icon: FiSettings }
  ]

  const { data, isLoading, error } = useQuery({
    queryKey: ['ceo-dashboard'],
    queryFn: fetchCEODashboard,
    refetchInterval: 30000, // Actualizar cada 30 segundos
  })

  const renderContent = () => {
    switch (activeTab) {
      case 'properties':
        return <PropertyCRM />
      case 'analytics':
        return (
          <div style={{ background: '#fff', padding: 24, borderRadius: 8, textAlign: 'center' }}>
            <div style={{ fontSize: 18, color: '#666' }}>
              Módulo de Analytics Avanzado en desarrollo
            </div>
          </div>
        )
      case 'organization':
        return (
          <div style={{ background: '#fff', padding: 24, borderRadius: 8, textAlign: 'center' }}>
            <div style={{ fontSize: 18, color: '#666' }}>
              Módulo de Gestión Organizacional en desarrollo
            </div>
          </div>
        )
      case 'settings':
        return (
          <div style={{ background: '#fff', padding: 24, borderRadius: 8, textAlign: 'center' }}>
            <div style={{ fontSize: 18, color: '#666' }}>
              Módulo de Configuración del Sistema en desarrollo
            </div>
          </div>
        )
      default:
        if (isLoading) {
          return (
            <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '200px' }}>
              <div style={{ color: '#666' }}>Cargando datos del dashboard...</div>
            </div>
          )
        }

        if (error) {
          return (
            <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '200px' }}>
              <div style={{ color: '#dc3545' }}>Error cargando datos: {(error as Error).message}</div>
            </div>
          )
        }

        const summary = data?.data?.summary

        return (
          <>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: 24, marginBottom: 32 }}>
              <div style={{ background: '#fff', borderRadius: 8, boxShadow: '0 1px 3px 0 rgba(0,0,0,0.1)', padding: 24 }}>
                <div style={{ color: '#666', fontSize: 14, marginBottom: 4 }}>Ingresos Totales</div>
                <div style={{ fontSize: 32, fontWeight: 700, color: '#000' }}>
                  ${summary?.total_revenue?.toLocaleString() || '0'}
                </div>
                <div style={{ color: '#28A745', fontSize: 13, marginTop: 4 }}>
                  ↑ {summary?.monthly_growth || 0}% (30 días)
                </div>
              </div>
              
              <div style={{ background: '#fff', borderRadius: 8, boxShadow: '0 1px 3px 0 rgba(0,0,0,0.1)', padding: 24 }}>
                <div style={{ color: '#666', fontSize: 14, marginBottom: 4 }}>Propiedades Activas</div>
                <div style={{ fontSize: 32, fontWeight: 700, color: '#000' }}>
                  {summary?.total_properties || 0}
                </div>
                <div style={{ color: '#28A745', fontSize: 13, marginTop: 4 }}>↑ 12% (30 días)</div>
              </div>
              
              <div style={{ background: '#fff', borderRadius: 8, boxShadow: '0 1px 3px 0 rgba(0,0,0,0.1)', padding: 24 }}>
                <div style={{ color: '#666', fontSize: 14, marginBottom: 4 }}>Agentes Activos</div>
                <div style={{ fontSize: 32, fontWeight: 700, color: '#000' }}>
                  {summary?.active_agents || 0}
                </div>
                <div style={{ color: '#28A745', fontSize: 13, marginTop: 4 }}>↑ 5% (30 días)</div>
              </div>
              
              <div style={{ background: '#fff', borderRadius: 8, boxShadow: '0 1px 3px 0 rgba(0,0,0,0.1)', padding: 24 }}>
                <div style={{ color: '#666', fontSize: 14, marginBottom: 4 }}>Usuarios Totales</div>
                <div style={{ fontSize: 32, fontWeight: 700, color: '#000' }}>
                  {summary?.total_users || 0}
                </div>
                <div style={{ color: '#17A2B8', fontSize: 13, marginTop: 4 }}>
                  {summary?.active_users || 0} activos
                </div>
              </div>
            </div>

            {/* Información del usuario actual */}
            {data?.data?.current_user && (
              <div style={{ background: '#f8f9fa', borderRadius: 8, padding: 16, marginTop: 24 }}>
                <div style={{ fontSize: 14, color: '#666', marginBottom: 8 }}>Usuario actual:</div>
                <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
                  <div>
                    <div style={{ fontWeight: 600 }}>{data.data.current_user.full_name}</div>
                    <div style={{ fontSize: 13, color: '#666' }}>{data.data.current_user.email}</div>
                  </div>
                  <div style={{ 
                    background: '#28A745', 
                    color: 'white', 
                    padding: '4px 8px', 
                    borderRadius: 4, 
                    fontSize: 12,
                    fontWeight: 600
                  }}>
                    {data.data.current_user.role.toUpperCase()}
                  </div>
                  {data.data.current_user.is_superuser && (
                    <div style={{ 
                      background: '#dc3545', 
                      color: 'white', 
                      padding: '4px 8px', 
                      borderRadius: 4, 
                      fontSize: 12,
                      fontWeight: 600
                    }}>
                      SUPERUSER
                    </div>
                  )}
                </div>
              </div>
            )}
          </>
        )
    }
  }

  return (
    <RoleDashboard
      title="Dashboard CEO"
      description="Vista general del negocio y control ejecutivo"
    >
      {/* Navigation Tabs */}
      <Flex mb={6} gap={2}>
        {tabs.map((tab) => (
          <Button
            key={tab.id}
            leftIcon={<tab.icon />}
            variant={activeTab === tab.id ? 'solid' : 'outline'}
            colorScheme={activeTab === tab.id ? 'blue' : 'gray'}
            size="sm"
            onClick={() => setActiveTab(tab.id)}
          >
            {tab.label}
          </Button>
        ))}
      </Flex>

      {renderContent()}
    </RoleDashboard>
  )
} 