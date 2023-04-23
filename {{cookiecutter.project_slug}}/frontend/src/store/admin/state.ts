import {IPermission, IRole, IUserProfile} from '@/interfaces';

export interface AdminState {
    users: IUserProfile[];
    roles: IRole[];
    permissions: IPermission[];
}
