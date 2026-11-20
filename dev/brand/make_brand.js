// OWNER Assistant brand images (black / blood-red / chrome).
// Draws everything as SVG and renders it with the pre-installed Chromium.
//
//   node dev/brand/make_brand.js          (run from the repo root)
//
// Writes resources/extras/owner_assistant_{avatar,thumb,1,2,3,alive,help,start,deploy,pm}.jpg
// Fonts: Orbitron + Rajdhani (SIL OFL 1.1, see dev/brand/fonts/).

const fs = require("fs");
const path = require("path");
const { chromium } = require("playwright");

const ROOT = path.resolve(__dirname, "..", "..");
const OUT = path.join(ROOT, "resources", "extras");
const FONTS = path.join(__dirname, "fonts");
const font = (f) => fs.readFileSync(path.join(FONTS, f)).toString("base64");

const RED = "#FF0000";

// Seeded random so the images are the same every run.
function rng(seed) {
  let s = seed >>> 0;
  return () => ((s = (s * 1664525 + 1013904223) >>> 0) / 4294967296);
}

function defs(id) {
  return `
  <defs>
    <linearGradient id="chrome${id}" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#ffffff"/>
      <stop offset="0.32" stop-color="#d9dde2"/>
      <stop offset="0.48" stop-color="#6b7077"/>
      <stop offset="0.53" stop-color="#2b2e33"/>
      <stop offset="0.62" stop-color="#9aa0a8"/>
      <stop offset="0.85" stop-color="#eef1f4"/>
      <stop offset="1" stop-color="#8d9299"/>
    </linearGradient>
    <linearGradient id="steel${id}" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="#3a3d42"/>
      <stop offset="0.45" stop-color="#15171a"/>
      <stop offset="0.7" stop-color="#2a2d31"/>
      <stop offset="1" stop-color="#0b0c0e"/>
    </linearGradient>
    <linearGradient id="hoodL${id}" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="#050506"/>
      <stop offset="0.55" stop-color="#2c2f34"/>
      <stop offset="1" stop-color="#141518"/>
    </linearGradient>
    <linearGradient id="hoodR${id}" x1="1" y1="0" x2="0" y2="0">
      <stop offset="0" stop-color="#050506"/>
      <stop offset="0.55" stop-color="#25282c"/>
      <stop offset="1" stop-color="#101114"/>
    </linearGradient>
    <linearGradient id="edge${id}" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#f2f4f7"/>
      <stop offset="0.5" stop-color="#8b9098"/>
      <stop offset="1" stop-color="#2a2c30" stop-opacity="0"/>
    </linearGradient>
    <radialGradient id="void${id}" cx="0.5" cy="0.45" r="0.6">
      <stop offset="0" stop-color="#140000"/>
      <stop offset="0.6" stop-color="#030000"/>
      <stop offset="1" stop-color="#000"/>
    </radialGradient>
    <radialGradient id="bg${id}" cx="0.5" cy="0.4" r="0.65">
      <stop offset="0" stop-color="#2a0000"/>
      <stop offset="0.45" stop-color="#0a0000"/>
      <stop offset="1" stop-color="#000"/>
    </radialGradient>
    <linearGradient id="fadeDown${id}" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#fff"/>
      <stop offset="0.72" stop-color="#fff"/>
      <stop offset="1" stop-color="#000"/>
    </linearGradient>
    <linearGradient id="bodyFade${id}" gradientUnits="userSpaceOnUse" x1="0" y1="560" x2="0" y2="715">
      <stop offset="0" stop-color="#fff"/>
      <stop offset="1" stop-color="#000"/>
    </linearGradient>
    <mask id="bodyMask${id}" maskUnits="userSpaceOnUse" x="0" y="0" width="1024" height="1024">
      <rect x="0" y="0" width="1024" height="1024" fill="url(#bodyFade${id})"/>
    </mask>
    <linearGradient id="rim${id}" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#4a4e55"/>
      <stop offset="1" stop-color="#1a1b1e"/>
    </linearGradient>
    <filter id="glow${id}" x="-50%" y="-50%" width="200%" height="200%">
      <feGaussianBlur stdDeviation="6" result="b"/>
      <feMerge><feMergeNode in="b"/><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
    <filter id="softglow${id}" x="-50%" y="-50%" width="200%" height="200%">
      <feGaussianBlur stdDeviation="3" result="b"/>
      <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
    <filter id="eyeglow${id}" x="-300%" y="-300%" width="700%" height="700%">
      <feGaussianBlur stdDeviation="10" result="b1"/>
      <feGaussianBlur in="SourceGraphic" stdDeviation="3" result="b2"/>
      <feMerge><feMergeNode in="b1"/><feMergeNode in="b1"/><feMergeNode in="b2"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
    <filter id="smoke${id}" x="0" y="0" width="100%" height="100%">
      <feTurbulence type="fractalNoise" baseFrequency="0.006 0.012" numOctaves="5" seed="7"/>
      <feColorMatrix type="matrix" values="0 0 0 0 0.6  0 0 0 0 0  0 0 0 0 0  0 0 0 2.4 -1.25"/>
    </filter>
    <filter id="textglow${id}" x="-20%" y="-40%" width="140%" height="180%">
      <feMorphology operator="dilate" radius="2" in="SourceAlpha" result="d"/>
      <feFlood flood-color="${RED}"/>
      <feComposite in2="d" operator="in" result="red"/>
      <feGaussianBlur in="red" stdDeviation="7" result="redb"/>
      <feMerge><feMergeNode in="redb"/><feMergeNode in="red"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
    <pattern id="grid${id}" width="32" height="32" patternUnits="userSpaceOnUse">
      <path d="M32 0H0V32" fill="none" stroke="#ff0000" stroke-opacity="0.06" stroke-width="1"/>
    </pattern>
  </defs>`;
}

