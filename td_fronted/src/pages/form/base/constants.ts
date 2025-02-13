import type { FormRule, UploadFile } from 'tdesign-vue-next';

export const FORM_RULES: Record<string, FormRule[]> = {
  name: [{ required: true, message: '请输入合同名称', type: 'error' }],
  type: [{ required: true, message: '请选择合同类型', type: 'error' }],
  payment: [{ required: true, message: '请选择合同收付类型', type: 'error' }],
  amount: [{ required: true, message: '请输入合同金额', type: 'error' }],
  partyA: [{ required: true, message: '请选择甲方', type: 'error' }],
  partyB: [{ required: true, message: '请选择乙方', type: 'error' }],
  signDate: [{ required: true, message: '请选择日期', type: 'error' }],
  startDate: [{ required: true, message: '请选择日期', type: 'error' }],
  endDate: [{ required: true, message: '请选择日期', type: 'error' }],
};

export const INITIAL_DATA = {
  name: '',
  type: '',
  partyA: '',
  partyB: '',
  signDate: '',
  startDate: '',
  endDate: '',
  payment: '1',
  amount: 0,
  comment: '',
  files: [] as Array<UploadFile>,
};

export const TYPE_OPTIONS = [
  { label: 'Type A', value: '1' },
  { label: 'Type B', value: '2' },
  { label: 'Type C', value: '3' },
];

export const PARTY_A_OPTIONS = [
  { label: 'Company A', value: '1' },
  { label: 'Company B', value: '2' },
  { label: 'Company C', value: '3' },
];

export const PARTY_B_OPTIONS = [
  { label: 'Company A', value: '1' },
  { label: 'Company B', value: '2' },
  { label: 'Company C', value: '3' },
];
