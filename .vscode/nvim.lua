local dap = require("dap")
dap.configurations.python = {
	{
		type = "python",
		request = "launch",
		name = "Launch bff test",
		program = "bff/test.py",
    cwd = "${workspaceFolder}",
		args = { "modules.dummy_module" },
		pythonPath = "${workspaceFolder}/.venv/bin/python",
	},
	{
		type = "python",
		request = "launch",
		name = "Launch file",
		program = "${file}",
		args = { "modules.dummy_module" },
	},
}
