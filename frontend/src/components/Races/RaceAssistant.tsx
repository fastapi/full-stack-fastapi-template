import { useState, useRef, useEffect } from "react"
import { MessageCircle, X, Send, Bot } from "lucide-react"
import { cn } from "@/lib/utils"
import { OpenAPI } from "@/client"
import { request as __request } from "@/client/core/request"

interface Message {
  role: "user" | "assistant"
  text: string
}

const SEED_QUESTIONS = [
  "Is this race beginner-friendly?",
  "What terrain should I expect?",
  "What's the elevation gain?",
  "Are there cutoff times?",
]

interface RaceAssistantProps {
  raceId: string
}

export function RaceAssistant({ raceId }: RaceAssistantProps) {
  const [open, setOpen] = useState(false)
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState("")
  const [loading, setLoading] = useState(false)
  const [rateLimited, setRateLimited] = useState(false)
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (open) bottomRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [messages, open])

  const sendMessage = async (question: string) => {
    if (!question.trim() || loading) return

    const userMsg: Message = { role: "user", text: question }
    setMessages((prev) => [...prev, userMsg])
    setInput("")
    setLoading(true)
    setRateLimited(false)

    try {
      const response = await __request(OpenAPI, {
        method: "POST",
        url: `/api/v1/races/${raceId}/ask`,
        body: { question },
        mediaType: "application/json",
      }) as { answer: string }

      setMessages((prev) => [
        ...prev,
        { role: "assistant", text: response.answer },
      ])
    } catch (error: unknown) {
      const status = (error as { status?: number })?.status
      if (status === 429) {
        setRateLimited(true)
        setMessages((prev) => [
          ...prev,
          {
            role: "assistant",
            text: "You're asking too fast! Please wait a moment before asking another question.",
          },
        ])
      } else {
        setMessages((prev) => [
          ...prev,
          { role: "assistant", text: "Sorry, I couldn't answer that right now. Please try again." },
        ])
      }
    } finally {
      setLoading(false)
    }
  }

  return (
    <>
      {/* Floating button */}
      <button
        onClick={() => setOpen(true)}
        className={cn(
          "fixed bottom-6 right-6 z-50 flex size-14 items-center justify-center rounded-full bg-primary text-primary-foreground shadow-lg transition-transform hover:scale-105",
          open && "hidden"
        )}
        title="Ask about this race"
      >
        <MessageCircle className="size-6" />
      </button>

      {/* Chat panel */}
      {open && (
        <div className="fixed bottom-6 right-6 z-50 flex w-80 flex-col rounded-xl border bg-background shadow-2xl sm:w-96">
          {/* Header */}
          <div className="flex items-center justify-between border-b px-4 py-3">
            <div className="flex items-center gap-2">
              <Bot className="size-5 text-primary" />
              <span className="font-semibold text-sm">Race Assistant</span>
            </div>
            <button
              onClick={() => setOpen(false)}
              className="rounded p-1 text-muted-foreground hover:text-foreground"
            >
              <X className="size-4" />
            </button>
          </div>

          {/* Messages */}
          <div className="flex-1 overflow-y-auto p-4 space-y-3 max-h-72">
            {messages.length === 0 && (
              <div className="space-y-3">
                <p className="text-sm text-muted-foreground">
                  Ask me anything about this race!
                </p>
                <div className="flex flex-wrap gap-2">
                  {SEED_QUESTIONS.map((q) => (
                    <button
                      key={q}
                      onClick={() => sendMessage(q)}
                      className="rounded-full border px-3 py-1 text-xs hover:bg-muted transition-colors"
                    >
                      {q}
                    </button>
                  ))}
                </div>
              </div>
            )}

            {messages.map((msg, i) => (
              <div
                key={i}
                className={cn(
                  "max-w-[85%] rounded-lg px-3 py-2 text-sm",
                  msg.role === "user"
                    ? "ml-auto bg-primary text-primary-foreground"
                    : "bg-muted text-foreground"
                )}
              >
                {msg.text}
              </div>
            ))}

            {loading && (
              <div className="flex gap-1 items-center text-muted-foreground">
                <span className="size-1.5 animate-bounce rounded-full bg-current [animation-delay:0ms]" />
                <span className="size-1.5 animate-bounce rounded-full bg-current [animation-delay:150ms]" />
                <span className="size-1.5 animate-bounce rounded-full bg-current [animation-delay:300ms]" />
              </div>
            )}
            <div ref={bottomRef} />
          </div>

          {/* Input */}
          <form
            onSubmit={(e) => {
              e.preventDefault()
              sendMessage(input)
            }}
            className="flex gap-2 border-t p-3"
          >
            <input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder={rateLimited ? "Rate limit reached…" : "Ask a question…"}
              disabled={loading || rateLimited}
              className="flex-1 rounded-md border bg-background px-3 py-1.5 text-sm outline-none focus:ring-1 focus:ring-ring disabled:opacity-50"
            />
            <button
              type="submit"
              disabled={!input.trim() || loading}
              className="rounded-md bg-primary px-3 py-1.5 text-primary-foreground disabled:opacity-40"
            >
              <Send className="size-4" />
            </button>
          </form>
        </div>
      )}
    </>
  )
}
