// 合同状态枚举
export const CONTRACT_STATUS = {
  FAIL: 0,
  AUDIT_PENDING: 1,
  EXEC_PENDING: 2,
  EXECUTING: 3,
  FINISH: 4,
};

// 合同类型枚举
export const CONTRACT_TYPES = {
  MAIN: 0,
  SUB: 1,
  SUPPLEMENT: 2,
};

// 合同收付类型枚举
export const CONTRACT_PAYMENT_TYPES = {
  PAYMENT: 0,
  RECEIPT: 1,
};

// 标签类型
type TagTheme = 'default' | 'success' | 'primary' | 'warning' | 'danger';
// 通知的优先级对应的标签类型
export const NOTIFICATION_TYPES: Map<string, TagTheme> = new Map([
  ['low', 'primary'],
  ['middle', 'warning'],
  ['high', 'danger'],
]);

// 通用请求头
export enum ContentTypeEnum {
  Json = 'application/json;charset=UTF-8',
  FormURLEncoded = 'application/x-www-form-urlencoded;charset=UTF-8',
  FormData = 'multipart/form-data;charset=UTF-8',
}
