#!/bin/sh
python -c "from pathlib import Path; required=['docs/index.md','docs/specification.md','docs/architecture.md','docs/domain.md','docs/api/public-interface.md','docs/diagrams/context.mmd','docs/diagrams/order-sequence.mmd','docs/diagrams/use-cases.mmd']; missing=[p for p in required if not Path(p).exists()]; assert not missing, missing; print('docs ok')"