function background(id, w, h, seed) {
  const r = rng(seed);
  let dots = "";
  for (let i = 0; i < Math.round((w * h) / 9000); i++) {
    const x = r() * w, y = r() * h, s = 0.6 + r() * 1.8, o = 0.15 + r() * 0.6;
    dots += `<circle cx="${x.toFixed(1)}" cy="${y.toFixed(1)}" r="${s.toFixed(2)}" fill="${RED}" opacity="${o.toFixed(2)}"/>`;
  }
  return `
  <rect width="${w}" height="${h}" fill="#000"/>
  <rect width="${w}" height="${h}" fill="url(#bg${id})"/>
  <rect width="${w}" height="${h}" fill="url(#grid${id})"/>
  <rect width="${w}" height="${h}" filter="url(#smoke${id})" opacity="0.3"/>
  <g filter="url(#softglow${id})">${dots}</g>`;
}

// The emblem (HUD ring + hooded guardian + crown), drawn in a 1024x1024 box
// centred on (512, 400). Place it with transform.
function emblem(id) {
  const cx = 512, cy = 400, R = 300;
  // HUD ring: arcs with a gap at the top for the crown
  const arc = (a0, a1, rad) => {
    const p = (a) => [cx + rad * Math.cos((a * Math.PI) / 180), cy + rad * Math.sin((a * Math.PI) / 180)];
    const [x0, y0] = p(a0), [x1, y1] = p(a1);
    return `M${x0.toFixed(1)} ${y0.toFixed(1)} A${rad} ${rad} 0 ${a1 - a0 > 180 ? 1 : 0} 1 ${x1.toFixed(1)} ${y1.toFixed(1)}`;
  };
  let ticks = "";
  for (let a = 0; a < 360; a += 6) {
    if (a > 246 && a < 294) continue; // crown gap
    const long = a % 30 === 0;
    const r1 = R + 14, r2 = R + (long ? 30 : 20);
    const c = Math.cos((a * Math.PI) / 180), s = Math.sin((a * Math.PI) / 180);
    ticks += `<line x1="${(cx + r1 * c).toFixed(1)}" y1="${(cy + r1 * s).toFixed(1)}" x2="${(cx + r2 * c).toFixed(1)}" y2="${(cy + r2 * s).toFixed(1)}" stroke="${RED}" stroke-width="${long ? 3 : 1.5}" opacity="${long ? 0.9 : 0.45}"/>`;
  }
  const ring = `
  <g filter="url(#softglow${id})" fill="none">
    <path d="${arc(-66, 66, R)}" stroke="${RED}" stroke-width="3" opacity="0.85"/>
    <path d="${arc(114, 246, R)}" stroke="${RED}" stroke-width="3" opacity="0.85"/>
    <path d="${arc(70, 110, R)}" stroke="${RED}" stroke-width="6"/>
    <path d="${arc(-40, 20, R - 22)}" stroke="#c9ccd1" stroke-width="2" opacity="0.6"/>
    <path d="${arc(160, 220, R - 22)}" stroke="#c9ccd1" stroke-width="2" opacity="0.6"/>
    <path d="${arc(-86, -70, R + 48)}" stroke="${RED}" stroke-width="2" opacity="0.6"/>
    <path d="${arc(250, 266, R + 48)}" stroke="${RED}" stroke-width="2" opacity="0.6"/>
    ${ticks}
  </g>`;

  // Hooded guardian: pauldrons + chest armour, hood drape, face void, eyes
  const hoodLeft = "M512 168 C470 188 418 232 392 296 C372 346 366 398 370 446 C373 486 362 520 336 548 L300 574 L384 594 L452 606 L512 632 Z";
  const hoodRight = "M512 168 C554 188 606 232 632 296 C652 346 658 398 654 446 C651 486 662 520 688 548 L724 574 L640 594 L572 606 L512 632 Z";
  const face = "M512 246 C474 262 440 300 428 352 C418 398 424 448 446 488 C462 516 488 536 512 546 C536 536 562 516 578 488 C600 448 606 398 596 352 C584 300 550 262 512 246 Z";
  const eyeL = "M444 404 L496 418 L492 432 L452 422 Z";
  const eyeR = "M580 404 L528 418 L532 432 L572 422 Z";
  const plate = (d, fill) => `<path d="${d}" fill="${fill}" stroke="url(#edge${id})" stroke-width="2.5" stroke-linejoin="miter"/>`;
  const body = `
  <g mask="url(#bodyMask${id})">
    ${plate("M512 600 L392 598 L360 720 L664 720 L632 598 Z", "#0b0c0e")}
    <path d="M512 636 L512 720" stroke="${RED}" stroke-width="3" filter="url(#softglow${id})"/>
    <path d="M466 662 L512 688 L558 662" fill="none" stroke="${RED}" stroke-width="2.5" filter="url(#softglow${id})"/>
    ${plate("M340 546 L246 592 L200 664 L226 724 L352 724 L398 604 Z", `url(#steel${id})`)}
    ${plate("M688 546 L778 592 L824 664 L798 724 L672 724 L626 604 Z", `url(#steel${id})`)}
    ${plate("M318 566 L250 600 L222 646 L330 632 Z", "#2a2d32")}
    ${plate("M706 566 L774 600 L802 646 L694 632 Z", "#2a2d32")}
    <path d="M236 664 L334 648 M788 664 L690 648" stroke="${RED}" stroke-width="2.5" filter="url(#softglow${id})"/>
    <path d="M256 628 L318 606 M768 628 L706 606" stroke="#e8ebef" stroke-width="1.5" opacity="0.7"/>
  </g>`;
  const hood = `
  ${body}
  <g mask="url(#bodyMask${id})">
    <path d="${hoodLeft}" fill="url(#hoodL${id})"/>
    <path d="${hoodRight}" fill="url(#hoodR${id})"/>
    <path d="M512 168 C470 188 418 232 392 296 C372 346 366 398 370 446 C373 486 362 520 336 548 L300 574" fill="none" stroke="url(#edge${id})" stroke-width="3"/>
    <path d="M512 168 C554 188 606 232 632 296 C652 346 658 398 654 446 C651 486 662 520 688 548 L724 574" fill="none" stroke="url(#edge${id})" stroke-width="3"/>
    <path d="M378 330 C364 390 366 450 378 500" fill="none" stroke="${RED}" stroke-width="2" opacity="0.55" filter="url(#softglow${id})"/>
    <path d="M646 330 C660 390 658 450 646 500" fill="none" stroke="${RED}" stroke-width="2" opacity="0.55" filter="url(#softglow${id})"/>
    <path d="M300 574 L384 594 L452 606 L512 632 L572 606 L640 594 L724 574" fill="none" stroke="#5a5f66" stroke-width="2"/>
    <path d="M410 300 C396 350 394 420 404 480 M614 300 C628 350 630 420 620 480" fill="none" stroke="#000" stroke-width="6" opacity="0.55"/>
    <path d="M436 560 C470 586 492 600 512 610 C532 600 554 586 588 560" fill="none" stroke="#000" stroke-width="5" opacity="0.5"/>
  </g>
  <path d="${face}" fill="none" stroke="url(#rim${id})" stroke-width="16"/>
  <path d="${face}" fill="url(#void${id})" stroke="#9aa0a8" stroke-width="1.5"/>
  <path d="M512 176 L512 238" stroke="#c9ccd1" stroke-width="2" opacity="0.5"/>
  <path d="M452 466 L512 486 L572 466" fill="none" stroke="#3a0000" stroke-width="2"/>
  <g filter="url(#eyeglow${id})">
    <path d="${eyeL}" fill="${RED}"/>
    <path d="${eyeR}" fill="${RED}"/>
  </g>
  <path d="M458 414 L490 422" stroke="#ffd0d0" stroke-width="2" stroke-linecap="round"/>
  <path d="M566 414 L534 422" stroke="#ffd0d0" stroke-width="2" stroke-linecap="round"/>`;

  // Crown above the hood
  const crown = `
  <g filter="url(#softglow${id})">
    <path d="M446 150 L432 92 L470 122 L490 80 L512 50 L534 80 L554 122 L592 92 L578 150 Z" fill="url(#chrome${id})" stroke="#ffffff" stroke-width="1.5"/>
    <rect x="442" y="150" width="140" height="16" fill="url(#chrome${id})" stroke="#ffffff" stroke-width="1.2"/>
    <path d="M512 56 L512 108 M490 86 L496 120 M534 86 L528 120 M436 100 L452 146 M588 100 L572 146" stroke="#5a5f66" stroke-width="1.5" opacity="0.8"/>
    <path d="M446 158 L578 158" stroke="${RED}" stroke-width="2" opacity="0.9"/>
    <path d="M512 112 L524 128 L512 144 L500 128 Z" fill="${RED}" filter="url(#eyeglow${id})"/>
    <circle cx="432" cy="92" r="4" fill="#fff"/><circle cx="592" cy="92" r="4" fill="#fff"/><circle cx="512" cy="50" r="4.5" fill="#fff"/>
  </g>`;

  return `${ring}${hood}${crown}`;
}

function ownerText(id, x, y, size, anchor = "middle") {
  // 3D extrusion (dark layers) + red outline glow + chrome face
  let ext = "";
  for (let i = 8; i >= 1; i--) {
    ext += `<text x="${x}" y="${y + i}" fill="${i > 4 ? "#1a0000" : "#3a3d42"}">OWNER</text>`;
  }
  return `
  <g font-family="Orbitron" font-weight="900" font-size="${size}" text-anchor="${anchor}" letter-spacing="${size * 0.04}">
    ${ext}
    <text x="${x}" y="${y}" fill="url(#chrome${id})" filter="url(#textglow${id})">OWNER</text>
    <text x="${x}" y="${y}" fill="none" stroke="#ffffff" stroke-opacity="0.55" stroke-width="1.2">OWNER</text>
  </g>`;
}

