from typing import List

from fastapi.logger import logger
from mysql.connector.pooling import PooledMySQLConnection
import re
from sedbackend.apps.cvs.design.storage import get_design_group
from sedbackend.apps.cvs.link_design_lifecycle.models import Rate, TimeFormat
from sedbackend.apps.cvs.market_input.storage import populate_external_factor
from sedbackend.apps.cvs.vcs import storage as vcs_storage
from sedbackend.apps.cvs.link_design_lifecycle import models, exceptions
from mysqlsb import FetchType, MySQLStatementBuilder

CVS_FORMULAS_TABLE = "cvs_design_mi_formulas"
CVS_FORMULAS_COLUMNS = [
    "project",
    "vcs_row",
    "design_group",
    "time",
    "time_latex",
    "time_comment",
    "time_unit",
    "cost",
    "cost_latex",
    "cost_comment",
    "revenue",
    "revenue_latex",
    "revenue_comment",
    "rate",
]

CVS_VALUE_DRIVERS_TABLE = "cvs_value_drivers"
CVS_VALUE_DRIVERS_COLUMNS = ["id", "user", "name", "unit"]

CVS_FORMULAS_VALUE_DRIVERS_TABLE = "cvs_formulas_value_drivers"
CVS_FORMULAS_VALUE_DRIVERS_COLUMNS = [
    "vcs_row",
    "design_group",
    "value_driver",
    "project",
]

CVS_FORMULAS_EXTERNAL_FACTORS_TABLE = "cvs_formulas_external_factors"
CVS_FORMULAS_EXTERNAL_FACTORS_COLUMNS = ["vcs_row", "design_group", "external_factor"]

CVS_EXTERNAL_FACTORS_TABLE = "cvs_market_inputs"
CVS_EXTERNAL_FACTORS_COLUMNS = ["id", "name", "unit"]
CVS_STAKEHOLDER_NEEDS_TABLE = "cvs_stakeholder_needs"
CVS_VCS_ROWS_TABLE = "cvs_vcs_rows"
CVS_VCS_NEED_DRIVERS_TABLE = "cvs_vcs_need_drivers"


def create_formulas(
    db_connection: PooledMySQLConnection,
    project_id: int,
    vcs_row_id: int,
    design_group_id: int,
    formula_row: models.FormulaRowPost,
):
    logger.debug(f"Creating formulas")

    value_driver_ids, external_factor_ids = find_vd_and_ef(
        [
            formula_row.time.text,
            formula_row.cost.text,
            formula_row.revenue.text,
        ]
    )

    values = [
        project_id,
        vcs_row_id,
        design_group_id,
        formula_row.time.text,
        formula_row.time.latex,
        formula_row.time.comment,
        formula_row.time_unit.value,
        formula_row.cost.text,
        formula_row.cost.latex,
        formula_row.cost.comment,
        formula_row.revenue.text,
        formula_row.revenue.latex,
        formula_row.revenue.comment,
        formula_row.rate.value,
    ]

    try:
        insert_statement = MySQLStatementBuilder(db_connection)
        insert_statement.insert(
            table=CVS_FORMULAS_TABLE, columns=CVS_FORMULAS_COLUMNS
        ).set_values(values=values).execute(fetch_type=FetchType.FETCH_NONE)
    except Exception as e:
        logger.error(f"Error while inserting formulas: {e}")
        raise exceptions.FormulasFailedUpdateException

    if value_driver_ids:
        add_value_driver_formulas(
            db_connection, vcs_row_id, design_group_id, value_driver_ids, project_id
        )
    if external_factor_ids:
        add_external_factor_formulas(
            db_connection, vcs_row_id, design_group_id, external_factor_ids
        )


def find_vd_and_ef(texts: List[str]) -> (List[str], List[int]):
    value_driver_ids = []
    external_factor_ids = []

    pattern = r'\{(?P<tag>vd|ef):(?P<id>\d+),"([^"]+)"\}'

    for text in texts:
        matches = re.findall(pattern, text)
        for tag, id_number, _ in matches:
            if tag == "vd":
                value_driver_ids.append(int(id_number))
            elif tag == "ef":
                external_factor_ids.append(int(id_number))

    return value_driver_ids, external_factor_ids


