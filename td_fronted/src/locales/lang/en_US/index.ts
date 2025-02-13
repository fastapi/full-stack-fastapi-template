import merge from 'lodash/merge';
import componentsLocale from 'tdesign-vue-next/es/locale/en_US';

import components from './components';
import layout from './layout';
import pages from './pages';

export default {
  lang: 'English',
  layout,
  pages,
  components,
  constants: {
    contract: {
      name: 'Name',
      status: 'Status',
      num: 'Number',
      type: 'Type',
      typePlaceholder: 'Please enter type',
      payType: 'Pay Type',
      amount: 'Amount',
      amountPlaceholder: 'Please enter amount',
      signDate: 'Sign Date',
      effectiveDate: 'Effective Date',
      endDate: 'End Date',
      createDate: 'Create Date',
      attachment: 'Attachment',
      company: 'Company',
      employee: 'Employee',
      pay: 'pay',
      receive: 'received',
      remark: 'remark',
      statusOptions: {
        fail: 'Failure',
        auditPending: 'Pending audit',
        execPending: 'Pending performance',
        executing: 'Successful',
        finish: 'Finish',
      },
      typeOptions: {
        main: 'Master contract',
        sub: 'Subcontract',
        supplement: 'Supplementary contract',
      },
    },
  },
  componentsLocale: merge({}, componentsLocale, {
    // 可以在此处定义更多自定义配置，具体可配置内容参看 API 文档
    // https://tdesign.tencent.com/vue-next/config?tab=api
    // pagination: {
    //   jumpTo: 'xxx'
    // },
  }),
};
