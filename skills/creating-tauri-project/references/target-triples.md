# Rust Target Triples for Tauri Sidecars

Tauri automatically appends the target triple to sidecar binary names.
Your binary in `src-tauri/binaries/` must be named:
`<backend-name>-<triple>[.exe]`

## Common Triples

| OS            | Arch     | Triple                              | Extension |
|---------------|----------|-------------------------------------|-----------|
| Windows       | x64      | `x86_64-pc-windows-msvc`            | `.exe`    |
| Windows       | ARM64    | `aarch64-pc-windows-msvc`           | `.exe`    |
| macOS         | Apple Silicon | `aarch64-apple-darwin`         | (none)    |
| macOS         | Intel    | `x86_64-apple-darwin`               | (none)    |
| Linux         | x64      | `x86_64-unknown-linux-gnu`          | (none)    |
| Linux         | ARM64    | `aarch64-unknown-linux-gnu`         | (none)    |
| Linux (musl)  | x64      | `x86_64-unknown-linux-musl`         | (none)    |

## Example File Names

For a backend named `my-backend`:

```
src-tauri/binaries/
├── my-backend-x86_64-pc-windows-msvc.exe
├── my-backend-aarch64-apple-darwin
├── my-backend-x86_64-apple-darwin
├── my-backend-x86_64-unknown-linux-gnu
└── .gitkeep
```

## `tauri.conf.json` `externalBin` entry

```json
"bundle": {
  "externalBin": ["binaries/my-backend"]
}
```

The path is the **prefix** — Tauri resolves the correct triple suffix at build/runtime.

## Getting the current machine's triple

```bash
rustc -Vv | grep host
```

## GitHub Actions matrix mapping

| `runs-on`           | Triple                          |
|---------------------|---------------------------------|
| `ubuntu-latest`     | `x86_64-unknown-linux-gnu`      |
| `macos-latest`      | `aarch64-apple-darwin`          |
| `macos-13`          | `x86_64-apple-darwin`           |
| `windows-latest`    | `x86_64-pc-windows-msvc`        |