def edit_formulas(
    db_connection: PooledMySQLConnection,
    project_id: int,
    vcs_row_id: int,
    design_group_id: int,
    formula_row: models.FormulaRowPost,
):
    logger.debug(f"Editing formulas")

    value_driver_ids, external_factor_ids = find_vd_and_ef(
        [
            formula_row.time.text,
            formula_row.cost.text,
            formula_row.revenue.text,
        ]
    )

    columns = CVS_FORMULAS_COLUMNS[3:]
    set_statement = ", ".join([col + " = %s" for col in columns])

    values = [
        formula_row.time.text,
        formula_row.time.latex,
        formula_row.time.comment,
        formula_row.time_unit.value,
        formula_row.cost.text,
        formula_row.cost.latex,
        formula_row.cost.comment,
        formula_row.revenue.text,
        formula_row.revenue.latex,
        formula_row.revenue.comment,
        formula_row.rate.value,
    ]

    # Update formula row
    update_statement = MySQLStatementBuilder(db_connection)
    _, _ = (
        update_statement.update(
            table=CVS_FORMULAS_TABLE, set_statement=set_statement, values=values
        )
        .where("vcs_row = %s and design_group = %s", [vcs_row_id, design_group_id])
        .execute(return_affected_rows=True)
    )

    update_value_driver_formulas(
        db_connection, vcs_row_id, design_group_id, value_driver_ids, project_id
    )

    update_external_factor_formulas(
        db_connection, vcs_row_id, design_group_id, external_factor_ids
    )


def add_value_driver_formulas(
    db_connection: PooledMySQLConnection,
    vcs_row_id: int,
    design_group_id: int,
    value_drivers: List[int],
    project_id: int,
):
    # Add value driver to formulas
    try:
        prepared_list = []
        insert_statement = f"INSERT INTO {CVS_FORMULAS_VALUE_DRIVERS_TABLE} (vcs_row, design_group, value_driver, project) VALUES"
        for value_driver_id in value_drivers:
            insert_statement += f"(%s, %s, %s, %s),"
            prepared_list += [vcs_row_id, design_group_id, value_driver_id, project_id]
        insert_statement = insert_statement[:-1]
        insert_statement += (
            " ON DUPLICATE KEY UPDATE vcs_row = vcs_row"  # On duplicate do nothing
        )
        with db_connection.cursor(prepared=True) as cursor:
            cursor.execute(insert_statement, prepared_list)
    except Exception as e:
        logger.error(f"Error while inserting value drivers: {e}")
        raise exceptions.FormulasFailedUpdateException


def delete_value_driver_formulas(
    db_connection: PooledMySQLConnection,
    vcs_row_id: int,
    design_group_id: int,
    value_drivers: List[int],
):
    delete_statement = MySQLStatementBuilder(db_connection)
    _, rows = (
        delete_statement.delete(CVS_FORMULAS_VALUE_DRIVERS_TABLE)
        .where(
            f'vcs_row = %s and design_group = %s and value_driver in ({",".join(["%s" for _ in range(len(value_drivers))])})',
            [vcs_row_id, design_group_id] + value_drivers,
        )
        .execute(return_affected_rows=True)
    )


def update_value_driver_formulas(
    db_connection: PooledMySQLConnection,
    vcs_row_id: int,
    design_group_id: int,
    value_drivers: List[int],
    project_id: int,
):
    where_statement = "vcs_row = %s and design_group = %s"
    select_statement = MySQLStatementBuilder(db_connection)
    value_driver_res = (
        select_statement.select(
            CVS_FORMULAS_VALUE_DRIVERS_TABLE, CVS_FORMULAS_VALUE_DRIVERS_COLUMNS
        )
        .where(where_statement, [vcs_row_id, design_group_id])
        .execute(fetch_type=FetchType.FETCH_ALL, dictionary=True)
    )

    delete_value_drivers = [
        value_driver["value_driver"]
        for value_driver in value_driver_res
        if value_driver["value_driver"] not in value_drivers
    ]
    add_value_drivers = [
        value_driver_id
        for value_driver_id in value_drivers
        if value_driver_id
        not in [value_driver["value_driver"] for value_driver in value_driver_res]
    ]

    if len(add_value_drivers):
        add_value_driver_formulas(
            db_connection, vcs_row_id, design_group_id, add_value_drivers, project_id
        )
    if len(delete_value_drivers):
        delete_value_driver_formulas(
            db_connection, vcs_row_id, design_group_id, delete_value_drivers
        )


