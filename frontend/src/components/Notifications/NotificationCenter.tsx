import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { Bell, Check, CheckCheck, Trash2, X } from "lucide-react"
import { useEffect, useRef, useState } from "react"

import type { NotificationPublic, NotificationsPublic } from "@/client"
import {
  NotificationsService,
  type NotificationType,
} from "@/client"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuGroup,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
  SheetTrigger,
} from "@/components/ui/sheet"
import { Skeleton } from "@/components/ui/skeleton"
import useCustomToast from "@/hooks/useCustomToast"
import { cn } from "@/lib/utils"
import { handleError } from "@/utils"

const getNotificationTypeColor = (type: NotificationType) => {
  switch (type) {
    case "info":
      return "bg-blue-500"
    case "success":
      return "bg-green-500"
    case "warning":
      return "bg-yellow-500"
    case "error":
      return "bg-red-500"
    default:
      return "bg-gray-500"
  }
}

const getNotificationTypeIcon = (type: NotificationType) => {
  switch (type) {
    case "info":
      return "ℹ️"
    case "success":
      return "✅"
    case "warning":
      return "⚠️"
    case "error":
      return "❌"
    default:
      return "📢"
  }
}

function NotificationItem({
  notification,
  onMarkRead,
  onDelete,
}: {
  notification: NotificationPublic
  onMarkRead: (id: string) => void
  onDelete: (id: string) => void
}) {
  const formatDate = (dateString: string | null | undefined) => {
    if (!dateString) return ""
    const date = new Date(dateString)
    const now = new Date()
    const diff = now.getTime() - date.getTime()
    const minutes = Math.floor(diff / 60000)
    const hours = Math.floor(diff / 3600000)
    const days = Math.floor(diff / 86400000)

    if (minutes < 1) return "Just now"
    if (minutes < 60) return `${minutes}m ago`
    if (hours < 24) return `${hours}h ago`
    if (days < 7) return `${days}d ago`
    return date.toLocaleDateString()
  }

  return (
    <div
      className={cn(
        "flex items-start gap-3 p-3 rounded-lg transition-colors",
        !notification.is_read && "bg-muted/50",
      )}
    >
      <div className="flex flex-col items-center gap-1">
        <div
          className={cn(
            "w-2 h-2 rounded-full",
            getNotificationTypeColor(notification.notification_type),
          )}
        />
        {!notification.is_read && (
          <div className="w-2 h-2 rounded-full bg-primary" />
        )}
      </div>
      <div className="flex-1 min-w-0">
        <div className="flex items-start justify-between gap-2">
          <div className="flex items-center gap-2">
            <span className="text-lg">{getNotificationTypeIcon(notification.notification_type)}</span>
            <h4
              className={cn(
                "font-medium text-sm",
                !notification.is_read && "font-semibold",
              )}
            >
              {notification.title}
            </h4>
          </div>
          <span className="text-xs text-muted-foreground whitespace-nowrap">
            {formatDate(notification.created_at)}
          </span>
        </div>
        {notification.message && (
          <p className="text-sm text-muted-foreground mt-1 line-clamp-2">
            {notification.message}
          </p>
        )}
        <div className="flex items-center gap-2 mt-2">
          {!notification.is_read && (
            <Button
              variant="ghost"
              size="sm"
              className="h-7 px-2 text-xs"
              onClick={() => onMarkRead(notification.id)}
            >
              <Check className="w-3 h-3 mr-1" />
              Mark read
            </Button>
          )}
          <Button
            variant="ghost"
            size="sm"
            className="h-7 px-2 text-xs text-destructive hover:text-destructive"
            onClick={() => onDelete(notification.id)}
          >
            <Trash2 className="w-3 h-3 mr-1" />
            Delete
          </Button>
        </div>
      </div>
    </div>
  )
}

function NotificationSkeleton() {
  return (
    <div className="flex items-start gap-3 p-3">
      <div className="flex flex-col items-center gap-1">
        <Skeleton className="w-2 h-2 rounded-full" />
        <Skeleton className="w-2 h-2 rounded-full" />
      </div>
      <div className="flex-1 space-y-2">
        <div className="flex items-center justify-between">
          <Skeleton className="h-4 w-32" />
          <Skeleton className="h-3 w-16" />
        </div>
        <Skeleton className="h-3 w-full" />
        <Skeleton className="h-3 w-2/3" />
      </div>
    </div>
  )
}

