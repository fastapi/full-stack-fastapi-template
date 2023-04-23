import { api } from '@/api';
import { ActionContext } from 'vuex';
import {
    IPermission,
    IPermissionUpdate,
    IRoleCreate,
    IRoleUpdate,
    IUserProfileCreate,
    IUserProfileUpdate
} from '@/interfaces';
import { State } from '../state';
import { AdminState } from './state';
import { getStoreAccessors } from 'typesafe-vuex';
import {
    commitSetUsers,
    commitSetUser,
    commitRoles,
    commitSetRole,
    commitPermissions,
    commitSetPermission
} from './mutations';
import { dispatchCheckApiError } from '../main/actions';
import { commitAddNotification, commitRemoveNotification } from '../main/mutations';

type MainContext = ActionContext<AdminState, State>;

export const actions = {
    async actionGetUsers(context: MainContext) {
        try {
            const response = await api.getUsers(context.rootState.main.token);
            if (response) {
                commitSetUsers(context, response.data);
            }
        } catch (error) {
            await dispatchCheckApiError(context, error);
        }
    },
    async actionUpdateUser(context: MainContext, payload: { id: number, user: IUserProfileUpdate }) {
        try {
            const loadingNotification = { content: 'saving', showProgress: true };
            commitAddNotification(context, loadingNotification);
            const response = (await Promise.all([
                api.updateUser(context.rootState.main.token, payload.id, payload.user),
                await new Promise((resolve, reject) => setTimeout(() => resolve(), 500)),
            ]))[0];
            commitSetUser(context, response.data);
            commitRemoveNotification(context, loadingNotification);
            commitAddNotification(context, { content: 'User successfully updated', color: 'success' });
        } catch (error) {
            await dispatchCheckApiError(context, error);
        }
    },
    async actionCreateUser(context: MainContext, payload: IUserProfileCreate) {
        try {
            const loadingNotification = { content: 'saving', showProgress: true };
            commitAddNotification(context, loadingNotification);
            const response = (await Promise.all([
                api.createUser(context.rootState.main.token, payload),
                await new Promise((resolve, reject) => setTimeout(() => resolve(), 500)),
            ]))[0];
            commitSetUser(context, response.data);
            commitRemoveNotification(context, loadingNotification);
            commitAddNotification(context, { content: 'User successfully created', color: 'success' });
        } catch (error) {
            await dispatchCheckApiError(context, error);
        }
    },
    async actionGetRoles(context: MainContext) {
        try {
            const response = await api.getRoles(context.rootState.main.token);
            if (response) {
                commitRoles(context, response.data);
            }
        } catch (error) {
            await dispatchCheckApiError(context, error);
        }
    },
    async actionCreateRole(context: MainContext, payload: IRoleCreate){
        try {
            const loadingNotification = { content: 'saving', showProgress: true };
            commitAddNotification(context, loadingNotification);
            const response = (await Promise.all([
                api.createRole(context.rootState.main.token, payload),
                await new Promise((resolve, reject) => setTimeout(() => resolve(), 500)),
            ]))[0];
            commitSetUser(context, response.data);
            commitRemoveNotification(context, loadingNotification);
            commitAddNotification(context, { content: 'User successfully created', color: 'success' });
        } catch (error) {
            await dispatchCheckApiError(context, error);
        }
    },
    async actionUpdateRole(context: MainContext, payload: { id: number, role: IRoleUpdate }) {
        try {
            const loadingNotification = { content: 'saving', showProgress: true };
            commitAddNotification(context, loadingNotification);
            const response = (await Promise.all([
                api.updateRole(context.rootState.main.token, payload.id, payload.role),
                await new Promise((resolve, reject) => setTimeout(() => resolve(), 500)),
            ]))[0];
            commitSetRole(context, response.data);
            commitRemoveNotification(context, loadingNotification);
            commitAddNotification(context, { content: 'Role successfully updated', color: 'success' });
        } catch (error) {
            await dispatchCheckApiError(context, error);
        }
    },
    async actionGetPermissions(context: MainContext) {
        try {
            const response = await api.getPermissions(context.rootState.main.token);
            if (response) {
                commitPermissions(context, response.data);
            }
        } catch (error) {
            await dispatchCheckApiError(context, error);
        }
    },
    async actionCreatePermission(context: MainContext, payload: IPermission){
        try {
            const loadingNotification = { content: 'saving', showProgress: true };
            commitAddNotification(context, loadingNotification);
            const response = (await Promise.all([
                api.createPermission(context.rootState.main.token, payload),
                await new Promise((resolve, reject) => setTimeout(() => resolve(), 500)),
            ]))[0];
            commitSetPermission(context, response.data);
            commitRemoveNotification(context, loadingNotification);
            commitAddNotification(context, { content: 'Permission successfully created', color: 'success' });
        } catch (error) {
            await dispatchCheckApiError(context, error);
        }
    },
    async actionUpdatePermission(context: MainContext, payload: { id: number, permission: IPermissionUpdate }) {
        try {
            const loadingNotification = { content: 'saving', showProgress: true };
            commitAddNotification(context, loadingNotification);
            const response = (await Promise.all([
                api.updatePermission(context.rootState.main.token, payload.id, payload.permission),
                await new Promise((resolve, reject) => setTimeout(() => resolve(), 500)),
            ]))[0];
            commitSetPermission(context, response.data);
            commitRemoveNotification(context, loadingNotification);
            commitAddNotification(context, { content: 'Permission successfully updated', color: 'success' });
        } catch (error) {
            await dispatchCheckApiError(context, error);
        }
    },
};

const { dispatch } = getStoreAccessors<AdminState, State>('');

export const dispatchCreateUser = dispatch(actions.actionCreateUser);
export const dispatchGetUsers = dispatch(actions.actionGetUsers);
export const dispatchUpdateUser = dispatch(actions.actionUpdateUser);
export const dispatchGetRoles = dispatch(actions.actionGetRoles);
export const dispatchCreateRole = dispatch(actions.actionCreateRole)
export const dispatchUpdateRole = dispatch(actions.actionUpdateRole)
export const dispatchGetPermissions = dispatch(actions.actionGetPermissions)
export const dispatchCreatePermission = dispatch(actions.actionCreatePermission);
export const dispatchUpdatePermission = dispatch(actions.actionUpdatePermission);