def add_external_factor_formulas(
    db_connection: PooledMySQLConnection,
    vcs_row_id: int,
    design_group_id: int,
    external_factors: List[int],
):
    try:
        prepared_list = []
        insert_statement = f"INSERT INTO {CVS_FORMULAS_EXTERNAL_FACTORS_TABLE} (vcs_row, design_group, external_factor) VALUES"
        for external_factor_id in external_factors:
            insert_statement += f"(%s, %s, %s),"
            prepared_list += [vcs_row_id, design_group_id, external_factor_id]
        insert_statement = insert_statement[:-1]
        insert_statement += (
            " ON DUPLICATE KEY UPDATE vcs_row = vcs_row"  # On duplicate do nothing
        )
        with db_connection.cursor(prepared=True) as cursor:
            cursor.execute(insert_statement, prepared_list)
    except Exception as e:
        logger.error(f"Error while inserting external factors: {e}")
        raise exceptions.FormulasFailedUpdateException


def delete_external_factor_formulas(
    db_connection: PooledMySQLConnection,
    vcs_row_id: int,
    design_group_id: int,
    external_factors: List[int],
):
    delete_statement = MySQLStatementBuilder(db_connection)
    _, _ = (
        delete_statement.delete(CVS_FORMULAS_EXTERNAL_FACTORS_TABLE)
        .where(
            f'vcs_row = %s and design_group = %s and external_factor in ({",".join(["%s" for _ in range(len(external_factors))])})',
            [vcs_row_id, design_group_id] + external_factors,
        )
        .execute(return_affected_rows=True)
    )


def update_external_factor_formulas(
    db_connection: PooledMySQLConnection,
    vcs_row_id: int,
    design_group_id: int,
    external_factors: List[int],
):
    where_statement = "vcs_row = %s and design_group = %s"
    select_statement = MySQLStatementBuilder(db_connection)
    external_factor_res = (
        select_statement.select(
            CVS_FORMULAS_EXTERNAL_FACTORS_TABLE, CVS_FORMULAS_EXTERNAL_FACTORS_COLUMNS
        )
        .where(where_statement, [vcs_row_id, design_group_id])
        .execute(fetch_type=FetchType.FETCH_ALL, dictionary=True)
    )

    delete_external_factors = [
        external_factor["external_factor"]
        for external_factor in external_factor_res
        if external_factor["external_factor"] not in external_factors
    ]
    add_external_factors = [
        external_factor_id
        for external_factor_id in external_factors
        if external_factor_id
        not in [
            external_factor["external_factor"]
            for external_factor in external_factor_res
        ]
    ]

    if len(add_external_factors):
        add_external_factor_formulas(
            db_connection, vcs_row_id, design_group_id, add_external_factors
        )
    if len(delete_external_factors):
        delete_external_factor_formulas(
            db_connection, vcs_row_id, design_group_id, delete_external_factors
        )


def update_formulas(
    db_connection: PooledMySQLConnection,
    project_id: int,
    vcs_id: int,
    design_group_id: int,
    formula_rows: List[models.FormulaRowPost],
) -> bool:
    vcs_storage.check_vcs(
        db_connection, project_id, vcs_id
    )  # Check if vcs exists and matches project
    get_design_group(
        db_connection, project_id, design_group_id
    )  # Check if design group exists and matches project

    for formula_row in formula_rows:
        vcs_storage.get_vcs_row(
            db_connection, project_id, formula_row.vcs_row_id
        )  # Check if vcs row exists

        count_statement = MySQLStatementBuilder(db_connection)
        count = (
            count_statement.count(CVS_FORMULAS_TABLE)
            .where(
                "vcs_row = %s and design_group = %s",
                [formula_row.vcs_row_id, design_group_id],
            )
            .execute(fetch_type=FetchType.FETCH_ONE, dictionary=True)
        )
        count = count["count"]

        if count == 0:
            create_formulas(
                db_connection,
                project_id,
                formula_row.vcs_row_id,
                design_group_id,
                formula_row,
            )
        elif count == 1:
            edit_formulas(
                db_connection,
                project_id,
                formula_row.vcs_row_id,
                design_group_id,
                formula_row,
            )
        else:
            raise exceptions.FormulasFailedUpdateException

    return True


