export interface IUserProfile {
    email: string;
    is_active: boolean;
    is_superuser: boolean;
    full_name: string;
    id: number;
}

export interface IUserProfileUpdate {
    email?: string;
    full_name?: string;
    password?: string;
    is_active?: boolean;
    is_superuser?: boolean;
}

export interface IUserProfileCreate {
    email: string;
    full_name?: string;
    password?: string;
    is_active?: boolean;
    is_superuser?: boolean;
}

export interface IRole {
    id: number;
    name: string;
    description?: string;
    pms?: object;
}

export interface IRoleUpdate {
    id?: number;
    name?: string;
    description?: string;
    pms?: object;
}

export interface IRoleCreate {
    name: string;
    description?: string;
    pms?: object;
}

export interface IPermission {
    id?: number;
    object: string;
    role_id: object;
    permissions?: object;
}

export interface IPermissionUpdate {
    id?: number;
    object?: string;
    role_id?: object;
    permissions?: object;
}
