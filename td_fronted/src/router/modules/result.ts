import Layout from '@/layouts/index.vue';

export default [
  {
    path: '/result',
    name: 'result',
    component: Layout,
    redirect: '/result/success',
    meta: {
      title: {
        zh_CN: '结果页',
        en_US: 'Result',
      },
      icon: 'check-circle',
    },
    children: [
      {
        path: 'success',
        name: 'ResultSuccess',
        component: () => import('@/pages/result/success/index.vue'),
        meta: {
          title: {
            zh_CN: '成功页',
            en_US: 'Success',
          },
        },
      },
      {
        path: 'fail',
        name: 'ResultFail',
        component: () => import('@/pages/result/fail/index.vue'),
        meta: {
          title: {
            zh_CN: '失败页',
            en_US: 'Fail',
          },
        },
      },
      {
        path: 'network-error',
        name: 'ResultNetworkError',
        component: () => import('@/pages/result/network-error/index.vue'),
        meta: {
          title: {
            zh_CN: '网络异常',
            en_US: 'Network Error',
          },
        },
      },
      {
        path: '403',
        name: 'Result403',
        component: () => import('@/pages/result/403/index.vue'),
        meta: { title: { zh_CN: '无权限', en_US: 'Forbidden' } },
      },
      {
        path: '404',
        name: 'Result404',
        component: () => import('@/pages/result/404/index.vue'),
        meta: { title: { zh_CN: '访问页面不存在页', en_US: 'Not Found' } },
      },
      {
        path: '500',
        name: 'Result500',
        component: () => import('@/pages/result/500/index.vue'),
        meta: { title: { zh_CN: '服务器出错页', en_US: 'Server Error' } },
      },
      {
        path: 'browser-incompatible',
        name: 'ResultBrowserIncompatible',
        component: () => import('@/pages/result/browser-incompatible/index.vue'),
        meta: { title: { zh_CN: '浏览器不兼容页', en_US: 'BrowserIncompatible' } },
      },
      {
        path: 'maintenance',
        name: 'ResultMaintenance',
        component: () => import('@/pages/result/maintenance/index.vue'),
        meta: { title: { zh_CN: '系统维护页', en_US: 'Maintenance' } },
      },
    ],
  },
];
