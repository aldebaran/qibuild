def setup_venv(build_worktree, python_worktree, config="system"):
    venv_root = create_environment(build_worktree, config=config)
    install_projects(venv_root, build_worktree, python_worktree)


def install_projects(venv_root, build_worktree, python_worktree,
                     python_version="2.7")
