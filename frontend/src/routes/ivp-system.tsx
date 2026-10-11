import { createFileRoute } from "@tanstack/react-router";
import { Fragment, useEffect, useState } from "react";
import { AnalysisResult, leopards, readResult } from "@/lib/panthera";
import { ResultDetails } from "@/components/ResultDetails";
import {
  Layers,
  Wand2,
  ScanSearch,
  Search,
  ShieldCheck,
  CheckCircle2,
  Fingerprint,
  Shuffle,
  Hash,
  SlidersHorizontal,
  ArrowRight,
  ArrowDown,
} from "lucide-react";

export const Route = createFileRoute("/ivp-system")({
  // "?view=result" is only added by the "View full IVP & AI details" button on the analysis page.
  validateSearch: (search: Record<string, unknown>): { view?: "result" } =>
    search["view"] === "result" ? { view: "result" } : {},
  head: () => ({
    meta: [
      { title: "Pipeline — How Identification Works | PANTHERA" },
      {
        name: "description",
        content:
          "How the PANTHERA Individual Verification Pipeline uses SIFT keypoint extraction and RANSAC geometric verification to identify leopards from their rosette patterns.",
      },
      { property: "og:title", content: "Pipeline — How Identification Works" },
      {
        property: "og:description",
        content: "SIFT keypoint matching and RANSAC geometric verification, explained.",
      },
    ],
  }),
  component: IVP,
});

const IVP_STAGES = [
  { icon: Layers, title: "Categorize", body: "Classifies image condition: normal, dark, red-tinted, obscured or grayscale" },
  { icon: Wand2, title: "Correct", body: "Applies condition-specific enhancement so the pattern reads clearly" },
  { icon: ScanSearch, title: "Extract Keypoints", body: "SIFT locates distinctive landmark points across the rosette pattern" },
  { icon: Search, title: "Match Candidates", body: "Compares keypoints against gallery photos of the same viewpoint" },
  { icon: ShieldCheck, title: "Verify Geometrically", body: "RANSAC filters for points that form a consistent spatial arrangement" },
  { icon: CheckCircle2, title: "Decide", body: "Verified point count decides confident match, possible match, or new leopard" },
];

const KEY_TERMS = [
  {
    icon: Fingerprint,
    term: "SIFT",
    full: "Scale-Invariant Feature Transform",
    body: "A classical computer vision algorithm that finds distinctive landmark points in an image, unaffected by scale or rotation — used here to locate points on a leopard's rosette pattern.",
  },
  {
    icon: Shuffle,
    term: "RANSAC",
    full: "Random Sample Consensus",
    body: "A geometric verification technique that checks whether matched keypoints between two photos form a consistent spatial arrangement, filtering out coincidental matches.",
  },
  {
    icon: Hash,
    term: "Verified Match Points",
    full: "The core matching signal",
    body: "The count of keypoints that survive RANSAC verification between a query photo and a gallery photo — the primary evidence used to decide if two photos show the same leopard.",
  },
  {
    icon: SlidersHorizontal,
    term: "Decision Threshold",
    full: "How the call is made",
    body: "20+ verified points → confident match. 6–19 → possible match, cross-checked against an independent AI identity estimate. Fewer than 6 → likely a new individual.",
  },
];

function IVP() {
  const { view } = Route.useSearch();
  const [result, setResult] = useState<AnalysisResult | null | undefined>(undefined);

  useEffect(() => {
    setResult(readResult());
  }, []);

  // Plain visits (nav link, footer) always get the general explanation below.
  if (view === "result") {
    if (result === undefined) return null;
    if (result && result.status === "success") return <ResultDetails result={result} />;
  }

  return (
    <div className="mx-auto max-w-7xl px-6 pt-36 pb-28 lg:px-10">
      <p className="eyebrow rise">Individual Verification Pipeline</p>
      <h1 className="rise mt-4 text-5xl text-cream lg:text-6xl" style={{ animationDelay: "0.15s" }}>
        Pipeline
      </h1>
      <p className="rise mt-5 max-w-2xl leading-relaxed text-muted-foreground" style={{ animationDelay: "0.3s" }}>
        The classical computer-vision half of PANTHERA's identification pipeline — SIFT keypoint
        extraction and RANSAC geometric verification, matching rosette patterns independent of any
        AI model.
      </p>

      <div className="mt-14">
        <p className="eyebrow">The Pipeline</p>
        <h2 className="mt-3 text-3xl text-cream lg:text-4xl">How a match is verified</h2>
        <div className="mt-10 flex flex-col overflow-x-auto lg:flex-row lg:items-stretch">
          {IVP_STAGES.map((s, i) => (
            <Fragment key={s.title}>
              <div className="glass-panel flex flex-1 flex-col items-center gap-2 rounded-sm px-4 py-6 text-center lg:min-w-[9.5rem]">
                <s.icon size={22} strokeWidth={1.4} className="text-primary" />
                <h3 className="mt-1 text-sm text-cream">{s.title}</h3>
                <p className="text-xs leading-relaxed text-muted-foreground">{s.body}</p>
              </div>
              {i < IVP_STAGES.length - 1 && (
                <div className="flex shrink-0 items-center justify-center py-2 lg:px-1 lg:py-0">
                  <ArrowDown size={18} className="text-primary lg:hidden" />
                  <ArrowRight size={18} className="hidden shrink-0 text-primary lg:block" />
                </div>
              )}
            </Fragment>
          ))}
        </div>
      </div>

      <div className="mt-16">
        <p className="eyebrow">Key Terms</p>
        <h2 className="mt-3 text-3xl text-cream lg:text-4xl">The vocabulary</h2>
        <div className="mt-10 grid gap-6 sm:grid-cols-2">
          {KEY_TERMS.map((t) => (
            <div key={t.term} className="glass-panel rounded-sm px-8 py-8">
              <div className="flex items-center gap-3">
                <t.icon size={20} className="text-primary" strokeWidth={1.5} />
                <h3 className="text-xl text-cream">{t.term}</h3>
              </div>
              <p className="eyebrow mt-3 text-[0.62rem]">{t.full}</p>
              <p className="mt-4 text-sm leading-relaxed text-muted-foreground">{t.body}</p>
            </div>
          ))}
        </div>
      </div>

      <div className="mt-16">
        <p className="eyebrow">Registry Sample</p>
        <h2 className="mt-3 text-3xl text-cream lg:text-4xl">Individuals on record</h2>
        <div className="mt-10 grid gap-6 md:grid-cols-3">
          {leopards.map((l) => (
            <div key={l.id} className="glass-panel flex gap-4 rounded-sm p-4">
              <img
                src={l.image}
                alt={`Registry photograph of ${l.id}`}
                loading="lazy"
                className="h-24 w-24 shrink-0 rounded-sm object-cover"
              />
              <div className="min-w-0">
                <p className="eyebrow text-primary">{l.id.slice(0, 8).toUpperCase()}</p>
                <p className="mt-1 truncate text-cream">{l.viewpoint}</p>
                <p className="mt-1 text-xs text-muted-foreground">{l.records} identification records</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
