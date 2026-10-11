import { createFileRoute, Link } from "@tanstack/react-router";
import { Fragment, useEffect, useState } from "react";
import {
  AnalysisResult,
  confirmNewLeopard,
  fetchDisplayableImage,
  media,
  readResult,
  readUpload,
} from "@/lib/panthera";
import {
  CheckCircle2,
  HelpCircle,
  SearchX,
  Sparkles,
  ArrowLeft,
  ArrowRight,
  ArrowDown,
  UploadCloud,
  ShieldCheck,
  Wand2,
  Compass,
  GitCompare,
  BrainCircuit,
  Loader2,
  FileSearch,
} from "lucide-react";

const PIPELINE_STAGES = [
  { icon: UploadCloud, title: "Upload Photo", body: "Submit a photograph for analysis" },
  { icon: ShieldCheck, title: "AI Validation", body: "Confirms the image contains a leopard" },
  { icon: Wand2, title: "IVP Correction", body: "Enhances image based on lighting condition" },
  { icon: Compass, title: "AI Orientation Detection", body: "Identifies which side of the leopard is visible" },
  { icon: GitCompare, title: "IVP Pattern Matching", body: "Compares rosette patterns using geometric verification" },
  { icon: BrainCircuit, title: "AI Identity Estimate", body: "Provides an independent identity prediction" },
  { icon: CheckCircle2, title: "Result", body: "Confident match, possible match, or new discovery" },
];

export const Route = createFileRoute("/analysis")({
  head: () => ({
    meta: [
      { title: "Identification Analysis — PANTHERA" },
      {
        name: "description",
        content:
          "Texture, pattern and edge similarity scores comparing an uploaded leopard against the PANTHERA registry.",
      },
      { property: "og:title", content: "Identification Analysis — PANTHERA" },
      {
        property: "og:description",
        content: "Similarity breakdown between an uploaded leopard image and its closest match.",
      },
    ],
  }),
  component: Analysis,
});

function Meter({ label, value }: { label: string; value: number }) {
  const [w, setW] = useState(0);
  useEffect(() => {
    const t = setTimeout(() => setW(value), 250);
    return () => clearTimeout(t);
  }, [value]);
  return (
    <div>
      <div className="flex items-baseline justify-between">
        <p className="text-sm text-cream/80">{label}</p>
        <p className="font-display text-xl text-primary">{value}%</p>
      </div>
      <div className="mt-2 h-[3px] w-full bg-secondary">
        <div
          className="h-full transition-[width] duration-[1400ms] ease-out"
          style={{ width: `${w}%`, background: "var(--gradient-ember)" }}
        />
      </div>
    </div>
  );
}

// IVP verified match points have no fixed upper bound, but the backend treats
// 20+ points as a confident match — used here only to render a 0-100% bar.
const IVP_CONFIDENT_THRESHOLD = 20;

function confidenceLabel(level: string | undefined): string {
  if (!level) return "—";
  const lead = level.split(" ")[0] ?? level;
  return lead.charAt(0).toUpperCase() + lead.slice(1);
}

function decisionLabel(decision: AnalysisResult["decision"]): string {
  if (decision === "MATCH") return "Match";
  if (decision === "POSSIBLE_MATCH") return "Possible Match";
  if (decision === "NEW_LEOPARD") return "New Leopard";
  return "—";
}

