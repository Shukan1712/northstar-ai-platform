import { build } from "esbuild";
import { createHash } from "node:crypto";
import { mkdir, readFile, rename, rm, writeFile } from "node:fs/promises";

await rm("dist", { recursive: true, force: true });
await mkdir("dist/assets", { recursive: true });

await build({
  entryPoints: ["src/main.tsx"],
  bundle: true,
  minify: true,
  sourcemap: false,
  format: "esm",
  target: ["es2020"],
  jsx: "automatic",
  outfile: "dist/assets/app.js"
});

await build({
  entryPoints: ["src/styles.css"],
  bundle: true,
  minify: true,
  outfile: "dist/assets/app.css"
});

const js = await readFile("dist/assets/app.js");
const css = await readFile("dist/assets/app.css");
const jsName = `app.${createHash("sha256").update(js).digest("hex").slice(0, 10)}.js`;
const cssName = `app.${createHash("sha256").update(css).digest("hex").slice(0, 10)}.css`;
await rename("dist/assets/app.js", `dist/assets/${jsName}`);
await rename("dist/assets/app.css", `dist/assets/${cssName}`);

const source = await readFile("index.html", "utf8");
const html = source
  .replace('<script type="module" src="/src/main.tsx"></script>', `<script type="module" src="/assets/${jsName}"></script>`)
  .replace("</head>", `    <link rel="stylesheet" href="/assets/${cssName}" />\n  </head>`);
await writeFile("dist/index.html", html);
console.log(`Northstar web production build created in dist/ (${jsName}, ${cssName}).`);
