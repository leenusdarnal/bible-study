#!/usr/bin/env node
"use strict";

/*
 * Metadata-only semantic audit adapter for Bridgeconn USFM Grammar.
 * It reads real USFM source in memory, converts to USJ and back, and writes
 * structural counts only. No verse wording is written to report files.
 *
 * The binary archives and extracted source files must live in an ephemeral
 * CI workspace; do not commit extracted source files to this repository.
 */
const fs = require("node:fs");
const path = require("node:path");
const crypto = require("node:crypto");
const { USFMParser } = require("usfm-grammar");

const PARSER_PACKAGE = "usfm-grammar";
const PARSER_VERSION = "3.2.3";
const SOURCE_IDS = ["engwebp", "eng-kjv"];
const USFM_SUFFIXES = new Set([".usfm", ".sfm"]);

function sha256(bytes) {
  return crypto.createHash("sha256").update(bytes).digest("hex");
}

function findUsfmFiles(root) {
  const files = [];
  function walk(dir) {
    for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
      const full = path.join(dir, entry.name);
      if (entry.isDirectory()) {
        walk(full);
      } else if (entry.isFile() && USFM_SUFFIXES.has(path.extname(entry.name).toLowerCase())) {
        files.push(full);
      }
    }
  }
  if (fs.existsSync(root)) walk(root);
  return files.sort();
}

function summariseUsj(root) {
  const typeCounts = Object.create(null);
  const markerCounts = Object.create(null);
  const bookCodes = [];
  const chapterNumbers = [];
  const verseNumbers = [];

  function visit(value) {
    if (Array.isArray(value)) {
      for (const child of value) visit(child);
      return;
    }
    if (!value || typeof value !== "object") return;

    if (typeof value.type === "string") {
      typeCounts[value.type] = (typeCounts[value.type] || 0) + 1;
      if (value.type === "book" && typeof value.code === "string") bookCodes.push(value.code);
      if (value.type === "chapter" && value.number !== undefined) chapterNumbers.push(String(value.number));
      if (value.type === "verse" && value.number !== undefined) verseNumbers.push(String(value.number));
    }
    if (typeof value.marker === "string") {
      markerCounts[value.marker] = (markerCounts[value.marker] || 0) + 1;
    }
    for (const [key, child] of Object.entries(value)) {
      if (key === "content" || key === "children") visit(child);
    }
  }

  visit(root);
  return {
    root_type: root && typeof root.type === "string" ? root.type : null,
    book_codes: bookCodes,
    chapter_node_count: chapterNumbers.length,
    verse_node_count: verseNumbers.length,
    node_type_counts: Object.fromEntries(Object.entries(typeCounts).sort()),
    marker_node_counts: Object.fromEntries(Object.entries(markerCounts).sort()),
  };
}

function errorPositions(errors) {
  return (errors || []).map((message) => {
    const match = String(message).match(/^At (\d+):(\d+),/);
    return match ? { line: Number(match[1]), column: Number(match[2]) } : { position: null };
  });
}

function sameStructure(a, b) {
  if (!a || !b) return false;
  return JSON.stringify({
    book_codes: a.book_codes,
    chapter_node_count: a.chapter_node_count,
    verse_node_count: a.verse_node_count,
  }) === JSON.stringify({
    book_codes: b.book_codes,
    chapter_node_count: b.chapter_node_count,
    verse_node_count: b.verse_node_count,
  });
}

function auditUsfmString(usfm, fileName = "fixture.usfm") {
  const source = String(usfm).replace(/^\uFEFF/, "");
  const parser = new USFMParser(source);
  const syntaxErrorsAtParse = parser.errors.length;

  let originalUsj = null;
  let conversionSucceeded = false;
  let conversionErrorCount = 0;
  let originalSummary = null;
  try {
    originalUsj = parser.toUSJ();
    conversionSucceeded = Boolean(originalUsj && !originalUsj.error && Array.isArray(originalUsj.content));
    if (conversionSucceeded) originalSummary = summariseUsj(originalUsj);
    else conversionErrorCount = 1;
  } catch (_error) {
    conversionErrorCount = 1;
  }

  const allOriginalErrors = parser.errors.length;
  const originalWarnings = parser.warnings.length;
  let roundTripSyntaxErrorCount = null;
  let roundTripConversionSucceeded = false;
  let roundTripSummary = null;
  let roundTripFailureCount = 0;

  if (conversionSucceeded) {
    try {
      const regenerated = new USFMParser(null, originalUsj);
      roundTripSyntaxErrorCount = regenerated.errors.length;
      if (roundTripSyntaxErrorCount === 0) {
        const regeneratedUsj = regenerated.toUSJ();
        roundTripConversionSucceeded = Boolean(
          regeneratedUsj && !regeneratedUsj.error && Array.isArray(regeneratedUsj.content)
        );
        if (roundTripConversionSucceeded) roundTripSummary = summariseUsj(regeneratedUsj);
        else roundTripFailureCount += 1;
      } else {
        roundTripFailureCount += 1;
      }
    } catch (_error) {
      roundTripFailureCount += 1;
    }
  } else {
    roundTripFailureCount += 1;
  }

  const roundTripMatches = sameStructure(originalSummary, roundTripSummary);
  const parserErrors = Math.max(syntaxErrorsAtParse, allOriginalErrors);
  const passed = parserErrors === 0
    && conversionSucceeded
    && roundTripSyntaxErrorCount === 0
    && roundTripConversionSucceeded
    && roundTripMatches;

  return {
    member_name: fileName,
    source_byte_size: Buffer.byteLength(source, "utf8"),
    source_sha256_utf8: sha256(Buffer.from(source, "utf8")),
    status: passed ? "passed" : "review_required",
    parse_error_count: parserErrors,
    parse_error_positions: errorPositions(parser.errors),
    parse_warning_count: originalWarnings,
    usj_conversion_succeeded: conversionSucceeded,
    usj_conversion_failure_count: conversionErrorCount,
    original_structure: originalSummary,
    roundtrip_syntax_error_count: roundTripSyntaxErrorCount,
    roundtrip_conversion_succeeded: roundTripConversionSucceeded,
    roundtrip_structure_matches: roundTripMatches,
    roundtrip_structure: roundTripSummary,
    roundtrip_failure_count: roundTripFailureCount,
  };
}