def get_all_formulas(
    db_connection: PooledMySQLConnection,
    project_id: int,
    vcs_id: int,
    design_group_id: int,
) -> List[models.FormulaRowGet]:
    logger.debug(f"Fetching all formulas with vcs_id={vcs_id}")

    get_design_group(
        db_connection, project_id, design_group_id
    )  # Check if design group exists and matches project
    vcs_rows = vcs_storage.get_vcs_table(
        db_connection, project_id, vcs_id
    )  # Check if vcs exists and matches project

    select_statement = MySQLStatementBuilder(db_connection)
    res = (
        select_statement.select(CVS_FORMULAS_TABLE, CVS_FORMULAS_COLUMNS)
        .inner_join("cvs_vcs_rows", "vcs_row = cvs_vcs_rows.id")
        .where("vcs = %s and design_group = %s", [vcs_id, design_group_id])
        .execute(fetch_type=FetchType.FETCH_ALL, dictionary=True)
    )

    if res is None:
        raise exceptions.FormulasNotFoundException

    all_used_vds, all_used_efs, all_row_vds = [], [], []

    if len(res):
        where_statement = (
            "(vcs_row, design_group) IN ("
            + ",".join(["(%s, %s)" for _ in range(len(res))])
            + ")"
        )
        prepared_list = []
        for r in res:
            prepared_list += [r["vcs_row"], r["design_group"]]

        with db_connection.cursor(prepared=True) as cursor:
            cursor.execute(
                f"SELECT id, name, unit, {CVS_VALUE_DRIVERS_TABLE}.project, vcs_row, design_group FROM {CVS_FORMULAS_VALUE_DRIVERS_TABLE} "
                f"INNER JOIN {CVS_VALUE_DRIVERS_TABLE} ON {CVS_FORMULAS_VALUE_DRIVERS_TABLE}.value_driver = cvs_value_drivers.id WHERE {where_statement}",
                prepared_list,
            )
            all_used_vds = [
                dict(zip(cursor.column_names, row)) for row in cursor.fetchall()
            ]

        with db_connection.cursor(prepared=True) as cursor:
            cursor.execute(
                f"SELECT id, name, unit, vcs_row, design_group FROM {CVS_FORMULAS_EXTERNAL_FACTORS_TABLE} "
                f"INNER JOIN {CVS_EXTERNAL_FACTORS_TABLE} ON {CVS_FORMULAS_EXTERNAL_FACTORS_TABLE}.external_factor = cvs_market_inputs.id WHERE {where_statement}",
                prepared_list,
            )
            all_used_efs = [
                dict(zip(cursor.column_names, row)) for row in cursor.fetchall()
            ]

    if vcs_rows:
        with db_connection.cursor(prepared=True) as cursor:
            logger.debug(f"Running")
            cursor.execute(
                f"SELECT {CVS_VALUE_DRIVERS_TABLE}.id, {CVS_VALUE_DRIVERS_TABLE}.name, {CVS_VALUE_DRIVERS_TABLE}.unit, {CVS_VALUE_DRIVERS_TABLE}.project, {CVS_VCS_ROWS_TABLE}.id AS vcs_row FROM {CVS_VCS_ROWS_TABLE} "
                f"INNER JOIN {CVS_STAKEHOLDER_NEEDS_TABLE} ON {CVS_STAKEHOLDER_NEEDS_TABLE}.vcs_row = {CVS_VCS_ROWS_TABLE}.id "
                f"INNER JOIN {CVS_VCS_NEED_DRIVERS_TABLE} ON {CVS_VCS_NEED_DRIVERS_TABLE}.stakeholder_need = {CVS_STAKEHOLDER_NEEDS_TABLE}.id "
                f"INNER JOIN {CVS_VALUE_DRIVERS_TABLE} ON {CVS_VALUE_DRIVERS_TABLE}.id = {CVS_VCS_NEED_DRIVERS_TABLE}.value_driver "
                f"WHERE {CVS_VCS_ROWS_TABLE}.id IN ({','.join(['%s' for _ in range(len(vcs_rows))])})",
                [row.id for row in vcs_rows],
            )
            all_row_vds = [
                dict(zip(cursor.column_names, row)) for row in cursor.fetchall()
            ]
            logger.debug(f"All row vds: {all_row_vds}")

    formulas = []
    for row in vcs_rows:
        row_res = [r for r in res if r["vcs_row"] == row.id]
        r = {}
        if row_res:
            r = row_res[0]
        else:
            r["vcs_row"] = row.id
            r["design_group"] = design_group_id
            r["time"] = ""
            r["time_latex"] = ""
            r["time_comment"] = ""
            r["cost"] = ""
            r["cost_latex"] = ""
            r["cost_comment"] = ""
            r["revenue"] = ""
            r["revenue_latex"] = ""
            r["revenue_comment"] = ""
            r["time_unit"] = TimeFormat.YEAR
            r["rate"] = Rate.PRODUCT
        r["row_value_drivers"] = [vd for vd in all_row_vds if vd["vcs_row"] == row.id]
        r["used_value_drivers"] = [
            vd
            for vd in all_used_vds
            if vd["vcs_row"] == row.id and vd["design_group"] == r["design_group"]
        ]
        r["used_external_factors"] = [
            ef
            for ef in all_used_efs
            if ef["vcs_row"] == row.id and ef["design_group"] == r["design_group"]
        ]
        formulas.append(populate_formula_row(db_connection, r))

    return formulas


