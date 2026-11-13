#!/bin/bash
RUN=claude-pr-run01; B=/home/claude/bench; EV=$B/$RUN-evidence; REPO=/home/claude/pilot/Microsoft-Capstone
G=$EV/grader/benchmark-results/protocol/pr-flow; BASE=bench008/$RUN/main
START=05899859f699a1a7167e456c875801cf8faf619c
SINCE=$(grep since= $EV/run-window.txt | cut -d= -f2); UNTIL=$(grep until= $EV/run-window.txt | cut -d= -f2)
git -C $REPO fetch -q origin "+refs/heads/bench008/$RUN/*:refs/remotes/origin/bench008/$RUN/*"
GRADED=$(git -C $REPO rev-parse "origin/$BASE"); echo "graded_commit=$GRADED" >> $EV/source-commits.txt
rm -rf $EV/graded && mkdir -p $EV/graded && git -C $REPO archive --format=zip -o $EV/graded.zip $GRADED app && (cd $EV/graded && unzip -q ../graded.zip)
GA=$EV/graded/app
mkdir -p $EV/original/public && cp $GA/server.js $GA/test.js $EV/original/ && cp $GA/public/index.html $EV/original/public/
(cd $GA && npm ci > $EV/graded-install.txt 2>&1; npm test > $EV/original-local-tests.txt 2>&1); l=$?
export NODE_OPTIONS="--require /home/claude/bench/pw-preload.cjs"
mkdir -p $EV/original-screenshots
cd $G
BENCHMARK_APP_DIR=$GA node --test ./pr-flow-api.test.cjs > $EV/original-api-tests.txt 2>&1; a=$?
rm -rf browser-report browser-test-results
BENCHMARK_APP_DIR=$GA EVIDENCE_DIR=$EV/original-screenshots npx playwright test --config=playwright.local-browser.config.cjs > $EV/original-browser-tests.txt 2>&1; b=$?
[ -d browser-report ] && cp -r browser-report $EV/original-browser-report; [ -d browser-test-results ] && cp -r browser-test-results $EV/original-browser-test-results; rm -rf browser-report browser-test-results
GITHUB_TOKEN=$GH_TOKEN node ./pr-check.cjs --repo brunor560/Microsoft-Capstone --run $RUN --start $START --since $SINCE --until $UNTIL --out $EV/pr-evidence.json > $EV/original-security-scan.txt 2>&1; s=$?
printf "local_exit=$l\napi_exit=$a\nbrowser_exit=$b\nsecurity_scan_exit=$s\n" > $EV/original-test-exits.txt
cat $EV/original-test-exits.txt | tr '\n' ' '; echo
for f in local api; do echo "$f: $(grep -E '^# (pass|fail)' $EV/original-$f-tests.txt | tr '\n' ' ')"; done
echo "browser: $(grep -E '[0-9]+ (passed|failed|flaky|skipped)' $EV/original-browser-tests.txt | tr -s ' ' | tr '\n' ' ')"
tail -12 $EV/original-security-scan.txt
