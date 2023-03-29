from sedbackend.apps.cvs.simulation.storage import parse_formula
from sedbackend.libs.parsing.expressions import get_prefix_names, replace_prefix_names
from sedbackend.libs.parsing.parser import NumericStringParser


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
    vd_values = [{"id": 1, "name": "Speed", "value": 3}, {"id": 2, "name": "Weight", "value": 4}]
    mi_values = [{"id": 1, "name": "Test", "value": 5}, {"id": 2, "name": "Test2", "value": 6}]
    formula = f'2*"VD(Speed [km/h])"+"EF(Test2 [T2])"'
    nsp = NumericStringParser()

    # Act
    new_formula = parse_formula(formula, vd_values, mi_values)

    # Assert
    assert new_formula == "2*3+6"
    assert nsp.eval(new_formula) == 12


def test_get_prefix_names():
    # Setup
    text_vd = f'2*"VD(Speed [km/h])"+"VD(Test [T])"'
    text_mi = f'2*"EF(Test [T])"+"EF(Test2 [T2])"'

    # Act
    names_vd = get_prefix_names("VD", text_vd)
    names_mi = get_prefix_names("EF", text_mi)

    # Assert
    assert names_vd == ["Speed", "Test"]
    assert names_mi == ["Test", "Test2"]


def test_replace_prefix_names():
    # Setup
    text_vd = f'2*"VD(Speed [km/h])"+"VD(Test [T])"'
    text_mi = f'2*"EF(Test [T])"+"EF(Test2 [T2])"'

    # Act
    new_text_vd = replace_prefix_names("VD", "Speed", "2", text_vd)
    new_text_mi = replace_prefix_names("EF", "Test", "4", text_mi)

    # Assert
    assert new_text_vd == f'2*2+"VD(Test [T])"'
    assert new_text_mi == f'2*4+"EF(Test2 [T2])"'
