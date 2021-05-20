from typing import List
from pandas import DataFrame
from sklearn.linear_model import Ridge
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score
from sklearn.preprocessing import PolynomialFeatures


def create_response_surface(data: DataFrame, output_cols: List[str],
                            drop_cols: List[str] = None,
                            degree: int = 2,
                            test_size: float = 0.20,
                            alpha: float = 0.5
                            ) -> (List[float], List[str], List[float]):
    """
    Creates a response surface
    :param data:
    :param output_cols:
    :param drop_cols:
    :param degree:
    :param test_size:
    :param alpha:
    :return: coefficients, factors, test results
    """
    # Remove data columns that are not of interest
    if drop_cols is not None:
        data = data.drop(columns=drop_cols)

    # Divide data into input data and output data
    input_set = data.drop(columns=output_cols)
    output_set = data[output_cols]

    # Create polynomial by multiplying factors to desired degree
    poly = PolynomialFeatures(degree=degree)
    polynomial_input_set = poly.fit_transform(input_set)

    # Split data into training batch, and test batch at random.
    x_train, x_test, y_train, y_test = train_test_split(polynomial_input_set, output_set, test_size=test_size)

    # Create the model using ridge method (a slightly fancier alternative to least squares)
    model = Ridge(alpha=alpha)
    model.fit(x_train, y_train)

    # Run the test data through the model, and score the models ability to predict the outcome
    predictions = model.predict(x_test)
    score = r2_score(y_test, predictions, multioutput='raw_values')
    return model.coef_, poly.get_feature_names(input_set.columns), score
