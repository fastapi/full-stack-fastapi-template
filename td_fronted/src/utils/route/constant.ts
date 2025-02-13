export const LAYOUT = () => import('@/layouts/index.vue');
export const BLANK_LAYOUT = () => import('@/layouts/blank.vue');
export const IFRAME = () => import('@/layouts/components/FrameBlank.vue');
export const EXCEPTION_COMPONENT = () => import('@/pages/result/500/index.vue');
export const PARENT_LAYOUT = () =>
  new Promise((resolve) => {
    resolve({ name: 'ParentLayout' });
  });

export const PAGE_NOT_FOUND_ROUTE = {
  path: '/:w+',
  name: '404Page',
  redirect: '/result/404',
};
