import { createFileRoute } from '@tanstack/react-router'
import LegalSystemPage from '../../pages/LegalSystemPage'

export const Route = createFileRoute('/_layout/legal')({
  component: LegalSystemPage,
  beforeLoad: ({ context, location }) => {
    // Check if user has access to legal system
    const user = context.user;
    if (!user) {
      throw new Error('Authentication required');
    }
    
    const allowedRoles = ['ceo', 'manager', 'agent'];
    if (!allowedRoles.includes(user.role)) {
      throw new Error('Insufficient permissions');
    }
  }
}) 