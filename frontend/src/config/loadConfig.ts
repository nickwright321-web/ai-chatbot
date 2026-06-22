export interface RuntimeConfig {
  websocketUrl: string;
}

export async function loadConfig(): Promise<RuntimeConfig> {
  const response = await fetch("/config.json", {
    cache: "no-store"
  });

  if (!response.ok) {
    throw new Error("Failed to load runtime config");
  }

  return response.json();
}
