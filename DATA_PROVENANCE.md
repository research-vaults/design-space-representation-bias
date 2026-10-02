# Data provenance and release boundaries

## Protein-policy records

`data/sampled_choices/` and `data/confirmatory_choices/` contain study-generated
selection identifiers, probability distributions, written menus, behavioural-class
mappings and aggregate execution utilities. These are numerical experimental
records, not patient records, protein sequences or copies of the underlying fitness
tables. Null records are retained; unsuccessful calls are not silently dropped.

Utilities were constructed from public SSMuLA fitness landscapes. Obtain upstream
tables independently from https://doi.org/10.5281/zenodo.13910506 and follow that
release's license and citation instructions. Those tables are not redistributed
here. Replaying cached utilities does not independently validate their construction
from raw fitness measurements.

Model names and recorded revision identifiers are experimental provenance. Model
weights, tokenizer files, provider software, credentials and billing records are
not included. Provider-derived numerical outputs are used for analysis; this
package does not relicense third-party models or provider services. Outputs are
fixed-choice records rather than personal conversations or copyrighted passages.

## Knapsack records

`data/knapsack_transport/` contains study-generated synthetic instances, menus,
class mappings, measured utilities, and model-choice distributions. The bundled
executor recomputes policy signatures and validates the transport measurements.
It does not invoke an external optimization service.

## Additional default-duplication measurements

`data/default_duplication/` retains 168 historical dose contrasts and 84 newer
constrained-choice distributions with model revisions and prompt hashes. The
local task descriptions refer to three AutoML datasets; their raw input rows are
not redistributed. The derived records preserve failed criteria as well as
descriptive fits. Read the adjacent README before interpreting these records.

## Licensing and scope

The original software's MIT license is preserved without removing its attribution.
No third-party source trees or template files are bundled. Upstream dataset and
model terms remain separate. The release gives numerical replay access, not a
license to redistribute unbundled upstream material or a claim that every original
experiment can be rerun without obtaining its dependencies.
