**qicomplete** is an introspective shell-completion script for the qi-suite of tools (qibuild, qisrc, qicd, etc.).

* Bash and Zsh support
* Dynamically parses the output of `--help` to adapt to actual commands
* Plugin system for ad-hoc completion of specific arguments, with rich plugin set (e.g. `qibuild deploy --url` completes hosts and deploys; `qisrc create` completes manifest URLs)

Bash Installation
=================

1. `sudo ln -s YOUR_WORKTREE/tools/qibuild/contrib/qicomplete/qi /etc/bash_completion.d`

	Note: files in the `/etc/bash_completion.d` directory are executed for completion scripts to hook into the completion system.

2. Restart your terminal or source your profile

Zsh Installation
================

1. Source the script in your `.zshrc.user` or `.zshrc`, e.g. add the following line:

		# Source qicomplete if present
		QICOMPLETE_ROOT="YOUR_WORKTREE/tools/qibuild/contrib/qicomplete"
		[ -f "$QICOMPLETE_ROOT/qi" ] && source "$QICOMPLETE_ROOT/qi"

2. Restart your terminal or source your profile

How it works
============

1. _Registration of the completion function_

	When your profile (typically .bashrc/.zshrc) is sourced at shell start, a line activates completion (`source /etc/bash_completion` in [bash][1], `autoload compinit && compinit` in [zsh][2]). During this activation, bash automatically executes scripts in some predefined directories — including `/etc/bash_completion.d` — which will get qicomplete executed and registered. With Zsh, the [bashcompinit][3] function must be autoloaded, so you need to source qicomplete manually, and this will also result in executing qicomplete.

	In both cases, qicomplete defines a completion function, `__qiComplete`, and registers it with the completion system by calling the shell's `complete` built-in function.

2. _Completion_

	When you hit tab, the shell's completion system looks up if the commmand you're calling has a registered completion function. If that's the case it calls this completion function (`__qiComplete` in our case) which returns possible completions, and interactively updates your command-line using those completions and according to your completion settings.

3. _Introspection_

	In order to find possible completions, `__qiComplete` extracts the root command (e.g. `qitoolchain`) in the command line being typed and completed (e.g. `qitoolchain create atom `), calls it with the `--help` option, and parses its output, determining what options are available, how many arguments they take, whether they're optionnal, and what subcommands are available.

	If there are subsequent words in the  the typed command is a subcommand that fits one found in the root command's help, it recursively calls the subcommand's `--help`, until it finds the (sub-)command actually being completed.

	This happens everytime you hit TAB, and the parsed model is used to generate appropriate completions.

4. _Plugin system_

	Named arguments in the `--help` are semantically opaque, so by default qicomplete will account (consider if it's mandatory or not, etc.) for any value you type but not complete it.

	To add completions for named arguments (e.g. `TOOLCHAIN_FEED` in `qitoolchain create NAME [TOOLCHAIN_FEED]`), qicomplete looks up an associative array in the environment called `__QICOMPLETE_PLUGINS`, searching for decreasingly specific keys made of the concatenation of the command name and the argument name (e.g. the `qitoolchain create TOOLCHAIN_FEED`), recursively looking up the argument name in the parent command if not found.

	For example, lookup for a `TOOLCHAIN_FEED` argument in the `qitoolchain create` sub-command will lookup:
	* `__QICOMPLETE_PLUGINS[qitoolchain create TOOLCHAIN_FEED]`
	* `__QICOMPLETE_PLUGINS[qitoolchain TOOLCHAIN_FEED]`
	* `__QICOMPLETE_PLUGINS[TOOLCHAIN_FEED]`

	If a completion plugin is found (e.g. `__QICOMPLETE_PLUGINS[TOOLCHAIN_FEED]="qitoolchain list | grep -Po "(?<=^\* ).+" | xargs"`), it is evaluated and it's stdout output used as a list of completion candidates.

Requirements
============

Bash v4.2+ or Zsh v5.0.2+.

[1]: https://www.gnu.org/software/bash/manual/html_node/Programmable-Completion.html "Bash Programmable Completion page"
[2]: http://zsh.sourceforge.net/Doc/Release/Completion-System.html "Zsh Completion System page"
[3]: http://zsh.sourceforge.net/Doc/Release/Completion-System.html#Use-of-compinit "Zsh compinit/bashcompinit"
