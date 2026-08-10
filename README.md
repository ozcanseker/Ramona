# Ramona
Generator and model validator for models based in yaml files.

<img src="docs/images/scaled.png" width="192" height="220" style="image-rendering: pixelated;">

# Keywords in yaml files

## "functions"

### globals 
assumes when the globals is used that it will be a string
also if using global() you have to use "" inbetween the +
you can also use it in a list like ["1", global("test1234"), "2"]


to get started:
pip install -e .