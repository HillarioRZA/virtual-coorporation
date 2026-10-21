import { describe, it, expect, beforeEach, afterEach } from "vitest";
import { getApiBase, getApiV1Base, getWsBase } from "@/lib/config";

describe("Frontend Dashboard Core Suite", () => {
  const originalEnv = process.env.NEXT_PUBLIC_API_URL;

  beforeEach(() => {
    delete process.env.NEXT_PUBLIC_API_URL;
  });

  afterEach(() => {
    if (originalEnv) {
      process.env.NEXT_PUBLIC_API_URL = originalEnv;
    } else {
      delete process.env.NEXT_PUBLIC_API_URL;
    }
  });

  it("resolves default backend host when environment variable is unset", () => {
    expect(getApiBase()).toBe("http://127.0.0.1:8000");
    expect(getApiV1Base()).toBe("http://127.0.0.1:8000/api/v1");
    expect(getWsBase()).toBe("ws://127.0.0.1:8000");
  });

  it("correctly cleans and formats custom NEXT_PUBLIC_API_URL with trailing slashes", () => {
    process.env.NEXT_PUBLIC_API_URL = "http://my-production-domain.com:8000/";
    expect(getApiBase()).toBe("http://my-production-domain.com:8000");
    expect(getApiV1Base()).toBe("http://my-production-domain.com:8000/api/v1");
    expect(getWsBase()).toBe("ws://my-production-domain.com:8000");
  });

  it("handles NEXT_PUBLIC_API_URL already including /api/v1 prefix gracefully", () => {
    process.env.NEXT_PUBLIC_API_URL = "http://my-production-domain.com/api/v1/";
    expect(getApiBase()).toBe("http://my-production-domain.com");
    expect(getApiV1Base()).toBe("http://my-production-domain.com/api/v1");
  });
});