def populate_formula(
    db_connection: PooledMySQLConnection,
    text: str = "",
    latex: str = "",
    comment: str = "",
) -> models.Formula:
    used_value_drivers = set()
    used_external_factors = set()
    # find all value drivers and external factors
    vd_pattern = r'\{vd:(?P<id>\d+),"([^"]+)"\}'
    vd_matches = re.findall(vd_pattern, text)
    for vd_id, _ in vd_matches:
        used_value_drivers.add(vd_id)
    ef_pattern = r'\{ef:(?P<id>\d+),"([^"]+)"\}'
    ef_matches = re.findall(ef_pattern, text)
    for ef_id, _ in ef_matches:
        used_external_factors.add(ef_id)

    # fetch value drivers and external factors
    vd_names = {}
    ef_names = {}
    if len(used_value_drivers):
        select_statement = MySQLStatementBuilder(db_connection)
        value_drivers = (
            select_statement.select(CVS_VALUE_DRIVERS_TABLE, CVS_VALUE_DRIVERS_COLUMNS)
            .where(
                "id IN ("
                + ",".join(["%s" for _ in range(len(used_value_drivers))])
                + ")",
                used_value_drivers,
            )
            .execute(fetch_type=FetchType.FETCH_ALL, dictionary=True)
        )
        for vd in value_drivers:
            vd_names[
                str(vd["id"])
            ] = f"{vd['name']} [{vd['unit'] if vd['unit'] else 'N/A'}]"
    if len(used_external_factors):
        select_statement = MySQLStatementBuilder(db_connection)
        external_factors = (
            select_statement.select(
                CVS_EXTERNAL_FACTORS_TABLE, CVS_EXTERNAL_FACTORS_COLUMNS
            )
            .where(
                "id IN ("
                + ",".join(["%s" for _ in range(len(used_external_factors))])
                + ")",
                used_external_factors,
            )
            .execute(fetch_type=FetchType.FETCH_ALL, dictionary=True)
        )
        for ef in external_factors:
            ef_names[
                str(ef["id"])
            ] = f"{ef['name']} [{ef['unit'] if ef['unit'] else 'N/A'}]"

    # replace value driver and external factors names in text
    for vd in used_value_drivers:
        vd_replace_pattern = r"\{vd:" + vd + r',"(.*?)"\}'
        vd_name = vd_names[vd] if vd in vd_names else "UNDEFINED [N/A]"
        text = re.sub(vd_replace_pattern, "{vd:" + vd + ',"' + vd_name + '"}', text)
        vd_latex_pattern = r"\\class{vd}{\\identifier{vd:" + vd + r"}{\\text{(.*?)}}}"
        latex_new = (
            re.escape("\\class")
            + "{vd}{"
            + re.escape("\\identifier")
            + "{vd:"
            + str(vd)
            + "}{"
            + re.escape("\\text")
            + "{"
            + str(vd_name)
            + "}}}"
        )
        latex = re.sub(vd_latex_pattern, latex_new, latex)
    for ef in used_external_factors:
        ef_replace_pattern = r"\{ef:" + ef + r',"(.*?)"\}'
        ef_name = ef_names[ef] if ef in ef_names else "UNDEFINED [N/A]"
        text = re.sub(ef_replace_pattern, "{ef:" + ef + ',"' + ef_name + '"}', text)
        ef_latex_pattern = r"\\class{ef}{\\identifier{ef:" + ef + r"}{\\text{(.*?)}}}"
        latex_new = (
            re.escape("\\class")
            + "{ef}{"
            + re.escape("\\identifier")
            + "{ef:"
            + str(ef)
            + "}{"
            + re.escape("\\text")
            + "{"
            + str(ef_name)
            + "}}}"
        )
        latex = re.sub(ef_latex_pattern, latex_new, latex)

    return models.Formula(text=text, latex=latex, comment=comment)


