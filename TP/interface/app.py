import PySimpleGUI as sg
import subprocess
import re

def run_prolog_query(mmse, functional_assessment, memory_complaints, behavioral_problems, adl):
    # Montar a consulta Prolog com base nos valores preenchidos
    query = f"diagnostic({mmse}, {functional_assessment}, {memory_complaints}, {behavioral_problems}, {adl}, X), write(X)."

    # Chamar o SWI-Prolog para executar a consulta
    result = subprocess.run(['swipl', '-s', '../rules.pl', '-g', query, '-t', 'halt'], capture_output=True, text=True)

    # Capturar a saída da consulta
    output = result.stdout.strip()

    # Processar a saída para extrair o valor de X
    match = re.search(r"(\d+)", output)
    if match:
        diagnosis_result = match.group(1)
        return "true" if diagnosis_result == "1" else "false"
    else:
        return "Result not found"

def validate_inputs(values):
    try:
        MMSE = float(values['-MMSE-'])
        FunctionalAssessment = float(values['-FA-'])
        MemoryComplaints = int(values['-MC-'])
        BehavioralProblems = int(values['-BP-'])
        ADL = float(values['-ADL-'])

        if MemoryComplaints not in [0, 1] or BehavioralProblems not in [0, 1]:
            return False, "MemoryComplaints and BehavioralProblems must be 0 or 1"

        return True, ""
    except ValueError:
        return False, "All values must be numeric and MemoryComplaints/BehavioralProblems must be 0 or 1"

# Definição do layout da interface gráfica
layout = [
    [sg.Text('Alzheimer Diagnosis System', size=(29, 1), font=('Helvetica', 20), justification='center')],
    [sg.Text('_' * 66)],
    [sg.Text('MMSE (Mini-Mental State Examination)', size=(30, 1)), sg.InputText(key='-MMSE-', size=(30, 1))],
    [sg.Text('Functional Assessment', size=(30, 1)), sg.InputText(key='-FA-', size=(30, 1))],
    [sg.Text('Memory Complaints (0 ou 1)', size=(30, 1)), sg.InputText(key='-MC-', size=(30, 1))],
    [sg.Text('Behavioral Problems (0 ou 1)', size=(30, 1)), sg.InputText(key='-BP-', size=(30, 1))],
    [sg.Text('ADL (Activities of Daily Living)', size=(30, 1)), sg.InputText(key='-ADL-', size=(30, 1))],
    [sg.Text('_' * 66)],
    [sg.Button('Diagnose', size=(15, 1)), sg.Button('Clean', size=(15, 1)), sg.Button('Exit', size=(15, 1))],
    [sg.Text('_' * 66)],
    [sg.Text('Diagnosis Result:', size=(30, 1)), sg.Text('', size=(23, 1), key='-RESULT-', font=('Helvetica', 12), justification='center', background_color='white')],
]

# Criar a janela
window = sg.Window('Alzheimer Diagnosis System', layout, resizable=True, finalize=True, background_color='darkgrey')

# Loop para capturar eventos da interface
while True:
    event, values = window.read()

    if event == sg.WINDOW_CLOSED or event == 'Exit':
        break

    if event == 'Diagnose':
        valid, message = validate_inputs(values)
        if not valid:
            sg.popup_error(message)
            continue

        functional_assessment = values['-FA-']
        adl = values['-ADL-']
        mmse = values['-MMSE-']
        memory_complaints = values['-MC-']
        behavioral_problems = values['-BP-']

        try:
            # Executar a consulta Prolog e obter o resultado
            result = run_prolog_query(mmse, functional_assessment, memory_complaints, behavioral_problems, adl)

            # Atualizar o texto do resultado na interface
            if result == "true":
                window['-RESULT-'].update('true', text_color='green')
            elif result == "false":
                window['-RESULT-'].update('false', text_color='red')
            else:
                window['-RESULT-'].update('Result not found', text_color='yellow')

        except Exception as e:
            sg.popup_error(f'An error occurred while executing the query: {str(e)}')

    elif event == 'Clean':
        window['-MMSE-'].update('')
        window['-FA-'].update('')
        window['-MC-'].update('')
        window['-BP-'].update('')
        window['-ADL-'].update('')
        window['-RESULT-'].update('')

# Fechar a janela ao sair do loop
window.close()