function badge(id, cx, cy, w, h, text, size) {
  const c = h / 2;
  const x0 = cx - w / 2, x1 = cx + w / 2, y0 = cy - h / 2, y1 = cy + h / 2;
  const shape = `M${x0 + c} ${y0} L${x1 - c} ${y0} L${x1} ${cy} L${x1 - c} ${y1} L${x0 + c} ${y1} L${x0} ${cy} Z`;
  return `
  <path d="${shape}" fill="#0a0000" stroke="${RED}" stroke-width="3" filter="url(#softglow${id})"/>
  <g filter="url(#softglow${id})" fill="${RED}">
    <rect x="${x0 - 40}" y="${cy - 1}" width="32" height="2"/>
    <rect x="${x1 + 8}" y="${cy - 1}" width="32" height="2"/>
  </g>
  <path d="M${x0 + c + 6} ${y0 + 6} L${x1 - c - 6} ${y0 + 6}" stroke="#c9ccd1" stroke-width="1" opacity="0.5"/>
  <text x="${cx}" y="${cy + size * 0.36}" text-anchor="middle" font-family="Orbitron" font-weight="800" font-size="${size}" letter-spacing="${size * 0.32}" fill="${RED}" filter="url(#softglow${id})">${text}</text>`;
}

function corners(w, h, m, len, color = RED) {
  return `<g stroke="${color}" stroke-width="3" fill="none" opacity="0.85">
    <path d="M${m} ${m + len} L${m} ${m} L${m + len} ${m}"/>
    <path d="M${w - m - len} ${m} L${w - m} ${m} L${w - m} ${m + len}"/>
    <path d="M${m} ${h - m - len} L${m} ${h - m} L${m + len} ${h - m}"/>
    <path d="M${w - m - len} ${h - m} L${w - m} ${h - m} L${w - m} ${h - m - len}"/>
  </g>`;
}

