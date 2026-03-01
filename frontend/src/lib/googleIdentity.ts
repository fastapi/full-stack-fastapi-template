type GoogleCredentialResponse = {
  credential?: string
}

type GoogleAccountsId = {
  initialize: (config: {
    client_id: string
    callback: (response: GoogleCredentialResponse) => void
  }) => void
  renderButton: (
    element: HTMLElement,
    options: Record<string, string | number | boolean>,
  ) => void
}

type GoogleWindow = Window & {
  google?: {
    accounts?: {
      id?: GoogleAccountsId
    }
  }
}

let googleScriptPromise: Promise<void> | null = null

export const loadGoogleIdentityScript = () => {
  if (typeof window === "undefined") {
    return Promise.reject(
      new Error("Google Identity is only available in browser"),
    )
  }

  const existing = (window as GoogleWindow).google?.accounts?.id
  if (existing) return Promise.resolve()

  if (googleScriptPromise) return googleScriptPromise

  googleScriptPromise = new Promise<void>((resolve, reject) => {
    const existingScript = document.querySelector<HTMLScriptElement>(
      'script[src="https://accounts.google.com/gsi/client"]',
    )
    if (existingScript) {
      existingScript.addEventListener("load", () => resolve(), { once: true })
      existingScript.addEventListener(
        "error",
        () => reject(new Error("Failed to load Google Identity script")),
        { once: true },
      )
      return
    }

    const script = document.createElement("script")
    script.src = "https://accounts.google.com/gsi/client"
    script.async = true
    script.defer = true
    script.onload = () => resolve()
    script.onerror = () =>
      reject(new Error("Failed to load Google Identity script"))
    document.head.appendChild(script)
  })

  return googleScriptPromise
}

export const renderGoogleSignInButton = async ({
  container,
  clientId,
  onCredential,
}: {
  container: HTMLElement
  clientId: string
  onCredential: (idToken: string) => void
}) => {
  await loadGoogleIdentityScript()

  const googleId = (window as GoogleWindow).google?.accounts?.id
  if (!googleId) {
    throw new Error("Google Identity SDK not available after script load")
  }

  googleId.initialize({
    client_id: clientId,
    callback: (response) => {
      if (response.credential) {
        onCredential(response.credential)
      }
    },
  })

  container.innerHTML = ""
  googleId.renderButton(container, {
    theme: "outline",
    size: "large",
    text: "signin_with",
    shape: "rectangular",
    width: Math.max(container.clientWidth || 320, 240),
  })
}
