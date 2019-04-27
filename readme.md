# Converter for the exchange from Aralia format to Open-PSA format

## quick start
1. parse Aralia to Open-PSA:
```
    cd parser
    python3 parser.py
```
2. use xftar to run all tests
```
    cd test
    python3 run.py
```

## description

|path|usage|
|-|-|
|raw/|Aralia format file|
|result/|Open-PSA format file|
|test/xftar_result|xftar result|
|test/statistic.xls|statistics including Module, MSC, Time, Memory|
|parser/statistic.xls| statistics including Gate, Event|