function avatarSVG() {
  const id = "a";
  return `<svg xmlns="http://www.w3.org/2000/svg" width="1024" height="1024" viewBox="0 0 1024 1024">
  ${defs(id)}
  ${background(id, 1024, 1024, 11)}
  <g transform="translate(0 -6)">${emblem(id)}</g>
  ${ownerText(id, 512, 830, 138)}
  ${badge(id, 512, 900, 470, 62, "ASSISTANT", 34)}
  </svg>`;
}

// Title fits in ~500px (Orbitron 900 is about 0.9em per letter)
function titleSize(t) {
  return Math.min(58, Math.floor(500 / (t.length * 0.9)));
}

// Subtitle fits in ~470px (Rajdhani bold ~0.55em + 0.18em spacing)
function subSize(t) {
  return Math.min(32, Math.floor(470 / (t.length * 0.73)));
}

// 16:9 banner: emblem on the left, words + title on the right
function bannerSVG(title, sub, seed) {
  const id = "b";
  const W = 1280, H = 720;
  return `<svg xmlns="http://www.w3.org/2000/svg" width="${W}" height="${H}" viewBox="0 0 ${W} ${H}">
  ${defs(id)}
  ${background(id, W, H, seed)}
  ${corners(W, H, 26, 54)}
  <g transform="translate(-30 30) scale(0.78)">${emblem(id)}</g>
  <path d="M700 120 L700 600" stroke="${RED}" stroke-width="2" opacity="0.5"/>
  ${ownerText(id, 975, 250, 112)}
  ${badge(id, 975, 312, 380, 50, "ASSISTANT", 26)}
  <text x="975" y="450" text-anchor="middle" font-family="Orbitron" font-weight="900" font-size="${titleSize(title)}" fill="#ffffff" letter-spacing="3" filter="url(#textglow${id})">${title}</text>
  <rect x="800" y="480" width="350" height="3" fill="${RED}" filter="url(#softglow${id})"/>
  <text x="975" y="530" text-anchor="middle" font-family="Rajdhani" font-weight="700" font-size="${subSize(sub)}" fill="#c9ccd1" letter-spacing="${(subSize(sub) * 0.18).toFixed(1)}">${sub}</text>
  </svg>`;
}

