import { Buffer } from "buffer"

function generateUUID(): string {
  // Reference: https://stackoverflow.com/a/2117523/709884
  // And: https://stackoverflow.com/a/61011303/295606
  return "10000000-1000-4000-8000-100000000000".replace(/[018]/g, (s) => {
    const c = Number.parseInt(s, 10)
    return (
      c ^
      (crypto.getRandomValues(new Uint8Array(1))[0] & (15 >> (c / 4)))
    ).toString(16)
  })
}

function isValidHttpUrl(urlString: string) {
  // https://stackoverflow.com/a/43467144
  let url
  try {
    url = new URL(urlString)
  } catch (_) {
    return false
  }
  return url.protocol === "http:" || url.protocol === "https:"
}

function getKeyByValue(object: any, value: any) {
  // https://stackoverflow.com/a/28191966/295606
  return Object.keys(object).find((key) => object[key] === value)
}

function getTimeInSeconds(): number {
  // https://stackoverflow.com/a/3830279/295606
  return Math.floor(new Date().getTime() / 1000)
}

function tokenExpired(token: string) {
  // https://stackoverflow.com/a/60758392/295606
  // https://stackoverflow.com/a/71953677/295606
  const expiry = JSON.parse(
    Buffer.from(token.split(".")[1], "base64").toString()
  ).exp
  return getTimeInSeconds() >= expiry
}

function tokenParser(token: string) {
  return JSON.parse(
    Buffer.from(token.split(".")[1], "base64").toString()
  )
}
  
  export {
    generateUUID,
    getTimeInSeconds,
    tokenExpired,
    getKeyByValue,
    isValidHttpUrl,
    tokenParser,
  }
  