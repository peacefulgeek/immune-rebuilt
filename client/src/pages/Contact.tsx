import { useState } from "react";
import { toast } from "sonner";
import { Send } from "lucide-react";

export default function Contact() {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [message, setMessage] = useState("");
  const [busy, setBusy] = useState(false);

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!name || !email || !message) {
      toast.error("All three fields, please.");
      return;
    }
    setBusy(true);
    try {
      const r = await fetch("/api/contact", {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({ name, email, message }),
      });
      const j = await r.json().catch(() => ({}));
      if (r.ok && j?.ok) {
        toast.success("Thank you. We'll write back.");
        setName(""); setEmail(""); setMessage("");
      } else {
        toast.error("Something didn't go through. Try again in a moment.");
      }
    } catch {
      toast.error("Network blink. Try once more.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="container py-14 md:py-20 grid md:grid-cols-12 gap-10">
      <div className="md:col-span-6">
        <p className="text-xs uppercase tracking-[.18em] text-[oklch(0.45_0.075_150)] mb-2">Reach the writer</p>
        <h1 className="text-3xl md:text-5xl font-semibold tracking-tight">Contact</h1>
        <p className="mt-5 text-[oklch(0.40_0.02_145)] text-lg leading-relaxed">
          Press, story tips, corrections, or you read something here that helped — we read everything.
          Replies are not medical advice, and they aren't always immediate.
        </p>
        <p className="mt-3 text-sm text-[oklch(0.45_0.02_145)]">
          For sister-site inquiries try{" "}
          <a href="https://theoraclelover.com" rel="noopener" className="underline">theoraclelover.com</a>.
        </p>
      </div>
      <form className="md:col-span-6 ar-card p-6 md:p-8 space-y-4" onSubmit={onSubmit}>
        <label className="block">
          <span className="block text-xs uppercase tracking-[.16em] text-[oklch(0.45_0.075_150)] mb-1.5">Your name</span>
          <input
            value={name}
            onChange={(e) => setName(e.target.value)}
            className="w-full bg-white border border-[oklch(0.86_0.020_95)] rounded-lg px-3.5 py-2.5 text-sm outline-none focus:border-[oklch(0.59_0.075_152)] focus:ring-2 focus:ring-[oklch(0.59_0.075_152/0.2)]"
            placeholder="What can we call you?"
          />
        </label>
        <label className="block">
          <span className="block text-xs uppercase tracking-[.16em] text-[oklch(0.45_0.075_150)] mb-1.5">Email</span>
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="w-full bg-white border border-[oklch(0.86_0.020_95)] rounded-lg px-3.5 py-2.5 text-sm outline-none focus:border-[oklch(0.59_0.075_152)] focus:ring-2 focus:ring-[oklch(0.59_0.075_152/0.2)]"
            placeholder="you@somewhere.com"
          />
        </label>
        <label className="block">
          <span className="block text-xs uppercase tracking-[.16em] text-[oklch(0.45_0.075_150)] mb-1.5">Message</span>
          <textarea
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            rows={6}
            className="w-full bg-white border border-[oklch(0.86_0.020_95)] rounded-lg px-3.5 py-2.5 text-sm outline-none focus:border-[oklch(0.59_0.075_152)] focus:ring-2 focus:ring-[oklch(0.59_0.075_152/0.2)] resize-y"
            placeholder="Tell us what you're working on, what helped, or what we got wrong."
          />
        </label>
        <button
          type="submit"
          disabled={busy}
          className="inline-flex items-center gap-2 rounded-full bg-[oklch(0.45_0.075_150)] text-white px-5 py-2.5 text-sm font-medium shadow-md hover:translate-y-[-1px] transition disabled:opacity-60"
        >
          {busy ? "Sending…" : "Send"}
          <Send className="h-4 w-4" />
        </button>
      </form>
    </div>
  );
}
