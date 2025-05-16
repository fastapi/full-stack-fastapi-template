import { forwardRef } from 'react'
import { Box, chakra } from '@chakra-ui/react'

// Interface simples para as props do Select
export interface SelectProps extends React.SelectHTMLAttributes<HTMLSelectElement> {
  /**
   * O texto do placeholder
   */
  placeholder?: string
  
  /**
   * Se o select está inválido
   */
  isInvalid?: boolean
  
  /**
   * Se o select está desabilitado
   */
  isDisabled?: boolean
}

export const Select = forwardRef<HTMLSelectElement, SelectProps>((props, ref) => {
  const {
    className,
    children,
    placeholder,
    isInvalid,
    isDisabled,
    ...rest
  } = props

  // Estilo básico para o select
  const selectStyles = {
    width: '100%',
    height: '40px',
    borderRadius: 'md',
    padding: '0 1rem',
    borderColor: isInvalid ? 'red.500' : 'gray.200',
    backgroundColor: 'white',
    _disabled: {
      opacity: 0.7,
      cursor: 'not-allowed',
    },
    _focus: {
      borderColor: 'blue.500',
      boxShadow: '0 0 0 1px var(--chakra-colors-blue-500)',
    },
  }

  return (
    <Box position="relative" width="100%">
      <chakra.select
        ref={ref}
        className={`chakra-select ${className || ''}`}
        disabled={isDisabled}
        css={selectStyles}
        {...rest}
      >
        {placeholder && <option value="">{placeholder}</option>}
        {children}
      </chakra.select>
    </Box>
  )
})

Select.displayName = 'Select'
