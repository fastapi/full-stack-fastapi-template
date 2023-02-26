import { ISendEmail, IMsg } from "@/interfaces"
import { apiCore } from "./core"

export const apiService = {
  // USER CONTACT MESSAGE
  async postEmailContact(data: ISendEmail) {
    return await useFetch<IMsg>(`${apiCore.url()}/service/contact`, 
      {
        method: "POST",
        body: data,
      }
    )
  },
}