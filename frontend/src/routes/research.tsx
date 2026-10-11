import { createFileRoute } from "@tanstack/react-router";
import { media, leopards } from "@/lib/panthera";

export const Route = createFileRoute("/research")({
  head: () => ({
    meta: [
      { title: "Research & Conservation Registry — PANTHERA" },
      {
        name: "description",
        content:
          "Individual leopard profiles, sighting histories and conservation research from the PANTHERA field programme.",
      },
      { property: "og:title", content: "Research & Conservation Registry — PANTHERA" },
      {
        property: "og:description",
        content: "Leopard profiles, sighting histories and identification records from the field.",
      },
    ],
  }),
  component: Research,
});

function Research() {
  return (
    <div>
      <section className="relative overflow-hidden">
        <img
          src={media.sunset}
          alt="Leopard resting on a branch above rainforest at sunset"
          className="h-[70vh] w-full object-cover slow-zoom"
        />
        <div className="veil absolute inset-0" />
        <div className="absolute inset-0 flex items-end">
          <div className="mx-auto w-full max-w-7xl px-6 pb-16 lg:px-10">
            <p className="eyebrow rise">Research & Conservation</p>
            <h1 className="rise mt-4 max-w-3xl text-5xl text-cream lg:text-7xl" style={{ animationDelay: "0.15s" }}>
              The individual registry
            </h1>
            <p className="rise mt-5 max-w-xl leading-relaxed text-cream/80" style={{ animationDelay: "0.3s" }}>
              Every leopard in our study landscape carries a file — built from photographs, not
              collars. These are the animals we know by name.
            </p>
          </div>
        </div>
      </section>

      <section className="mx-auto max-w-7xl px-6 py-24 lg:px-10">
        <div className="space-y-10">
          {leopards.map((l, i) => (
            <article
              key={l.id}
              className={`grid gap-8 lg:grid-cols-2 lg:items-center ${
                i % 2 ? "lg:[&>figure]:order-2" : ""
              }`}
            >
              <figure className="group relative overflow-hidden rounded-sm" style={{ boxShadow: "var(--shadow-deep)" }}>
                <img
                  src={l.image}
                  alt={`Individual ${l.id}, ${l.viewpoint.toLowerCase()} view`}
                  loading="lazy"
                  className="h-[28rem] w-full object-cover transition-transform duration-[1400ms] group-hover:scale-105"
                />
                <span className="absolute left-5 top-5 bg-background/70 px-3 py-1.5 text-[0.62rem] uppercase tracking-[0.22em] text-primary backdrop-blur">
                  {l.id.slice(0, 8).toUpperCase()}
                </span>
              </figure>
              <div>
                <p className="eyebrow">Individual Profile</p>
                <h2 className="mt-3 text-4xl text-cream lg:text-5xl">{l.id.slice(0, 8).toUpperCase()}</h2>
                <dl className="mt-8 grid grid-cols-2 gap-x-8 gap-y-6">
                  {[
                    ["Individual ID", l.id],
                    ["Viewpoint", l.viewpoint],
                    ["Identification Records", `${l.records}`],
                  ].map(([k, v]) => (
                    <div key={k} className="border-t border-border/70 pt-3">
                      <dt className="text-[0.65rem] uppercase tracking-[0.2em] text-muted-foreground">
                        {k}
                      </dt>
                      <dd className="mt-1.5 text-cream/90">{v}</dd>
                    </div>
                  ))}
                </dl>
              </div>
            </article>
          ))}
        </div>
      </section>

      <section className="border-t border-border/60">
        <div className="mx-auto grid max-w-7xl gap-10 px-6 py-20 md:grid-cols-3 lg:px-10">
          {[
            [
              "Non-invasive by design",
              "No darting, no collars, no handling. Identification relies entirely on photographs collected from passive camera nodes.",
            ],
            [
              "Population trends",
              "Repeat identifications across seasons yield survival estimates, territory shifts and cub recruitment rates.",
            ],
            [
              "Conflict mitigation",
              "Knowing which individual moves near settlements lets forest teams respond to an animal, not a rumour.",
            ],
          ].map(([t, d]) => (
            <div key={t}>
              <h3 className="text-2xl text-cream">{t}</h3>
              <p className="mt-3 text-sm leading-relaxed text-muted-foreground">{d}</p>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}
