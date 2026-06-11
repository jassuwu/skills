#!/usr/bin/env bun

// BMS Watcher — BookMyShow ticket availability CLI
// Zero npm dependencies. Uses Bun's native fetch() and regex parsing.

import { readFileSync, writeFileSync, existsSync } from "fs";
import { resolve, dirname } from "path";

// --- Types ---

interface Watch {
  id: string;
  movie: string;
  regionCode: string;
  city: string;
  formats: string[];
  language: string;
  seatFilter: "optimal" | "all";
  theatres: Theatre[];
}

interface Theatre {
  venueCode: string;
  name: string;
}

interface WatchesConfig {
  watches: Watch[];
}

interface BMSVenue {
  VenueCode: string;
  VenueName: string;
  VenueAddress: string;
  VenueSubRegion: string;
  Latitude: string;
  Longitude: string;
}

interface BMSCategory {
  PriceDesc: string;
  CurPrice: string;
  AvailStatus: string;
  BestAvailableSeats: number;
  SeatsAvail: string;
}

interface BMSShowTime {
  ShowTime: string;
  ShowDateTime: string;
  SessionId: string;
  Categories: BMSCategory[];
  SessionUnpaid?: string;
}

interface BMSChildEvent {
  EventDimension: string;
  EventLanguage: string;
  EventCode: string;
  ShowTimes: BMSShowTime[];
}

interface BMSEvent {
  EventTitle: string;
  EventCode: string;
  ChildEvents: BMSChildEvent[];
}

interface BMSShowDetail {
  Event: BMSEvent[];
}

interface BMSCinemaResponse {
  ShowDetails: BMSShowDetail[];
}

interface MatchCategory {
  name: string;
  price: string;
  available: boolean;
  isOptimal: boolean;
  seatsAvailable: number;
}

interface ShowMatch {
  key: string;
  venue: string;
  venueCode: string;
  format: string;
  language: string;
  showTime: string;
  showDate: string;
  bookingUrl: string;
  categories: MatchCategory[];
  hasOptimalSeats: boolean;
}

interface WatchResult {
  watchId: string;
  movie: string;
  status: "not_listed" | "listed_wrong_format" | "listed_no_seats" | "found";
  availableFormats: string[];
  matches: ShowMatch[];
}

interface CheckOutput {
  results: WatchResult[];
  checkedAt: string;
}

// --- Constants ---

const USER_AGENTS = [
  "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
  "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.2 Safari/605.1.15",
  "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
  "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
];

const SCRIPT_DIR = dirname(resolve(Bun.argv[1]));
const WATCHES_PATH = resolve(SCRIPT_DIR, "watches.json");

// --- Helpers ---

function randomUA(): string {
  return USER_AGENTS[Math.floor(Math.random() * USER_AGENTS.length)];
}

function makeHeaders(opts?: { json?: boolean; referer?: string }): Record<string, string> {
  return {
    "User-Agent": randomUA(),
    Accept: opts?.json
      ? "application/json, text/plain, */*"
      : "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    Referer: opts?.referer || "https://in.bookmyshow.com/",
    "Cache-Control": "no-cache",
    "sec-ch-ua": '"Chromium";v="131", "Not_A Brand";v="24"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"macOS"',
    "sec-fetch-dest": opts?.json ? "empty" : "document",
    "sec-fetch-mode": opts?.json ? "cors" : "navigate",
    "sec-fetch-site": "same-origin",
  };
}

function slugify(name: string): string {
  return name
    .replace(/[^0-9a-zA-Z ]+/g, "")
    .toLowerCase()
    .replace(/ +/g, "-");
}

function todayStr(): string {
  const now = new Date();
  const y = now.getFullYear();
  const m = String(now.getMonth() + 1).padStart(2, "0");
  const d = String(now.getDate()).padStart(2, "0");
  return `${y}${m}${d}`;
}

function formatDate(yyyymmdd: string): string {
  const y = yyyymmdd.slice(0, 4);
  const m = parseInt(yyyymmdd.slice(4, 6)) - 1;
  const d = parseInt(yyyymmdd.slice(6, 8));
  const date = new Date(parseInt(y), m, d);
  return date.toLocaleDateString("en-IN", {
    weekday: "short",
    day: "numeric",
    month: "short",
    year: "numeric",
  });
}

