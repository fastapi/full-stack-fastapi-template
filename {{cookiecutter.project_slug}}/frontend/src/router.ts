import Vue from 'vue';
import Router from 'vue-router';

import RouterComponent from './components/RouterComponent.vue';

Vue.use(Router);

const router =  new Router({
  mode: 'history',
  base: process.env.BASE_URL,
  routes: [
    {
      path: '/',
      component: () => import(/* webpackChunkName: "start" */ './views/main/Start.vue'),
      children: [
        {
          path: 'login',
          // route level code-splitting
          // this generates a separate chunk (about.[hash].js) for this route
          // which is lazy-loaded when the route is visited.
          component: () => import(/* webpackChunkName: "login" */ './views/Login.vue'),
        },
        {
          path: 'recover-password',
          component: () => import(/* webpackChunkName: "recover-password" */ './views/PasswordRecovery.vue'),
        },
        {
          path: 'reset-password',
          component: () => import(/* webpackChunkName: "reset-password" */ './views/ResetPassword.vue'),
        },
        {
          path: 'main',
          component: () => import(/* webpackChunkName: "main" */ './views/main/Main.vue'),
          children: [
            {
              path: 'dashboard',
              component: () => import(/* webpackChunkName: "main-dashboard" */ './views/main/Dashboard.vue'),
            },
            {
              path: 'profile',
              component: RouterComponent,
              redirect: 'profile/view',
              children: [
                {
                  path: 'view',
                  component: () => import(
                    /* webpackChunkName: "main-profile" */ './views/main/profile/UserProfile.vue'),
                },
                {
                  path: 'edit',
                  component: () => import(
                    /* webpackChunkName: "main-profile-edit" */ './views/main/profile/UserProfileEdit.vue'),
                },
                {
                  path: 'password',
                  component: () => import(
                    /* webpackChunkName: "main-profile-password" */ './views/main/profile/UserProfileEditPassword.vue'),
                },
              ],
            },
            {
              path: 'admin',
              component: () => import(/* webpackChunkName: "main-admin" */ './views/main/admin/Admin.vue'),
              redirect: 'admin/users/all',
              children: [
                {
                  path: 'users',
                  redirect: 'users/all',
                },
                {
                  path: 'users/all',
                  component: () => import(
                    /* webpackChunkName: "main-admin-users" */ './views/main/admin/AdminUsers.vue'),
                },
                {
                  path: 'users/edit/:id',
                  name: 'main-admin-users-edit',
                  component: () => import(
                    /* webpackChunkName: "main-admin-users-edit" */ './views/main/admin/EditUser.vue'),
                },
                {
                  path: 'users/create',
                  name: 'main-admin-users-create',
                  component: () => import(
                    /* webpackChunkName: "main-admin-users-create" */ './views/main/admin/CreateUser.vue'),
                },
                //   ROLES
                {
                  path: 'roles',
                  redirect: 'roles/all'
                },
                {
                  path: 'roles/all',
                  component: () => import('./views/main/admin/AdminRoles.vue'),
                },
                {
                  path: 'roles/edit/:id',
                  name: 'main-admin-roles-edit',
                  component: () => import(
                    /* webpackChunkName: "main-admin-users-edit" */ './views/main/admin/EditRole.vue'),
                },
                {
                  path: 'roles/create',
                  name: 'main-admin-roles-create',
                  component: () => import(
                    /* webpackChunkName: "main-admin-users-create" */ './views/main/admin/CreateRole.vue'),
                },
                //   PERMISSIONS
                {
                  path: 'permissions',
                  redirect: 'permissions/all'
                },
                {
                  path: 'permissions/all',
                  component: () => import('./views/main/admin/AdminPermissions.vue'),
                },
                {
                  path: 'permissions/edit/:id',
                  name: 'main-admin-permissions-edit',
                  component: () => import(
                    /* webpackChunkName: "main-admin-users-edit" */ './views/main/admin/EditPermission.vue'),
                },
                {
                  path: 'permissions/create',
                  name: 'main-admin-permissions-create',
                  component: () => import(
                    /* webpackChunkName: "main-admin-users-create" */ './views/main/admin/CreatePermission.vue'),
                },
              ],
            },
          ],
        },
      ],
    },
    {
      path: '/*', redirect: '/',
    },
  ],
});

router.beforeEach((to, from, next) => {
  console.log('Hit the route, Jack!', to);
  return next();
});

export default router;
