# Supabase setup (Voltaris Lead Manager)

This app now saves leads/notes in **Supabase**, so it works on GitHub Pages and any static host.

## 1. Create a project

1. Go to https://supabase.com and sign in
2. **New project** → choose name/password/region → create

## 2. Create tables

1. In Supabase: **SQL Editor** → **New query**
2. Paste everything from `supabase/schema.sql`
3. Click **Run**

## 3. Add API keys to the app

1. Supabase: **Project Settings** → **API**
2. Copy:
   - **Project URL**
   - **anon public** key
3. Open `js/supabase-config.js` and paste them:

```js
window.SUPABASE_CONFIG = {
  url: "https://YOUR_PROJECT_REF.supabase.co",
  anonKey: "YOUR_ANON_KEY"
};
```

## 4. Run / publish

### Local
- Open `leads.html` in a browser (or use any static server)
- Or keep using GitHub Pages after push

### GitHub Pages
1. Commit `js/supabase-config.js` with your anon key (anon key is public by design)
2. Push to GitHub
3. Open: https://shrutithakorau.github.io/voltaris-energy-brand-guidelines/leads.html

## Security note

Google SSO is built into `leads.html`. Follow **[GOOGLE-AUTH-SETUP.md](GOOGLE-AUTH-SETUP.md)** to enable the Google provider, then run `supabase/require-authenticated-rls.sql` so only signed-in users can access leads.

## Optional: migrate old local SQLite leads

If you still have local data in `data/leads.db`, tell the assistant to export/import it into Supabase.
