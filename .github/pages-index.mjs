// Writes index.html pages for the site that .github/workflows/ddi.yml builds: one at the
// root for main and its list of releases, and one in each release folder. Each page
// links the files that are in its folder, so it lists what was built and nothing else.
// Usage, in the repository: node pages-index.mjs <site> <owner/name>
import { execFileSync } from "node:child_process";
import { readdirSync, statSync, writeFileSync } from "node:fs";
import { join } from "node:path";

const [site, repo] = process.argv.slice(2);
if (!site || !repo) {
  console.error("Usage: node pages-index.mjs <site> <owner/name>");
  process.exit(2);
}

const html = (s) =>
  s.replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" })[c]);
const link = (path, text) =>
  `<a href="${html(path.split("/").map(encodeURIComponent).join("/"))}">${html(text)}</a>`;
const byName = (a, b) => (a < b ? -1 : a > b ? 1 : 0);

// Every file under dir, as paths relative to it, in a fixed order; release folders and
// index pages are left out (each index.html is this script's, written over on each run).
function filesIn(dir, prefix = "") {
  return readdirSync(join(dir, prefix))
    .sort(byName)
    .flatMap((name) => {
      const path = prefix + name;
      if (statSync(join(dir, path)).isDirectory())
        return prefix === "" && isRelease(name) ? [] : filesIn(dir, `${path}/`);
      return name === "index.html" ? [] : [path];
    });
}

const isRelease = (name) => /^v[1-9][0-9]*$/.test(name);
const isInstrumentDdi = (f) => /^instruments\/[^/]+\.json$/.test(f) && !f.endsWith(".columns.json");

// The files of one build: the workspace DDI, then each instrument with its DDI, QSF and
// column maps (instruments/<name>-ddi-<source>.columns.json), then any other file.
function listing(dir, level) {
  const files = filesIn(dir);
  const instruments = files
    .filter(isInstrumentDdi)
    .map((f) => f.slice("instruments/".length, -".json".length));
  // A map belongs to the instrument with the longest name that it starts with.
  const ownerOf = (f) =>
    instruments.filter((n) => f.startsWith(`instruments/${n}-ddi-`)).sort((a, b) => b.length - a.length)[0];
  const listed = new Set();
  const take = (f, text) => (listed.add(f), link(f, text));
  const parts = [];
  if (files.includes("ddi.json"))
    parts.push(`<p>${take("ddi.json", "ddi.json")}: the DDI of the workspace</p>`);
  if (instruments.length) {
    parts.push(`<h${level}>Instruments</h${level}>`, "<dl>");
    for (const name of instruments) {
      const own = `instruments/${name}`;
      const items = [take(`${own}.json`, `${name}.json`) + ": DDI"];
      if (files.includes(`${own}.qsf`)) items.push(take(`${own}.qsf`, `${name}.qsf`) + ": Qualtrics survey");
      for (const f of files.filter((f) => f.endsWith(".columns.json") && ownerOf(f) === name))
        items.push(take(f, f.slice("instruments/".length)) + `: map of the ${html(f.slice(own.length + 5, -".columns.json".length))} columns`);
      parts.push(`<dt>${html(name)}</dt>`, ...items.map((i) => `<dd>${i}</dd>`));
    }
    parts.push("</dl>");
  }
  const other = files.filter((f) => !listed.has(f));
  if (other.length)
    parts.push(`<h${level}>Other files</h${level}>`, "<ul>", ...other.map((f) => `<li>${link(f, f)}</li>`), "</ul>");
  return parts;
}

// One line on citing, with an example from the release: the DDI of its first
// instrument, or else its workspace DDI, if it has either.
function cite(tag) {
  const files = filesIn(join(site, tag));
  const example = files.find(isInstrumentDdi) ?? files.find((f) => f === "ddi.json");
  return (
    "<p>To cite the DDI of a release in a dataset, give its address on this site to <code>qretools responses --ddi</code> (QREtools 2.0.0-alpha.13 or later)" +
    (example ? `, for example <code>${html(`${tag}/${example}`)}</code>` : "") +
    ". The dataset records the address and the SHA-256 digest of the file. " +
    "The files of main change, but the files of a release stay the same.</p>"
  );
}

function page(title, body) {
  return [
    "<!DOCTYPE html>",
    '<html lang="en">',
    "<head>",
    '<meta charset="utf-8">',
    '<meta name="viewport" content="width=device-width, initial-scale=1">',
    '<meta name="color-scheme" content="light dark">',
    `<title>${html(title)}</title>`,
    "</head>",
    "<body>",
    `<h1>${html(title)}</h1>`,
    ...body,
    "</body>",
    "</html>",
    "",
  ].join("\n");
}

// The date of each tag: the tagger's date for a tag made by the Release workflow.
const dates = Object.fromEntries(
  execFileSync("git", ["for-each-ref", "--format=%(refname:short) %(creatordate:short)", "refs/tags"], {
    encoding: "utf8",
  })
    .split("\n")
    .filter(Boolean)
    .map((line) => line.split(" ")),
);
const dated = (tag) =>
  dates[tag] ? ` <time datetime="${html(dates[tag])}">${html(dates[tag])}</time>` : "";

const releases = readdirSync(site)
  .filter((name) => isRelease(name) && statSync(join(site, name)).isDirectory())
  .sort((a, b) => Number(b.slice(1)) - Number(a.slice(1)));

for (const tag of releases)
  writeFileSync(
    join(site, tag, "index.html"),
    page(`${repo} ${tag}`, [`<p>${dates[tag] ? `Released${dated(tag)}. ` : ""}<a href="../">All releases</a></p>`, ...listing(join(site, tag), 2), cite(tag)]),
  );

writeFileSync(
  join(site, "index.html"),
  page(repo, [
    "<h2>main</h2>",
    ...listing(site, 3),
    ...(releases.length
      ? ["<h2>Releases</h2>", "<ul>", ...releases.map((t) => `<li>${link(`${t}/`, t)}${dated(t)}</li>`), "</ul>", cite(releases[0])]
      : []),
  ]),
);
