import { Link } from "@tanstack/react-router";
import { useEffect, useState } from "react";
import { ArrowLeft, BookOpen } from "lucide-react";
import { AnalysisResult, fetchDisplayableImage, readUpload } from "@/lib/panthera";

// Thresholds mirror the backend's decision rules (decision.py); they are only used to
// explain the outcome in words. Every number shown for the photo comes from the result.
const CONFIDENT = 20;
const POSSIBLE = 6;
const AI_AGREE_PCT = 50;
const AI_LED_PCT = 70;

const pct = (v: number | undefined) => (v == null ? "—" : `${Math.round(v * 100)}%`);

function decisionLabel(d: AnalysisResult["decision"]): string {
  if (d === "MATCH") return "Match";
  if (d === "POSSIBLE_MATCH") return "Possible Match";
  if (d === "NEW_LEOPARD") return "New Leopard";
  return "—";
}

function viewpointSource(source: string | undefined): string {
  if (source === "ai") return "predicted by the AI";
  if (source === "user") return "chosen by you";
  if (source === "dataset_record") return "taken from the dataset record";
  return "—";
}

// One plain-language sentence describing how the two signals were combined for this photo.
function explainDecision(r: AnalysisResult): string {
  const points = r.ivp?.verified_match_points ?? 0;
  const aiName = r.ai?.predicted_leopard_name ?? "a leopard";
  const aiConf = Math.round((r.ai?.confidence ?? 0) * 100);
  switch (r.path) {
    case "exact_record":
      return "This exact photograph is already in the registry, so it was recognised directly from its file fingerprint rather than by pattern matching.";
    case "confident_both_agree":
      return `IVP found ${points} verified points (${CONFIDENT} or more is a confident match) and the AI identity estimate independently named the same leopard (${aiConf}% confidence).`;
    case "confident_ivp_alone":
      return `IVP found ${points} verified points, enough for a confident match on its own, even though the AI identity estimate (${aiName}, ${aiConf}%) pointed to a different leopard.`;
    case "possible_upgraded_by_ai":
      return `IVP found ${points} verified points, which falls in the uncertain ${POSSIBLE}–${CONFIDENT - 1} range. The AI independently named the same leopard at ${aiConf}% (${AI_AGREE_PCT}% or more is needed), which upgraded the result to a match.`;
    case "possible_ivp_led":
      return `IVP found ${points} verified points, in the uncertain ${POSSIBLE}–${CONFIDENT - 1} range. The AI estimate (${aiName}, ${aiConf}%) did not confirm it, so the result stays a possible match.`;
    case "possible_ai_led":
      return `IVP found fewer than ${POSSIBLE} verified points (${points}), so pattern matching alone was inconclusive. The AI estimate named ${aiName} at ${aiConf}% (${AI_LED_PCT}% or more is needed), so it is shown as a possible match.`;
    case "new_leopard":
      return `IVP found fewer than ${POSSIBLE} verified points (${points}) and the AI estimate was below ${AI_LED_PCT}% (${aiConf}%), so no existing individual matched closely enough. This is treated as a new leopard.`;
    default:
      return "—";
  }
}

function Bar({ label, value, note }: { label: string; value: number; note?: string | undefined }) {
  const [w, setW] = useState(0);
  useEffect(() => {
    const t = setTimeout(() => setW(value), 200);
    return () => clearTimeout(t);
  }, [value]);
  return (
    <div>
      <div className="flex items-baseline justify-between gap-4">
        <p className="text-sm text-cream/80">{label}</p>
        <p className="font-display text-xl text-primary">{value}%</p>
      </div>
      <div className="mt-2 h-[3px] w-full bg-secondary">
        <div
          className="h-full transition-[width] duration-[1200ms] ease-out"
          style={{ width: `${w}%`, background: "var(--gradient-ember)" }}
        />
      </div>
      {note && <p className="mt-2 text-xs text-muted-foreground">{note}</p>}
    </div>
  );
}

