#!/bin/sh
python -c "from pathlib import Path; required=['docs/specification.md','docs/architecture.md','docs/domain.md','docs/diagrams/context.mmd','docs/diagrams/order-sequence.mmd']; missing=[p for p in required if not Path(p).exists()]; assert not missing, missing; print('docs ok')"