export function NotificationCenter() {
  const [isOpen, setIsOpen] = useState(false)
  const [wsConnected, setWsConnected] = useState(false)
  const wsRef = useRef<WebSocket | null>(null)
  const queryClient = useQueryClient()
  const { showSuccessToast, showErrorToast } = useCustomToast()

  const { data: notificationsData, isLoading } = useQuery<NotificationsPublic>({
    queryKey: ["notifications"],
    queryFn: () => NotificationsService.readNotifications({ skip: 0, limit: 50 }),
    refetchInterval: 30000,
  })

  const markReadMutation = useMutation({
    mutationFn: (id: string) =>
      NotificationsService.markNotificationRead({ id }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["notifications"] })
      showSuccessToast("Notification marked as read")
    },
    onError: handleError.bind(showErrorToast),
  })

  const markAllReadMutation = useMutation({
    mutationFn: () => NotificationsService.markAllNotificationsRead(),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["notifications"] })
      showSuccessToast("All notifications marked as read")
    },
    onError: handleError.bind(showErrorToast),
  })

  const deleteMutation = useMutation({
    mutationFn: (id: string) =>
      NotificationsService.deleteNotification({ id }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["notifications"] })
      showSuccessToast("Notification deleted")
    },
    onError: handleError.bind(showErrorToast),
  })

  useEffect(() => {
    const token = localStorage.getItem("access_token")
    if (!token) return

    const protocol = window.location.protocol === "https:" ? "wss:" : "ws:"
    const wsUrl = `${protocol}//${window.location.host}/ws/notifications?token=${token}`

    const connect = () => {
      try {
        const ws = new WebSocket(wsUrl)
        wsRef.current = ws

        ws.onopen = () => {
          setWsConnected(true)
        }

        ws.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data)
            if (data.type === "notification") {
              queryClient.invalidateQueries({ queryKey: ["notifications"] })
            }
          } catch {
            // Ignore non-JSON messages
          }
        }

        ws.onclose = () => {
          setWsConnected(false)
          setTimeout(connect, 5000)
        }

        ws.onerror = () => {
          setWsConnected(false)
        }
      } catch {
        setTimeout(connect, 5000)
      }
    }

    connect()

    return () => {
      if (wsRef.current) {
        wsRef.current.close()
      }
    }
  }, [queryClient])

  const unreadCount = notificationsData?.unread_count || 0
  const notifications = notificationsData?.data || []

  const handleMarkRead = (id: string) => {
    markReadMutation.mutate(id)
  }

  const handleMarkAllRead = () => {
    markAllReadMutation.mutate()
  }

  const handleDelete = (id: string) => {
    deleteMutation.mutate(id)
  }

  return (
    <Sheet open={isOpen} onOpenChange={setIsOpen}>
      <SheetTrigger asChild>
        <Button variant="ghost" size="icon" className="relative">
          <Bell className="h-5 w-5" />
          {unreadCount > 0 && (
            <Badge
              variant="destructive"
              className="absolute -top-1 -right-1 h-5 w-5 p-0 flex items-center justify-center text-xs"
            >
              {unreadCount > 99 ? "99+" : unreadCount}
            </Badge>
          )}
          <span className="sr-only">Notifications</span>
        </Button>
      </SheetTrigger>
      <SheetContent className="w-full sm:max-w-md">
        <SheetHeader className="flex flex-row items-center justify-between">
          <SheetTitle className="text-xl">Notifications</SheetTitle>
          <div className="flex items-center gap-2">
            {wsConnected && (
              <Badge variant="secondary" className="text-xs">
                <span className="w-2 h-2 bg-green-500 rounded-full mr-1" />
                Live
              </Badge>
            )}
            {unreadCount > 0 && (
              <Button
                variant="ghost"
                size="sm"
                className="h-8 text-xs"
                onClick={handleMarkAllRead}
                disabled={markAllReadMutation.isPending}
              >
                <CheckCheck className="w-4 h-4 mr-1" />
                Mark all read
              </Button>
            )}
          </div>
        </SheetHeader>
        <div className="mt-6 space-y-2 max-h-[calc(100vh-120px)] overflow-y-auto">
          {isLoading ? (
            Array.from({ length: 5 }).map((_, i) => (
              <NotificationSkeleton key={i} />
            ))
          ) : notifications.length === 0 ? (
            <div className="flex flex-col items-center justify-center text-center py-12">
              <div className="rounded-full bg-muted p-4 mb-4">
                <Bell className="h-8 w-8 text-muted-foreground" />
              </div>
              <h3 className="text-lg font-semibold">No notifications</h3>
              <p className="text-muted-foreground">
                You don't have any notifications yet
              </p>
            </div>
          ) : (
            notifications.map((notification) => (
              <NotificationItem
                key={notification.id}
                notification={notification}
                onMarkRead={handleMarkRead}
                onDelete={handleDelete}
              />
            ))
          )}
        </div>
      </SheetContent>
    </Sheet>
  )
}