function auditDirectory(sourceDir) {
  const files = [];
  const summaryBySource = {};

  for (const sourceId of SOURCE_IDS) {
    const root = path.join(sourceDir, sourceId);
    const names = findUsfmFiles(root);
    const sourceResults = [];

    for (const fullPath of names) {
      const bytes = fs.readFileSync(fullPath);
      const relative = path.relative(root, fullPath).split(path.sep).join("/");
      let text;
      try {
        text = bytes.toString("utf8");
        if (Buffer.from(text, "utf8").length === 0) throw new Error("empty file");
      } catch (_error) {
        sourceResults.push({
          member_name: relative,
          source_byte_size: bytes.length,
          source_sha256_utf8: sha256(bytes),
          status: "review_required",
          read_error_count: 1,
        });
        continue;
      }
      const result = auditUsfmString(text, relative);
      sourceResults.push(result);
    }

    const successCount = sourceResults.filter((x) => x.status === "passed").length;
    const errorCount = sourceResults.filter((x) => x.status !== "passed").length;
    const coreBookCodes = new Set(
      sourceResults.flatMap((x) => x.original_structure?.book_codes || [])
    );

    const summary = {
      source_id: sourceId,
      member_count: sourceResults.length,
      passed_count: successCount,
      review_required_count: errorCount,
      parsed_book_id_count: coreBookCodes.size,
      aggregate_chapter_nodes: sourceResults.reduce((n, x) => n + (x.original_structure?.chapter_node_count || 0), 0),
      aggregate_verse_nodes: sourceResults.reduce((n, x) => n + (x.original_structure?.verse_node_count || 0), 0),
      aggregate_parse_errors: sourceResults.reduce((n, x) => n + (x.parse_error_count || 0), 0),
      aggregate_parse_warnings: sourceResults.reduce((n, x) => n + (x.parse_warning_count || 0), 0),
      aggregate_roundtrip_failures: sourceResults.reduce((n, x) => n + (x.roundtrip_failure_count || 0), 0),
    };
    summaryBySource[sourceId] = summary;

    for (const result of sourceResults) {
      files.push({ source_id: sourceId, ...result });
    }
  }

  const totalFailures = files.filter((x) => x.status !== "passed").length;
  return {
    schema_version: 1,
    generated_at_utc: new Date().toISOString(),
    parser: { package: PARSER_PACKAGE, version: PARSER_VERSION, syntax_family: "USFM 3.x grammar" },
    description: "Metadata-only semantic parser report. No Scripture wording is included.",
    summary_by_source: summaryBySource,
    total_files: files.length,
    passed_files: files.length - totalFailures,
    review_required_files: totalFailures,
    files,
  };
}

function main() {
  const args = process.argv.slice(2);
  let sourceDir = null;
  let outputPath = null;
  for (let i = 0; i < args.length; i++) {
    if (args[i] === "--source-dir") sourceDir = args[++i];
    else if (args[i] === "--output") outputPath = args[++i];
    else throw new Error("Unknown argument: " + args[i]);
  }
  if (!sourceDir || !outputPath) {
    throw new Error("Usage: node tools/usfm_semantic_audit.cjs --source-dir DIR --output FILE");
  }

  const report = auditDirectory(sourceDir);
  fs.mkdirSync(path.dirname(path.resolve(outputPath)), { recursive: true });
  fs.writeFileSync(outputPath, JSON.stringify(report, null, 2) + "\n", "utf8");

  for (const [sourceId, result] of Object.entries(report.summary_by_source)) {
    process.stdout.write(JSON.stringify(result) + "\n");
  }
  process.stdout.write(JSON.stringify({
    parser: report.parser,
    total_files: report.total_files,
    passed_files: report.passed_files,
    review_required_files: report.review_required_files,
    report_file: outputPath,
  }) + "\n");

  if (report.total_files === 0 || report.review_required_files > 0) process.exitCode = 1;
}

if (require.main === module) {
  try {
    main();
  } catch (_error) {
    // Do not print exception contents: third-party parser errors may contain source text.
    process.stderr.write("Semantic USFM audit failed. Inspect the metadata-only report and tool configuration.\n");
    process.exitCode = 1;
  }
}

module.exports = { auditUsfmString, auditDirectory, summariseUsj };
