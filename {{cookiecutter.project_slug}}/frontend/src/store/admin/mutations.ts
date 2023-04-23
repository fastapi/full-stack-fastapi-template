import {IPermission, IRole, IUserProfile} from '@/interfaces';
import { AdminState } from './state';
import { getStoreAccessors } from 'typesafe-vuex';
import { State } from '../state';

export const mutations = {
    setUsers(state: AdminState, payload: IUserProfile[]) {
        state.users = payload;
    },
    setUser(state: AdminState, payload: IUserProfile) {
        const users = state.users.filter((user: IUserProfile) => user.id !== payload.id);
        users.push(payload);
        state.users = users;
    },
    setRoles(state: AdminState, payload: IRole[]) {
        state.roles = payload;
    },
    setRole(state: AdminState, payload: IRole) {
        const roles = state.roles.filter((role: IRole) => role.id !== payload.id);
        roles.push(payload);
        state.roles = roles;
    },
    setPermissions(state: AdminState, payload: IPermission[]) {
        state.permissions = payload;
    },
    setPermission(state: AdminState, payload: IPermission) {
        const permissions = state.permissions.filter((permission: IPermission) => permission.id !== payload.id);
        permissions.push(payload);
        state.permissions = permissions;
    },
};

const { commit } = getStoreAccessors<AdminState, State>('');

export const commitSetUser = commit(mutations.setUser);
export const commitSetUsers = commit(mutations.setUsers);
export const commitRoles = commit(mutations.setRoles);
export const commitSetRole = commit(mutations.setRole);
export const commitPermissions = commit(mutations.setPermissions);
export const commitSetPermission = commit(mutations.setPermission);
