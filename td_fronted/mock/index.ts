import Mock from 'mockjs';
import { MockMethod } from 'vite-plugin-mock';

export default [
  {
    url: '/api/get-purchase-list',
    method: 'get',
    response: () => ({
      code: 0,
      data: {
        ...Mock.mock({
          'list|1-100': [
            {
              index: /S20201228115950[0-9][0-9][0-9]/,
              pdName: 'Macbook',
              pdNum: 'p_tmp_60a637cd0d',
              'purchaseNum|1-100': 100,
              adminName: '财务部111',
              updateTime: '2020-05-20@date("HH:mm:ss")',
              pdType: '电子产品',
            },
            {
              index: /S20201228115950[0-9][0-9][0-9]/,
              pdName: 'Macbook',
              pdNum: 'p_tmp_60a637cd0d',
              'purchaseNum|1-100': 100,
              adminName: '财务部',
              updateTime: '2020-05-20@date("HH:mm:ss")',
            },
          ],
        }),
      },
    }),
  },
  {
    url: '/api/get-list',
    method: 'get',
    response: () => ({
      code: 0,
      data: {
        ...Mock.mock({
          'list|1-100': [
            {
              'index|+1': 1,
              'status|1': '@natural(0, 4)',
              no: 'BH00@natural(01, 100)',
              name: '@city()办公用品采购项目',
              'paymentType|1': '@natural(0, 1)',
              'contractType|1': '@natural(0, 2)',
              updateTime: '2020-05-30 @date("HH:mm:ss")',
              amount: '@natural(10, 500),000,000',
              adminName: '@cname()',
            },
          ],
        }),
      },
    }),
  },
  {
    url: '/api/detail-basic',
    method: 'get',
    response: () => ({
      code: 0,
      data: {
        ...Mock.mock({
          name: 'td_20023747',
          loginType: 'Web',
          currentRole: 'Admin',
          rightsList: '通用权限',
          userStatus: '启用',
          language: '简体中文',
          timeZone: '(GMT+08:00)中国时区—北京（Asia/Beijing）',
        }),
      },
    }),
  },
  {
    url: '/api/get-card-list',
    method: 'get',
    response: () => ({
      code: 0,
      data: {
        ...Mock.mock({
          'list|48-50': [
            {
              'index|+1': 1,
              isSetup: '@boolean',
              'type|1': '@natural(1, 5)',
              'banner|1': [
                'https://tdesign.gtimg.com/starter/cloud-db.jpg',
                'https://tdesign.gtimg.com/starter/cloud-server.jpg',
                'https://tdesign.gtimg.com/starter/ssl.jpg',
                'https://tdesign.gtimg.com/starter/t-sec.jpg',
                'https://tdesign.gtimg.com/starter/face-recognition.jpg',
              ],
              'name|1': ['人脸识别', 'SSL证书', 'CVM', '云数据库', 'T-Sec 云防火墙'],
              'description|1': [
                '基于腾讯优图强大的面部分析技术，提供包括人脸检测与分析、五官定位、人脸搜索、人脸比对、人脸',
                '云硬盘为您提供用于CVM的持久性数据块级存储服务。云硬盘中的数据自动地可用区内以多副本冗',
                'SSL证书又叫服务器证书，腾讯云为您提供证书的一站式服务，包括免费、付费证书的申请、管理及部',
                '腾讯安全云防火墙产品，是腾讯云安全团队结合云原生的优势，自主研发的SaaS化防火墙产品，无需客无需客无需客无需客无需客无需客无需客',
                '云数据库MySQL为用户提供安全可靠，性能卓越、易于维护的企业级云数据库服务。',
              ],
            },
          ],
        }),
      },
    }),
  },
  {
    url: '/api/get-project-list',
    method: 'get',
    response: () => ({
      code: 0,
      data: {
        ...Mock.mock({
          'list|1-50': [
            {
              'index|+1': 1,
              adminPhone: '+86 13587609955',
              updateTime: '2020-05-30 @date("HH:mm:ss")',
              'adminName|1': ['顾娟	', '常刚', '郑洋'],
              'name|1': [
                '沧州市办公用品采购项目',
                '红河哈尼族彝族自治州办公用品采购项目	',
                '铜川市办公用品采购项目',
                '陇南市办公用品采购项目	',
                '六安市办公用品采购项目	 ',
              ],
            },
          ],
        }),
      },
    }),
  },
  {
    url: '/api/post',
    method: 'post',
    timeout: 2000,
    response: {
      code: 0,
      data: {
        name: 'vben',
      },
    },
  },
  {
    url: '/api/get-menu-list-i18n',
    method: 'get',
    timeout: 2000,
    response: {
      code: 0,
      data: {
        ...Mock.mock({
          list: [
            {
              path: '/list',
              name: 'list',
              component: 'LAYOUT',
              redirect: '/list/base',
              meta: {
                title: {
                  zh_CN: '列表页',
                  en_US: 'List',
                },
                icon: 'view-list',
              },
              children: [
                {
                  path: 'base',
                  name: 'ListBase',
                  component: '/list/base/index',
                  meta: {
                    title: {
                      zh_CN: '基础列表页',
                      en_US: 'Base List',
                    },
                  },
                },
                {
                  path: 'card',
                  name: 'ListCard',
                  component: '/list/card/index',
                  meta: {
                    title: {
                      zh_CN: '卡片列表页',
                      en_US: 'Card List',
                    },
                  },
                },
                {
                  path: 'filter',
                  name: 'ListFilter',
                  component: '/list/filter/index',
                  meta: {
                    title: {
                      zh_CN: '筛选列表页',
                      en_US: 'Filter List',
                    },
                  },
                },
                {
                  path: 'tree',
                  name: 'ListTree',
                  component: '/list/tree/index',
                  meta: {
                    title: {
                      zh_CN: '树状筛选列表页',
                      en_US: 'Tree List',
                    },
                  },
                },
              ],
            },
            {
              path: '/form',
              name: 'form',
              component: 'LAYOUT',
              redirect: '/form/base',
              meta: {
                title: {
                  zh_CN: '表单页',
                  en_US: 'Form',
                },
                icon: 'edit-1',
              },
              children: [
                {
                  path: 'base',
                  name: 'FormBase',
                  component: '/form/base/index',
                  meta: {
                    title: {
                      zh_CN: '基础表单页',
                      en_US: 'Base Form',
                    },
                  },
                },
                {
                  path: 'step',
                  name: 'FormStep',
                  component: '/form/step/index',
                  meta: {
                    title: {
                      zh_CN: '分步表单页',
                      en_US: 'Step Form',
                    },
                  },
                },
              ],
            },
            {
              path: '/detail',
              name: 'detail',
              component: 'LAYOUT',
              redirect: '/detail/base',
              meta: {
                title: {
                  zh_CN: '详情页',
                  en_US: 'Detail',
                },
                icon: 'layers',
              },
              children: [
                {
                  path: 'base',
                  name: 'DetailBase',
                  component: '/detail/base/index',
                  meta: {
                    title: {
                      zh_CN: '基础详情页',
                      en_US: 'Base Detail',
                    },
                  },
                },
                {
                  path: 'advanced',
                  name: 'DetailAdvanced',
                  component: '/detail/advanced/index',
                  meta: {
                    title: {
                      zh_CN: '多卡片详情页',
                      en_US: 'Card Detail',
                    },
                  },
                },
                {
                  path: 'deploy',
                  name: 'DetailDeploy',
                  component: '/detail/deploy/index',
                  meta: {
                    title: {
                      zh_CN: '数据详情页',
                      en_US: 'Data Detail',
                    },
                  },
                },
                {
                  path: 'secondary',
                  name: 'DetailSecondary',
                  component: '/detail/secondary/index',
                  meta: {
                    title: {
                      zh_CN: '二级详情页',
                      en_US: 'Secondary Detail',
                    },
                  },
                },
              ],
            },
            {
              path: '/frame',
              name: 'Frame',
              component: 'Layout',
              redirect: '/frame/doc',
              meta: {
                icon: 'internet',
                title: {
                  zh_CN: '外部页面',
                  en_US: 'External',
                },
              },
              children: [
                {
                  path: 'doc',
                  name: 'Doc',
                  component: 'IFrame',
                  meta: {
                    frameSrc: 'https://tdesign.tencent.com/starter/docs/vue-next/get-started',
                    title: {
                      zh_CN: '使用文档（内嵌）',
                      en_US: 'Documentation(IFrame)',
                    },
                  },
                },
                {
                  path: 'TDesign',
                  name: 'TDesign',
                  component: 'IFrame',
                  meta: {
                    frameSrc: 'https://tdesign.tencent.com/vue-next/getting-started',
                    title: {
                      zh_CN: 'TDesign 文档（内嵌）',
                      en_US: 'TDesign (IFrame)',
                    },
                  },
                },
                {
                  path: 'TDesign2',
                  name: 'TDesign2',
                  component: 'IFrame',
                  meta: {
                    frameSrc: 'https://tdesign.tencent.com/vue-next/getting-started',
                    frameBlank: true,
                    title: {
                      zh_CN: 'TDesign 文档（外链',
                      en_US: 'TDesign Doc(Link)',
                    },
                  },
                },
              ],
            },
          ],
        }),
      },
    },
  },
] as MockMethod[];
