# parametrized pony db instantiation

* Tests to parametrize pony definition
* Tests to map a subset of tables
* Tests to reuse entities without defining all foreign entities

# run

classical `pip install -r requirements.txt`
copy and modify `config.py`
create database and user

run tests with `pytest` for example

# discoveries

Drop all tables only drops the tables associated to that mapping

Entities can be reused but not accros different definition functions since
the inner class location differs