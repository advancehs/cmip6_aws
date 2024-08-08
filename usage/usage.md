# Usage

To use cmip6_aws in a project:

```
from cmip6_aws import cmip6_aws

cmip6 = cmip6_aws.CMIP6()

# 使用示例
print(cmip6.model())  # 显示所有 models

print(cmip6.scenario("CESM2"))
print(cmip6.variable("ssp585"))
print(cmip6.year())

cmip6.idm("aa","CESM2","ssp585","pr","2015v1.1")
cmip6.down(r"C:\Users\10197\cmip6_aws\cmip6_aws2\aa","CESM2","ssp585","pr",["2015v1.1","2016v1.1"],(5,55),(55,56))
```
