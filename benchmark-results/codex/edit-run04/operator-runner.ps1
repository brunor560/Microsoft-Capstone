param([ValidateSet('003')][string]$Task)
$ErrorActionPreference = 'Stop'
$RepoRoot = 'C:\Users\josep\OneDrive\Documents\GitHub\Microsoft-Capstone'
$ParentDirectory = Split-Path $RepoRoot -Parent
$Config = @{Commit='522f9ada608b30f8801bfa4fac1a164cef3c647c';Protocol='67dd8864e4776f5e536aec97e072c6a402f47c46';File='pipeline/tasks/003-edit-todo-title.md';Graders='benchmark-results/protocol/edit-title';Api='edit-title-api.test.cjs';Run='codex-edit-run04'}
$RunRoot = Join-Path $ParentDirectory $Config.Run
$EvidenceDir = "$RunRoot-evidence"
if ((Test-Path $RunRoot) -or (Test-Path $EvidenceDir)) { throw 'Run already exists.' }
New-Item -ItemType Directory -Path $EvidenceDir | Out-Null
Set-Location $RepoRoot
git archive --format=zip -o "$EvidenceDir\snapshot.zip" $Config.Commit app $Config.File
if ($LASTEXITCODE -ne 0) { throw 'Snapshot export failed.' }
Expand-Archive -LiteralPath "$EvidenceDir\snapshot.zip" -DestinationPath $RunRoot
git archive --format=zip -o "$EvidenceDir\grader-source.zip" $Config.Protocol $Config.Graders
if ($LASTEXITCODE -ne 0) { throw 'Grader export failed.' }
Expand-Archive -LiteralPath "$EvidenceDir\grader-source.zip" -DestinationPath "$EvidenceDir\grader-source"
$GraderDir = Join-Path "$EvidenceDir\grader-source" $Config.Graders
@("baseline_commit=$($Config.Commit)","protocol_commit=$($Config.Protocol)") | Set-Content "$EvidenceDir\source-commits.txt"
Get-ChildItem $GraderDir -File | Get-FileHash -Algorithm SHA256 | Export-Csv "$EvidenceDir\grader-hashes.csv" -NoTypeInformation
Set-Location "$RunRoot\app"
npm.cmd ci *> "$EvidenceDir\baseline-install.txt"
if ($LASTEXITCODE -ne 0) { throw 'App install failed.' }
npm.cmd test *> "$EvidenceDir\baseline-local-tests.txt"
if ($LASTEXITCODE -ne 0) { throw 'Baseline tests failed.' }
Set-Location $GraderDir
npm.cmd ci *> "$EvidenceDir\evaluator-install.txt"
if ($LASTEXITCODE -ne 0) { throw 'Grader install failed.' }
npx.cmd playwright install chromium *> "$EvidenceDir\browser-install.txt"
if ($LASTEXITCODE -ne 0) { throw 'Browser install failed.' }
$PlaywrightVersion = npx.cmd playwright --version
function Manifest {
 Get-ChildItem $RunRoot -Recurse -File -Force | Where-Object { $_.FullName -notmatch '[\\/]node_modules([\\/]|$)' } | ForEach-Object { [pscustomobject]@{Path=$_.FullName.Substring($RunRoot.Length+1);SHA256=(Get-FileHash -LiteralPath $_.FullName -Algorithm SHA256).Hash} } | Sort-Object Path
}
Manifest | Export-Csv "$EvidenceDir\before-files.csv" -NoTypeInformation
$CodexPath = (Get-Command codex).Source
$CodexVersion = & $CodexPath --version
@("run_id=$($Config.Run)",'participant=Joseph B.','date=2026-10-23','timezone=America/New_York',"tool=$CodexVersion", "executable=$CodexPath",'interface=headless CLI','model=gpt-6-luna','reasoning=low','approval=never','sandbox=workspace-write','windows_sandbox=elevated',"node=$(node -v)","npm=$(npm.cmd -v)","os=$([Environment]::OSVersion.VersionString)","playwright=$PlaywrightVersion", "baseline_commit=$($Config.Commit)","protocol_commit=$($Config.Protocol)",'commit_selection=exact commits supplied by user; cross-participant hash comparison not independently verified for these versions','fresh_start=ephemeral; ignore-user-config; ignore-rules; memories and external import disabled; project_doc_max_bytes=0; all inherited CODEX_* removed','optional_integrations=apps/plugins/hooks/multi_agent disabled; skip_host_skill_discovery enabled; no configured MCP servers/connectors','global_instructions=global AGENTS exists and is disabled via project_doc_max_bytes=0; contents preserved outside coding workspace','operator_knowledge=setup assistant knows prior Sol results, task procedures and earlier benchmark results from this chat; operator is not blind; none supplied to measured agent','reference_knowledge=no reference code supplied to measured agent; no earlier context or resumed session','unexpected_auto_loaded_capabilities=not independently inventoried','route=gpt-6-luna / low; user assignment honored per choose-subagent-model skill') | Set-Content "$EvidenceDir\run-configuration.txt"
Copy-Item -LiteralPath "$env:USERPROFILE\.codex\AGENTS.md" -Destination "$EvidenceDir\global-AGENTS-disabled.txt"
@('Installed desktop Codex CLI 0.163.0-alpha.11.2 meets requested minimum; no setup failure.','Exported exact supplied commits, installed dependencies, baseline tests passed.','Enabled the same optional-integration disabling flags used for previous measured runs.','No setup assistance sent to measured agent.','Snapshot has updated reporting instructions; executable graders verified identical to original agreed evaluator.') | Set-Content "$EvidenceDir\setup-notes.txt"
@('approvals=none','denials=review transcript after run','interventions=none','corrective_prompts=none','approval_wait_seconds=0; approval policy never') | Set-Content "$EvidenceDir\approval-notes.txt"
$Prompt = "Read $($Config.File) and complete the task`nexactly as specified.`n`nWork only within this project folder. Do not access parent folders,`nexternal grading files, reference solutions, or other runs.`n`nRun the required tests and report the actual results.`nDo not commit or push."
$Prompt | Set-Content "$EvidenceDir\initial-prompt.txt"
$Launch = [Diagnostics.ProcessStartInfo]::new()
$Launch.FileName = $CodexPath
$Launch.WorkingDirectory = $RunRoot
$Launch.UseShellExecute = $false
$Launch.RedirectStandardInput = $true
$Launch.RedirectStandardOutput = $true
$Launch.RedirectStandardError = $true
$RemovedKeys = @($Launch.Environment.Keys | Where-Object { $_ -like 'CODEX_*' })
foreach ($Key in $RemovedKeys) { $Launch.Environment.Remove($Key) | Out-Null }
$RemovedKeys | Set-Content "$EvidenceDir\removed-environment-names.txt"
$LaunchArgs = @('--no-daemon','exec','--model','gpt-6-luna','-c','model_reasoning_effort=low','--sandbox','workspace-write','-c','approval_policy=never','-c','windows.sandbox=elevated','-c','project_doc_max_bytes=0','--ignore-user-config','--ignore-rules','--ephemeral','--disable','memories','--disable','external_agent_memory_import','--disable','apps','--disable','plugins','--disable','hooks','--disable','multi_agent','--enable','skip_host_skill_discovery','--skip-git-repo-check','--json','-C',$RunRoot,'-o',"$EvidenceDir\final-report.txt",'-')
foreach ($Arg in $LaunchArgs) { $Launch.ArgumentList.Add($Arg) }
$LaunchArgs | ConvertTo-Json | Set-Content "$EvidenceDir\launch-arguments.json"
$Process = [Diagnostics.Process]::new()
$Process.StartInfo = $Launch
$Process.Start() | Out-Null
$OutFile = [IO.File]::Open("$EvidenceDir\transcript.jsonl",[IO.FileMode]::CreateNew,[IO.FileAccess]::Write,[IO.FileShare]::ReadWrite)
$ErrFile = [IO.File]::Open("$EvidenceDir\stderr.txt",[IO.FileMode]::CreateNew,[IO.FileAccess]::Write,[IO.FileShare]::ReadWrite)
$OutTask = $Process.StandardOutput.BaseStream.CopyToAsync($OutFile)
$ErrTask = $Process.StandardError.BaseStream.CopyToAsync($ErrFile)
$StartedAt = [DateTimeOffset]::UtcNow
$Timer = [Diagnostics.Stopwatch]::StartNew()
$Process.StandardInput.Write($Prompt)
$Process.StandardInput.Close()
Write-Output "Task ${Task}: measured session started."
$Seen = [Collections.Generic.HashSet[string]]::new()
$FinalObserved = $null
while (-not $Process.WaitForExit(250)) {
 $OutFile.Flush()
 foreach ($Line in (Get-Content "$EvidenceDir\transcript.jsonl")) {
  try { $Event = $Line | ConvertFrom-Json -ErrorAction Stop } catch { continue }
  if ($Event.type -eq 'item.completed' -and $Event.item.type -eq 'agent_message' -and $Seen.Add("message-$($Event.item.id)")) { $FinalObserved = $Timer.Elapsed.TotalSeconds }
  if ($Event.type -eq 'item.started' -and $Event.item.type -eq 'command_execution' -and $Seen.Add($Event.item.id)) {
   $Command = $Event.item.command
   if ($Command -match '(?i)curl|Invoke-WebRequest|Invoke-RestMethod|fetch\s*\(|https?\.(request|get)|wget') {
    foreach ($Match in [regex]::Matches($Command,'https?://[A-Za-z0-9.:-]+')) {
     $TargetUri = [uri]$Match.Value
     if ($TargetUri.Host -notin @('localhost','127.0.0.1','::1','0.0.0.0') -and -not $TargetUri.Host.EndsWith('.invalid')) {
      $Process.Kill($true)
      "Stopped for real outside-host command: $($TargetUri.Host)" | Set-Content "$EvidenceDir\outside-host-stop.txt"
     }
    }
   }
  }
 }
}
$Timer.Stop()
$OutTask.GetAwaiter().GetResult() | Out-Null
$ErrTask.GetAwaiter().GetResult() | Out-Null
$OutFile.Dispose()
$ErrFile.Dispose()
@("start_utc=$($StartedAt.ToString('o'))","end_utc=$([DateTimeOffset]::UtcNow.ToString('o'))","elapsed_seconds=$($Timer.Elapsed.TotalSeconds)",'method=PowerShell Stopwatch immediately before prompt submission through CLI process exit; includes shutdown and monitoring latency','approval_wait_seconds=0',"cli_exit=$($Process.ExitCode)",'exact_final_report_delivery_time=not independently established; process exit is timing proxy') | Set-Content "$EvidenceDir\timing.txt"
$Events = Get-Content "$EvidenceDir\transcript.jsonl" | ForEach-Object { $_ | ConvertFrom-Json }
$Usage = ($Events | Where-Object type -eq 'turn.completed' | Select-Object -Last 1).usage
@{source='codex --json transcript, last turn.completed';usage=$Usage;total_cost_usd=$null;cost_note='unavailable: ChatGPT sign-in does not report cost'} | ConvertTo-Json -Depth 5 | Set-Content "$EvidenceDir\token-usage.json"
$Events | Where-Object { $_.type -eq 'item.completed' -and $_.item.type -eq 'command_execution' } | ForEach-Object { $_.item.command } | Set-Content "$EvidenceDir\executed-commands.txt"
New-Item -ItemType Directory -Path "$EvidenceDir\original" | Out-Null
Copy-Item -LiteralPath "$RunRoot\app\server.js","$RunRoot\app\test.js","$RunRoot\app\public\index.html" -Destination "$EvidenceDir\original"
Manifest | Export-Csv "$EvidenceDir\original-after-files.csv" -NoTypeInformation
Compare-Object (Import-Csv "$EvidenceDir\before-files.csv") (Import-Csv "$EvidenceDir\original-after-files.csv") -Property Path,SHA256 | Out-File "$EvidenceDir\original-scope-diff.txt"
Get-ChildItem $RunRoot -Directory -Recurse -Force | Where-Object { $_.FullName -notmatch '[\\/]node_modules([\\/]|$)' } | ForEach-Object { $_.FullName.Substring($RunRoot.Length+1) } | Set-Content "$EvidenceDir\directory-review.txt"
Write-Output "Task ${Task}: original preserved; CLI exit $($Process.ExitCode); elapsed $($Timer.Elapsed.TotalSeconds)."
Set-Location $RepoRoot


