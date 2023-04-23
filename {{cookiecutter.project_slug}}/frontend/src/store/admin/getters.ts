import { AdminState } from './state';
import { getStoreAccessors } from 'typesafe-vuex';
import { State } from '../state';

export const getters = {
    adminUsers: (state: AdminState) => state.users,
    adminOneUser: (state: AdminState) => (userId: number) => {
        const filteredUsers = state.users.filter((user) => user.id === userId);
        if (filteredUsers.length > 0) {
            return { ...filteredUsers[0] };
        }
    },
    adminRoles: (state: AdminState) => state.roles,
    adminOneRole: (state: AdminState) => (roleId: number) => {
        const filteredRoles = state.roles.filter((role) => role.id === roleId);
        if (filteredRoles.length > 0) {
            return { ...filteredRoles[0] };
        }
    },
    adminPermissions: (state: AdminState) => state.permissions,
    adminOnePermission: (state: AdminState) => (permissionId: number) => {
        const filteredPermissions = state.permissions.filter((permission) => permission.id === permissionId);
        if (filteredPermissions.length > 0) {
            return { ...filteredPermissions[0] };
        }
    },
};

const { read } = getStoreAccessors<AdminState, State>('');

export const readAdminOneUser = read(getters.adminOneUser);
export const readAdminUsers = read(getters.adminUsers);
export const readAdminRoles = read(getters.adminRoles);
export const readAdminOneRole = read(getters.adminOneRole);
export const readAdminPermissions = read(getters.adminPermissions);
export const readAdminOnePermission = read(getters.adminOnePermission);

