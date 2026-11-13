#!/bin/bash
RUN=claude-pr-run01; B=/home/claude/bench; RR=$B/$RUN; EV=$B/$RUN-evidence
S=/tmp/claude-0/-home-claude/dfe388ce-7fe5-5646-9ef8-0b6b485befec/scratchpad
source $B/pr/claude-args.sh
printf 'cd %s && env -u GH_TOKEN -u GITHUB_TOKEN freshenv.sh -p "$(cat initial-prompt.txt)" %s < /dev/null\n' "$RR" "${ARGS[*]}" | sed 's#/home/claude/bench/pr/mcp-github.json#mcp-config-redacted.json (token redacted)#' > $EV/run-command.txt
cd $RR
SINCE=$(date -u +%Y-%m-%dT%H:%M:%S.%3NZ); START=$(date -u +%s.%N)
echo "since=$SINCE" > $EV/run-window.txt
env -u GH_TOKEN -u GITHUB_TOKEN $S/freshenv.sh -p "$(cat $EV/initial-prompt.txt)" "${ARGS[@]}" < /dev/null > $EV/transcript.jsonl 2> $EV/cli-stderr.txt
RC=$?; END=$(date -u +%s.%N); UNTIL=$(date -u +%Y-%m-%dT%H:%M:%S.%3NZ)
echo "until=$UNTIL" >> $EV/run-window.txt
printf "start_utc=$SINCE\nend_utc=$UNTIL\ncli_exit=$RC\n" > $EV/timing-raw.txt
python3 -c "print('elapsed_seconds=%.1f'%($END-$START))" >> $EV/timing-raw.txt
cat $EV/timing-raw.txt
