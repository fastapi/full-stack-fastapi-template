import { createFileRoute } from '@tanstack/react-router'
import { useState } from 'react'
import { FiUsers, FiSettings, FiBarChart2, FiHome, FiShield, FiTrendingUp, FiActivity, FiChevronRight, FiEye, FiHeadphones, FiUserCheck, FiPlus } from 'react-icons/fi'

// Import existing admin components
import { CEODashboard } from '../components/Admin/CEODashboard'
import { ManagerDashboard } from '../components/Admin/ManagerDashboard'
import { HRDashboard } from '../components/Admin/HRDashboard'
import { AgentDashboard } from '../components/Admin/AgentDashboard'
import { SupervisorDashboard } from '../components/Admin/SupervisorDashboard'
import { SupportDashboard } from '../components/Admin/SupportDashboard'
import { UserManagement } from '../components/Admin/UserManagement'
import { PropertyCRM } from '../components/Admin/PropertyCRM'

function AdminDashboard() {
  const [activeSection, setActiveSection] = useState('overview')

  const systemMetrics = {
    totalUsers: 1247,
    activeProperties: 856,
    totalRevenue: 15420000,
    activeAgents: 45,
    supportTickets: 23,
    systemUptime: '99.9%'
  }

  const quickActions = [
    { icon: FiPlus, label: 'Agregar Usuario', action: () => setActiveSection('users'), color: '#28A745' },
    { icon: FiHome, label: 'CRM Propiedades', action: () => setActiveSection('properties'), color: '#007BFF' },
    { icon: FiBarChart2, label: 'Reportes', action: () => setActiveSection('ceo'), color: '#6F42C1' },
    { icon: FiSettings, label: 'Configuración', action: () => {}, color: '#6C757D' }
  ]

  const roleManagement = [
    { role: 'CEO', component: 'ceo', icon: FiShield, description: 'Vista ejecutiva general', users: 1 },
    { role: 'Manager', component: 'manager', icon: FiUserCheck, description: 'Gestión operativa', users: 8 },
    { role: 'HR', component: 'hr', icon: FiUsers, description: 'Recursos humanos', users: 3 },
    { role: 'Agent', component: 'agent', icon: FiHome, description: 'Agentes inmobiliarios', users: 45 },
    { role: 'Supervisor', component: 'supervisor', icon: FiEye, description: 'Supervisión y control', users: 12 },
    { role: 'Support', component: 'support', icon: FiHeadphones, description: 'Atención al cliente', users: 15 }
  ]

  const renderContent = () => {
    switch (activeSection) {
      case 'ceo':
        return <CEODashboard />
      case 'manager':
        return <ManagerDashboard />
      case 'hr':
        return <HRDashboard />
      case 'agent':
        return <AgentDashboard />
      case 'supervisor':
        return <SupervisorDashboard />
      case 'support':
        return <SupportDashboard />
      case 'users':
        return <UserManagement />
      case 'properties':
        return <PropertyCRM />
      default:
        return (
          <div style={{ padding: '24px' }}>
            <div style={{ marginBottom: '32px' }}>
              <h1 style={{ fontSize: '32px', fontWeight: '700', color: '#1a202c', marginBottom: '8px' }}>
                Panel de Administración GENIUS INDUSTRIES
              </h1>
              <p style={{ fontSize: '16px', color: '#666', marginBottom: '24px' }}>
                Vista centralizada de todo el sistema inmobiliario
              </p>
              
              <div style={{
                background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                color: 'white',
                padding: '16px 20px',
                borderRadius: '12px',
                display: 'flex',
                alignItems: 'center',
                gap: '16px'
              }}>
                <FiActivity size={24} />
                <div>
                  <div style={{ fontWeight: '600' }}>Sistema Operativo</div>
                  <div style={{ fontSize: '14px', opacity: 0.9 }}>
                    Uptime: {systemMetrics.systemUptime} • Última actualización: hace 2 min
                  </div>
                </div>
              </div>
            </div>

            <div style={{ 
              display: 'grid', 
              gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', 
              gap: '24px',
              marginBottom: '32px'
            }}>
              <div style={{ 
                background: '#fff', 
                borderRadius: '16px', 
                boxShadow: '0 4px 6px -1px rgba(0,0,0,0.1)', 
                padding: '24px',
                border: '1px solid #e2e8f0'
              }}>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  <div>
                    <div style={{ color: '#666', fontSize: '14px', marginBottom: '4px' }}>Usuarios Totales</div>
                    <div style={{ fontSize: '36px', fontWeight: '700', color: '#1a202c' }}>
                      {systemMetrics.totalUsers.toLocaleString()}
                    </div>
                    <div style={{ color: '#28A745', fontSize: '13px', marginTop: '4px' }}>
                      ↑ 12% este mes
                    </div>
                  </div>
                  <div style={{ 
                    background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', 
                    borderRadius: '12px', 
                    padding: '12px',
                    color: 'white'
                  }}>
                    <FiUsers size={24} />
                  </div>
                </div>
              </div>

              <div style={{ 
                background: '#fff', 
                borderRadius: '16px', 
                boxShadow: '0 4px 6px -1px rgba(0,0,0,0.1)', 
                padding: '24px',
                border: '1px solid #e2e8f0'
              }}>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  <div>
                    <div style={{ color: '#666', fontSize: '14px', marginBottom: '4px' }}>Propiedades Activas</div>
                    <div style={{ fontSize: '36px', fontWeight: '700', color: '#1a202c' }}>
                      {systemMetrics.activeProperties.toLocaleString()}
                    </div>
                    <div style={{ color: '#28A745', fontSize: '13px', marginTop: '4px' }}>
                      ↑ 8% este mes
                    </div>
                  </div>
                  <div style={{ 
                    background: 'linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%)', 
                    borderRadius: '12px', 
                    padding: '12px',
                    color: '#b7791f'
                  }}>
                    <FiHome size={24} />
                  </div>
                </div>
              </div>

              <div style={{ 
                background: '#fff', 
                borderRadius: '16px', 
                boxShadow: '0 4px 6px -1px rgba(0,0,0,0.1)', 
                padding: '24px',
                border: '1px solid #e2e8f0'
              }}>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  <div>
                    <div style={{ color: '#666', fontSize: '14px', marginBottom: '4px' }}>Ingresos Totales</div>
                    <div style={{ fontSize: '36px', fontWeight: '700', color: '#1a202c' }}>
                      ${(systemMetrics.totalRevenue / 1000000).toFixed(1)}M
                    </div>
                    <div style={{ color: '#28A745', fontSize: '13px', marginTop: '4px' }}>
                      ↑ 23% este mes
                    </div>
                  </div>
                  <div style={{ 
                    background: 'linear-gradient(135deg, #a8edea 0%, #fed6e3 100%)', 
                    borderRadius: '12px', 
                    padding: '12px',
                    color: '#0891b2'
                  }}>
                    <FiTrendingUp size={24} />
                  </div>
                </div>
              </div>
            </div>

            <div style={{ marginBottom: '32px' }}>
              <h2 style={{ fontSize: '24px', fontWeight: '600', color: '#1a202c', marginBottom: '16px' }}>
                Acciones Rápidas
              </h2>
              <div style={{ 
                display: 'grid', 
                gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', 
                gap: '16px'
              }}>
                {quickActions.map((action, index) => (
                  <button
                    key={index}
                    onClick={action.action}
                    style={{
                      background: '#fff',
                      border: '1px solid #e2e8f0',
                      borderRadius: '12px',
                      padding: '20px',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '12px',
                      cursor: 'pointer',
                      transition: 'all 0.2s',
                      textAlign: 'left'
                    }}
                  >
                    <div style={{ 
                      background: action.color, 
                      color: 'white', 
                      borderRadius: '8px', 
                      padding: '8px' 
                    }}>
                      <action.icon size={18} />
                    </div>
                    <span style={{ fontWeight: '500', color: '#1a202c' }}>{action.label}</span>
                  </button>
                ))}
              </div>
            </div>

            <div>
              <h2 style={{ fontSize: '24px', fontWeight: '600', color: '#1a202c', marginBottom: '16px' }}>
                Gestión por Roles
              </h2>
              <div style={{ 
                display: 'grid', 
                gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', 
                gap: '16px'
              }}>
                {roleManagement.map((role, index) => (
                  <button
                    key={index}
                    onClick={() => setActiveSection(role.component)}
                    style={{
                      background: '#fff',
                      border: '1px solid #e2e8f0',
                      borderRadius: '12px',
                      padding: '20px',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'space-between',
                      cursor: 'pointer',
                      transition: 'all 0.2s',
                      textAlign: 'left'
                    }}
                  >
                    <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
                      <div style={{ 
                        background: '#f7fafc', 
                        borderRadius: '10px', 
                        padding: '12px',
                        color: '#3182ce'
                      }}>
                        <role.icon size={24} />
                      </div>
                      <div>
                        <div style={{ fontWeight: '600', color: '#1a202c', marginBottom: '4px' }}>
                          {role.role} Dashboard
                        </div>
                        <div style={{ fontSize: '14px', color: '#666' }}>
                          {role.description}
                        </div>
                        <div style={{ fontSize: '12px', color: '#3182ce', marginTop: '2px' }}>
                          {role.users} usuarios activos
                        </div>
                      </div>
                    </div>
                    <FiChevronRight size={20} style={{ color: '#666' }} />
                  </button>
                ))}
              </div>
            </div>
          </div>
        )
    }
  }

  return (
    <div style={{ 
      minHeight: '100vh', 
      background: 'linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%)',
      padding: '20px'
    }}>
      {activeSection !== 'overview' && (
        <div style={{
          background: '#fff',
          borderRadius: '12px',
          padding: '16px 24px',
          marginBottom: '20px',
          boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
          display: 'flex',
          alignItems: 'center',
          gap: '16px'
        }}>
          <button
            onClick={() => setActiveSection('overview')}
            style={{
              background: '#3182ce',
              color: 'white',
              border: 'none',
              borderRadius: '8px',
              padding: '8px 16px',
              cursor: 'pointer',
              fontSize: '14px',
              fontWeight: '500'
            }}
          >
            ← Volver al Panel Principal
          </button>
          <div style={{ color: '#666' }}>
            {roleManagement.find(r => r.component === activeSection)?.role || 
             (activeSection === 'users' ? 'Gestión de Usuarios' : 
              activeSection === 'properties' ? 'CRM de Propiedades' : '')} Dashboard
          </div>
        </div>
      )}

      <div style={{
        background: '#fff',
        borderRadius: '16px',
        boxShadow: '0 4px 6px -1px rgba(0,0,0,0.1)',
        overflow: 'hidden'
      }}>
        {renderContent()}
      </div>
    </div>
  )
}

export const Route = createFileRoute('/admin')({
  component: AdminDashboard,
})
