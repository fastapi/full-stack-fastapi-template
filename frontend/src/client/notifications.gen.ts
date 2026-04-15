import type { CancelablePromise } from './core/CancelablePromise';
import { OpenAPI } from './core/OpenAPI';
import { request as __request } from './core/request';

export type NotificationType = 'info' | 'success' | 'warning' | 'error';

export type NotificationPublic = {
    title: string;
    message?: (string | null);
    notification_type: NotificationType;
    is_read: boolean;
    action_url?: (string | null);
    id: string;
    user_id: string;
    created_at?: (string | null);
    updated_at?: (string | null);
};

export type NotificationsPublic = {
    data: Array<NotificationPublic>;
    count: number;
    unread_count: number;
};

export type NotificationCreate = {
    title: string;
    message?: (string | null);
    notification_type?: NotificationType;
    action_url?: (string | null);
    user_id: string;
};

export type NotificationUpdate = {
    title?: (string | null);
    message?: (string | null);
    is_read?: (boolean | null);
};

export type Message = {
    message: string;
};

export type NotificationsReadNotificationsData = {
    skip?: number;
    limit?: number;
    unread_only?: boolean;
};

export type NotificationsReadNotificationsResponse = NotificationsPublic;

export type NotificationsCreateNotificationData = {
    requestBody: NotificationCreate;
};

export type NotificationsCreateNotificationResponse = NotificationPublic;

export type NotificationsReadNotificationData = {
    id: string;
};

export type NotificationsReadNotificationResponse = NotificationPublic;

export type NotificationsUpdateNotificationData = {
    id: string;
    requestBody: NotificationUpdate;
};

export type NotificationsUpdateNotificationResponse = NotificationPublic;

export type NotificationsDeleteNotificationData = {
    id: string;
};

export type NotificationsDeleteNotificationResponse = Message;

export type NotificationsMarkNotificationReadData = {
    id: string;
};

export type NotificationsMarkNotificationReadResponse = NotificationPublic;

export type NotificationsMarkAllNotificationsReadResponse = Message;

export class NotificationsService {
    /**
     * Read Notifications
     * Retrieve notifications for the current user.
     * @param data The data for the request.
     * @param data.skip
     * @param data.limit
     * @param data.unread_only
     * @returns NotificationsPublic Successful Response
     * @throws ApiError
     */
    public static readNotifications(data: NotificationsReadNotificationsData = {}): CancelablePromise<NotificationsReadNotificationsResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/notifications/',
            query: {
                skip: data.skip,
                limit: data.limit,
                unread_only: data.unread_only
            },
            errors: {
                422: 'Validation Error'
            }
        });
    }
    
    /**
     * Create Notification
     * Create new notification.
     * Only superusers can create notifications for other users.
     * Regular users can only create notifications for themselves.
     * @param data The data for the request.
     * @param data.requestBody
     * @returns NotificationPublic Successful Response
     * @throws ApiError
     */
    public static createNotification(data: NotificationsCreateNotificationData): CancelablePromise<NotificationsCreateNotificationResponse> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/notifications/',
            body: data.requestBody,
            mediaType: 'application/json',
            errors: {
                422: 'Validation Error'
            }
        });
    }
    
    /**
     * Read Notification
     * Get notification by ID.
     * @param data The data for the request.
     * @param data.id
     * @returns NotificationPublic Successful Response
     * @throws ApiError
     */
    public static readNotification(data: NotificationsReadNotificationData): CancelablePromise<NotificationsReadNotificationResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/notifications/{id}',
            path: {
                id: data.id
            },
            errors: {
                422: 'Validation Error'
            }
        });
    }
    
    /**
     * Update Notification
     * Update a notification.
     * @param data The data for the request.
     * @param data.id
     * @param data.requestBody
     * @returns NotificationPublic Successful Response
     * @throws ApiError
     */
    public static updateNotification(data: NotificationsUpdateNotificationData): CancelablePromise<NotificationsUpdateNotificationResponse> {
        return __request(OpenAPI, {
            method: 'PUT',
            url: '/api/v1/notifications/{id}',
            path: {
                id: data.id
            },
            body: data.requestBody,
            mediaType: 'application/json',
            errors: {
                422: 'Validation Error'
            }
        });
    }
    
    /**
     * Delete Notification
     * Delete a notification.
     * @param data The data for the request.
     * @param data.id
     * @returns Message Successful Response
     * @throws ApiError
     */
    public static deleteNotification(data: NotificationsDeleteNotificationData): CancelablePromise<NotificationsDeleteNotificationResponse> {
        return __request(OpenAPI, {
            method: 'DELETE',
            url: '/api/v1/notifications/{id}',
            path: {
                id: data.id
            },
            errors: {
                422: 'Validation Error'
            }
        });
    }
    
    /**
     * Mark Notification Read
     * Mark a notification as read.
     * @param data The data for the request.
     * @param data.id
     * @returns NotificationPublic Successful Response
     * @throws ApiError
     */
    public static markNotificationRead(data: NotificationsMarkNotificationReadData): CancelablePromise<NotificationsMarkNotificationReadResponse> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/notifications/{id}/mark-read',
            path: {
                id: data.id
            },
            errors: {
                422: 'Validation Error'
            }
        });
    }
    
    /**
     * Mark All Notifications Read
     * Mark all notifications as read for the current user.
     * @returns Message Successful Response
     * @throws ApiError
     */
    public static markAllNotificationsRead(): CancelablePromise<NotificationsMarkAllNotificationsReadResponse> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/notifications/mark-all-read',
            errors: {
                422: 'Validation Error'
            }
        });
    }
}
