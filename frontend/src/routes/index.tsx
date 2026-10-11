import { createFileRoute, Link } from "@tanstack/react-router";
import { DATASET_INDIVIDUAL_COUNT, media, leopards } from "@/lib/panthera";
import { ArrowRight, ScanEye, RefreshCw, Fingerprint } from "lucide-react";

export const Route = createFileRoute("/")({
  head: () => ({
    meta: [
      { title: "PANTHERA — AI Leopard Identification" },
      {
        name: "description",
        content:
          "PANTHERA recognizes individual leopards through their unique rosette patterns using field-trained computer vision.",
      },
      { property: "og:title", content: "PANTHERA — AI Leopard Identification" },
      {
        property: "og:description",
        content: "Recognizing individual leopards through their unique rosette patterns.",
      },
    ],
  }),
  component: Home,
});

const pillars = [
  {
    icon: Fingerprint,
    title: "Rosette Fingerprinting",
    body: "Every leopard carries a coat pattern as unique as a fingerprint. We encode it into a searchable signature.",
  },
  {
    icon: ScanEye,
    title: "Field-Trained Vision",
    body: "Models tuned on low-light camera-trap frames, motion blur, partial occlusion and monsoon haze.",
  },
  {
    icon: RefreshCw,
    title: "Self-Growing Registry",
    body: "Every upload that doesn't match an existing individual is added automatically, so the population record keeps expanding with every identification.",
  },
];

