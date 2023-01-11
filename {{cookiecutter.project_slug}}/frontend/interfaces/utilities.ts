/* eslint-disable camelcase */

export interface ITokenResponse {
  access_token: string
  refresh_token: string
  token_type: string
}

export interface IWebToken {
  claim: string
}

export interface INewTOTP {
  secret?: string
  key: string
  uri: string
}


export interface IEnableTOTP {
  claim: string
  uri: string
  password?: string
}

export interface ISendEmail {
  email: string
  subject: string
  content: string
}

export interface IMsg {
  msg: string
}

export interface INotification {
  uid?: string
  title: string
  content: string
  icon?: "success" | "error" | "information"
  showProgress?: boolean
}