function ConfirmLeopardPanel({ result }: { result: AnalysisResult }) {
  const [state, setState] = useState<"idle" | "saving" | "saved" | "error">("idle");
  const [errorMessage, setErrorMessage] = useState("");

  if (!result.leopard || !result.upload_id) {
    return null;
  }

  const handleConfirm = async () => {
    setState("saving");
    try {
      await confirmNewLeopard(result.upload_id!);
      setState("saved");
    } catch {
      setErrorMessage("Could not save to the registry. Please try again.");
      setState("error");
    }
  };

  if (state === "saved") {
    return (
      <p className="mt-8 flex items-center justify-center gap-2 text-sm text-primary">
        <CheckCircle2 size={16} /> Added to the registry
      </p>
    );
  }

  return (
    <div className="mt-8 flex flex-col items-center gap-3">
      <button
        onClick={handleConfirm}
        disabled={state === "saving"}
        className="inline-flex items-center gap-3 rounded-xl bg-primary px-8 py-3.5 text-[0.7rem] uppercase tracking-[0.24em] text-primary-foreground transition-all hover:brightness-110 disabled:opacity-60"
      >
        {state === "saving" && <Loader2 size={15} className="animate-spin" />}
        Confirm &amp; Save to Registry
      </button>
      {state === "error" && <p className="text-sm text-destructive">{errorMessage}</p>}
    </div>
  );
}

// Opens the IVP System page in "report" mode, filled with this photo's own results.
function DetailsLink() {
  return (
    <Link
      to="/ivp-system"
      search={{ view: "result" }}
      className="inline-flex items-center gap-3 rounded-xl border border-primary/60 px-7 py-3.5 text-[0.7rem] uppercase tracking-[0.24em] text-primary transition-colors hover:bg-primary hover:text-primary-foreground"
    >
      <FileSearch size={15} /> View full IVP &amp; AI details
    </Link>
  );
}