const PAGES = [
  ["avatar", avatarSVG, 1024, 1024],
  ["1", () => bannerSVG("COMMAND CENTER", "PERSONAL TELEGRAM ASSISTANT", 21), 1280, 720],
  ["2", () => bannerSVG("ALWAYS ON GUARD", "FAST  ·  SECURE  ·  LOYAL", 22), 1280, 720],
  ["3", () => bannerSVG("AT YOUR SERVICE", "BUILT FOR THE OWNER", 23), 1280, 720],
  ["alive", () => bannerSVG("SYSTEM ONLINE", "ALIVE  ·  FAST  ·  SECURE", 24), 1280, 720],
  ["help", () => bannerSVG("HELP MENU", "ALL COMMANDS · ONE PLACE", 25), 1280, 720],
  ["start", () => bannerSVG("WELCOME", "PERSONAL TELEGRAM ASSISTANT", 26), 1280, 720],
  ["deploy", () => bannerSVG("DEPLOYED", "YOUR ASSISTANT IS READY", 27), 1280, 720],
  ["pm", () => bannerSVG("PM SECURITY", "WAIT FOR THE OWNER TO REPLY", 28), 1280, 720],
];

(async () => {
  const css = `
    @font-face { font-family: Orbitron; font-weight: 900; src: url(data:font/woff2;base64,${font("orbitron-latin-900-normal.woff2")}) format("woff2"); }
    @font-face { font-family: Orbitron; font-weight: 800; src: url(data:font/woff2;base64,${font("orbitron-latin-800-normal.woff2")}) format("woff2"); }
    @font-face { font-family: Orbitron; font-weight: 600; src: url(data:font/woff2;base64,${font("orbitron-latin-600-normal.woff2")}) format("woff2"); }
    @font-face { font-family: Rajdhani; font-weight: 700; src: url(data:font/woff2;base64,${font("rajdhani-latin-700-normal.woff2")}) format("woff2"); }
    html, body { margin: 0; background: #000; }`;
  const browser = await chromium.launch();
  const only = process.argv[2];
  for (const [name, make, w, h] of PAGES) {
    if (only && only !== name) continue;
    const page = await browser.newPage({ viewport: { width: w, height: h }, deviceScaleFactor: 1 });
    await page.setContent(`<!doctype html><html><head><style>${css}</style></head><body>${make()}</body></html>`);
    await page.evaluate(() => document.fonts.ready);
    const file = path.join(OUT, `owner_assistant_${name}.jpg`);
    await page.screenshot({ path: file, type: "jpeg", quality: 90, clip: { x: 0, y: 0, width: w, height: h } });
    console.log("wrote", path.relative(ROOT, file));
    await page.close();
  }
  await browser.close();
})();
