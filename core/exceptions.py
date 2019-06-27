class CommandErrorHandled(Exception):
	"""Raise this when command errored but handled internally. Thus the command completion log will not run."""
	def __init__(self):
		description = "Command error handled internally."
		super().__init__(description)