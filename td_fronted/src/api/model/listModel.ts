export interface ListResult {
  list: Array<ListModel>;
}
export interface ListModel {
  adminName: string;
  amount: string;
  contractType: number;
  index: number;
  name: string;
  no: string;
  paymentType: number;
  status: number;
  updateTime: Date;
}

export interface CardListResult {
  list: Array<CardList>;
}
export interface CardList {
  banner: string;
  description: string;
  index: number;
  isSetup: boolean;
  name: string;
  type: number;
}
