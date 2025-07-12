"use client"

import { useToast as useChakraToast } from "@chakra-ui/react"
import { createContext, useContext, useEffect, ReactNode } from "react"

// Tipos para las opciones del toast
type ToastOptions = {
  title?: string;
  description?: string;
  status?: "info" | "warning" | "success" | "error" | "loading";
  duration?: number;
  isClosable?: boolean;
  position?: "top" | "top-right" | "top-left" | "bottom" | "bottom-right" | "bottom-left";
  [key: string]: any;
};

type ToasterContextType = {
  toast: (options: ToastOptions) => void;
  close: (toastId?: string | number) => void;
  closeAll: () => void;
  isActive: (toastId: string | number) => boolean;
  update: (toastId: string | number, options: Partial<ToastOptions>) => void;
};

// Creamos un contexto para el toaster
const ToasterContext = createContext<ToasterContextType | null>(null);

// Hook personalizado para usar el toaster
export const useToaster = (): ToasterContextType => {
  const context = useContext(ToasterContext);
  if (!context) {
    throw new Error("useToaster debe usarse dentro de un ToasterProvider");
  }
  return context;
};

// Proveedor del toaster
export const ToasterProvider = ({ children }: { children: ReactNode }) => {
  const toast = useChakraToast();
  
  const showToast = (options: ToastOptions) => {
    const {
      title,
      description,
      status = "info",
      duration = 5000,
      isClosable = true,
      position = "top-end",
      ...rest
    } = options;

    return toast({
      title,
      description,
      status,
      duration,
      isClosable,
      position,
      ...rest,
    });
  };

  const toasterValue: ToasterContextType = {
    toast: showToast,
    close: toast.close,
    closeAll: toast.closeAll,
    isActive: toast.isActive,
    update: toast.update,
  };

  return (
    <ToasterContext.Provider value={toasterValue}>
      {children}
    </ToasterContext.Provider>
  );
};

// Componente que usa el toaster
export const Toaster = () => {
  const toast = useToaster();
  
  // Ejemplo de cómo usar el toaster
  useEffect(() => {
    // Esto es solo para demostración, puedes eliminarlo
    toast.toast({
      title: "Bienvenido",
      description: "La aplicación se ha cargado correctamente",
      status: "success",
      duration: 5000,
      isClosable: true,
    });
  }, [toast]);
  
  // En Chakra UI v2, el Toaster se maneja automáticamente
  // No necesitamos renderizar nada aquí
  return null;
};

// Objeto para usar el toaster fuera de componentes React
export const toaster = {
  toast: (options: ToastOptions) => {
    console.warn("El toaster se está usando fuera de un componente React. Asegúrate de usar el hook useToaster dentro de componentes funcionales.");
    
    // Esta implementación es solo para evitar errores, pero no mostrará ningún toast
    // ya que no tenemos acceso al contexto aquí
    console.log("Toast intentado:", options);
  },
  close: (toastId?: string | number) => {
    console.warn("No se puede cerrar el toast fuera de un componente React");
  },
  closeAll: () => {
    console.warn("No se pueden cerrar todos los toasts fuera de un componente React");
  },
  isActive: (toastId: string | number) => {
    console.warn("No se puede verificar el estado del toast fuera de un componente React");
    return false;
  },
  update: (toastId: string | number, options: Partial<ToastOptions>) => {
    console.warn("No se puede actualizar el toast fuera de un componente React");
  },
};
