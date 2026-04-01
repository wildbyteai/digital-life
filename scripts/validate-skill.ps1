param(
    [string]$Root = (Split-Path -Parent $PSScriptRoot)
)

$ErrorActionPreference = "Stop"

$skillMap = @(
    @{ slug = "past_life"; reference = "past-life" },
    @{ slug = "cringe_archaeology"; reference = "cringe-archaeology" },
    @{ slug = "ai_clone"; reference = "ai-clone" },
    @{ slug = "legacy_audit"; reference = "legacy-audit" },
    @{ slug = "epitaph"; reference = "epitaph" }
)

$requiredRootFiles = @(
    "README.md",
    "SKILL.md",
    "LICENSE",
    ".gitignore",
    ".gitattributes",
    "profiles/README.md",
    "agents/openai.yaml",
    "assets/digital-life-small.svg",
    "assets/digital-life-large.svg",
    "examples/README.md",
    "examples/legacy_audit_demo.json",
    "examples/legacy_audit_demo.md",
    "examples/ai_clone_demo.json",
    "examples/ai_clone_demo.md",
    "scripts/validate-skill.py"
)

$errors = @()

function Add-Error {
    param(
        [string]$Message
    )

    $script:errors += $Message
}

function Assert-Exists {
    param(
        [string]$RelativePath
    )

    $fullPath = Join-Path $Root $RelativePath
    if (-not (Test-Path -LiteralPath $fullPath)) {
        Add-Error ("Missing file or directory: {0}" -f $RelativePath)
    }
}

foreach ($path in $requiredRootFiles) {
    Assert-Exists -RelativePath $path
}

Assert-Exists -RelativePath "profiles/history/.gitkeep"

foreach ($entry in $skillMap) {
    Assert-Exists -RelativePath ("layer0/{0}.md" -f $entry.slug)
    Assert-Exists -RelativePath ("prompts/{0}.md" -f $entry.slug)
    Assert-Exists -RelativePath ("profiles/templates/{0}.json" -f $entry.slug)
    Assert-Exists -RelativePath ("references/{0}.md" -f $entry.reference)

    $templatePath = Join-Path $Root ("profiles/templates/{0}.json" -f $entry.slug)
    if (Test-Path -LiteralPath $templatePath) {
        try {
            $template = Get-Content -LiteralPath $templatePath -Raw -Encoding UTF8 | ConvertFrom-Json
            if ($template.skill -ne $entry.slug) {
                Add-Error ("Template skill field mismatch: profiles/templates/{0}.json -> {1}" -f $entry.slug, $template.skill)
            }
        }
        catch {
            Add-Error ("Invalid JSON template: profiles/templates/{0}.json" -f $entry.slug)
        }
    }
}

$exampleJsonFiles = @(
    "examples/legacy_audit_demo.json",
    "examples/ai_clone_demo.json"
)

foreach ($relativePath in $exampleJsonFiles) {
    $fullPath = Join-Path $Root $relativePath
    if (Test-Path -LiteralPath $fullPath) {
        try {
            Get-Content -LiteralPath $fullPath -Raw -Encoding UTF8 | ConvertFrom-Json | Out-Null
        }
        catch {
            Add-Error ("Invalid example JSON: {0}" -f $relativePath)
        }
    }
}

$gitignorePath = Join-Path $Root ".gitignore"
if (Test-Path -LiteralPath $gitignorePath) {
    $gitignore = Get-Content -LiteralPath $gitignorePath -Encoding UTF8
    $requiredPatterns = @(
        "profiles/*.json",
        "profiles/*.md",
        "!profiles/README.md",
        "profiles/history/*",
        "!profiles/history/.gitkeep"
    )

    foreach ($requiredPattern in $requiredPatterns) {
        if ($gitignore -notcontains $requiredPattern) {
            Add-Error (".gitignore missing rule: {0}" -f $requiredPattern)
        }
    }
}

if ($errors.Count -gt 0) {
    Write-Host "Validation failed:" -ForegroundColor Red
    foreach ($item in $errors) {
        Write-Host ("- {0}" -f $item) -ForegroundColor Red
    }
    exit 1
}

Write-Host "Validation passed:" -ForegroundColor Green
Write-Host ("- skills: {0}" -f $skillMap.Count)
Write-Host "- prompts / layer0 / references / templates are present"
Write-Host "- profiles layout and privacy ignore rules are in place"
Write-Host "- agents metadata, icon assets, and example outputs are present"