export function NotificationDropdown() {
  const queryClient = useQueryClient()
  const { showSuccessToast, showErrorToast } = useCustomToast()

  const { data: notificationsData, isLoading } = useQuery<NotificationsPublic>({
    queryKey: ["notifications"],
    queryFn: () => NotificationsService.readNotifications({ skip: 0, limit: 10 }),
    refetchInterval: 30000,
  })

  const markReadMutation = useMutation({
    mutationFn: (id: string) =>
      NotificationsService.markNotificationRead({ id }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["notifications"] })
    },
    onError: handleError.bind(showErrorToast),
  })

  const markAllReadMutation = useMutation({
    mutationFn: () => NotificationsService.markAllNotificationsRead(),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["notifications"] })
      showSuccessToast("All notifications marked as read")
    },
    onError: handleError.bind(showErrorToast),
  })

  const unreadCount = notificationsData?.unread_count || 0
  const notifications = notificationsData?.data || []

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="ghost" size="icon" className="relative">
          <Bell className="h-5 w-5" />
          {unreadCount > 0 && (
            <Badge
              variant="destructive"
              className="absolute -top-1 -right-1 h-5 w-5 p-0 flex items-center justify-center text-xs"
            >
              {unreadCount > 99 ? "99+" : unreadCount}
            </Badge>
          )}
          <span className="sr-only">Notifications</span>
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent className="w-80" align="end">
        <DropdownMenuLabel className="flex items-center justify-between">
          <span>Notifications</span>
          {unreadCount > 0 && (
            <Button
              variant="ghost"
              size="sm"
              className="h-6 text-xs"
              onClick={() => markAllReadMutation.mutate()}
              disabled={markAllReadMutation.isPending}
            >
              <CheckCheck className="w-3 h-3 mr-1" />
              Mark all read
            </Button>
          )}
        </DropdownMenuLabel>
        <DropdownMenuSeparator />
        <DropdownMenuGroup className="max-h-80 overflow-y-auto">
          {isLoading ? (
            Array.from({ length: 3 }).map((_, i) => (
              <div key={i} className="p-3">
                <Skeleton className="h-4 w-3/4 mb-2" />
                <Skeleton className="h-3 w-full" />
              </div>
            ))
          ) : notifications.length === 0 ? (
            <div className="p-4 text-center text-muted-foreground">
              No notifications
            </div>
          ) : (
            notifications.map((notification) => (
              <DropdownMenuItem
                key={notification.id}
                className={cn(
                  "flex flex-col items-start p-3 cursor-pointer",
                  !notification.is_read && "bg-muted/50",
                )}
                onClick={() => {
                  if (!notification.is_read) {
                    markReadMutation.mutate(notification.id)
                  }
                }}
              >
                <div className="flex items-center justify-between w-full">
                  <span className="font-medium text-sm flex items-center gap-1">
                    <span>{getNotificationTypeIcon(notification.notification_type)}</span>
                    {notification.title}
                  </span>
                  {!notification.is_read && (
                    <div className="w-2 h-2 rounded-full bg-primary" />
                  )}
                </div>
                {notification.message && (
                  <p className="text-xs text-muted-foreground mt-1 line-clamp-2">
                    {notification.message}
                  </p>
                )}
              </DropdownMenuItem>
            ))
          )}
        </DropdownMenuGroup>
        <DropdownMenuSeparator />
        <DropdownMenuItem className="justify-center text-sm text-muted-foreground">
          View all notifications
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  )
}
