import axios from 'axios';
import { apiUrl } from '@/env';
import {
  IUserProfile,
  IUserProfileUpdate,
  IUserProfileCreate,
  IRoleCreate,
  IRole,
  IRoleUpdate,
  IPermission, IPermissionUpdate,
} from './interfaces';

function authHeaders(token: string) {
  return {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  };
}

export const api = {
  async logInGetToken(username: string, password: string) {
    const params = new URLSearchParams();
    params.append('username', username);
    params.append('password', password);

    return axios.post(`${apiUrl}/api/v1/login/access-token`, params);
  },
  async getMe(token: string) {
    return axios.get<IUserProfile>(`${apiUrl}/api/v1/users/me`, authHeaders(token));
  },
  async updateMe(token: string, data: IUserProfileUpdate) {
    return axios.put<IUserProfile>(`${apiUrl}/api/v1/users/me`, data, authHeaders(token));
  },
  async getUsers(token: string) {
    return axios.get<IUserProfile[]>(`${apiUrl}/api/v1/users/`, authHeaders(token));
  },
  async updateUser(token: string, userId: number, data: IUserProfileUpdate) {
    return axios.put(`${apiUrl}/api/v1/users/${userId}`, data, authHeaders(token));
  },
  async createUser(token: string, data: IUserProfileCreate) {
    return axios.post(`${apiUrl}/api/v1/users/`, data, authHeaders(token));
  },
  async passwordRecovery(email: string) {
    return axios.post(`${apiUrl}/api/v1/password-recovery/${email}`);
  },
  async resetPassword(password: string, token: string) {
    return axios.post(`${apiUrl}/api/v1/reset-password/`, {
      new_password: password,
      token,
    });
  },
  async getRoles(token: string) {
    return axios.get<IRole[]>(`${apiUrl}/api/v1/roles/`, authHeaders(token));
  },
  async createRole(token: string, data: IRoleCreate) {
    return axios.post(`${apiUrl}/api/v1/roles/`, data, authHeaders(token));
  },
  async updateRole(token: string, roleId: number, data: IRoleUpdate) {
    return axios.put(`${apiUrl}/api/v1/roles/${roleId}`, data, authHeaders(token));
  },
  async getPermissions(token: string) {
    return axios.get<IPermission[]>(`${apiUrl}/api/v1/permissions/`, authHeaders(token));
  },
  async createPermission(token: string, data: IPermission) {
    return axios.post(`${apiUrl}/api/v1/permissions/`, data, authHeaders(token));
  },
  async updatePermission(token: string, permissionId: number, data: IPermissionUpdate) {
    return axios.put(`${apiUrl}/api/v1/permissions/${permissionId}`, data, authHeaders(token));
  },
};
