import { createFileRoute } from "@tanstack/react-router";
import { useState } from "react";
import { media } from "@/lib/panthera";
import { Mail, MapPin, Phone } from "lucide-react";

export const Route = createFileRoute("/reach-us")({
  head: () => ({
    meta: [
      { title: "Reach Us — PANTHERA Field Programme" },
      {
        name: "description",
        content:
          "Contact the PANTHERA research collective about leopard identification, data partnerships or field collaboration.",
      },
      { property: "og:title", content: "Reach Us — PANTHERA Field Programme" },
      {
        property: "og:description",
        content: "Get in touch about leopard identification, data partnerships or field work.",
      },
    ],
  }),
  component: ReachUs,
});

function ReachUs() {
  const [sent, setSent] = useState(false);

  return (
    <div className="relative min-h-screen">
      <img
        src={media.waterfall}
        alt=""
        aria-hidden
        className="fixed inset-0 h-full w-full object-cover opacity-25"
      />
      <div className="veil fixed inset-0" />

      <div className="relative mx-auto max-w-6xl px-6 pt-36 pb-28 lg:px-10">
        <p className="eyebrow rise">Contact</p>
        <h1 className="rise mt-4 text-5xl text-cream lg:text-6xl" style={{ animationDelay: "0.15s" }}>
          Reach Us
        </h1>
        <p className="rise mt-5 max-w-xl leading-relaxed text-cream/75" style={{ animationDelay: "0.3s" }}>
          For data partnerships, camera-node deployment or access to the identification registry.
        </p>

        <div className="mt-14 grid gap-10 lg:grid-cols-[1fr_1.1fr]">
          <div className="space-y-6">
            {[
              [MapPin, "Field Station", "Africa Field Research Station"],
              [Mail, "Email", "field@panthera.org"],
              [Phone, "Field Line", "+91 80 4000 1180"],
            ].map(([Icon, k, v]) => {
              const I = Icon as typeof Mail;
              return (
                <div key={k as string} className="glass-panel flex gap-4 rounded-sm p-6">
                  <I size={18} className="mt-1 shrink-0 text-primary" strokeWidth={1.5} />
                  <div>
                    <p className="eyebrow">{k as string}</p>
                    <p className="mt-2 text-cream/90">{v as string}</p>
                  </div>
                </div>
              );
            })}
          </div>

          <form
            onSubmit={(e) => {
              e.preventDefault();
              setSent(true);
            }}
            className="glass-panel space-y-5 rounded-sm p-8"
            style={{ boxShadow: "var(--shadow-deep)" }}
          >
            {[
              { label: "Name", type: "text", name: "name" },
              { label: "Email", type: "email", name: "email" },
              { label: "Organisation", type: "text", name: "org" },
            ].map((f) => (
              <div key={f.name}>
                <label className="eyebrow" htmlFor={f.name}>
                  {f.label}
                </label>
                <input
                  id={f.name}
                  name={f.name}
                  type={f.type}
                  required={f.name !== "org"}
                  className="mt-2 w-full rounded-sm border border-input bg-background/40 px-4 py-3 text-cream outline-none transition-colors focus:border-primary"
                />
              </div>
            ))}
            <div>
              <label className="eyebrow" htmlFor="message">
                Message
              </label>
              <textarea
                id="message"
                name="message"
                rows={5}
                required
                className="mt-2 w-full resize-none rounded-sm border border-input bg-background/40 px-4 py-3 text-cream outline-none transition-colors focus:border-primary"
              />
            </div>
            <button
              type="submit"
              className="w-full rounded-xl bg-primary px-8 py-4 text-[0.72rem] uppercase tracking-[0.26em] text-primary-foreground transition-all hover:brightness-110"
            >
              {sent ? "Message received" : "Send Message"}
            </button>
            {sent && (
              <p className="text-center text-sm text-muted-foreground">
                Thank you — our field team replies within two working days.
              </p>
            )}
          </form>
        </div>
      </div>
    </div>
  );
}
