import { useEffect, useRef, useState } from "react";
import { MessageCircle, X, Send, Loader2 } from "lucide-react";
import { askChatbot } from "@/lib/panthera";

interface ChatMessage {
  role: "user" | "assistant";
  text: string;
  suggestions?: string[];
}

// Starter chips shown before the first question; each is answered by the backend like any typed question.
const STARTERS = [
  "What do leopards eat?",
  "Where do leopards live?",
  "Why do leopards have spots?",
  "How does PANTHERA identify a leopard?",
];

const WELCOME: ChatMessage = {
  role: "assistant",
  text: "Hi! Ask me about leopards (diet, habitat, spots, behaviour), how our identification works, our accuracy, or look up a leopard by its ID.",
};

export function ChatWidget() {
  const [open, setOpen] = useState(false);
  const [messages, setMessages] = useState<ChatMessage[]>([WELCOME]);
  const [input, setInput] = useState("");
  const [sending, setSending] = useState(false);
  const [error, setError] = useState("");
  const listRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    listRef.current?.scrollTo({ top: listRef.current.scrollHeight, behavior: "smooth" });
  }, [messages, open]);

  const send = async (raw: string) => {
    const question = raw.trim();
    if (!question || sending) return;

    setMessages((m) => [...m, { role: "user", text: question }]);
    setInput("");
    setError("");
    setSending(true);
    try {
      const result = await askChatbot(question);
      setMessages((m) => [
        ...m,
        { role: "assistant", text: result.answer, suggestions: result.suggestions ?? [] },
      ]);
    } catch {
      setError("Could not reach the assistant. Please try again.");
    } finally {
      setSending(false);
    }
  };

  const handleSend = (e: React.FormEvent) => {
    e.preventDefault();
    void send(input);
  };

  // Chips only appear under the latest assistant message, so old ones don't clutter the history.
  const lastIndex = messages.length - 1;

  return (
    <div className="fixed bottom-6 right-6 z-50 flex flex-col items-end gap-4">
      {open && (
        <div
          className="glass-panel flex h-[28rem] w-[22rem] max-w-[calc(100vw-3rem)] flex-col overflow-hidden rounded-sm"
          style={{ boxShadow: "var(--shadow-deep)" }}
        >
          <div className="flex items-center justify-between border-b border-border/60 px-5 py-4">
            <div>
              <p className="eyebrow">Panthera Assistant</p>
              <p className="mt-1 text-sm text-cream/80">Leopards, identification &amp; the registry</p>
            </div>
            <button
              onClick={() => setOpen(false)}
              aria-label="Close chat"
              className="shrink-0 text-cream/60 transition-colors hover:text-primary"
            >
              <X size={18} />
            </button>
          </div>

          <div ref={listRef} className="flex-1 space-y-3 overflow-y-auto px-5 py-4">
            {messages.map((m, i) => {
              const chips = i === 0 ? STARTERS : m.suggestions ?? [];
              return (
                <div key={i} className={m.role === "user" ? "flex justify-end" : ""}>
                  <div
                    className={`max-w-[85%] whitespace-pre-line rounded-sm px-4 py-2.5 text-sm leading-relaxed ${
                      m.role === "user"
                        ? "bg-primary text-primary-foreground"
                        : "bg-secondary text-cream/90"
                    }`}
                  >
                    {m.text}
                  </div>
                  {m.role === "assistant" && i === lastIndex && !sending && chips.length > 0 && (
                    <div className="mt-2 flex flex-wrap gap-1.5">
                      {chips.map((c) => (
                        <button
                          key={c}
                          type="button"
                          onClick={() => void send(c)}
                          className="rounded-xl border border-primary/40 px-3 py-1 text-left text-xs text-primary transition-colors hover:bg-primary/10"
                        >
                          {c}
                        </button>
                      ))}
                    </div>
                  )}
                </div>
              );
            })}
            {sending && (
              <div className="flex items-center gap-2 text-xs text-muted-foreground">
                <Loader2 size={13} className="animate-spin" /> Thinking…
              </div>
            )}
            {error && <p className="text-xs text-destructive">{error}</p>}
          </div>

          <form
            onSubmit={handleSend}
            className="flex items-center gap-2 border-t border-border/60 px-4 py-3"
          >
            <input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Type a question…"
              className="flex-1 bg-transparent text-sm text-cream placeholder:text-muted-foreground outline-none"
            />
            <button
              type="submit"
              disabled={sending || !input.trim()}
              aria-label="Send"
              className="flex h-8 w-8 shrink-0 items-center justify-center rounded-xl bg-primary text-primary-foreground transition-all hover:brightness-110 disabled:opacity-40"
            >
              <Send size={14} />
            </button>
          </form>
        </div>
      )}

      <button
        onClick={() => setOpen((v) => !v)}
        aria-label={open ? "Close chat" : "Open chat"}
        className="flex h-14 w-14 items-center justify-center rounded-full bg-primary text-primary-foreground transition-all hover:brightness-110"
        style={{ boxShadow: "var(--shadow-deep)" }}
      >
        {open ? <X size={22} /> : <MessageCircle size={22} />}
      </button>
    </div>
  );
}