function Stage({ n, title, what, value }: { n: number; title: string; what: string; value: string }) {
  return (
    <div className="glass-panel flex flex-col gap-2 rounded-sm px-5 py-5">
      <p className="eyebrow text-primary">Stage {n}</p>
      <h3 className="text-lg text-cream">{title}</h3>
      <p className="text-xs leading-relaxed text-muted-foreground">{what}</p>
      <p className="mt-auto border-t border-border/50 pt-3 text-sm text-cream/90">{value}</p>
    </div>
  );
}

// Size and resolution of the photo the user uploaded, measured in the browser from the stored copy.
function usePhotoFacts() {
  const [facts, setFacts] = useState<{ width: number; height: number; bytes: number } | null>(null);
  useEffect(() => {
    const dataUrl = readUpload()?.dataUrl;
    if (!dataUrl) return;
    const base64 = dataUrl.split(",")[1] ?? "";
    const bytes = Math.floor((base64.length * 3) / 4);
    const img = new Image();
    img.onload = () => setFacts({ width: img.naturalWidth, height: img.naturalHeight, bytes });
    img.src = dataUrl;
  }, []);
  return facts;
}

function formatBytes(b: number): string {
  return b >= 1024 * 1024 ? `${(b / (1024 * 1024)).toFixed(2)} MB` : `${Math.round(b / 1024)} KB`;
}

