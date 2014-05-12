import qipy.venv

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--setup", action="store_true", dest="setup")
    parser.add_argument("command", nargs="+")

    # Handle -c, -p, --release arguments:
    qisys.parsers.build_config(parser)
    build_worktree = qibuild.parsers.get_build_worktree(args)
    build_config = qibuild.parser.get_build_config(args)
    build_worktree.build_config = build_config
    config = build_config.active_config

    if args.setup:
        qipy.venv.setup_venv()

    run_from_venv(args.command)

if __name__ == "__main__":
    main()