def populate_formula_row(
    db_connection: PooledMySQLConnection, db_result
) -> models.FormulaRowGet:
    return models.FormulaRowGet(
        vcs_row_id=db_result["vcs_row"],
        design_group_id=db_result["design_group"],
        time=populate_formula(
            db_connection,
            text=db_result["time"],
            latex=db_result["time_latex"],
            comment=db_result["time_comment"],
        ),
        time_unit=db_result["time_unit"],
        cost=populate_formula(
            db_connection,
            text=db_result["cost"],
            latex=db_result["cost_latex"],
            comment=db_result["cost_comment"],
        ),
        revenue=populate_formula(
            db_connection,
            text=db_result["revenue"],
            latex=db_result["revenue_latex"],
            comment=db_result["revenue_comment"],
        ),
        rate=db_result["rate"],
        row_value_drivers=[
            vcs_storage.populate_value_driver(valueDriver)
            for valueDriver in db_result["row_value_drivers"]
        ]
        if db_result["row_value_drivers"] is not None
        else [],
        used_value_drivers=[
            vcs_storage.populate_value_driver(valueDriver)
            for valueDriver in db_result["used_value_drivers"]
        ]
        if db_result["used_value_drivers"] is not None
        else [],
        used_external_factors=[
            populate_external_factor(externalFactor)
            for externalFactor in db_result["used_external_factors"]
        ]
        if db_result["used_external_factors"] is not None
        else [],
    )


def delete_formulas(
    db_connection: PooledMySQLConnection,
    project_id: int,
    vcs_row_id: int,
    design_group_id: int,
) -> bool:
    logger.debug(f"Deleting formulas with vcs_row_id: {vcs_row_id}")

    get_design_group(
        db_connection, project_id, design_group_id
    )  # Check if design group exists and matches project
    vcs_storage.get_vcs_row(db_connection, project_id, vcs_row_id)

    delete_statement = MySQLStatementBuilder(db_connection)
    _, rows = (
        delete_statement.delete(CVS_FORMULAS_TABLE)
        .where("vcs_row = %s and design_group = %s", [vcs_row_id, design_group_id])
        .execute(return_affected_rows=True)
    )

    if rows != 1:
        raise exceptions.FormulasFailedDeletionException

    return True


def get_vcs_dg_pairs(
    db_connection: PooledMySQLConnection, project_id: int
) -> List[models.VcsDgPairs]:
    query = (
        "SELECT cvs_vcss.name AS vcs_name, cvs_vcss.id AS vcs_id, cvs_design_groups.name AS design_group_name, "
        "cvs_design_groups.id AS design_group_id, \
    (SELECT count(*) FROM cvs_vcs_rows WHERE cvs_vcs_rows.vcs = cvs_vcss.id) \
    = ((SELECT (count(*)) FROM cvs_design_mi_formulas INNER JOIN cvs_vcs_rows ON cvs_vcs_rows.id = vcs_row WHERE "
        "cvs_design_mi_formulas.design_group=cvs_design_groups.id AND vcs=cvs_vcss.id)) \
    AS has_formulas FROM cvs_vcss, cvs_design_groups WHERE cvs_vcss.project = %s AND cvs_design_groups.project = %s \
    GROUP BY vcs_id, design_group_id ORDER BY has_formulas DESC;"
    )

    with db_connection.cursor(prepared=True) as cursor:
        # Log for sanity check
        logger.debug(f"get_vcs_dg_pairs: '{query}'")

        # Execute query
        cursor.execute(query, [project_id, project_id])

        # Get result
        res_dict = []
        rs = cursor.fetchall()
        for res in rs:
            zip(cursor.column_names, res)
            res_dict.append(
                models.VcsDgPairs(
                    vcs=res[0],
                    vcs_id=res[1],
                    design_group=res[2],
                    design_group_id=res[3],
                    has_formulas=res[4],
                )
            )

    return res_dict
