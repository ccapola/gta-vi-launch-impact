"""Pipeline errors. Every one of these stops the build; none is caught and papered over."""


class PipelineError(Exception):
    """Base class for all pipeline failures."""


class ParseError(PipelineError):
    """A value could not be parsed unambiguously."""


class MissingInputError(PipelineError):
    """A required input is absent from the dataset (or a field is empty)."""


class EvidenceError(PipelineError):
    """A figure's evidence quote is not found word for word in its evidence file."""


class FreezeError(PipelineError):
    """The frozen method is missing, already locked, or has been changed since the lock."""


class SanityError(PipelineError):
    """A model sanity check failed (claim reproduction, Super Bowl cap)."""
