import {
  IUserProfile,
  IUserProfileUpdate,
  IUserProfileCreate,
  IUserOpenProfileCreate
} from "./profile"

import {
  ITokenResponse,
  IWebToken,
  INewTOTP,
  IEnableTOTP,
  ISendEmail,
  IMsg,
  INotification
} from "./utilities"

// https://stackoverflow.com/a/64782482/295606
interface IKeyable {
  [key: string]: any | any[]
}
  
export {
  IKeyable,
  IUserProfile,
  IUserProfileUpdate,
  IUserProfileCreate,
  IUserOpenProfileCreate,
  ITokenResponse,
  IWebToken,
  INewTOTP,
  IEnableTOTP,
  ISendEmail,
  IMsg,
  INotification
}