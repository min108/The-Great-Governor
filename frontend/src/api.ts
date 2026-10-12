export async function api<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(path, init);
  if (!response.ok) {
    let message = response.statusText;
    try {
      const data = await response.json();
      message = data.detail || message;
    } catch {
      /* ignore */
    }
    throw new Error(typeof message === "string" ? message : JSON.stringify(message));
  }
  return response.json();
}

export type Relation = {
  id: string;
  rel_type: string;
  way: string;
  other_kind: string;
  other_id: string;
  other_name: string;
  period: string;
  condition: string;
  confirm_status: string;
  evidence: string;
};

export function hrefFor(kind: string, id: string) {
  if (kind === "standard") return `/standards/${id}`;
  if (kind === "algorithm") return `/algorithms/${id}`;
  if (kind === "object") return `/objects/${id}`;
  return `/assets/${id}`;
}
