import { t } from '@/locales';

export const BASE_INFO_DATA = [
  {
    name: t('constants.contract.name'),
    value: '总部办公用品采购项目',
    type: null,
  },
  {
    name: t('constants.contract.status'),
    value: '履行中',
    type: {
      key: 'contractStatus',
      value: 'inProgress',
    },
  },
  {
    name: t('constants.contract.num'),
    value: 'BH00010',
    type: null,
  },
  {
    name: t('constants.contract.type'),
    value: t('constants.contract.typeOptions.main'),
    type: null,
  },
  {
    name: t('constants.contract.payType'),
    value: t('constants.contract.pay'),
    type: null,
  },
  {
    name: t('constants.contract.amount'),
    value: '¥ 5,000,000',
    type: null,
  },
  {
    name: t('constants.contract.company'),
    value: '腾讯科技（深圳）有限公司',
    type: null,
  },
  {
    name: t('constants.contract.employee'),
    value: '欧尚',
    type: null,
  },
  {
    name: t('constants.contract.signDate'),
    value: '2020-12-20',
    type: null,
  },
  {
    name: t('constants.contract.effectiveDate'),
    value: '2021-01-20',
    type: null,
  },
  {
    name: t('constants.contract.endDate'),
    value: '2022-12-20',
    type: null,
  },
  {
    name: t('constants.contract.attachment'),
    value: '总部办公用品采购项目合同.pdf',
    type: {
      key: 'contractAnnex',
      value: 'pdf',
    },
  },
  {
    name: t('constants.contract.remark'),
    value: '--',
    type: null,
  },
  {
    name: t('constants.contract.createDate'),
    value: '2020-12-22 10:00:00',
    type: null,
  },
];

export const PRODUCT_LIST = [
  {
    name: 'MacBook Pro 2021',
    subtitle: '苹果公司（Apple Inc. ）',
    size: '13.3 英寸',
    cpu: 'Apple M1',
    memory: 'RAM 16GB',
    info: '最高可选配 16GB 内存 · 最高可选配 2TB 存储设备 电池续航最长达 18 小时',
    use: 1420,
    stock: 1500,
  },
  {
    name: 'Surface Laptop Go',
    subtitle: '微软（Microsoft Corporation）',
    size: '12.4 英寸',
    cpu: 'Core i7',
    memory: 'RAM 16GB',
    info: '常规使用 Surface，续航时间最长可达13小时 随时伴您工作',
    use: 120,
    stock: 2000,
  },
];
