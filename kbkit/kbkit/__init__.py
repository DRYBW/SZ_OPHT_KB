"""kbkit — a tissue knowledge-base construction kit.

Layers (see DESIGN §2):

  core        tissue-independent: schema, evidence discipline, ranking,
              aggregation, evaluation protocol, machine gates, service shell
  plugin      one directory per tissue, loaded via plugin.yaml
  data plane  NOT shipped (licences + size); the kit ships *how to build and
              how to check*, never the corpus itself

Single source of truth: the plugin skeleton, the templates and the CLI all
derive from the schema declared in this package.  Nothing is duplicated by hand.
"""

__version__ = "0.1.0"
SCHEMA_VERSION = "1.0"
