// Checks a pull request against CONTRIBUTING.md. Reads PR_TITLE, PR_BODY,
// HEAD_REF and BASE_REF from the environment; prints every problem and exits
// 1 if there are any.

const title = process.env.PR_TITLE || '';
const body = (process.env.PR_BODY || '').replace(/\r\n/g, '\n');
const head = process.env.HEAD_REF || '';
const base = process.env.BASE_REF || '';

const problems = [];

if (!/\/main$/.test(base)) {
  problems.push(`The pull request must target your base branch (ending in /main), not "${base}".`);
} else {
  const prefix = base.replace(/\/main$/, '/');
  if (!head.startsWith(prefix) || head.length <= prefix.length || head === base) {
    problems.push(`Branch "${head}" must be named "${prefix}<short-description>".`);
  }
}

if (!/^(feat|fix|test|docs|refactor|chore)(\([\w-]+\))?: \S.{3,}$/.test(title.trim())) {
  problems.push(`Title "${title}" is not Conventional Commits style, for example "feat: add todo statistics".`);
}

function section(name) {
  const m = body.match(new RegExp(`^##\\s+${name}\\s*\\n([\\s\\S]*?)(?=^##\\s|(?![\\s\\S]))`, 'im'));
  return m ? m[1].trim() : null;
}

const requirements = section('Requirements');
if (requirements === null) {
  problems.push('The description has no "## Requirements" section.');
} else if (!/\bREQ-\d{2}\b/.test(requirements)) {
  problems.push('The "## Requirements" section lists no requirement IDs (REQ-01, REQ-02, ...).');
}

const testing = section('Testing');
if (testing === null) {
  problems.push('The description has no "## Testing" section.');
} else if (testing.length < 10) {
  problems.push('The "## Testing" section is empty or too short; say what you ran and the results.');
}

if (problems.length) {
  for (const p of problems) console.log(`::error::${p}`);
  console.log(`\n${problems.length} problem(s). See CONTRIBUTING.md.`);
  process.exit(1);
}
console.log('Pull request rules: all passed.');
