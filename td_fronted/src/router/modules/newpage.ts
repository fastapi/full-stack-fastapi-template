import Layout from '@/layouts/index.vue';

export default [
  {
    path: '/new',
    name: 'new',
    component: Layout,
    redirect: '/new_pages/index',
    meta: {
      title: {
        zh_CN: '新页面',
        en_US: 'new pages',
      },
      icon: 'circle',
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
    ],
  },
];