function loadWatches(): WatchesConfig {
  if (!existsSync(WATCHES_PATH)) {
    console.error(`Error: watches.json not found at ${WATCHES_PATH}`);
    process.exit(1);
  }
  return JSON.parse(readFileSync(WATCHES_PATH, "utf-8"));
}

function log(msg: string) {
  const ts = new Date().toLocaleTimeString("en-IN", {
    timeZone: "Asia/Kolkata",
    hour12: false,
  });
  console.error(`[${ts}] ${msg}`);
}

// --- HTTP via curl (bypasses Cloudflare TLS fingerprinting) ---

async function curlFetch(url: string, opts?: { referer?: string }): Promise<{ status: number; body: string }> {
  const referer = opts?.referer || "https://in.bookmyshow.com/";
  const ua = randomUA();

  const proc = Bun.spawn([
    "curl", "-s", "--http1.1",
    "-w", "\n__HTTP_STATUS__:%{http_code}",
    "-L", // follow redirects
    "-H", `User-Agent: ${ua}`,
    "-H", "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "-H", "Accept-Language: en-US,en;q=0.9",
    "-H", `Referer: ${referer}`,
    "-H", 'sec-ch-ua: "Chromium";v="131", "Not_A Brand";v="24"',
    "-H", "sec-ch-ua-mobile: ?0",
    "-H", 'sec-ch-ua-platform: "macOS"',
    "-H", "sec-fetch-dest: document",
    "-H", "sec-fetch-mode: navigate",
    "-H", "sec-fetch-site: same-origin",
    "-H", "sec-fetch-user: ?1",
    "-H", "upgrade-insecure-requests: 1",
    url,
  ], { stdout: "pipe", stderr: "pipe" });

  const output = await new Response(proc.stdout).text();
  await proc.exited;

  const statusMatch = output.match(/__HTTP_STATUS__:(\d+)$/);
  const status = statusMatch ? parseInt(statusMatch[1]) : 0;
  const body = output.replace(/\n__HTTP_STATUS__:\d+$/, "");

  return { status, body };
}

// --- BMS API ---

async function fetchVenues(regionCode: string): Promise<BMSVenue[]> {
  // Scrape from the cinemas page since the API is Cloudflare-blocked
  const citySlug = regionCode.toLowerCase() === "chen" ? "chennai"
    : regionCode.toLowerCase() === "mumbai" ? "mumbai"
    : regionCode.toLowerCase() === "bang" ? "bengaluru"
    : regionCode.toLowerCase() === "hyd" ? "hyderabad"
    : regionCode.toLowerCase() === "ncr" ? "delhi-ncr"
    : regionCode.toLowerCase();

  const url = `https://in.bookmyshow.com/${citySlug}/cinemas`;
  log(`Fetching venues from ${url}...`);

  const { status, body: html } = await curlFetch(url, {
    referer: `https://in.bookmyshow.com/${citySlug}/movies`,
  });

  if (status !== 200) {
    throw new Error(`Cinemas page returned ${status}`);
  }

  // Extract venue data from embedded JSON in the HTML
  const venues: BMSVenue[] = [];
  const seen = new Set<string>();

  // Pattern: "VenueCode":"XXXX"..."VenueName":"Name"
  const venueRegex = /"VenueCode":"([^"]+)"[^}]*?"VenueName":"([^"]+)"/g;
  let match;
  while ((match = venueRegex.exec(html)) !== null) {
    const code = match[1];
    const name = match[2];
    if (!seen.has(code)) {
      seen.add(code);
      // Try to extract address and subregion too
      const blockStart = html.lastIndexOf("{", match.index);
      const blockEnd = html.indexOf("}", match.index + match[0].length);
      const block = html.slice(blockStart, blockEnd + 1);

      const addrMatch = block.match(/"VenueAddress":"([^"]*?)"/);
      const subMatch = block.match(/"VenueSubRegion":"([^"]*?)"/);
      const latMatch = block.match(/"Latitude":"([^"]*?)"/);
      const lngMatch = block.match(/"Longitude":"([^"]*?)"/);

      venues.push({
        VenueCode: code,
        VenueName: name,
        VenueAddress: addrMatch?.[1] || "",
        VenueSubRegion: subMatch?.[1] || "",
        Latitude: latMatch?.[1] || "",
        Longitude: lngMatch?.[1] || "",
      });
    }
  }

  return venues;
}

