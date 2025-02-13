import componentsLocale from 'tdesign-vue-next/es/locale/zh_CN';

import components from './components';
import layout from './layout';
import pages from './pages';

export default {
  lang: '简体中文',
  layout,
  pages,
  components,
  constants: {
    contract: {
      name: '合同名称',
      status: '合同状态',
      num: '合同编号',
      type: '合同类型',
      typePlaceholder: '请输入类型',
      payType: '合同收支类型',
      amount: '合同金额',
      amountPlaceholder: '请输入金额',
      signDate: '合同签订日期',
      effectiveDate: '合同生效日期',
      endDate: '合同结束日期',
      createDate: '合同创建时间',
      company: '甲方',
      employee: '乙方',
      pay: '付款',
      receive: '收款',
      remark: '备注',
      attachment: '附件',
      statusOptions: {
        fail: '审核失败',
        auditPending: '待审核',
        execPending: '待履行',
        executing: '审核成功',
        finish: '已完成',
      },
      typeOptions: {
        main: '主合同',
        sub: '子合同',
        supplement: '补充合同',
      },
    },
  },
  componentsLocale,
};
