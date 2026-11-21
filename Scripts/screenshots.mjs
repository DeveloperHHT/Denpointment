// Takes the screenshots for the user guide (and a visual check) from a running demo server.
//
//   python main.py --demo --port 5057
//   PLAYWRIGHT_PATH=/path/to/node_modules/playwright node Scripts/screenshots.mjs http://127.0.0.1:5057 Docs/Images
//
// Playwright is not a dependency of the app, point PLAYWRIGHT_PATH at any installation of it.
import { createRequire } from "node:module";
import { mkdirSync } from "node:fs";

const require = createRequire(import.meta.url);
const { chromium } = require(process.env.PLAYWRIGHT_PATH || "playwright");

const base = process.argv[2] || "http://127.0.0.1:5000";
const out = process.argv[3] || "Docs/Images";
const only = process.argv[4]; // optional: "light", "dark" or "mobile"
mkdirSync(out, { recursive: true });

const PASSWORD = "demo1234";
const ACCOUNTS = {
  patient: "patient@denpointment.example",
  free: "patient2@denpointment.example",
  fresh: "fresh@denpointment.example",
  dentist: "dentist@denpointment.example",
};

async function login(page, email) {
  await page.goto(base + "/");
  await page.fill("#email", email);
  await page.fill("#password", PASSWORD);
  await page.click("button[type=submit]");
  await page.waitForURL("**/dashboard");
}

async function shot(page, name, { full = false } = {}) {
  await page.waitForTimeout(900); // let the entrance animations finish
  await page.screenshot({ path: `${out}/${name}.png`, fullPage: full });
  console.log("saved", name);
}

async function scenes(browser, suffix, context) {
  const open = async (email) => {
    const ctx = await browser.newContext(context);
    const page = await ctx.newPage();
    if (email) await login(page, email);
    return [ctx, page];
  };
  const theme = suffix.startsWith("dark") ? "dark" : "light";
  const setTheme = async (page) => page.addInitScript((t) => localStorage.setItem("denpointment-theme", t), theme);

  // --- signed out ---
  let [ctx, page] = await open(null);
  await setTheme(page);
  await page.goto(base + "/");
  await shot(page, `login-${suffix}`);
  await page.goto(base + "/register");
  await shot(page, `register-${suffix}`, { full: true });
  await ctx.close();

  // --- a patient ---
  [ctx, page] = await open(ACCOUNTS.patient);
  await setTheme(page); await page.reload();
  await shot(page, `patient-dashboard-${suffix}`);
  await page.goto(base + "/appointments");
  await shot(page, `patient-appointments-${suffix}`, { full: true });
  await page.goto(base + "/profile/");
  await shot(page, `profile-${suffix}`, { full: true });
  await page.goto(base + "/profile/addresses/add");
  await shot(page, `address-form-${suffix}`);
  const detail = await page.goto(base + "/appointments").then(() => page.locator("a:has-text('Details')").first().getAttribute("href"));
  if (detail) { await page.goto(base + detail); await shot(page, `patient-treatment-${suffix}`); }
  await ctx.close();

  // --- a patient who can book ---
  [ctx, page] = await open(ACCOUNTS.free);
  await setTheme(page);
  await page.goto(base + "/appointments/book");
  await page.locator(".choice").first().click();
  await page.locator(".hours .choice").nth(2).click();
  await shot(page, `book-${suffix}`, { full: true });
  await ctx.close();

  // --- a new account ---
  [ctx, page] = await open(ACCOUNTS.fresh);
  await setTheme(page); await page.reload();
  await shot(page, `fresh-dashboard-${suffix}`);
  await ctx.close();

  // --- the dentist ---
  [ctx, page] = await open(ACCOUNTS.dentist);
  await setTheme(page); await page.reload();
  await shot(page, `dentist-dashboard-${suffix}`);
  await page.goto(base + "/dentist/appointments/today");
  await shot(page, `today-${suffix}`);
  const add = await page.locator("a:has-text('Add treatment')").first().getAttribute("href");
  await page.goto(base + add);
  await page.fill("#action", "dental filling");
  await page.fill("#complaint", "toothache");
  await page.fill("#charge", "120");
  await shot(page, `treatment-form-${suffix}`);
  await page.goto(base + "/dentist/appointments/today");
  const medicines = await page.locator("a:has-text('Medicines')").first().getAttribute("href");
  await page.goto(base + medicines);
  await shot(page, `medicines-${suffix}`);
  for (const [name, url, full] of [["upcoming", "/dentist/appointments/upcoming", false], ["history", "/dentist/treatments", true],
      ["holidays", "/dentist/holidays", true], ["holiday-form", "/dentist/holidays/add", false],
      ["patient-profile", "/dentist/patients/1", true], ["statistics", "/dentist/statistics", true]]) {
    await page.goto(base + url);
    await shot(page, `${name}-${suffix}`, { full });
  }
  await ctx.close();
}

// BROWSER_PATH lets a browser that is already on the machine be used instead of the one Playwright downloads.
const browser = await chromium.launch(process.env.BROWSER_PATH ? { executablePath: process.env.BROWSER_PATH } : {});
const sets = {
  light: ["light", { viewport: { width: 1440, height: 900 }, deviceScaleFactor: 1.5 }],
  dark: ["dark", { viewport: { width: 1440, height: 900 }, deviceScaleFactor: 1.5 }],
  mobile: ["mobile", { viewport: { width: 390, height: 844 }, deviceScaleFactor: 2, isMobile: true, hasTouch: true }],
};
for (const [key, [suffix, context]] of Object.entries(sets)) {
  if (only && only !== key) continue;
  await scenes(browser, suffix, context);
}
await browser.close();
