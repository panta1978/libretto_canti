import os, re
#import pandas as pd

# INPUT and OUTPUT Files / Folders
InputMainTexFile = os.getcwd() + '\\libretto_canti.tex'
InputFolder = os.getcwd() + '\\canti\\'
OutputFolder = os.getcwd() + '\\html\\'

# List of INPUT Files (from libretto_canti.tex - ACTIVE SONGS ONLY)
with open(InputMainTexFile, 'r', encoding='UTF-8') as f:
    TxtMain = f.readlines()
InputFiles = [t[13:t.find('}')]+'.tex' for t in TxtMain if t.startswith('\\input{canti')]
#InputFiles = [f for f in os.listdir(InputFolder) if f.endswith('.tex')]

# Open Output File
with open(OutputFolder + 'Songs_DB.csv', 'w') as fout:
    fout.write('Index;Title;HtmlCode\n')

    for (nsong,InputFile) in enumerate(InputFiles):

        # Open Input File
        with open(InputFolder + InputFile, 'r', encoding='UTF8') as f:
            TxtIn = f.readlines()

        # Remove empty lines, \n characters, and leading spaces
        TxtInMod = [t.replace('\n','').lstrip(' ') for t in TxtIn if len(t)>1]

        # Remove 'begin{tabular} and end{tabular} lines
        TxtInMod = [t for t in TxtInMod if not('{tabular}' in t)]

        # Find '\\spazio'
        N_Sp = [n for (n, t) in enumerate(TxtInMod) if '\\spazio' in t]

        # Separate song blocks and look for refrain blocks
        N_Sp.insert(0,0)
        N_Sp.append(len(TxtInMod)+1)
        IsRefrain = [] # 0 if verse, 1 if refrain
        for ns in N_Sp[:-1]:
            IsRefrain.append('\\rit' in TxtInMod[ns+1])

        # From \\emph{...} to <em>...</em>
        for (n,t) in enumerate(TxtInMod):
            TxtF = re.findall('\\\\emph{.*?}', t)
            TxtR = re.findall('\\\\emph{(.*?)}', t)
            for (tf,tr) in zip(TxtF,TxtR):
                TxtInMod[n] = TxtInMod[n].replace(tf, '<em>'+tr+'</em>')

        # From \\textbf{...} to <strong>...</strong>
        for (n,t) in enumerate(TxtInMod):
            TxtF = re.findall('\\\\textbf{.*?}', t)
            TxtR = re.findall('\\\\textbf{(.*?)}', t)
            for (tf, tr) in zip(TxtF, TxtR):
                TxtInMod[n] = TxtInMod[n].replace(tf, '<strong>' + tr + '</strong>')

        # From \\taize{...} to <p class='canto-taize'>...</'p'>
        for (n,t) in enumerate(TxtInMod):
            TxtF = re.findall('\\\\taize{.*?}', t)
            TxtR = re.findall('\\\\taize{(.*?)}', t)
            for (tf, tr) in zip(TxtF, TxtR):
                TxtInMod[n] = TxtInMod[n].replace(tf, '<p class=""canto-taize"">' + tr + '</p>')

        # From \\volte{N} to (N volte)
        for (n, t) in enumerate(TxtInMod):
            TxtF = re.findall('\\\\volte{.*?}', t)
            TxtR = re.findall('\\\\volte{(.*?)}', t)
            for (tf, tr) in zip(TxtF, TxtR):
                TxtInMod[n] = TxtInMod[n].replace(tf, '(' + tr + ' volte)')

        # Remove and update some texts
        RemUpdTexts = {
            '\\\\':         '',
            '\\rit':        '',
            '\\canto':      '',
            '{':            '',
            '}':            '',
            '\\spazio':     '',
            '``':           '\'',
            '\'\'':         '\'',
            '\\ae\\':       'ae',
            '\\ae ':        'ae',
            '\\ae,':        'ae,',
            '\\oe\\':       'oe',
            '\\oe ':        'oe',
            '\\oe,':        'oe,',
            '\\small':      '',
            '$\\dagger$':   '+',
            '\\newpage':    '',
            '\t':           ' ',
            '&':            ' - ',
            '  ':           ' ',
        }

        for RemUpd in RemUpdTexts:
            TxtInMod = [t.replace(RemUpd, RemUpdTexts[RemUpd]) for t in TxtInMod]

        # Manage Verse numbers
        Nv = 0
        for (n,t) in enumerate(TxtInMod):
            if '\\strofa' in t:
                Nv = Nv+1
                TxtInMod[n] = TxtInMod[n].replace('\\strofa', f'{Nv}.')

        # Create blocks (if a refreain contains ... it is replaced by the previous one)
        Txt_Bl = []
        CurrRefr = -1
        for nb,(ns, ne) in enumerate(zip(N_Sp[:-1], N_Sp[1:])):
            if not(IsRefrain[nb]):
                Txt_Bl.append(TxtInMod[ns+1:ne])
            elif not('...' in TxtInMod[ns+1]):
                Txt_Bl.append(TxtInMod[ns+1:ne])
                CurrRefr = nb
            else:
                nsold = N_Sp[CurrRefr]
                neold = N_Sp[CurrRefr+1]
                Txt_Bl.append(TxtInMod[nsold+1:neold])


        # Write number and title
        fout.write(f'{nsong+1};"{TxtInMod[0]}";')

        # Title
        fout.write(f'"<p class=""nome-canto"">{nsong+1} ' + TxtInMod[0] +'</p>')

        # Write blocks
        for (tb,ir) in zip(Txt_Bl,IsRefrain):
            if ir:
                fout.write('<p class=""canto-ritornello"">')
            else:
                fout.write('<p class=""canto-testo"">')
            for (n,t) in enumerate(tb):
                tt = t.replace('"','""')
                if n<len(tb)-1:
                    fout.write(tt + '</br>')
                else:
                    fout.write(tt)
            fout.write('</p>')

        # End of Line
        fout.write('"\n')


