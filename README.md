Teacher-Assistant
=================
Usage:
- Install Dependency `pip install -r dependency.txt`
- Fix `sqlalchemy-migrate` bug, patch `site-packages/migrate/versioning/schema.py`. change `Line 10` into 
```python
from sqlalchemy import exc as sa_exceptions
```
- Build sqlite file by `python db_create.py`
- Run `python run.py`
- Visit `127.0.0.1:5000`

TA is compatable with Sina AppEngine.
