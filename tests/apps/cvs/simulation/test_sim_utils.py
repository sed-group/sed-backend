from sedbackend.apps.cvs.simulation.storage import parse_formula
from sedbackend.libs.formula_parser.parser import NumericStringParser


def test_parse_formula_simple():
    # Setup
    formula = f'(3+1)/2'
    vd_values = []
    mi_values = []
    nsp = NumericStringParser()

    # Act
    new_formula = parse_formula(formula, vd_values, mi_values)

    # Assert
    assert new_formula == formula
    assert nsp.eval(new_formula) == 2


def test_parse_formula_values():
    # Setup
    vd_values = [{"id": 47241, "name": "Speed", "unit": "0-1", "value": 10}]
    mi_values = [{"id": 114, "name": "Fuel Cost", "unit": "k€/liter", "value": 5}]
    formula = '2+{vd:47241,"Design Similarity [0-1]"}/{ef:114,"Fuel Cost [k€/liter]"}'
    nsp = NumericStringParser()

    # Act
    new_formula = parse_formula(formula, vd_values, mi_values)

    # Assert
    assert new_formula == "2+10/5"
    assert nsp.eval(new_formula) == 4


def test_parse_formula_vd_no_exist():
    # Setup
    vd_values = [{"id": 47241, "name": "Speed", "unit": "0-1", "value": 10}]
    mi_values = [{"id": 114, "name": "Fuel Cost", "unit": "k€/liter", "value": 5}]
    formula = '2+{vd:1,"Design Similarity [0-1]"}/{ef:114,"Fuel Cost [k€/liter]"}'
    nsp = NumericStringParser()

    # Act
    new_formula = parse_formula(formula, vd_values, mi_values)

    # Assert
    assert new_formula == "2+0/5"
    assert nsp.eval(new_formula) == 2