export function ResultDetails({ result }: { result: AnalysisResult }) {
  const [keypointSrc, setKeypointSrc] = useState<string | null>(null);
  const photo = usePhotoFacts();

  useEffect(() => {
    if (!result.keypoint_image_url) return;
    let objectUrl: string | null = null;
    let cancelled = false;
    fetchDisplayableImage(result.keypoint_image_url).then((src) => {
      if (cancelled) return;
      objectUrl = src;
      setKeypointSrc(src);
    });
    return () => {
      cancelled = true;
      if (objectUrl) URL.revokeObjectURL(objectUrl);
    };
  }, [result.keypoint_image_url]);

  const ivp = result.ivp;
  const ai = result.ai;
  const name = result.leopard?.name ?? "—";
  const points = ivp?.verified_match_points;
  const keypoints = ivp?.keypoints_extracted;

  // Every figure is read from this photo's result or derived from it; "—" when unavailable.
  const numbers: [string, string][] = [
    ["Photo resolution", photo ? `${photo.width} × ${photo.height} px` : "—"],
    ["Photo size", photo ? formatBytes(photo.bytes) : "—"],
    ["Megapixels", photo ? `${((photo.width * photo.height) / 1_000_000).toFixed(1)} MP` : "—"],
    ["Keypoints found", keypoints != null ? keypoints.toLocaleString() : "—"],
    ["Gallery photos searched", ivp ? ivp.candidates_searched.toLocaleString() : "—"],
    ["Verified points", points != null ? `${points}` : "—"],
    [
      "Keypoints verified",
      points != null && keypoints ? `${((points / keypoints) * 100).toFixed(1)}%` : "—",
    ],
    [
      "Vs. confident threshold",
      points != null ? `${points} vs ${CONFIDENT} needed (${(points / CONFIDENT).toFixed(1)}×)` : "—",
    ],
    ["AI identity confidence", pct(ai?.confidence)],
    ["AI viewpoint confidence", pct(result.viewpoint?.ai_confidence)],
    ["Prior records", result.leopard?.photo_count != null ? `${result.leopard.photo_count} photos` : "—"],
    [
      "Viewpoints on record",
      result.leopard?.viewpoints_on_record ? `${result.leopard.viewpoints_on_record.length} of 4` : "—",
    ],
  ];

  return (
    <div className="mx-auto max-w-7xl px-6 pt-36 pb-28 lg:px-10">
      <p className="eyebrow rise">Your Analysis · Full Report</p>
      <h1 className="rise mt-4 text-5xl text-cream lg:text-6xl" style={{ animationDelay: "0.15s" }}>
        IVP &amp; AI Report
      </h1>
      <p className="rise mt-5 max-w-2xl leading-relaxed text-muted-foreground" style={{ animationDelay: "0.3s" }}>
        How PANTHERA reached its decision for this photograph, stage by stage: what the classical
        pattern-verification pipeline (IVP) found, what the four AI models estimated, and how the two
        were combined.
      </p>

      <div className="mt-8 flex flex-wrap gap-4">
        <Link
          to="/analysis"
          className="inline-flex items-center gap-3 rounded-xl border border-border px-7 py-3.5 text-[0.7rem] uppercase tracking-[0.24em] text-cream/80 transition-colors hover:border-primary hover:text-primary"
        >
          <ArrowLeft size={15} /> Back to result
        </Link>
        <Link
          to="/ivp-system"
          className="inline-flex items-center gap-3 rounded-xl border border-border px-7 py-3.5 text-[0.7rem] uppercase tracking-[0.24em] text-cream/80 transition-colors hover:border-primary hover:text-primary"
        >
          <BookOpen size={15} /> General explanation
        </Link>
      </div>

      <div className="mt-10 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {[
          ["Decision", decisionLabel(result.decision)],
          ["Individual", name],
          ["IVP Verified Points", ivp ? `${ivp.verified_match_points}` : "—"],
          ["AI Identity Confidence", pct(ai?.confidence)],
        ].map(([k, v]) => (
          <div key={k} className="glass-panel rounded-sm px-6 py-6">
            <p className="eyebrow">{k}</p>
            <p className="mt-2 font-display text-3xl text-cream">{v}</p>
          </div>
        ))}
      </div>

      <div className="mt-10">
        <p className="eyebrow">By the numbers</p>
        <div className="mt-4 grid grid-cols-2 gap-3 md:grid-cols-3 lg:grid-cols-4">
          {numbers.map(([k, v]) => (
            <div key={k} className="glass-panel rounded-sm px-5 py-4">
              <p className="eyebrow text-[0.6rem]">{k}</p>
              <p className="mt-1.5 font-display text-xl text-cream">{v}</p>
            </div>
          ))}
        </div>
      </div>

      <div className="glass-panel mt-6 rounded-sm px-8 py-8">
        <p className="eyebrow text-primary">How the decision was made</p>
        <p className="mt-3 leading-relaxed text-cream/90">{explainDecision(result)}</p>
        {result.warnings && result.warnings.length > 0 && (
          <div className="mt-4 space-y-1.5 border-t border-border/50 pt-4">
            {result.warnings.map((w, i) => (
              <p key={i} className="text-xs leading-relaxed text-muted-foreground">
                {w}
              </p>
            ))}
          </div>
        )}
      </div>

      <div className="mt-16">
        <p className="eyebrow">IVP · Classical Computer Vision</p>
        <h2 className="mt-3 text-3xl text-cream lg:text-4xl">Pattern verification for this photo</h2>
        <div className="mt-10 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          <Stage
            n={1}
            title="Categorize"
            what="Classifies the image condition: normal, dark, red-tinted, obscured or grayscale."
            value={
              result.category
                ? `${result.category.detected} (${pct(result.category.confidence)} confidence)`
                : "—"
            }
          />
          <Stage
            n={2}
            title="Correct"
            what="Applies enhancement so the rosette pattern reads clearly."
            value={result.correction_applied ?? "—"}
          />
          <Stage
            n={3}
            title="Extract Keypoints"
            what="SIFT locates distinctive landmark points across the rosette pattern."
            value={ivp ? `${ivp.keypoints_extracted.toLocaleString()} keypoints found` : "—"}
          />
          <Stage
            n={4}
            title="Match Candidates"
            what="Compares keypoints against gallery photos of the same viewpoint."
            value={
              ivp
                ? `${ivp.candidates_searched.toLocaleString()} gallery photos searched (${result.viewpoint?.used ?? "—"} view)`
                : "—"
            }
          />
          <Stage
            n={5}
            title="Verify Geometrically"
            what="RANSAC keeps only the points that form a consistent spatial arrangement."
            value={
              ivp
                ? `${ivp.verified_match_points} verified points${
                    ivp.matched_photo_file ? ` · best photo ${ivp.matched_photo_file}` : ""
                  }`
                : "—"
            }
          />
          <Stage
            n={6}
            title="Decide"
            what="The verified point count, cross-checked with the AI estimate, sets the outcome."
            value={`${decisionLabel(result.decision)} · ${result.confidence_level ?? "—"} confidence`}
          />
        </div>

        {keypointSrc && (
          <figure className="glass-panel mt-6 overflow-hidden rounded-sm">
            <figcaption className="eyebrow border-b border-border/60 px-5 py-4">Matched Keypoints</figcaption>
            <img
              src={keypointSrc}
              alt="SIFT keypoints matched between the uploaded photograph and the registry photograph"
              className="w-full object-contain"
            />
          </figure>
        )}
      </div>

      <div className="mt-16">
        <p className="eyebrow">AI · Four Neural Networks</p>
        <h2 className="mt-3 text-3xl text-cream lg:text-4xl">What the AI models estimated</h2>
        <div className="mt-10 grid gap-6 lg:grid-cols-[1.2fr_0.8fr]">
          <div className="glass-panel space-y-7 rounded-sm px-8 py-8">
            <Bar
              label="Leopard check"
              value={Math.round((result.validator?.confidence ?? 0) * 100)}
              note="Confidence that the photograph shows a leopard."
            />
            <Bar
              label="Image condition"
              value={Math.round((result.category?.confidence ?? 0) * 100)}
              note={result.category ? `Detected: ${result.category.detected}` : undefined}
            />
            <Bar
              label="Viewpoint"
              value={Math.round((result.viewpoint?.ai_confidence ?? 0) * 100)}
              note={
                result.viewpoint
                  ? `AI predicted: ${result.viewpoint.ai_predicted}. Used: ${result.viewpoint.used} (${viewpointSource(result.viewpoint.source)}).`
                  : undefined
              }
            />
            <Bar
              label="Identity estimate"
              value={Math.round((ai?.confidence ?? 0) * 100)}
              note={ai ? `Predicted individual: ${ai.predicted_leopard_name}` : undefined}
            />
          </div>
          <div className="glass-panel rounded-sm px-8 py-8">
            <p className="eyebrow text-primary">AI vs IVP</p>
            <p className="mt-3 text-cream">
              {ai?.agrees_with_ivp === true
                ? "The AI identity estimate agrees with the IVP pattern match."
                : ai?.agrees_with_ivp === false
                  ? "The AI identity estimate differs from the IVP pattern match."
                  : "The AI estimate was not used to confirm a pattern match for this photo."}
            </p>
            <dl className="mt-6 space-y-4 text-sm">
              {[
                ["IVP match", ivp?.matched_leopard_id ? ivp.matched_leopard_id.slice(0, 8).toUpperCase() : "none"],
                ["AI estimate", ai?.predicted_leopard_id ? ai.predicted_leopard_id.slice(0, 8).toUpperCase() : "—"],
                ["Prior records", result.leopard?.photo_count != null ? `${result.leopard.photo_count}` : "—"],
              ].map(([k, v]) => (
                <div key={k} className="flex justify-between gap-6 border-b border-border/50 pb-3">
                  <dt className="text-muted-foreground">{k}</dt>
                  <dd className="text-right text-cream/90">{v}</dd>
                </div>
              ))}
            </dl>
          </div>
        </div>
      </div>
    </div>
  );
}