async function fetchCinemaPage(
  regionCode: string,
  venue: Theatre,
  date: string,
  city?: string
): Promise<BMSCinemaResponse | null> {
  const venueSlug = slugify(venue.name);
  const url = `https://in.bookmyshow.com/buytickets/${venueSlug}/cinema-${regionCode.toLowerCase()}-${venue.venueCode}-MT/${date}`;

  log(`Checking ${venue.name} for ${date}...`);

  try {
    const { status, body: html } = await curlFetch(url, {
      referer: `https://in.bookmyshow.com/${city || "chennai"}/movies`,
    });

    if (status !== 200) {
      log(`  HTTP ${status} for ${venue.name}`);
      return null;
    }

    // Extract UAPI JSON from script tag
    const uapiMatch = html.match(
      /var\s+UAPI\s*=\s*JSON\.parse\(\s*"(.+?)"\s*\)\s*;/
    );

    if (!uapiMatch) {
      // Check if it's a Cloudflare challenge
      if (
        html.includes("cf-browser-verification") ||
        html.includes("challenge-platform")
      ) {
        log(`  Cloudflare challenge detected for ${venue.name}`);
      } else {
        log(`  No UAPI data found for ${venue.name}`);
      }
      return null;
    }

    // Unescape the JSON string
    let jsonStr = uapiMatch[1];
    // The string is double-escaped: \" becomes ", \\ becomes \, etc.
    jsonStr = jsonStr.replace(/\\"/g, '"');
    jsonStr = jsonStr.replace(/\\\\/g, "\\");

    const parsed = JSON.parse(jsonStr) as BMSCinemaResponse;
    return parsed;
  } catch (err) {
    log(
      `  Error fetching ${venue.name}: ${err instanceof Error ? err.message : err}`
    );
    return null;
  }
}

function findMatchesForWatch(
  response: BMSCinemaResponse,
  watch: Watch,
  venue: Theatre,
  date: string
): { matches: ShowMatch[]; foundFormats: string[] } {
  const matches: ShowMatch[] = [];
  const foundFormats: string[] = [];

  if (!response.ShowDetails || response.ShowDetails.length === 0) {
    return { matches, foundFormats };
  }

  for (const showDetail of response.ShowDetails) {
    if (!showDetail.Event) continue;

    for (const event of showDetail.Event) {
      // Case-insensitive substring match for movie name
      if (
        !event.EventTitle.toLowerCase().includes(watch.movie.toLowerCase())
      ) {
        continue;
      }

      // Movie found at this venue — collect available formats
      for (const child of event.ChildEvents || []) {
        const formatLang = `${child.EventLanguage} ${child.EventDimension}`;
        if (!foundFormats.includes(formatLang)) {
          foundFormats.push(formatLang);
        }

        // Check if this child event matches our format + language filters
        const formatMatch = watch.formats.some(
          (f) => child.EventDimension.toLowerCase() === f.toLowerCase()
        );
        const langMatch =
          child.EventLanguage.toLowerCase() === watch.language.toLowerCase();

        if (!formatMatch || !langMatch) continue;

        // Check each showtime
        for (const showTime of child.ShowTimes || []) {
          if (!showTime.Categories || showTime.Categories.length === 0)
            continue;

          // Sort categories by price (ascending = front to back)
          const sortedCats = [...showTime.Categories].sort(
            (a, b) => parseFloat(a.CurPrice) - parseFloat(b.CurPrice)
          );

          // Determine optimal tier (2nd-highest price)
          const uniquePrices = [
            ...new Set(sortedCats.map((c) => c.CurPrice)),
          ].sort((a, b) => parseFloat(a) - parseFloat(b));
          const optimalPrice =
            uniquePrices.length >= 2
              ? uniquePrices[uniquePrices.length - 2]
              : uniquePrices[uniquePrices.length - 1];

          const categories: MatchCategory[] = sortedCats.map((cat) => ({
            name: cat.PriceDesc,
            price: cat.CurPrice,
            available: cat.AvailStatus === "A",
            isOptimal: cat.CurPrice === optimalPrice,
            seatsAvailable: cat.BestAvailableSeats || 0,
          }));

          const hasAnyAvailable = categories.some((c) => c.available);
          if (!hasAnyAvailable) continue;

          const hasOptimalSeats = categories.some(
            (c) => c.isOptimal && c.available
          );

          // Apply seat filter
          if (watch.seatFilter === "optimal" && !hasOptimalSeats) {
            // Still include but flag as non-optimal
          }

          const movieSlug = slugify(event.EventTitle);
          const bookingUrl = `https://in.bookmyshow.com/buytickets/${movieSlug}-${watch.city}/movie-${watch.regionCode.toLowerCase()}-${child.EventCode}-MT/`;

          const key = `${watch.id}|${venue.venueCode}|${date}|${showTime.ShowTime.replace(/[: ]/g, "")}|${child.EventDimension.replace(/ /g, "")}`;

          matches.push({
            key,
            venue: venue.name,
            venueCode: venue.venueCode,
            format: `${child.EventLanguage} ${child.EventDimension}`,
            language: child.EventLanguage,
            showTime: showTime.ShowTime,
            showDate: date,
            bookingUrl,
            categories,
            hasOptimalSeats,
          });
        }
      }
    }
  }

  return { matches, foundFormats };
}

// --- Commands ---

async function discoverVenues(regionCode: string, filter?: string) {
  const venues = await fetchVenues(regionCode);

  if (venues.length === 0) {
    console.log(`No venues found for region ${regionCode}.`);
    return;
  }

  let filtered = venues;
  if (filter) {
    const f = filter.toLowerCase();
    filtered = venues.filter(
      (v) =>
        v.VenueName?.toLowerCase().includes(f) ||
        v.VenueAddress?.toLowerCase().includes(f) ||
        v.VenueSubRegion?.toLowerCase().includes(f)
    );
  }

  // Sort alphabetically
  filtered.sort((a, b) => (a.VenueName || "").localeCompare(b.VenueName || ""));

  console.log(
    `\nVenues in ${regionCode}${filter ? ` (filter: "${filter}")` : ""}: ${filtered.length} found\n`
  );
  console.log("Code      | Name                                      | Area");
  console.log("----------+-------------------------------------------+---------------------------");

  for (const v of filtered) {
    const code = (v.VenueCode || "").padEnd(9);
    const name = (v.VenueName || "").slice(0, 41).padEnd(41);
    const area = v.VenueSubRegion || v.VenueAddress || "";
    console.log(`${code} | ${name} | ${area}`);
  }

  console.log(
    `\nTo add theatres, copy venue codes into watches.json theatres array.`
  );
  console.log(`Example:`);
  console.log(
    `  { "venueCode": "${filtered[0]?.VenueCode || "XXXX"}", "name": "${filtered[0]?.VenueName || "Theatre Name"}" }`
  );
}

async function check(watchId?: string) {
  const config = loadWatches();
  const watches = watchId
    ? config.watches.filter((w) => w.id === watchId)
    : config.watches;

  if (watches.length === 0) {
    console.error(
      watchId
        ? `No watch found with id "${watchId}"`
        : "No watches configured in watches.json"
    );
    process.exit(1);
  }

  const results: WatchResult[] = [];

  for (const watch of watches) {
    log(`Checking watch "${watch.id}": ${watch.movie} in ${watch.city}`);

    if (watch.theatres.length === 0) {
      log(`  No theatres configured for "${watch.id}". Run --discover-venues.`);
      results.push({
        watchId: watch.id,
        movie: watch.movie,
        status: "not_listed",
        availableFormats: [],
        matches: [],
      });
      continue;
    }

    const allMatches: ShowMatch[] = [];
    const allFoundFormats: string[] = [];
    let movieFoundAnywhere = false;

    // Check today + next 14 days
    const today = new Date();
    const dates: string[] = [];
    for (let i = 0; i < 14; i++) {
      const d = new Date(today);
      d.setDate(d.getDate() + i);
      const y = d.getFullYear();
      const m = String(d.getMonth() + 1).padStart(2, "0");
      const day = String(d.getDate()).padStart(2, "0");
      dates.push(`${y}${m}${day}`);
    }

    for (const theatre of watch.theatres) {
      for (const date of dates) {
        const response = await fetchCinemaPage(
          watch.regionCode,
          theatre,
          date,
          watch.city
        );
        if (!response) continue;

        const { matches, foundFormats } = findMatchesForWatch(
          response,
          watch,
          theatre,
          date
        );

        if (foundFormats.length > 0) {
          movieFoundAnywhere = true;
          for (const fmt of foundFormats) {
            if (!allFoundFormats.includes(fmt)) {
              allFoundFormats.push(fmt);
            }
          }
        }

        allMatches.push(...matches);

        // Small delay between requests
        await Bun.sleep(1500);
      }
    }

    // Determine status
    let status: WatchResult["status"];
    if (allMatches.length > 0) {
      status = "found";
    } else if (movieFoundAnywhere) {
      // Movie exists but no matching format/language/seats
      const hasRightFormat = allFoundFormats.some((fmt) => {
        const parts = fmt.split(" ");
        const lang = parts[0];
        const dim = parts.slice(1).join(" ");
        return (
          lang.toLowerCase() === watch.language.toLowerCase() &&
          watch.formats.some((f) => dim.toLowerCase() === f.toLowerCase())
        );
      });
      status = hasRightFormat ? "listed_no_seats" : "listed_wrong_format";
    } else {
      status = "not_listed";
    }

    results.push({
      watchId: watch.id,
      movie: watch.movie,
      status,
      availableFormats: allFoundFormats,
      matches: allMatches,
    });
  }

  const output: CheckOutput = {
    results,
    checkedAt: new Date().toISOString(),
  };

  // Output JSON to stdout (logs go to stderr)
  console.log(JSON.stringify(output, null, 2));
}

async function testDiscord() {
  const webhookUrl = process.env.BMS_DISCORD_WEBHOOK;
  if (!webhookUrl) {
    console.error(
      "Error: BMS_DISCORD_WEBHOOK environment variable not set."
    );
    process.exit(1);
  }

  const payload = {
    username: "BMS Watcher",
    embeds: [
      {
        title: "Test Alert — BMS Watcher is Working!",
        description: "This is a test notification from your BookMyShow watcher.",
        color: 0x2ecc71,
        fields: [
          { name: "Movie", value: "Test Movie", inline: true },
          { name: "Format", value: "Hindi 2D IMAX", inline: true },
          { name: "Theatre", value: "Test Theatre", inline: true },
          { name: "Time", value: "7:00 PM", inline: true },
          {
            name: "Seat Availability",
            value:
              "✅ GOLD (₹350) — Available  ⭐\n✅ RECLINER (₹600) — Available\n❌ CLASSIC (₹200) — Sold Out",
            inline: false,
          },
          {
            name: "Book Now",
            value: "[Click here](https://in.bookmyshow.com/)",
            inline: false,
          },
        ],
        footer: { text: "BMS Watcher • Test Alert" },
        timestamp: new Date().toISOString(),
      },
    ],
  };

  const resp = await fetch(webhookUrl, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  if (resp.status === 204 || resp.ok) {
    console.log("Test notification sent successfully!");
  } else {
    console.error(
      `Failed to send test notification: HTTP ${resp.status}`,
      await resp.text()
    );
  }
}

async function watchMode() {
  const webhookUrl = process.env.BMS_DISCORD_WEBHOOK;
  if (!webhookUrl) {
    console.error("Error: BMS_DISCORD_WEBHOOK environment variable not set.");
    process.exit(1);
  }

  const pollInterval = 45_000; // 45 seconds
  const sentKeys = new Set<string>();

  log("Starting BMS Watcher in standalone mode...");
  log(`Poll interval: ${pollInterval / 1000}s`);

  const runCheck = async () => {
    const config = loadWatches();

    for (const watch of config.watches) {
      if (watch.theatres.length === 0) continue;

      const today = new Date();
      const dates: string[] = [];
      for (let i = 0; i < 14; i++) {
        const d = new Date(today);
        d.setDate(d.getDate() + i);
        const y = d.getFullYear();
        const m = String(d.getMonth() + 1).padStart(2, "0");
        const day = String(d.getDate()).padStart(2, "0");
        dates.push(`${y}${m}${day}`);
      }

      for (const theatre of watch.theatres) {
        for (const date of dates) {
          const response = await fetchCinemaPage(
            watch.regionCode,
            theatre,
            date
          );
          if (!response) continue;

          const { matches } = findMatchesForWatch(
            response,
            watch,
            theatre,
            date
          );

          const newMatches = matches.filter((m) => !sentKeys.has(m.key));
          if (newMatches.length === 0) continue;

          // Send Discord notification
          const embeds = newMatches.slice(0, 10).map((match) => {
            const seatsText = match.categories
              .map((c) => {
                const status = c.available ? "✅" : "❌";
                const optimal = c.isOptimal ? " ⭐ BEST VIEWING" : "";
                const seats = c.available
                  ? ` (${c.seatsAvailable} seats)`
                  : "";
                return `${status} ${c.name} (₹${c.price})${seats}${optimal}`;
              })
              .join("\n");

            return {
              title: `${match.hasOptimalSeats ? "🎬" : "⚠️"} ${watch.movie} — ${match.hasOptimalSeats ? "Tickets Available!" : "Non-Optimal Seats Only"}`,
              url: match.bookingUrl,
              color: match.hasOptimalSeats ? 0x2ecc71 : 0xe67e22,
              fields: [
                { name: "Theatre", value: match.venue, inline: true },
                { name: "Format", value: match.format, inline: true },
                {
                  name: "Date",
                  value: formatDate(match.showDate),
                  inline: true,
                },
                { name: "Time", value: match.showTime, inline: true },
                {
                  name: "Seat Availability",
                  value: seatsText,
                  inline: false,
                },
                {
                  name: "Book Now",
                  value: `[Click here](${match.bookingUrl})`,
                  inline: false,
                },
              ],
              footer: { text: `BMS Watcher • ${match.key}` },
              timestamp: new Date().toISOString(),
            };
          });

          const resp = await fetch(webhookUrl, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ username: "BMS Watcher", embeds }),
          });

          if (resp.status === 204 || resp.ok) {
            for (const m of newMatches) {
              sentKeys.add(m.key);
            }
            log(
              `Sent ${newMatches.length} alert(s) for ${watch.movie} at ${theatre.name}`
            );
          } else if (resp.status === 429) {
            const retryAfter = resp.headers.get("Retry-After");
            log(
              `Rate limited. Retry after ${retryAfter}s`
            );
            if (retryAfter) await Bun.sleep(parseInt(retryAfter) * 1000);
          } else {
            log(
              `Discord error: HTTP ${resp.status}`
            );
          }

          await Bun.sleep(1500);
        }
      }
    }
  };

  // Run immediately, then on interval
  await runCheck();
  setInterval(runCheck, pollInterval);
}

