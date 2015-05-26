class EAN13:
    encode = {
        'A' : (
            '3211',
            '2221',
            '2122',
            '1411',
            '1132',
            '1231',
            '1114',
            '1312',
            '1213',
            '3112'
        ),
        'B' : (
            '1123',
            '1222',
            '2212',
            '1141',
            '2311',
            '1321',
            '4111',
            '2131',
            '3121',
            '2113'
        ),
        'C' : (
            '3211',
            '2221',
            '2122',
            '1411',
            '1132',
            '1231',
            '1114',
            '1312',
            '1213',
            '3112'
        )
    }

    sets = (
        'AAAAAA',
        'AABABB',
        'AABBAB',
        'AABBBA',
        'ABAABB',
        'ABBAAB',
        'ABBBAA',
        'ABABAB',
        'ABABBA',
        'ABBABA'
    )

    metrics = {
        'quiet_zone' : {
            'begin' : 0.363,
            'end'   : 0.231
        },
        'height' : {
            'standard' : 2.285,
            'guard'    : 2.450
        },
        'X-dimension' : 0.033
    }

    def __init__(self, code):
        if len(code) != 12:
            raise Exception('Code must contain 12 digit : check digit is computed')
        self.__code = code
        self.__check_digit = self.compute_check_digit()
        EAN13.metrics['height']['guard-standard'] = EAN13.metrics['height']['guard'] - EAN13.metrics['height']['standard']

    def compute_check_digit(self):
        P = 0
        I = 0
        for pos, digit in enumerate(self.__code):
            pos += 1
            digit = int(digit)
            if pos % 2 == 0:
                P += digit
            else:
                I += digit
        C = 3 * P + I
        M = C // 10
        if C % 10 != 0:
            M += 1
        M *= 10
        return M - C

    def generate_barcode(self):
        barcode_left = ''
        barcode_right = ''
        i = 1
        for s in EAN13.sets[int(self.__code[0])]:
            barcode_left += EAN13.encode[s][int(self.__code[i])]
            i += 1
        while i < 12:
            barcode_right += EAN13.encode['C'][int(self.__code[i])]
            i += 1
        barcode_right += EAN13.encode['C'][self.__check_digit]

        return (barcode_left, barcode_right)

    def latex_normal_guard_zone(self, x):
        str_latex = ''
        bars = ('black', 'white', 'black')
        for coul in bars:
            str_latex += '\\fill[{}] ({},{}) rectangle ({},0);'.format(coul, x, EAN13.metrics['height']['guard'], x + EAN13.metrics['X-dimension'])
            x += EAN13.metrics['X-dimension']
        return (str_latex, x)

    def latex_central_guard_zone(self, x):
        str_latex = ''
        bars = ('white', 'black', 'white', 'black', 'white')
        for coul in bars:
            str_latex += '\\fill[{}] ({},{}) rectangle ({},0);'.format(coul, x, EAN13.metrics['height']['guard'], x + EAN13.metrics['X-dimension'])
            x += EAN13.metrics['X-dimension']
        return (str_latex, x)

    def latex_module(self, x, color, module_size):
        end_x = x + module_size * EAN13.metrics['X-dimension']
        return ('\\fill[{}] ({},{}) rectangle ({},{});'.format(color, x, EAN13.metrics['height']['guard'], end_x, EAN13.metrics['height']['guard-standard']), end_x)

    def barcode2latex(self):
        (barcode_left, barcode_right) = self.generate_barcode()
        current_x = EAN13.metrics['quiet_zone']['begin']

        # Zone de garde normale
        str_latex, current_x = self.latex_normal_guard_zone(current_x)

        # Partie gauche
        mod_num = 0
        for module_size in barcode_left:
            if mod_num % 2 == 0:
                color = 'white'
            else:
                color = 'black'
            latex, current_x = self.latex_module(current_x, color, int(module_size))
            str_latex += latex
            mod_num += 1

        # Zone de garde centrale
        latex, current_x = self.latex_central_guard_zone(current_x)
        str_latex += latex

        # Partie droite
        mod_num = 0
        for module_size in barcode_right:
            if mod_num % 2 == 0:
                color = 'black'
            else:
                color = 'white'
            latex, current_x = self.latex_module(current_x, color, int(module_size))
            str_latex += latex
            mod_num += 1

        # Zone de garde normale
        latex, current_x = self.latex_normal_guard_zone(current_x)
        str_latex += latex

        return '\\begin{tikzpicture}\n' + str_latex + '\\end{tikzpicture}\n';


    def __str__(self):
        return "{} {} {}{}".format(self.__code[0], self.__code[1:7], self.__code[7:], self.__check_digit)

if __name__ == '__main__':
    code = EAN13('978272349971')
    try:
        with open('ean13_glmf.tex', 'w') as fic:
            fic.write('\\documentclass[a4paper,11pt]{article}\n')
            fic.write('\\usepackage{tikz}\n')
            fic.write('\\begin{document}\n')
            fic.write(code.barcode2latex())
            fic.write('\\end{document}\n')
    except IOError:
        print('Impossible d\'écrire le fichier!')
        exit(1)
    print('Fichier ean13_glmf.tex généré !')
    import os
    os.system('pdflatex ean13_glmf.tex')
