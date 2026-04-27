# CI/CD: GitHub Actions Release Workflow

## `.github/workflows/release.yml`

This is the recommended multi-platform release workflow. It:
1. Builds the backend sidecar for all three platforms in parallel
2. Uploads each binary as a build artifact
3. Runs `tauri build` on each platform using the pre-built sidecar

```yaml
name: Release

on:
  push:
    tags:
      - 'v*'

permissions:
  contents: write

jobs:
  # ─────────────────────────────────────────────
  # Job 1: Build backend sidecar for each platform
  # ─────────────────────────────────────────────
  build-backend:
    strategy:
      fail-fast: false
      matrix:
        include:
          - platform: ubuntu-latest
            triple: x86_64-unknown-linux-gnu
            ext: ""
          - platform: macos-latest
            triple: aarch64-apple-darwin
            ext: ""
          - platform: macos-13
            triple: x86_64-apple-darwin
            ext: ""
          - platform: windows-latest
            triple: x86_64-pc-windows-msvc
            ext: ".exe"

    runs-on: ${{ matrix.platform }}

    steps:
      - uses: actions/checkout@v4

      # ── Python backend example ──
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - name: Install Python deps
        run: pip install -r backend/requirements.txt pyinstaller

      - name: Build sidecar (Python → binary)
        run: |
          pyinstaller --onefile \
            --name <backend-name> \
            backend/src/main.py \
            --distpath dist-backend

      - name: Rename to triple-suffixed name
        shell: bash
        run: |
          mkdir -p src-tauri/binaries
          mv dist-backend/<backend-name>${{ matrix.ext }} \
             src-tauri/binaries/<backend-name>-${{ matrix.triple }}${{ matrix.ext }}

      - name: Upload sidecar artifact
        uses: actions/upload-artifact@v4
        with:
          name: sidecar-${{ matrix.triple }}
          path: src-tauri/binaries/<backend-name>-${{ matrix.triple }}${{ matrix.ext }}

  # ─────────────────────────────────────────────
  # Job 2: Build Tauri app for each platform
  # ─────────────────────────────────────────────
  build-tauri:
    needs: build-backend
    strategy:
      fail-fast: false
      matrix:
        include:
          - platform: ubuntu-latest
            triple: x86_64-unknown-linux-gnu
            ext: ""
          - platform: macos-latest
            triple: aarch64-apple-darwin
            ext: ""
          - platform: macos-13
            triple: x86_64-apple-darwin
            ext: ""
          - platform: windows-latest
            triple: x86_64-pc-windows-msvc
            ext: ".exe"

    runs-on: ${{ matrix.platform }}

    steps:
      - uses: actions/checkout@v4

      - name: Download sidecar for this platform
        uses: actions/download-artifact@v4
        with:
          name: sidecar-${{ matrix.triple }}
          path: src-tauri/binaries/

      - name: Make sidecar executable (Unix)
        if: runner.os != 'Windows'
        run: chmod +x src-tauri/binaries/<backend-name>-${{ matrix.triple }}

      - name: Install Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'

      - name: Install pnpm
        uses: pnpm/action-setup@v3
        with:
          version: 9

      - name: Install Rust stable
        uses: dtolnay/rust-toolchain@stable

      - name: Install Linux dependencies
        if: runner.os == 'Linux'
        run: |
          sudo apt-get update
          sudo apt-get install -y \
            libwebkit2gtk-4.1-dev libappindicator3-dev librsvg2-dev patchelf

      - name: Install frontend deps
        run: pnpm install

      - name: Build Tauri app
        uses: tauri-apps/tauri-action@v0
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          # macOS codesigning (optional but recommended for distribution):
          # APPLE_CERTIFICATE: ${{ secrets.APPLE_CERTIFICATE }}
          # APPLE_CERTIFICATE_PASSWORD: ${{ secrets.APPLE_CERTIFICATE_PASSWORD }}
          # APPLE_SIGNING_IDENTITY: ${{ secrets.APPLE_SIGNING_IDENTITY }}
          # APPLE_ID: ${{ secrets.APPLE_ID }}
          # APPLE_PASSWORD: ${{ secrets.APPLE_PASSWORD }}
          # APPLE_TEAM_ID: ${{ secrets.APPLE_TEAM_ID }}
        with:
          tagName: ${{ github.ref_name }}
          releaseName: '<ProjectName> ${{ github.ref_name }}'
          releaseBody: 'See CHANGELOG for release notes.'
          releaseDraft: true
          prerelease: false
```

## Secrets to configure in GitHub

Go to **Settings → Secrets and variables → Actions** and add:

| Secret name                  | Required for             |
|------------------------------|--------------------------|
| `GITHUB_TOKEN`               | Auto-provided, no action |
| `APPLE_CERTIFICATE`          | macOS notarization       |
| `APPLE_CERTIFICATE_PASSWORD` | macOS notarization       |
| `APPLE_SIGNING_IDENTITY`     | macOS notarization       |
| `APPLE_ID`                   | macOS notarization       |
| `APPLE_PASSWORD`             | macOS app-specific pw    |
| `APPLE_TEAM_ID`              | macOS notarization       |

## Triggering a release

```bash
git tag v0.1.0
git push origin v0.1.0
```

This triggers the workflow which creates a **draft** GitHub Release with all platform installers attached.
