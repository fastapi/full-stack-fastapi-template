import { Box, Container, Text } from "@chakra-ui/react"
import { createFileRoute } from "@tanstack/react-router"

//import useAuth from "@/hooks/useAuth"

export const Route = createFileRoute("/_layout/tickets")({
  component: Tickets,
})

function Tickets() {
  //const { user: currentUser } = useAuth()

  return (
    <>
      <Container maxW="full">
        <Box pt={12} m={4}>
            <Text>
                  <ul>
                        <ol><b>Página de Listagem de Tickets</b></ol>
                        <li>Requisitos: </li>
                        <li>- Exibição dos tickets cadastrados em formato de tabela ou lista com informações resumidas (título, status, prioridade, data de criação)</li>
                        <li>- Campo de busca para filtrar por palavra-chave</li>
                        <li>- Filtros para status, data, prioridade e categoria</li>
                        <li>- Opções de ordenação e paginação para facilitar a navegação</li>
                  </ul>
            </Text>
            
        </Box>
      </Container>
    </>
  )
}



