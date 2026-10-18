/**
 * Preset Model LLM & Provider untuk Konfigurasi Agen Korporat.
 */

export interface ProviderOption {
  id: string;
  label: string;
}

export const LLM_PROVIDERS: ProviderOption[] = [
  { id: "openrouter", label: "OpenRouter (Free Presets)" },
  { id: "deepseek", label: "DeepSeek Official" },
  { id: "anthropic", label: "Anthropic Claude" },
  { id: "openai", label: "OpenAI GPT" },
  { id: "gemini", label: "Google Gemini" },
  { id: "groq", label: "Groq High-Speed" },
  { id: "ollama", label: "Ollama Local" },
  { id: "openai_compatible", label: "Custom Provider (Format OpenAI)" },
];

export const RECOMMENDED_PRESETS: Record<string, string[]> = {
  openrouter: [
    "deepseek/deepseek-r1:free",
    "deepseek/deepseek-chat:free",
    "google/gemini-2.0-flash-exp:free",
    "meta-llama/llama-3.3-70b-instruct:free",
    "qwen/qwen-2.5-coder-32b-instruct:free",
  ],
  deepseek: ["deepseek-reasoner", "deepseek-chat"],
  anthropic: ["claude-3-5-sonnet-20241022", "claude-3-5-haiku-20241022"],
  openai: ["gpt-4o", "gpt-4o-mini", "o1-mini"],
  gemini: ["gemini-2.5-flash", "gemini-2.5-pro"],
  groq: ["llama-3.3-70b-versatile", "mixtral-8x7b-32768"],
  ollama: ["llama3.2", "qwen2.5-coder:7b", "deepseek-r1:8b"],
  openai_compatible: [],
  custom: [],
};

export const AGENT_TOOLS = [
  { id: "read_file", label: "Baca File" },
  { id: "write_file", label: "Tulis File" },
  { id: "ast_patch_file", label: "AST Patch File" },
  { id: "search_codebase", label: "Cari Kode (Simbol & Teks)" },
  { id: "web_search", label: "Web Search" },
  { id: "execute_code", label: "Eksekusi Kode (Terminal)" },
  { id: "inspect_db_schema", label: "Inspect DB Schema" },
  { id: "validate_api_contract", label: "Validate API Contract" },
  { id: "git_diff_summary", label: "Git Diff Summary" },
  { id: "runtime_tool_builder", label: "Runtime Tool Builder" },
];
