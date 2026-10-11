import heroVideo from "@/assets/hero.mp4.asset.json";
import sunset from "@/assets/leopard-sunset.jpg.asset.json";
import foliage from "@/assets/leopard-foliage.jpg.asset.json";
import waterfall from "@/assets/leopard-waterfall.jpg.asset.json";
import leopardA from "@/assets/dataset/leopard-a.jpg";
import leopardB from "@/assets/dataset/leopard-b.jpg";
import leopardC from "@/assets/dataset/leopard-c.jpg";

export const media = {
  heroVideo: heroVideo.url,
  sunset: sunset.url,
  foliage: foliage.url,
  waterfall: waterfall.url,
};

// Set VITE_API_BASE_URL (e.g. in a .env file) to the hosted backend; falls back to local dev.
export const API_BASE_URL: string = import.meta.env["VITE_API_BASE_URL"] ?? "http://localhost:8090";

export interface AnalysisResult {
  status: "success" | "rejected" | "error";
  message?: string;
  decision?: "MATCH" | "POSSIBLE_MATCH" | "NEW_LEOPARD";
  path?: string;
  demo_category?: string | null;
  confidence_level?: string;
  exact_record?: boolean;
  warnings?: string[];
  correction_applied?: string;
  validator?: { confidence: number };
  category?: { detected: string; confidence: number };
  viewpoint?: {
    used: string;
    source: "ai" | "user" | "dataset_record";
    ai_predicted: string;
    ai_confidence: number;
  };
  ivp?: {
    verified_match_points: number;
    matched_leopard_id: string | null;
    matched_photo_file: string | null;
    keypoints_extracted: number;
    candidates_searched: number;
  };
  ai?: {
    predicted_leopard_id: string;
    predicted_leopard_name: string;
    confidence: number;
    agrees_with_ivp: boolean | null;
  };
  leopard?: {
    id: string;
    name: string;
    is_new: boolean;
    photo_count: number;
    viewpoints_on_record: string[];
  };
  matched_photo_file?: string | null;
  upload_id?: string;
  uploaded_image_url?: string;
  matched_image_url?: string;
  keypoint_image_url?: string;
}

// Bypasses the ngrok free-tier "you are about to visit this site" interstitial,
// which ngrok injects for browser-style GET requests to *.ngrok-free.dev and would
// otherwise return its own warning HTML instead of the actual API response. Harmless
// no-op against a non-ngrok host (e.g. once deployed to Render/Railway).
const NGROK_SKIP_HEADER = { "ngrok-skip-browser-warning": "true" };

export async function analyzeLeopardImage(file: File, viewpoint?: string): Promise<AnalysisResult> {
  const formData = new FormData();
  formData.append("image", file);
  if (viewpoint) formData.append("viewpoint", viewpoint);
  const response = await fetch(`${API_BASE_URL}/analyze`, {
    method: "POST",
    headers: NGROK_SKIP_HEADER,
    body: formData,
  });
  if (!response.ok) {
    throw new Error(`Analysis request failed with status ${response.status}`);
  }
  return response.json();
}

export async function confirmNewLeopard(
  uploadId: string
): Promise<{ status: string; leopard_id: string; leopard_name: string; message: string }> {
  const response = await fetch(`${API_BASE_URL}/confirm-new`, {
    method: "POST",
    headers: { ...NGROK_SKIP_HEADER, "Content-Type": "application/json" },
    body: JSON.stringify({ upload_id: uploadId }),
  });
  if (!response.ok) {
    throw new Error(`Confirm request failed with status ${response.status}`);
  }
  return response.json();
}

export async function askChatbot(question: string): Promise<{ status: string; answer: string; suggestions?: string[] }> {
  const response = await fetch(`${API_BASE_URL}/chat`, {
    method: "POST",
    headers: { ...NGROK_SKIP_HEADER, "Content-Type": "application/json" },
    body: JSON.stringify({ question }),
  });
  if (!response.ok) {
    throw new Error(`Chat request failed with status ${response.status}`);
  }
  return response.json();
}

// The backend now returns ready-to-use relative URLs (e.g. "/image?path=gallery/x.jpg"),
// so this just anchors them to the current API host.
export function imageUrl(relativeUrl: string | null | undefined): string | null {
  if (!relativeUrl) return null;
  return `${API_BASE_URL}${relativeUrl}`;
}

// A plain <img src> pointing at the ngrok URL hits the browser-warning
// interstitial (it can't carry the skip header), so images are fetched
// manually with that header and handed to <img> as a local blob URL instead.
export async function fetchDisplayableImage(relativeUrl: string | null | undefined): Promise<string | null> {
  const url = imageUrl(relativeUrl);
  if (!url) return null;
  const response = await fetch(url, { headers: NGROK_SKIP_HEADER });
  if (!response.ok) return null;
  const blob = await response.blob();
  return URL.createObjectURL(blob);
}

const KEY = "panthera:upload";
const RESULT_KEY = "panthera:result";

export function storeUpload(dataUrl: string, name: string) {
  sessionStorage.setItem(KEY, JSON.stringify({ dataUrl, name }));
}

export function readUpload(): { dataUrl: string; name: string } | null {
  if (typeof window === "undefined") return null;
  const raw = sessionStorage.getItem(KEY);
  if (!raw) return null;
  try {
    return JSON.parse(raw);
  } catch {
    return null;
  }
}

export function storeResult(result: AnalysisResult) {
  sessionStorage.setItem(RESULT_KEY, JSON.stringify(result));
}

export function readResult(): AnalysisResult | null {
  if (typeof window === "undefined") return null;
  const raw = sessionStorage.getItem(RESULT_KEY);
  if (!raw) return null;
  try {
    return JSON.parse(raw);
  } catch {
    return null;
  }
}

// Real entries from the training dataset (leopard_mapping.csv) — actual
// individual IDs and photograph counts, not fabricated figures.
export const DATASET_INDIVIDUAL_COUNT = 431;

export const leopards = [
  {
    id: "81ad30d8-15c7-492e-918b-d9592d8f3f08",
    image: leopardA,
    records: 232,
    viewpoint: "Right profile",
  },
  {
    id: "23078cd2-337a-4f60-b5d1-31cff51b9c47",
    image: leopardB,
    records: 23,
    viewpoint: "Front-facing",
  },
  {
    id: "59e30bdf-a8e4-4f2f-b003-2a84e2cd7384",
    image: leopardC,
    records: 6,
    viewpoint: "Right profile",
  },
];
