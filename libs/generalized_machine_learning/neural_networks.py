from enum import Enum
from typing import List
from pandas import DataFrame
from sklearn.neural_network import MLPRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score
from sklearn.preprocessing import StandardScaler


class ActivationFunction(Enum):
    LOGISTIC = 'logistic'       # sigmoid function
    IDENTITY = 'identity'       # no-op
    TANH = 'tanh'               # hyperbolic tan function
    RELU = 'relu'               # rectified linear unit function


class Solver(Enum):
    LBFGS = 'lbfgs'             # Optimizer of quasi-Netwon method family
    SGD = 'sgd'                 # Stochastic gradient descent
    ADAM = 'adam'               # Stochastic gradient-based optimizer


def create_regression_neural_network(data: DataFrame, output_cols: List[str],
                                     drop_cols: List[str] = None,
                                     scale_data: bool = True,
                                     activation_function: ActivationFunction = ActivationFunction.RELU,
                                     solver: Solver = Solver.ADAM,
                                     test_size: float = 0.2,
                                     mini_match_size='auto',
                                     hidden_layer_sizes=(100,)
                                     ):
    # Remove data columns that are not of interest

    if drop_cols is not None:
        data = data.drop(columns=drop_cols)

    # Divide data into input data and output data
    input_set = data.drop(columns=output_cols)
    output_set = data[output_cols]

    x_train, x_test, y_train, y_test = train_test_split(input_set, output_set, test_size=test_size)

    # Scale data
    if scale_data is True:
        scaler = StandardScaler()
        scaler.fit(x_train)
        x_train = scaler.transform(x_train)
        x_test = scaler.transform(x_test)

    # Activation functions: identity, logistic, rely, softmax, tanh
    # Solvers: sgd (stochastic gradiant decent), lbfgs, adam
    model = MLPRegressor(activation=activation_function.value,
                         solver=solver.value,
                         batch_size=mini_match_size,
                         hidden_layer_sizes=hidden_layer_sizes)
    model.fit(x_train, y_train)
    predictions = model.predict(x_test)
    score = r2_score(y_test, predictions, multioutput='raw_values')
    print(score)


def create_classification_neural_network():
    pass