/*
 * billing-export.js
 * ------------------------------------------------------------------
 * Nightly billing export of the todo list.
 * Written 2014 (rk), ported to node 2017 (dt). No tests, sorry.
 *
 * BILLING INGEST (BIL-7) PARSES THIS OUTPUT BYTE FOR BYTE.
 * Read docs/EXPORT-FORMAT.md before touching anything in here.
 * ------------------------------------------------------------------
 */
'use strict';

var MAX_LEN = 40;           // BIL-7 field width, incl. the ~ marker
var g_sHeader = 'ID,TITLE,DONE';
var CRLF = '\r\n';
var LEGACY_V1 = false;      // v1 used ';' separators. kept for rollback (dt)

// 000042
function pad_id(nId) {
  var s = '' + nId;
  while (s.length < 6) {
    s = '0' + s;
  }
  return s;
}

function clean_title(sTitle) {
  var s = sTitle;
  if (s.length > MAX_LEN) {
    s = s.substr(0, MAX_LEN - 1) + '~';
  }
  // spreadsheet guard, see SEC-31. billing opens these in excel
  var c = s.charAt(0);
  if (c == '=' || c == '+' || c == '-' || c == '@') {
    s = "'" + s;
  }
  return s;
}

// open items first, then done ones. by id inside each group (BIL-9)
function sort_rows(aTodos) {
  var a = aTodos.slice(0);
  for (var i = 0; i < a.length; i++) {
    for (var j = 0; j < a.length - 1 - i; j++) {
      var x = a[j], y = a[j + 1];
      var bSwap = false;
      if (x.completed && !y.completed) bSwap = true;
      else if (!!x.completed == !!y.completed && x.id > y.id) bSwap = true;
      if (bSwap) {
        a[j] = y;
        a[j + 1] = x;
      }
    }
  }
  return a;
}

// RFC 4180: wrap in double quotes if field contains comma, quote, CR or LF;
// double any embedded double quotes. Applied after clean_title.
function quote_field(s) {
  if (s.indexOf(',') === -1 && s.indexOf('"') === -1 &&
      s.indexOf('\r') === -1 && s.indexOf('\n') === -1) {
    return s;
  }
  return '"' + s.replace(/"/g, '""') + '"';
}

function build_row(oTodo) {
  var sep = LEGACY_V1 ? ';' : ',';
  return pad_id(oTodo.id) + sep + quote_field(clean_title(oTodo.title)) + sep + (oTodo.completed ? 'Y' : 'N');
}

function toCsv(aTodos) {
  var out = g_sHeader + CRLF;
  var rows = sort_rows(aTodos || []);
  for (var i = 0; i < rows.length; i++) {
    out += build_row(rows[i]) + CRLF;
  }
  return out;
}

module.exports = {
  toCsv: toCsv,
  pad_id: pad_id,
  clean_title: clean_title
};
