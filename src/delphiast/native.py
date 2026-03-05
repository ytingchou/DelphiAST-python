from __future__ import annotations

from dataclasses import dataclass
import os
import platform
from pathlib import Path
import subprocess


@dataclass
class NativeParserSyntaxErrorInfo:
    line: int
    col: int
    file_name: str
    message: str


class NativeParserBuildError(RuntimeError):
    pass


class NativeParserExecutionError(RuntimeError):
    pass


class NativeParserSyntaxError(RuntimeError):
    def __init__(self, info: NativeParserSyntaxErrorInfo):
        super().__init__(info.message)
        self.info = info


_REPO_ROOT = Path(__file__).resolve().parents[2]
_PACKAGE_ROOT = Path(__file__).resolve().parent
_VENDOR_ROOT = _PACKAGE_ROOT / "_vendor"
_SOURCE_ROOT = _VENDOR_ROOT / "Source"
_BUILD_DIR = Path(
    os.environ.get("DELPHIAST_BUILD_DIR", str(Path.home() / ".cache" / "delphiast" / "native_build"))
)
_TOOL_SOURCE = _VENDOR_ROOT / "tools" / "pascal_bridge" / "delphiast_parse_to_xml.lpr"
_TOOL_BINARY = _BUILD_DIR / "delphiast_parse_to_xml"
_ALLOW_FPC_BUILD = os.environ.get("DELPHIAST_ALLOW_FPC_BUILD", "0") == "1"


def _platform_dir_name() -> str:
    system = platform.system().lower()
    machine = platform.machine().lower()
    if machine in {"amd64", "x64"}:
        machine = "x86_64"
    return f"{system}-{machine}"


def _packaged_binary() -> Path:
    name = "delphiast_parse_to_xml.exe" if os.name == "nt" else "delphiast_parse_to_xml"
    return _VENDOR_ROOT / "bin" / _platform_dir_name() / name


def _fpc_command() -> list[str]:
    root = str(_SOURCE_ROOT)
    return [
        "fpc",
        "-Mdelphi",
        f"-Fu{root}",
        f"-Fu{root}/SimpleParser",
        f"-Fu{root}/FreePascalSupport",
        f"-Fu{root}/FreePascalSupport/FPC_StringBuilder/Src",
        f"-Fi{root}/SimpleParser",
        f"-FE{_BUILD_DIR}",
        f"-FU{_BUILD_DIR}",
        str(_TOOL_SOURCE),
    ]


def ensure_parser_binary() -> Path:
    packaged = _packaged_binary()
    if packaged.exists():
        # The wheel can ship a non-executable bit depending on build environment.
        packaged.chmod(packaged.stat().st_mode | 0o111)
        return packaged

    if not _ALLOW_FPC_BUILD:
        raise NativeParserBuildError(
            "No bundled native parser for this platform and fallback build is disabled. "
            "Set DELPHIAST_ALLOW_FPC_BUILD=1 to enable FPC compilation fallback."
        )

    _BUILD_DIR.mkdir(parents=True, exist_ok=True)
    if not _SOURCE_ROOT.exists():
        raise NativeParserBuildError(
            f"Missing bundled Delphi source at '{_SOURCE_ROOT}'. "
            "Reinstall the package with full data files."
        )

    source_mtime = _TOOL_SOURCE.stat().st_mtime
    parser_mtime = (_SOURCE_ROOT / "SimpleParser" / "SimpleParser.pas").stat().st_mtime
    if _TOOL_BINARY.exists() and _TOOL_BINARY.stat().st_mtime >= max(source_mtime, parser_mtime):
        return _TOOL_BINARY

    proc = subprocess.run(
        _fpc_command(),
        cwd=_REPO_ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    if proc.returncode != 0:
        raise NativeParserBuildError(
            "Failed to build native parser helper.\n"
            f"stdout:\n{proc.stdout}\n"
            f"stderr:\n{proc.stderr}"
        )
    if not _TOOL_BINARY.exists():
        raise NativeParserBuildError("Native parser helper compiled but binary was not found.")
    return _TOOL_BINARY


def run_parser_to_xml(file_name: str | Path, interface_only: bool = False) -> str:
    binary = ensure_parser_binary()
    args = [str(binary), str(Path(file_name).resolve())]
    if interface_only:
        args.append("--interface-only")

    proc = subprocess.run(
        args,
        cwd=_REPO_ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )

    if proc.returncode == 0:
        return proc.stdout

    stderr = (proc.stderr or "").strip()
    if stderr.startswith("SYNTAX_ERROR|"):
        parts = stderr.split("|", 4)
        line = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else 0
        col = int(parts[2]) if len(parts) > 2 and parts[2].isdigit() else 0
        file_name_out = parts[3] if len(parts) > 3 else ""
        message = parts[4] if len(parts) > 4 else "Syntax error"
        raise NativeParserSyntaxError(NativeParserSyntaxErrorInfo(line, col, file_name_out, message))

    raise NativeParserExecutionError(
        f"Native parser failed (exit {proc.returncode}). stderr: {stderr or '<empty>'}"
    )