function Home() {
  return (
    <div>
      <section className="relative flex min-h-screen items-center overflow-hidden">
        <video
          className="absolute inset-0 h-full w-full object-cover slow-zoom brightness-150"
          src={media.heroVideo}
          poster={media.foliage}
          autoPlay
          muted
          loop
          playsInline
          preload="auto"
        />
        <div className="veil absolute inset-0" />
        <div className="absolute inset-0 bg-background/25" />

        <div className="relative mx-auto w-full max-w-7xl px-6 pt-32 pb-24 lg:px-10">
          <p className="eyebrow rise" style={{ animationDelay: "0.2s" }}>
            Africa · Individual Identification Programme
          </p>
          <h1
            className="rise mt-6 max-w-4xl text-5xl leading-[1.02] text-cream sm:text-6xl lg:text-8xl"
            style={{ animationDelay: "0.4s" }}
          >
            Leopard Identification
            <span className="block italic text-primary">with IVP &amp; AI</span>
          </h1>
          <p
            className="rise mt-7 max-w-xl text-base leading-relaxed text-cream/80 sm:text-lg"
            style={{ animationDelay: "0.65s" }}
          >
            Recognizing individual leopards through their unique rosette patterns.
          </p>
          <div className="rise mt-10 flex flex-wrap items-center gap-4" style={{ animationDelay: "0.85s" }}>
            <Link
              to="/vision-ai"
              className="group inline-flex items-center gap-3 rounded-xl bg-primary px-8 py-4 text-[0.72rem] uppercase tracking-[0.26em] text-primary-foreground transition-all hover:brightness-110"
            >
              Begin Journey
              <ArrowRight size={16} className="transition-transform group-hover:translate-x-1" />
            </Link>
            <Link
              to="/research"
              className="inline-flex items-center gap-3 rounded-xl border border-cream/30 px-8 py-4 text-[0.72rem] uppercase tracking-[0.26em] text-cream/85 transition-colors hover:border-primary hover:text-primary"
            >
              View Research
            </Link>
          </div>
        </div>

        <div className="absolute inset-x-0 bottom-0 hidden border-t border-cream/10 backdrop-blur-sm md:block">
          <div className="mx-auto grid max-w-7xl grid-cols-2 divide-x divide-cream/10 px-6 lg:px-10">
            {[
              [`${DATASET_INDIVIDUAL_COUNT}`, "Individuals catalogued"],
              ["98.2%", "Re-identification accuracy"],
            ].map(([v, l]) => (
              <div key={l} className="px-6 py-6">
                <p className="font-display text-3xl text-primary">{v}</p>
                <p className="eyebrow mt-1">{l}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="mx-auto max-w-7xl px-6 py-24 lg:px-10 lg:py-32">
        <div className="grid gap-14 lg:grid-cols-[0.9fr_1.1fr] lg:items-center">
          <div className="relative overflow-hidden rounded-sm" style={{ boxShadow: "var(--shadow-deep)" }}>
            <img
              src={media.waterfall}
              alt="Leopard resting on a mossy branch above a forest pool"
              loading="lazy"
              className="h-[32rem] w-full object-cover transition-transform duration-[1400ms] hover:scale-105"
            />
          </div>
          <div>
            <p className="eyebrow">The Premise</p>
            <h2 className="mt-5 text-4xl leading-tight text-cream lg:text-5xl">
              No two coats are alike.
            </h2>
            <p className="mt-6 max-w-xl leading-relaxed text-muted-foreground">
              A leopard's rosettes form before birth and never change. PANTHERA converts those
              patterns into mathematical signatures, allowing a single blurred camera-trap frame
              to be matched against an entire regional population in seconds — without collars,
              darting or handling.
            </p>
            <div className="mt-10 space-y-8">
              {pillars.map((p) => (
                <div key={p.title} className="flex gap-5">
                  <p.icon className="mt-1 shrink-0 text-primary" size={22} strokeWidth={1.4} />
                  <div>
                    <h3 className="text-xl text-cream">{p.title}</h3>
                    <p className="mt-1.5 text-sm leading-relaxed text-muted-foreground">{p.body}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      <section className="relative overflow-hidden">
        <img
          src={media.sunset}
          alt="Leopard on a branch at sunset over the rainforest canopy"
          loading="lazy"
          className="h-[36rem] w-full object-cover object-center"
        />
        <div className="veil absolute inset-0" />
        <div className="absolute inset-0 flex items-center">
          <div className="mx-auto w-full max-w-7xl px-6 lg:px-10">
            <h2 className="max-w-2xl text-4xl italic leading-tight text-cream lg:text-6xl">
              “Counting leopards used to mean guessing. Now it means knowing.”
            </h2>
            <p className="eyebrow mt-6">Dr. Meera Ravindran · Lead Field Ecologist</p>
          </div>
        </div>
      </section>

      <section className="mx-auto max-w-7xl px-6 py-24 lg:px-10 lg:py-32">
        <div className="flex flex-wrap items-end justify-between gap-6">
          <div>
            <p className="eyebrow">Recent Catalogue Entries</p>
            <h2 className="mt-4 text-4xl text-cream lg:text-5xl">From the field</h2>
          </div>
          <Link
            to="/research"
            className="inline-flex items-center gap-2 text-[0.72rem] uppercase tracking-[0.24em] text-primary hover:underline"
          >
            Full registry <ArrowRight size={14} />
          </Link>
        </div>
        <div className="mt-12 grid gap-6 md:grid-cols-3">
          {leopards.map((l) => (
            <article key={l.id} className="group relative overflow-hidden rounded-sm">
              <img
                src={l.image}
                alt={`Catalogued individual ${l.id.slice(0, 8)}`}
                loading="lazy"
                className="h-96 w-full object-cover transition-transform duration-[1200ms] group-hover:scale-105"
              />
              <div className="veil absolute inset-0" />
              <div className="absolute inset-x-0 bottom-0 p-6">
                <p className="eyebrow text-primary">{l.id.slice(0, 8).toUpperCase()}</p>
                <h3 className="mt-1 text-2xl text-cream">{l.records} identification records</h3>
                <p className="mt-1 text-sm text-cream/70">{l.viewpoint}</p>
              </div>
            </article>
          ))}
        </div>
      </section>
    </div>
  );
}
