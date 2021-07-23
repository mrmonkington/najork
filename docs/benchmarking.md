
## Is Jinja2 fast enough for expression evaluation in OscMessage templates?
```
In [32]: ti = Timer('from jinja2 import Template\nimport math\nt = Template("/mo/mo/{{ money }}/{{ math.sin(val * math.pi) }}")\nfor i in range(1000): t.render(money="hello", val=i, math=math)')

In [33]: ti.timeit(number=1)
Out[33]: 0.014126522990409285
```

Yeah looks ok.
