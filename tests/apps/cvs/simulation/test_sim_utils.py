from sedbackend.apps.cvs.simulation.storage import parse_formula
from sedbackend.libs.formula_parser.expressions import get_prefix_names, get_prefix_variables, \
    replace_prefix_variables
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
    vd_values = [{"id": 1, "name": "Speed", "unit": "km/h", "value": 3},
                 {"id": 2, "name": "Weight", "unit": "kg", "value": 4}]
    mi_values = [{"id": 1, "name": "Test", "unit": "T", "value": 5},
                 {"id": 2, "name": "Test 2", "unit": "T2", "value": 6}]
    formula = f'2*"VD(DontExist [km/h])"+"EF(Dont Exist [T2])"'
    nsp = NumericStringParser()

    # Act
    new_formula = parse_formula(formula, vd_values, mi_values)

    # Assert
    assert new_formula == "2*0+0"
    assert nsp.eval(new_formula) == 0


def test_parse_formula_unit_no_exist():
    # Setup
    vd_values = [{"id": 1, "name": "Speed", "unit": None, "value": 3}]
    mi_values = [{"id": 2, "name": "Test 2", "unit": None, "value": 6}]
    formula = f'2*"VD(Speed [N/A])"+"EF(Test 2 [N/A])"'
    nsp = NumericStringParser()

    # Act
    new_formula = parse_formula(formula, vd_values, mi_values)

    # Assert
    assert new_formula == "2*3+6"
    assert nsp.eval(new_formula) == 12


def test_get_prefix_variables():
    # Setup
    text_vd = f'2*"VD(Speed [km/h])"+"VD(Test [T])"'
    text_mi = f'2*"EF(Test (OK) [T])"+"EF(Test2 [T2])"'

    # Act
    variables_vd = get_prefix_variables("VD", text_vd)
    variables_mi = get_prefix_variables("EF", text_mi)

    # Assert
    assert variables_vd == ["Speed [km/h]", "Test [T]"]
    assert variables_mi == ["Test (OK) [T]", "Test2 [T2]"]


def test_get_prefix_names():
    # Setup
    text_vd = f'2*"VD(Speed King [L] [km/h])"+"VD(Test(L) */&¢€ [T])"'
    text_mi = f'2*"EF(Test (OK) [T])"+"EF(Test2 [T2])"'

    # Act
    names_vd = get_prefix_names("VD", text_vd)
    names_mi = get_prefix_names("EF", text_mi)

    # Assert
    assert names_vd == ["Speed King [L]", "Test(L) */&¢€"]
    assert names_mi == ["Test (OK)", "Test2"]


def test_replace_prefix_variables():
    # Setup
    text_vd = f'2*"VD(Speed [km/h])"+"VD(Test [T])"'
    text_mi = f'2*"EF(Test (OK) [T])"+"EF(Test2 [T2])"'

    # Act
    new_text_vd = replace_prefix_variables("VD", "Speed [km/h]", "2", text_vd)
    new_text_mi = replace_prefix_variables("EF", "Test (OK) [T]", "4", text_mi)

    # Assert
    assert new_text_vd == f'2*2+"VD(Test [T])"'
    assert new_text_mi == f'2*4+"EF(Test2 [T2])"'


def test_value_not_found():
    # Setup
    vd_values = [{"id": 1, "name": "Speed", "unit": "km/h", "value": 2}]
    mi_values = [{"id": 2, "name": "Test 2", "unit": "T", "value": 3}]
    formula = f'2*"VD(NO [km/h])"+"EF(NOTFOUND [T])"'
    nsp = NumericStringParser()

    # Act
    new_formula = parse_formula(formula, vd_values, mi_values)

    # Assert
    assert new_formula == "2*0+0"
    assert nsp.eval(new_formula) == 0

