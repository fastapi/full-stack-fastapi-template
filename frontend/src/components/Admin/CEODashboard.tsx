import { Grid, GridItem, Stat, StatLabel, StatNumber, StatHelpText } from '@chakra-ui/react'
import { RoleDashboard } from '../Common/RoleDashboard'

export const CEODashboard = () => {
  return (
    <RoleDashboard
      title="Dashboard Global"
      description="Vista general del negocio y KPIs principales"
    >
      <Grid templateColumns="repeat(3, 1fr)" gap={6}>
        <GridItem>
          <Stat>
            <StatLabel>Ingresos Totales</StatLabel>
            <StatNumber>$1,234,567</StatNumber>
            <StatHelpText>↑ 23.36% (30 días)</StatHelpText>
          </Stat>
        </GridItem>
        <GridItem>
          <Stat>
            <StatLabel>Propiedades Activas</StatLabel>
            <StatNumber>156</StatNumber>
            <StatHelpText>↑ 12% (30 días)</StatHelpText>
          </Stat>
        </GridItem>
        <GridItem>
          <Stat>
            <StatLabel>Agentes Activos</StatLabel>
            <StatNumber>45</StatNumber>
            <StatHelpText>↑ 5% (30 días)</StatHelpText>
          </Stat>
        </GridItem>
      </Grid>
    </RoleDashboard>
  )
} 