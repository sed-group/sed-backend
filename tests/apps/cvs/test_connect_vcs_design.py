import pytest

import tests.testutils as testutils
import tests.apps.cvs.testutils as tu

import sedbackend.apps.core.users.implementation as impl_users

def test_create_formulas(client, std_headers, std_user):
  #Setup
  current_user = impl_users.impl_get_user_with_username(std_user.username)
  project = tu.seed_random_project(current_user.id)

  tr = tu.random_table_row(project.id)
  


def test_get_all_formulas(client, std_headers, std_user):
  pass


def test_edit_formulas(client, std_headers, std_user):
  pass


def test_delete_formulas(client, std_headers, std_user):
  pass


def test_get_vcs_dg_pairs(client, std_headers, std_user):
  pass
