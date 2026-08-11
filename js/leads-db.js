/**
 * Supabase-backed API shim matching the previous /api/* routes
 * used by leads.html
 */
(function () {
  const PRODUCT_TYPES = new Set(["solar", "battery", "solar-battery"]);
  const LEAD_SOURCES = new Set(["social_media", "third_party", "channel_partner"]);
  const PHASES = new Set(["single", "three"]);
  const STATUSES = new Set([
    "lead",
    "opportunity",
    "quoted",
    "closed_won",
    "closed_lost",
    "installation",
  ]);
  const NOTE_STATUSES = new Set([
    "opportunity",
    "quoted",
    "closed_won",
    "closed_lost",
    "installation",
  ]);
  const ALLOWED_TRANSITIONS = {
    lead: new Set(["opportunity"]),
    opportunity: new Set(["quoted"]),
    quoted: new Set(["closed_won", "closed_lost"]),
    closed_won: new Set(["installation"]),
    closed_lost: new Set(),
    installation: new Set(),
  };

  let client = null;

  function configured() {
    const cfg = window.SUPABASE_CONFIG || {};
    return Boolean(cfg.url && cfg.anonKey);
  }

  function getClient() {
    if (!configured()) {
      throw new Error(
        "Supabase is not configured. Add your Project URL and anon key in js/supabase-config.js"
      );
    }
    if (!client) {
      if (!window.supabase || !window.supabase.createClient) {
        throw new Error("Supabase library failed to load.");
      }
      client = window.supabase.createClient(
        window.SUPABASE_CONFIG.url,
        window.SUPABASE_CONFIG.anonKey
      );
    }
    return client;
  }

  function uid(prefix) {
    return (
      prefix +
      "_" +
      Math.random().toString(16).slice(2) +
      Date.now().toString(16).slice(-6)
    );
  }

  function normalizeStatus(status) {
    const s = (status || "lead").toLowerCase();
    return s === "closed_won" ? "installation" : s;
  }

  function rowToLead(row) {
    return {
      id: row.id,
      customerName: row.customer_name,
      mobile: row.mobile,
      email: row.email,
      address: row.address,
      productType: row.product_type,
      nmi: row.nmi || "",
      leadSource: row.lead_source || "",
      phase: row.phase,
      status: row.status,
      createdAt: row.created_at,
      updatedAt: row.updated_at,
    };
  }

  function rowToNote(row) {
    return {
      id: row.id,
      leadId: row.lead_id,
      body: row.body,
      createdAt: row.created_at,
    };
  }

  function validateLead(payload, { partial = false } = {}) {
    const customerName = String(payload.customerName || "").trim();
    const mobile = String(payload.mobile || "").trim();
    const email = String(payload.email || "").trim();
    const address = String(payload.address || "").trim();
    const productType = String(payload.productType || "").trim();
    const nmi = String(payload.nmi || "").trim().toUpperCase();
    const leadSource = String(payload.leadSource || "").trim();
    const phase = String(payload.phase || "").trim();
    let status = String(payload.status || "lead").trim().toLowerCase() || "lead";

    if (!partial || "customerName" in payload) {
      if (!customerName) throw new Error("Customer name is required.");
    }
    if (!partial || "mobile" in payload) {
      if (!mobile) throw new Error("Mobile number is required.");
    }
    if (!partial || "email" in payload) {
      if (!email || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
        throw new Error("A valid email address is required.");
      }
    }
    if (!partial || "address" in payload) {
      if (!address) throw new Error("Address is required.");
    }
    if (!partial || "productType" in payload) {
      if (!PRODUCT_TYPES.has(productType)) {
        throw new Error("Product type must be solar, battery, or solar-battery.");
      }
    }
    if (!partial || "leadSource" in payload) {
      if (!LEAD_SOURCES.has(leadSource)) {
        throw new Error("Select a source of lead.");
      }
    }
    if (!partial || "phase" in payload) {
      if (!PHASES.has(phase)) throw new Error("Phase must be single or three.");
    }
    if (nmi && (nmi.length > 11 || !/^[A-Z0-9]+$/.test(nmi))) {
      throw new Error("NMI must be up to 11 letters/numbers.");
    }
    if (!STATUSES.has(status)) throw new Error("Invalid status.");
    status = normalizeStatus(status);

    return {
      customer_name: customerName,
      mobile,
      email,
      address,
      product_type: productType,
      nmi: nmi || null,
      lead_source: leadSource,
      phase,
      status,
    };
  }

  async function listLeads(query = {}) {
    const db = getClient();
    let q = db.from("leads").select("*").order("created_at", { ascending: false });
    if (query.status && query.status !== "all") {
      q = q.eq("status", query.status);
    }
    const { data, error } = await q;
    if (error) throw new Error(error.message);
    let leads = (data || []).map(rowToLead);
    const text = (query.q || "").trim().toLowerCase();
    if (text) {
      leads = leads.filter((l) =>
        [
          l.customerName,
          l.mobile,
          l.email,
          l.address,
          l.nmi,
          l.leadSource,
          l.productType,
          l.phase,
          l.status,
        ]
          .join(" ")
          .toLowerCase()
          .includes(text)
      );
    }
    return { leads, count: leads.length };
  }

  async function getLead(id) {
    const db = getClient();
    const { data, error } = await db.from("leads").select("*").eq("id", id).single();
    if (error) throw new Error(error.message);
    return { lead: rowToLead(data) };
  }

  async function createLead(payload) {
    const body = validateLead({ ...payload, status: payload.status || "lead" });
    const now = new Date().toISOString();
    const row = {
      id: uid("lead"),
      ...body,
      created_at: now,
      updated_at: now,
    };
    const db = getClient();
    const { data, error } = await db.from("leads").insert(row).select("*").single();
    if (error) throw new Error(error.message);
    return { lead: rowToLead(data) };
  }

  async function patchLead(id, payload) {
    const currentRes = await getLead(id);
    const current = currentRes.lead;
    const requestedStatus = String(payload.status || current.status)
      .trim()
      .toLowerCase();

    if (!STATUSES.has(requestedStatus)) throw new Error("Invalid status.");

    if (requestedStatus !== current.status) {
      const allowed = ALLOWED_TRANSITIONS[current.status] || new Set();
      if (requestedStatus === "closed_won") {
        if (!allowed.has("closed_won")) {
          throw new Error(
            `Cannot move from ${current.status} to closed_won. Follow the pipeline.`
          );
        }
      } else if (!allowed.has(requestedStatus)) {
        const nextSteps = [...allowed].join(", ") || "none";
        throw new Error(
          `Invalid step. From ${current.status} you can only move to: ${nextSteps}.`
        );
      }
    }

    const merged = {
      customerName: payload.customerName ?? current.customerName,
      mobile: payload.mobile ?? current.mobile,
      email: payload.email ?? current.email,
      address: payload.address ?? current.address,
      productType: payload.productType ?? current.productType,
      nmi: payload.nmi ?? current.nmi,
      leadSource: payload.leadSource ?? current.leadSource,
      phase: payload.phase ?? current.phase,
      status: requestedStatus,
    };
    const body = validateLead(merged);
    const now = new Date().toISOString();

    const db = getClient();
    const { data, error } = await db
      .from("leads")
      .update({
        ...body,
        updated_at: now,
      })
      .eq("id", id)
      .select("*")
      .single();
    if (error) throw new Error(error.message);

    return {
      lead: rowToLead(data),
      movedToInstallation: requestedStatus === "closed_won",
      openedNotes: NOTE_STATUSES.has(body.status),
    };
  }

  async function deleteLead(id) {
    const db = getClient();
    const { error } = await db.from("leads").delete().eq("id", id);
    if (error) throw new Error(error.message);
    return { ok: true, id };
  }

  async function listNotes(leadId) {
    const leadRes = await getLead(leadId);
    const db = getClient();
    const { data, error } = await db
      .from("notes")
      .select("*")
      .eq("lead_id", leadId)
      .order("created_at", { ascending: false });
    if (error) throw new Error(error.message);
    return {
      lead: leadRes.lead,
      notes: (data || []).map(rowToNote),
      count: (data || []).length,
    };
  }

  async function createNote(leadId, payload) {
    const leadRes = await getLead(leadId);
    const status = leadRes.lead.status;
    if (!NOTE_STATUSES.has(status)) {
      throw new Error("Move this record to Opportunity before adding notes.");
    }
    const body = String(payload.body || "").trim();
    if (!body) throw new Error("Note text is required.");
    if (body.length > 5000) throw new Error("Note is too long (max 5000 characters).");

    const now = new Date().toISOString();
    const row = {
      id: uid("note"),
      lead_id: leadId,
      body,
      created_at: now,
    };
    const db = getClient();
    const { data, error } = await db.from("notes").insert(row).select("*").single();
    if (error) throw new Error(error.message);

    await db.from("leads").update({ updated_at: now }).eq("id", leadId);
    return { note: rowToNote(data) };
  }

  async function health() {
    if (!configured()) {
      return {
        ok: false,
        error: "Supabase config missing",
      };
    }
    const db = getClient();
    const { error } = await db.from("leads").select("id", { count: "exact", head: true });
    if (error) throw new Error(error.message);
    return { ok: true, provider: "supabase" };
  }

  /**
   * Drop-in replacement for fetch('/api/...').
   */
  async function api(path, options = {}) {
    const method = (options.method || "GET").toUpperCase();
    let payload = {};
    if (options.body) {
      payload = typeof options.body === "string" ? JSON.parse(options.body) : options.body;
    }

    const clean = path.split("?")[0];
    const qs = new URLSearchParams(path.includes("?") ? path.split("?")[1] : "");

    if (clean === "/api/health" && method === "GET") return health();

    if (clean === "/api/leads" && method === "GET") {
      return listLeads({ q: qs.get("q") || "", status: qs.get("status") || "" });
    }
    if (clean === "/api/leads" && method === "POST") return createLead(payload);

    let m = clean.match(/^\/api\/leads\/([^/]+)$/);
    if (m && method === "GET") return getLead(decodeURIComponent(m[1]));
    if (m && method === "PATCH") return patchLead(decodeURIComponent(m[1]), payload);
    if (m && method === "DELETE") return deleteLead(decodeURIComponent(m[1]));

    m = clean.match(/^\/api\/leads\/([^/]+)\/notes$/);
    if (m && method === "GET") return listNotes(decodeURIComponent(m[1]));
    if (m && method === "POST") return createNote(decodeURIComponent(m[1]), payload);

    throw new Error("Not found");
  }

  window.VoltarisDB = {
    api,
    configured,
    health,
  };
})();
