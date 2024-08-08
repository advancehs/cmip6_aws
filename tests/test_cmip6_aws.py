#!/usr/bin/env python

"""Tests for `cmip6_aws` package."""


import unittest

from cmip6_aws import cmip6_aws


# class TestCmip6_aws(unittest.TestCase):
    # """Tests for `cmip6_aws` package."""

    # def setUp(self):
    #     """Set up test fixtures, if any."""

    # def tearDown(self):
    #     """Tear down test fixtures, if any."""

    # def test_000_something(self):
    #     """Test something."""
if __name__ == "__main__":

    cmip6 = cmip6_aws.CMIP6()

    # 使用示例
    print(cmip6.model())  # 显示所有 models

    print(cmip6.scenario("CESM2"))

    print(cmip6.member("ssp585"))
    print(cmip6.variable())
    print(cmip6.year())

    cmip6.idm("aa", "CESM2", "ssp585", "r4i1p1f1", "pr", "2015v1.1")
    cmip6.down(r"C:\Users\10197\cmip6_aws\cmip6_aws2\aa","CESM2","ssp585","r4i1p1f1","pr","2015v1.1",(5,55),(55,56))