// --- CLI ---

async function main() {
  const args = Bun.argv.slice(2);

  if (args.includes("--help") || args.includes("-h")) {
    console.log(`
BMS Watcher — BookMyShow ticket availability CLI

Usage:
  bun run bms-watcher.ts --discover-venues --region <CODE> [--filter <text>]
  bun run bms-watcher.ts --check [--watch-id <id>]
  bun run bms-watcher.ts --watch
  bun run bms-watcher.ts --test-discord

Commands:
  --discover-venues  List all theatre venues for a region
    --region <CODE>  Region code (e.g., CHEN, BANG, HYD, MUM)
    --filter <text>  Filter venues by name/area (optional)

  --check            Check all watches, output JSON to stdout
    --watch-id <id>  Check a specific watch only (optional)

  --watch            Standalone polling mode with Discord webhook
                     Requires BMS_DISCORD_WEBHOOK env var

  --test-discord     Send a test notification to Discord webhook
                     Requires BMS_DISCORD_WEBHOOK env var

Config:
  watches.json       Watch configurations (same directory as script)
`);
    return;
  }

  if (args.includes("--discover-venues")) {
    const regionIdx = args.indexOf("--region");
    const regionCode =
      regionIdx !== -1 ? args[regionIdx + 1] : undefined;
    if (!regionCode) {
      console.error("Error: --region <CODE> is required (e.g., --region CHEN)");
      process.exit(1);
    }
    const filterIdx = args.indexOf("--filter");
    const filter = filterIdx !== -1 ? args[filterIdx + 1] : undefined;
    await discoverVenues(regionCode, filter);
    return;
  }

  if (args.includes("--test-discord")) {
    await testDiscord();
    return;
  }

  if (args.includes("--watch")) {
    await watchMode();
    return;
  }

  // Default: --check mode
  const watchIdIdx = args.indexOf("--watch-id");
  const watchId = watchIdIdx !== -1 ? args[watchIdIdx + 1] : undefined;
  await check(watchId);
}

main().catch((err) => {
  console.error("Fatal error:", err);
  process.exit(1);
});