function Analysis() {
  const [uploaded, setUploaded] = useState<string | null>(null);
  const [result, setResult] = useState<AnalysisResult | null | undefined>(undefined);
  const [matchedImageSrc, setMatchedImageSrc] = useState<string | null>(null);
  const [keypointImageSrc, setKeypointImageSrc] = useState<string | null>(null);

  useEffect(() => {
    setUploaded(readUpload()?.dataUrl ?? null);
    setResult(readResult());
  }, []);

  useEffect(() => {
    if (!result?.matched_image_url) return;
    let objectUrl: string | null = null;
    let cancelled = false;
    fetchDisplayableImage(result.matched_image_url).then((src) => {
      if (cancelled) return;
      objectUrl = src;
      setMatchedImageSrc(src);
    });
    return () => {
      cancelled = true;
      if (objectUrl) URL.revokeObjectURL(objectUrl);
    };
  }, [result?.matched_image_url]);

  useEffect(() => {
    if (!result?.keypoint_image_url) return;
    let objectUrl: string | null = null;
    let cancelled = false;
    fetchDisplayableImage(result.keypoint_image_url).then((src) => {
      if (cancelled) return;
      objectUrl = src;
      setKeypointImageSrc(src);
    });
    return () => {
      cancelled = true;
      if (objectUrl) URL.revokeObjectURL(objectUrl);
    };
  }, [result?.keypoint_image_url]);

  if (result === undefined) {
    return null;
  }

  if (!result) {
    return (
      <div className="relative min-h-screen">
        <div className="mx-auto max-w-7xl px-6 pt-36 pb-28 lg:px-10">
          <p className="eyebrow rise">Analyse · Step 02</p>
          <h1 className="rise mt-4 text-5xl text-cream lg:text-6xl" style={{ animationDelay: "0.15s" }}>
            Identification Analysis
          </h1>
          <p
            className="rise mt-4 max-w-2xl leading-relaxed text-muted-foreground"
            style={{ animationDelay: "0.3s" }}
          >
            Upload a photograph to identify individual leopards using our hybrid pattern-verification
            and AI system.
          </p>

          <div className="mt-12 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            {[
              ["Identification Accuracy", "73.7%"],
              ["Top-5 Accuracy", "82.6%"],
              ["Confidence Precision", "92%"],
              ["AI Models", "4"],
            ].map(([k, v]) => (
              <div key={k} className="glass-panel rounded-sm px-6 py-6">
                <p className="eyebrow">{k}</p>
                <p className="mt-2 font-display text-3xl text-cream">{v}</p>
              </div>
            ))}
          </div>

          <div className="mt-16">
            <p className="eyebrow">The Pipeline</p>
            <h2 className="mt-3 text-3xl text-cream lg:text-4xl">How identification works</h2>
            <div className="mt-10 flex flex-col overflow-x-auto lg:flex-row lg:items-stretch">
              {PIPELINE_STAGES.map((s, i) => (
                <Fragment key={s.title}>
                  <div className="glass-panel flex flex-1 flex-col items-center gap-2 rounded-sm px-4 py-6 text-center lg:min-w-[9.5rem]">
                    <s.icon size={22} strokeWidth={1.4} className="text-primary" />
                    <h3 className="mt-1 text-sm text-cream">{s.title}</h3>
                    <p className="text-xs leading-relaxed text-muted-foreground">{s.body}</p>
                  </div>
                  {i < PIPELINE_STAGES.length - 1 && (
                    <div className="flex shrink-0 items-center justify-center py-2 lg:px-1 lg:py-0">
                      <ArrowDown size={18} className="text-primary lg:hidden" />
                      <ArrowRight size={18} className="hidden shrink-0 text-primary lg:block" />
                    </div>
                  )}
                </Fragment>
              ))}
            </div>
          </div>

          <div className="mt-16 grid gap-6 lg:grid-cols-2">
            <div className="glass-panel rounded-sm px-8 py-8">
              <p className="eyebrow text-primary">IVP</p>
              <h3 className="mt-2 text-2xl text-cream">Pattern Verification</h3>
              <p className="mt-4 leading-relaxed text-muted-foreground">
                Classical computer vision — SIFT keypoint matching combined with RANSAC geometric
                verification — compares the precise, physical arrangement of a leopard's rosette
                pattern against the registry. This runs independently of any AI model, giving a
                verification signal grounded purely in geometry.
              </p>
            </div>
            <div className="glass-panel rounded-sm px-8 py-8">
              <p className="eyebrow text-primary">AI</p>
              <h3 className="mt-2 text-2xl text-cream">Intelligent Assistance</h3>
              <p className="mt-4 leading-relaxed text-muted-foreground">
                Four separate AI models support the pipeline: confirming the photo shows a leopard,
                assessing lighting and image condition, detecting which side of the animal is
                visible, and producing an independent identity estimate to cross-check the
                pattern-verification result.
              </p>
            </div>
          </div>

          <div className="mt-14 text-center">
            <Link
              to="/vision-ai"
              className="group inline-flex items-center gap-3 rounded-xl bg-primary px-8 py-4 text-[0.72rem] uppercase tracking-[0.26em] text-primary-foreground transition-all hover:brightness-110"
            >
              Upload Photograph
              <ArrowRight size={16} className="transition-transform group-hover:translate-x-1" />
            </Link>
          </div>
        </div>
      </div>
    );
  }

  const isRejected = result.status === "rejected" || result.status === "error";
  const isNew = result.decision === "NEW_LEOPARD";
  const isPossible = result.decision === "POSSIBLE_MATCH";

  return (
    <div className="relative min-h-screen">
      <div className="mx-auto max-w-7xl px-6 pt-36 pb-28 lg:px-10">
        <div className="flex flex-wrap items-end justify-between gap-6">
          <div>
            <p className="eyebrow rise">Analyse · Step 02</p>
            <h1 className="rise mt-4 text-5xl text-cream lg:text-6xl" style={{ animationDelay: "0.15s" }}>
              Identification Analysis
            </h1>
          </div>
        </div>

        {isRejected ? (
          <div
            className="glass-panel mt-12 rounded-sm px-8 py-24 text-center"
            style={{ boxShadow: "var(--shadow-deep)" }}
          >
            <SearchX size={44} strokeWidth={1} className="mx-auto text-muted-foreground" />
            <h2 className="mt-6 text-4xl text-cream">No Leopard Detected</h2>
            <p className="mx-auto mt-4 max-w-md leading-relaxed text-muted-foreground">
              {result.message ?? "The uploaded image could not be identified as a leopard."}
            </p>
            <Link
              to="/vision-ai"
              className="mt-10 inline-flex items-center gap-3 rounded-xl border border-primary/60 px-8 py-3.5 text-[0.7rem] uppercase tracking-[0.24em] text-primary transition-colors hover:bg-primary hover:text-primary-foreground"
            >
              Upload another image
            </Link>
          </div>
        ) : isNew ? (
          <div
            className="glass-panel mt-12 rounded-sm px-8 py-24 text-center"
            style={{ boxShadow: "var(--shadow-deep)" }}
          >
            <Sparkles size={44} strokeWidth={1} className="mx-auto text-primary" />
            <h2 className="mt-6 text-4xl text-cream">New Leopard Discovered</h2>
            <p className="mx-auto mt-4 max-w-md leading-relaxed text-muted-foreground">
              No existing individual matched closely enough. Confirm below to add this leopard to
              the registry as a new record.
            </p>
            <div className="mx-auto mt-8 flex max-w-md flex-wrap justify-center gap-8">
              <div>
                <p className="eyebrow">Name</p>
                <p className="mt-2 font-display text-2xl text-cream">{result.leopard?.name ?? "—"}</p>
              </div>
              <div>
                <p className="eyebrow">Assigned ID</p>
                <p className="mt-2 font-display text-2xl text-cream">{result.leopard?.id ?? "—"}</p>
              </div>
              <div>
                <p className="eyebrow">Detected Viewpoint</p>
                <p className="mt-2 font-display text-2xl text-cream">{result.viewpoint?.used ?? "—"}</p>
              </div>
            </div>
            {result.warnings && result.warnings.length > 0 && (
              <div className="mx-auto mt-6 max-w-md space-y-1.5">
                {result.warnings.map((w, i) => (
                  <p key={i} className="text-xs leading-relaxed text-muted-foreground">
                    {w}
                  </p>
                ))}
              </div>
            )}
            <ConfirmLeopardPanel result={result} />
            <div className="mt-6 flex flex-wrap items-center justify-center gap-4">
              <DetailsLink />
            </div>
            <Link
              to="/vision-ai"
              className="mt-6 inline-flex items-center gap-3 rounded-xl border border-primary/60 px-8 py-3.5 text-[0.7rem] uppercase tracking-[0.24em] text-primary transition-colors hover:bg-primary hover:text-primary-foreground"
            >
              Upload another image
            </Link>
          </div>
        ) : (
          <>
            {isPossible && (
              <div className="glass-panel mt-12 flex items-center gap-4 rounded-sm px-6 py-5">
                <HelpCircle size={22} className="shrink-0 text-primary" />
                <p className="text-sm text-cream/85">
                  This is a possible match, not a confident one — the two signals below didn't fully
                  agree. Review the photos and confirm if it's the same individual.
                </p>
              </div>
            )}

            <div className="mt-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
              {[
                ["Decision", decisionLabel(result.decision)],
                ["Closest Match", result.leopard?.name ?? result.leopard?.id ?? "—"],
                [
                  "IVP Verified Points",
                  result.ivp?.verified_match_points != null ? `${result.ivp.verified_match_points}` : "—",
                ],
                ["Confidence", confidenceLabel(result.confidence_level)],
              ].map(([k, v]) => (
                <div key={k} className="glass-panel rounded-sm px-6 py-6">
                  <p className="eyebrow">{k}</p>
                  <p className="mt-2 font-display text-3xl text-cream">{v}</p>
                </div>
              ))}
            </div>

            {result.warnings && result.warnings.length > 0 && (
              <div className="mt-4 space-y-1.5">
                {result.warnings.map((w, i) => (
                  <p key={i} className="text-xs leading-relaxed text-muted-foreground">
                    {w}
                  </p>
                ))}
              </div>
            )}

            <div className="mt-8 grid items-stretch gap-6 lg:grid-cols-[1fr_auto_1fr]">
              <figure className="glass-panel overflow-hidden rounded-sm">
                <figcaption className="eyebrow border-b border-border/60 px-5 py-4">
                  Uploaded Image
                </figcaption>
                <img
                  src={uploaded ?? media.waterfall}
                  alt="Uploaded leopard submitted for identification"
                  className="h-[26rem] w-full object-cover"
                />
              </figure>

              <div className="flex items-center justify-center">
                <span className="font-display text-2xl italic text-primary">vs</span>
              </div>

              <figure className="glass-panel overflow-hidden rounded-sm">
                <figcaption className="eyebrow flex items-center justify-between border-b border-border/60 px-5 py-4">
                  Database Match
                  <span className="text-primary">{result.leopard?.name ?? result.leopard?.id ?? "—"}</span>
                </figcaption>
                <img
                  src={matchedImageSrc ?? media.waterfall}
                  alt={`Registry photograph of ${result.leopard?.id ?? "matched individual"}`}
                  className="h-[26rem] w-full object-cover"
                />
              </figure>
            </div>

            {keypointImageSrc && (
              <figure className="glass-panel mt-6 overflow-hidden rounded-sm">
                <figcaption className="eyebrow border-b border-border/60 px-5 py-4">
                  Matched Keypoints
                </figcaption>
                <img
                  src={keypointImageSrc}
                  alt="Visualization of SIFT keypoints matched between the two photographs"
                  className="w-full object-contain"
                />
              </figure>
            )}

            <div className="mt-8 grid gap-8 lg:grid-cols-[1.2fr_0.8fr]">
              <div className="glass-panel space-y-7 rounded-sm px-8 py-8">
                {[
                  {
                    label: "IVP Match Strength",
                    value: Math.min(
                      100,
                      Math.round(((result.ivp?.verified_match_points ?? 0) / IVP_CONFIDENT_THRESHOLD) * 100)
                    ),
                  },
                  {
                    label: "AI Identity Confidence",
                    value: Math.round((result.ai?.confidence ?? 0) * 100),
                  },
                  {
                    label: "AI Viewpoint Confidence",
                    value: Math.round((result.viewpoint?.ai_confidence ?? 0) * 100),
                  },
                  {
                    label: "AI Category Confidence",
                    value: Math.round((result.category?.confidence ?? 0) * 100),
                  },
                ].map((m) => (
                  <Meter key={m.label} {...m} />
                ))}
              </div>
              <div className="glass-panel rounded-sm px-8 py-8">
                <div className="flex items-center gap-3">
                  <CheckCircle2 className="text-primary" size={20} />
                  <p className="text-cream">
                    {result.ai?.agrees_with_ivp === true
                      ? "AI agrees with IVP pattern match"
                      : result.ai?.agrees_with_ivp === false
                        ? "AI identity estimate differs from IVP match"
                        : "Verified against registry"}
                  </p>
                </div>
                <dl className="mt-6 space-y-4 text-sm">
                  {[
                    ["Name", result.leopard?.name ?? "—"],
                    ["Individual ID", result.leopard?.id ?? "—"],
                    ["Detected viewpoint", result.viewpoint?.used ?? "—"],
                    ["Detected condition", result.category?.detected ?? "—"],
                    [
                      "Prior records",
                      result.leopard?.photo_count != null
                        ? `${result.leopard.photo_count} identification records`
                        : "—",
                    ],
                  ].map(([k, v]) => (
                    <div key={k} className="flex justify-between gap-6 border-b border-border/50 pb-3">
                      <dt className="text-muted-foreground">{k}</dt>
                      <dd className="text-right text-cream/90">{v}</dd>
                    </div>
                  ))}
                </dl>
              </div>
            </div>

            {isPossible && <ConfirmLeopardPanel result={result} />}

            <div className="mt-10 flex flex-wrap gap-4">
              <Link
                to="/vision-ai"
                className="inline-flex items-center gap-3 rounded-xl border border-border px-7 py-3.5 text-[0.7rem] uppercase tracking-[0.24em] text-cream/80 transition-colors hover:border-primary hover:text-primary"
              >
                <ArrowLeft size={15} /> Analyze another
              </Link>
              <DetailsLink />
            </div>
          </>
        )}
      </div>
    </div>
  );
}
