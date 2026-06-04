param(
    [string]$NoteFile = "",
    [switch]$Watch,
    [int]$IntervalSec = 10,
    [switch]$NoPush
)

$ErrorActionPreference = "Stop"

$RepoDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$PublisherScript = Join-Path $RepoDir "obsidian_to_jekyll.py"
$SourceDir = "C:\Users\oprio\Documents\git_obsidian\notes"
$CommitMessage = "Publish notes from Obsidian"

function Invoke-PublishOnce {
    if ($NoteFile -ne "") {
        python "$PublisherScript" --source "$SourceDir" --file "$NoteFile"
    }
    else {
        python "$PublisherScript" --source "$SourceDir"
    }

    $hasPostChanges = git status --porcelain _posts
    if (-not $hasPostChanges) {
        Write-Host "No changes in _posts."
        return
    }

    git add _posts
    git commit -m "$CommitMessage"

    if (-not $NoPush) {
        git push
    }
}

Push-Location $RepoDir
try {
    if ($Watch) {
        Write-Host "Watching and auto-publishing every $IntervalSec seconds..."
        while ($true) {
            Invoke-PublishOnce
            Start-Sleep -Seconds ([Math]::Max(5, $IntervalSec))
        }
    }
    else {
        Invoke-PublishOnce
    }
}
finally {
    Pop-Location
}
