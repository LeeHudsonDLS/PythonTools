import numpy as np
import pandas as pd
import argparse


parser = argparse.ArgumentParser(description="Process some CSV data.")
parser.add_argument('csv_path', type=str, help='Path to the CSV file')
parser.add_argument('rawPotPV', type=str, help='Raw potentiometer PV')
parser.add_argument('excelRawPotFirstCell', type=str, help='First cell in Excel for raw potentiometer')

args = parser.parse_args()

# # Load data from CSV
# csv_path = "FE24B_UX.csv"  # Change this to your CSV path
# rawPotPV = "FE24B-CS-POT-01:ADC1_VALUE"
# args.excelRawPotFirstCell = "C2"

df = pd.read_csv(args.csv_path)
# Extract columns
potentiometer = df['Pot'].values
encoder = df['Encoder'].values

# Fit a 5th-degree polynomial: encoder = f(potentiometer)
coefficients = np.polyfit(potentiometer, encoder, 5)

# Assign coefficients to named variables (highest degree first)
G, F, E, D, C, B = coefficients  # Corresponds to A^5 down to A^0

# Display named variables
print(f"B = {B:.10e}")
print(f"C = {C:.10e}")
print(f"D = {D:.10e}")
print(f"E = {E:.10e}")
print(f"F = {F:.10e}")
print(f"G = {G:.10e}")

# Optional: Build the expression string
expression = f"(({B:.10e})*(A**0)) + (({C:.10e})*(A**1)) + (({D:.10e})*(A**2)) + " \
             f"(({E:.10e})*(A**3)) + (({F:.10e})*(A**4)) + (({G:.10e})*(A**5))"

calcRecord = f'<records.calc B="{B:.10e}" C="{C:.10e}" CALC="((A^0)*B)+((A^1)*C)+((A^2)*D)+((A^3)*E)+((A^4)*F)+((A^5)*G)" D="{D:.10e}" E="{E:.10e}" EGU="mm" F="{F:.10e}" G="{F:.10e}" INPA="{args.rawPotPV}" PREC="4" SCAN=".1 second" name="" record=""/>'

excelForm = f"=({B:.10e}*POWER({args.excelRawPotFirstCell},0))+({C:.10e}*POWER({args.excelRawPotFirstCell},1))+({D:.10e}*POWER({args.excelRawPotFirstCell},2))+({E:.10e}*POWER({args.excelRawPotFirstCell},3))+({F:.10e}*POWER({args.excelRawPotFirstCell},4))+({G:.10e}*POWER({args.excelRawPotFirstCell},5))"

print("\nPolynomial Expression:")
print(expression)

print("\nEPICS calc record:")
print(calcRecord)

print("\nExcel formula:")
print(excelForm)