import argparse
import logging
from pathlib import Path
import shutil
from subprocess import list2cmdline
import sys

log = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(description="Shim management tool")
    subparsers = parser.add_subparsers(dest="command", help="the command to execute")
    subparsers.required = True

    parent_parser = argparse.ArgumentParser(add_help=False)
    parent_parser.add_argument("-v", "--verbose", action="store_true", help="shows debug messages")

    add_parser = subparsers.add_parser(
        "add",
        description="Creates a new shim",
        help="creates a new shim",
        parents=[parent_parser],
    )
    add_parser.add_argument("name")
    add_parser.add_argument("path", type=Path)
    add_parser.add_argument("args", nargs=argparse.REMAINDER)
    add_parser.set_defaults(func=do_add)

    list_parser = subparsers.add_parser(
        "list",
        description="Lists the added shims",
        help="lists the added shims",
        parents=[parent_parser],
    )
    list_parser.set_defaults(func=do_list)

    show_parser = subparsers.add_parser(
        "show",
        description="Shows information about a shim",
        help="shows information about a shim",
        parents=[parent_parser],
    )
    show_parser.add_argument("name")
    show_parser.set_defaults(func=do_show)

    remove_parser = subparsers.add_parser(
        "remove", description="Removes a shim", help="deletes a shim", parents=[parent_parser]
    )
    remove_parser.add_argument("name")
    remove_parser.set_defaults(func=do_remove)

    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(levelname)-8s %(name)s %(message)s",
    )

    try:
        args.func(args)
    except Exception:
        log.exception("Unexpected error encountered.")
        sys.exit(2)


def do_add(args):
    log.debug("Checking that path exists")
    if not args.path.is_file():
        raise FileNotFoundError(f"File does not exist: {args.path.absolute()}")

    shim_source_path = Path(__file__).parent / "Shim.exe"

    shim_exec_path = SHIM_DIR / (args.name + ".exe")
    shim_data_path = SHIM_DIR / (args.name + ".shim")

    log.debug(f"Adding shim data file: {shim_data_path}")
    with shim_data_path.open("w") as f:
        print("path =", args.path.absolute(), file=f)
        print("args =", list2cmdline(args.args), file=f)

    log.debug(f"Copying shim executable to: {shim_exec_path}")
    shutil.copy(shim_source_path, shim_exec_path)


def do_list(args):
    for path in SHIM_DIR.glob("*.shim"):
        print(path.name[: -len(".shim")])


def do_show(args):
    shim_data_path = SHIM_DIR / (args.name + ".shim")
    if not shim_data_path.is_file():
        raise Exception(f"Unknown shim: {args.name}")
    print(shim_data_path.read_text())


def do_remove(args):
    shim_exec_path = SHIM_DIR / (args.name + ".exe")
    shim_data_path = SHIM_DIR / (args.name + ".shim")

    log.debug("Checking that files exist")
    if not shim_exec_path.is_file():
        raise Exception(f"Not found: {shim_exec_path}")
    if not shim_data_path.is_file():
        raise Exception(f"Not found: {shim_data_path}")

    log.debug(f"Removing executable: {shim_exec_path}")
    shim_exec_path.unlink()
    log.debug(f"Removing data file: {shim_data_path}")
    shim_data_path.unlink()


SHIM_DIR = Path(r"C:\CustomTools\Shortcuts")

if __name__ == "__main__":
    main()
