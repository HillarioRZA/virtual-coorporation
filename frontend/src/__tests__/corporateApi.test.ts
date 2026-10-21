import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { fetchBranches, fetchActiveBranch, createDivision } from "@/lib/corporateApi";

describe("Corporate API Client Suite", () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("fetchBranches returns mapped corporate branches on HTTP 200", async () => {
    const mockBranches = [
      {
        id: "branch_main",
        name: "Main Production",
        slug: "main",
        description: "Default corporate branch",
        is_active_main: true,
        created_at: "2026-10-20T00:00:00",
        updated_at: "2026-10-20T00:00:00",
      },
    ];

    vi.spyOn(global, "fetch").mockResolvedValueOnce({
      ok: true,
      status: 200,
      json: async () => mockBranches,
    } as Response);

    const result = await fetchBranches();
    expect(result).toHaveLength(1);
    expect(result[0].id).toBe("branch_main");
    expect(result[0].is_active_main).toBe(true);
  });

  it("fetchActiveBranch throws descriptive error when active branch is not found", async () => {
    vi.spyOn(global, "fetch").mockResolvedValueOnce({
      ok: false,
      status: 404,
      statusText: "Not Found",
      json: async () => ({ detail: "Active branch tidak ditemukan." }),
    } as Response);

    await expect(fetchActiveBranch()).rejects.toThrow("Active branch tidak ditemukan.");
  });

  it("createDivision correctly serializes payload and parses created division response", async () => {
    const mockCreated = {
      id: "div_eng",
      branch_id: "branch_main",
      name: "Engineering",
      slug: "engineering",
      description: "Software engineering department",
      accent_color: "#3B82F6",
      icon_name: "Code",
      is_system_default: true,
      order_index: 1,
      created_at: "2026-10-20T00:00:00",
    };

    const fetchSpy = vi.spyOn(global, "fetch").mockResolvedValueOnce({
      ok: true,
      status: 201,
      json: async () => mockCreated,
    } as Response);

    const payload = {
      branch_id: "branch_main",
      name: "Engineering",
      slug: "engineering",
      description: "Software engineering department",
      accent_color: "#3B82F6",
      icon_name: "Code",
      order_index: 1,
    };

    const res = await createDivision(payload);
    expect(fetchSpy).toHaveBeenCalled();
    expect(res.name).toBe("Engineering");
    expect(res.slug).toBe("engineering");
  });
});
