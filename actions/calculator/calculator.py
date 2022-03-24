import pyswan


def calculate_mathematic_equation(equation):
    equations = pyswan.parse(equation, dim=['equation'])
    res = []
    for equation in equations:
        if equation['type'] == 'equation':
            res.append(equation['value'])

    return res


if __name__ == '__main__':
    exp = calculate_mathematic_equation('100.8+230乘以23')
    print(exp[0])
