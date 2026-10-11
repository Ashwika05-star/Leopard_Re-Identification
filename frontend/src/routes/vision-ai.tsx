import { createFileRoute, useNavigate } from "@tanstack/react-router";
import { useRef, useState } from "react";
import { analyzeLeopardImage, media, storeResult, storeUpload } from "@/lib/panthera";
import { UploadCloud, Image as ImageIcon, Loader2, X } from "lucide-react";

export const Route = createFileRoute("/vision-ai")({
  head: () => ({
    meta: [
      { title: "Identify a Leopard — PANTHERA Analyse" },
      {
        name: "description",
        content:
          "Upload a leopard image and compare its unique markings against individuals in the PANTHERA database.",
      },
      { property: "og:title", content: "Identify a Leopard — PANTHERA Analyse" },
      {
        property: "og:description",
        content: "Compare a leopard's markings against the PANTHERA individual registry.",
      },
    ],
  }),
  component: VisionAI,
});

const ACCEPT = ["image/jpeg", "image/png", "image/webp"];

function VisionAI() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [fileName, setFileName] = useState("");
  const [dragging, setDragging] = useState(false);
  const [error, setError] = useState("");
  const [analyzing, setAnalyzing] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);
  const navigate = useNavigate();

  const handleFile = (file: File) => {
    if (!ACCEPT.includes(file.type)) {
      setError("Unsupported format. Please use JPG, PNG or WEBP.");
      return;
    }
    setError("");
    setSelectedFile(file);
    setFileName(file.name);
    const reader = new FileReader();
    reader.onload = () => setPreview(String(reader.result));
    reader.readAsDataURL(file);
  };

  const analyze = async () => {
    if (!selectedFile || !preview) return;
    setAnalyzing(true);
    setError("");
    storeUpload(preview, fileName);
    try {
      const result = await analyzeLeopardImage(selectedFile);
      storeResult(result);
      navigate({ to: "/analysis" });
    } catch {
      setError("Could not reach the analysis server. Please try again.");
      setAnalyzing(false);
    }
  };

  return (
    <div className="relative min-h-screen">
      <img
        src={media.foliage}
        alt=""
        aria-hidden
        className="fixed inset-0 h-full w-full object-cover opacity-30"
      />
      <div className="veil fixed inset-0" />

      <div className="relative mx-auto max-w-4xl px-6 pt-40 pb-28 lg:px-10">
        <p className="eyebrow rise">Analyse · Step 01</p>
        <h1 className="rise mt-5 text-5xl text-cream lg:text-6xl" style={{ animationDelay: "0.15s" }}>
          Identify a Leopard
        </h1>
        <p
          className="rise mt-5 max-w-xl leading-relaxed text-cream/75"
          style={{ animationDelay: "0.3s" }}
        >
          Upload a leopard image to compare its unique markings with individuals in our database.
        </p>

        <div className="rise mt-12" style={{ animationDelay: "0.45s" }}>
          {!preview ? (
            <div
              onDragOver={(e) => {
                e.preventDefault();
                setDragging(true);
              }}
              onDragLeave={() => setDragging(false)}
              onDrop={(e) => {
                e.preventDefault();
                setDragging(false);
                const f = e.dataTransfer.files[0];
                if (f) handleFile(f);
              }}
              onClick={() => inputRef.current?.click()}
              className={`glass-panel flex cursor-pointer flex-col items-center justify-center rounded-sm border-dashed px-8 py-24 text-center transition-all duration-300 ${
                dragging ? "border-primary bg-primary/10" : "hover:border-primary/50"
              }`}
              style={{ boxShadow: "var(--shadow-deep)" }}
            >
              <UploadCloud size={44} strokeWidth={1} className="text-primary" />
              <p className="mt-6 font-display text-3xl text-cream">Drop leopard image here</p>
              <p className="mt-3 text-sm text-cream/60">
                or <span className="text-primary underline underline-offset-4">Browse Files</span>
              </p>
              <p className="eyebrow mt-8">JPG · PNG · WEBP</p>
              <input
                ref={inputRef}
                type="file"
                accept="image/jpeg,image/png,image/webp"
                className="hidden"
                onChange={(e) => {
                  const f = e.target.files?.[0];
                  if (f) handleFile(f);
                }}
              />
            </div>
          ) : (
            <div className="glass-panel rounded-sm p-5" style={{ boxShadow: "var(--shadow-deep)" }}>
              <div className="relative overflow-hidden rounded-sm">
                <img src={preview} alt="Uploaded leopard" className="max-h-[30rem] w-full object-cover" />
                <button
                  onClick={() => {
                    setSelectedFile(null);
                    setPreview(null);
                    setFileName("");
                  }}
                  className="absolute right-3 top-3 rounded-sm bg-background/70 p-2 text-cream backdrop-blur transition-colors hover:text-primary"
                  aria-label="Remove image"
                >
                  <X size={16} />
                </button>
                {analyzing && (
                  <div className="absolute inset-0 flex flex-col items-center justify-center bg-background/70 backdrop-blur-sm">
                    <Loader2 className="animate-spin text-primary" size={32} />
                    <p className="eyebrow mt-5">Extracting rosette signature…</p>
                  </div>
                )}
              </div>
              <div className="mt-5 flex flex-wrap items-center justify-between gap-4">
                <p className="flex items-center gap-2 text-sm text-cream/70">
                  <ImageIcon size={15} className="text-primary" />
                  {fileName}
                </p>
                <button
                  onClick={analyze}
                  disabled={analyzing}
                  className="rounded-xl bg-primary px-8 py-3.5 text-[0.72rem] uppercase tracking-[0.26em] text-primary-foreground transition-all hover:brightness-110 disabled:opacity-60"
                >
                  {analyzing ? "Analyzing…" : "Analyze Image"}
                </button>
              </div>
            </div>
          )}
          {error && <p className="mt-4 text-sm text-destructive">{error}</p>}
        </div>

        <div className="mt-16 grid gap-8 sm:grid-cols-3">
          {[
            ["01", "Clear coat visible", "Flank or shoulder rosettes give the strongest signature."],
            ["02", "Any light condition", "Night-vision and infrared camera-trap frames are supported."],
            ["03", "Nothing is stored", "Field uploads stay local to this session until you submit."],
          ].map(([n, t, d]) => (
            <div key={n} className="border-t border-border/70 pt-5">
              <p className="eyebrow text-primary">{n}</p>
              <p className="mt-2 text-cream">{t}</p>
              <p className="mt-1.5 text-sm leading-relaxed text-muted-foreground">{d}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
