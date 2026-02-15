import inspect
from deepeval import evaluate as deepeval_evaluate
print("evaluate() params =", list(inspect.signature(deepeval_evaluate).parameters.keys()))
