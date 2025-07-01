import { RoleDashboard } from '../Common/RoleDashboard'

export const CEODashboard = () => {
  return (
    <RoleDashboard
      title="Dashboard Global"
      description="Vista general del negocio y KPIs principales"
    >
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 24 }}>
        <div style={{ background: '#fff', borderRadius: 8, boxShadow: '0 1px 3px 0 rgba(0,0,0,0.1)', padding: 24 }}>
          <div style={{ color: '#666', fontSize: 14, marginBottom: 4 }}>Ingresos Totales</div>
          <div style={{ fontSize: 32, fontWeight: 700, color: '#000' }}>$1,234,567</div>
          <div style={{ color: '#28A745', fontSize: 13, marginTop: 4 }}>↑ 23.36% (30 días)</div>
        </div>
        <div style={{ background: '#fff', borderRadius: 8, boxShadow: '0 1px 3px 0 rgba(0,0,0,0.1)', padding: 24 }}>
          <div style={{ color: '#666', fontSize: 14, marginBottom: 4 }}>Propiedades Activas</div>
          <div style={{ fontSize: 32, fontWeight: 700, color: '#000' }}>156</div>
          <div style={{ color: '#28A745', fontSize: 13, marginTop: 4 }}>↑ 12% (30 días)</div>
        </div>
        <div style={{ background: '#fff', borderRadius: 8, boxShadow: '0 1px 3px 0 rgba(0,0,0,0.1)', padding: 24 }}>
          <div style={{ color: '#666', fontSize: 14, marginBottom: 4 }}>Agentes Activos</div>
          <div style={{ fontSize: 32, fontWeight: 700, color: '#000' }}>45</div>
          <div style={{ color: '#28A745', fontSize: 13, marginTop: 4 }}>↑ 5% (30 días)</div>
        </div>
      </div>
    </RoleDashboard>
  )
} 