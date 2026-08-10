# Ramone
Generator for ingestion en loading of datasources, before using dbt


# Keywords in yaml files

## "functions"

### globals 
assumes when the globals is used that it will be a string
also if using global() you have to use "" inbetween the +
you can also use it in a list like ["1", global("test1234"), "2"]