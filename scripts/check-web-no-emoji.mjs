#!/usr/bin/env node
/**
 * 扫描 apps/web 下前端相关文件，禁止出现 emoji 字符。
 * 图标请使用 lucide-react（https://lucide.dev/packages）。
 *
 * 用法：
 *   node scripts/check-web-no-emoji.mjs           # 检查 apps/web 全量（排除 node_modules、.next）
 *   node scripts/check-web-no-emoji.mjs --staged  # 仅检查 git 暂存区中 apps/web 下文件
 *   node scripts/check-web-no-emoji.mjs path/a.tsx path/b.css  # 检查指定文件
 */

import { execSync } from "node:child_process";
import emojiRegex from "emoji-regex";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(__dirname, "..");

const EXT = new Set([
  ".ts",
  ".tsx",
  ".js",
  ".jsx",
  ".mjs",
  ".cjs",
  ".css",
  ".mdx",
  ".md",
]);

const SKIP_DIR = new Set(["node_modules", ".next", "dist", ".turbo"]);

function shouldScanFile(relPath) {
  const normalized = relPath.split(path.sep).join("/");
  if (!normalized.startsWith("apps/web/")) {
    return false;
  }
  if (normalized.includes("/node_modules/") || normalized.includes("/.next/")) {
    return false;
  }
  return EXT.has(path.extname(relPath));
}

function walk(dir, acc) {
  let entries;
  try {
    entries = fs.readdirSync(dir, { withFileTypes: true });
  } catch {
    return;
  }
  for (const ent of entries) {
    if (SKIP_DIR.has(ent.name)) {
      continue;
    }
    const full = path.join(dir, ent.name);
    if (ent.isDirectory()) {
      walk(full, acc);
    } else if (ent.isFile()) {
      const rel = path.relative(ROOT, full);
      if (shouldScanFile(rel)) {
        acc.push(rel);
      }
    }
  }
}

function getStagedFiles() {
  const out = execSync("git diff --cached --name-only -z", {
    cwd: ROOT,
    encoding: "utf8",
    maxBuffer: 10 * 1024 * 1024,
  });
  const files = [];
  if (!out) {
    return files;
  }
  for (const chunk of out.split("\0")) {
    if (chunk && shouldScanFile(chunk)) {
      files.push(chunk);
    }
  }
  return files;
}

function lineHasEmoji(line) {
  const re = emojiRegex();
  return re.test(line);
}

function checkFile(relPath) {
  const abs = path.join(ROOT, relPath);
  if (!fs.existsSync(abs)) {
    return [];
  }
  const text = fs.readFileSync(abs, "utf8");
  const lines = text.split(/\r?\n/);
  const hits = [];
  lines.forEach((line, i) => {
    if (lineHasEmoji(line)) {
      hits.push({ line: i + 1, sample: line.trim().slice(0, 120) });
    }
  });
  return hits;
}

function main() {
  const args = process.argv.slice(2);
  let files;

  if (args[0] === "--staged") {
    files = getStagedFiles();
  } else if (args.length > 0) {
    files = args.map((f) => path.normalize(f)).filter(shouldScanFile);
  } else {
    files = [];
    walk(path.join(ROOT, "apps", "web"), files);
  }

  if (files.length === 0) {
    process.exit(0);
  }

  let failed = false;
  for (const rel of files) {
    const hits = checkFile(rel);
    for (const h of hits) {
      failed = true;
      const posixPath = rel.split(path.sep).join("/");
      console.error(
        `${posixPath}:${h.line}: 检测到 emoji，请移除并使用 lucide-react 图标替代（https://lucide.dev/icons）`,
      );
      if (h.sample) {
        console.error(`  ${h.sample}`);
      }
    }
  }

  if (failed) {
    console.error("");
    console.error(
      "说明：UI 与前端文案中禁止使用 emoji；请使用已依赖的 lucide-react 中的图标组件。",
    );
    process.exit(1);
  }
  process.exit(0);
}

main();
