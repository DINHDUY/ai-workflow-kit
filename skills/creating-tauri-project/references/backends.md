# Backend Templates

## Python / FastAPI

### `backend/src/main.py`
```python
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="<ProjectName> Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["tauri://localhost", "http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/api/hello")
def hello():
    return {"message": "Hello from Python backend!"}

if __name__ == "__main__":
    # Tauri will spawn this as a sidecar on a fixed port
    uvicorn.run(app, host="127.0.0.1", port=8000)
```

### `backend/requirements.txt`
```
fastapi>=0.110.0
uvicorn[standard]>=0.29.0
```

### Build command (in root `package.json`)
```json
"build:backend": "cd backend && pyinstaller --onefile --name <backend-name> src/main.py --distpath ../src-tauri/binaries"
```

### `backend/backend.spec` (optional PyInstaller spec)
```python
# -*- mode: python -*-
a = Analysis(['src/main.py'], ...)
```

---

## .NET (ASP.NET Core Minimal API)

### `backend/src/Program.cs`
```csharp
var builder = WebApplication.CreateBuilder(args);
builder.Services.AddCors(options => {
    options.AddDefaultPolicy(policy => {
        policy.WithOrigins("tauri://localhost", "http://localhost:5173")
              .AllowAnyHeader().AllowAnyMethod();
    });
});

var app = builder.Build();
app.UseCors();

app.MapGet("/health", () => new { status = "ok" });
app.MapGet("/api/hello", () => new { message = "Hello from .NET backend!" });

app.Run("http://127.0.0.1:8000");
```

### `backend/<ProjectName>.csproj`
```xml
<Project Sdk="Microsoft.NET.Sdk.Web">
  <PropertyGroup>
    <OutputType>Exe</OutputType>
    <TargetFramework>net8.0</TargetFramework>
    <Nullable>enable</Nullable>
    <ImplicitUsings>enable</ImplicitUsings>
    <PublishSingleFile>true</PublishSingleFile>
    <SelfContained>true</SelfContained>
  </PropertyGroup>
</Project>
```

### Build commands (per platform, in CI)
```bash
# Windows x64
dotnet publish -c Release -r win-x64 -o src-tauri/binaries/

# macOS ARM
dotnet publish -c Release -r osx-arm64 -o src-tauri/binaries/

# Linux x64
dotnet publish -c Release -r linux-x64 -o src-tauri/binaries/
```

---

## Go

### `backend/src/main.go`
```go
package main

import (
    "encoding/json"
    "net/http"
)

func main() {
    mux := http.NewServeMux()
    mux.HandleFunc("/health", func(w http.ResponseWriter, r *http.Request) {
        w.Header().Set("Content-Type", "application/json")
        json.NewEncoder(w).Encode(map[string]string{"status": "ok"})
    })
    mux.HandleFunc("/api/hello", func(w http.ResponseWriter, r *http.Request) {
        w.Header().Set("Content-Type", "application/json")
        json.NewEncoder(w).Encode(map[string]string{"message": "Hello from Go backend!"})
    })
    http.ListenAndServe("127.0.0.1:8000", mux)
}
```

### `backend/go.mod`
```
module github.com/<author>/<project-name>/backend

go 1.22
```

### Build commands
```bash
# From repo root (adjust GOOS/GOARCH per platform)
GOOS=windows GOARCH=amd64 go build -o src-tauri/binaries/<n>-x86_64-pc-windows-msvc.exe ./backend/src
GOOS=darwin  GOARCH=arm64 go build -o src-tauri/binaries/<n>-aarch64-apple-darwin          ./backend/src
GOOS=linux   GOARCH=amd64 go build -o src-tauri/binaries/<n>-x86_64-unknown-linux-gnu      ./backend/src
```
