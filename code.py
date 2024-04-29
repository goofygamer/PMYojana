import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

class PMYojana():
    def __init__(self) -> None:
        self.DCR = 33e6 #DCR Program cost per MW
        self.NON_DCR = 26e6 #Non-DCR Program cost per MW
        self.INFLATION = 0.06 #Inflation Rate
        self.YOJANA_LENGTH = 25 #How long is the Yojana
        self.UNITS = 4500

    def total_return(self, bid_rate: float, project_size: float):
        nominal_per_year = project_size * 4500 * 365 * bid_rate #Return in Rupees/per year      
        dictionary = {'Year': np.arange(1, 26), 'Gross Return': [nominal_per_year] * self.YOJANA_LENGTH}
        absolute_structure = pd.DataFrame.from_dict(dictionary)       

        return absolute_structure


    def emi_payment(self, loan_size: float, pay_emi_in: int, bank_loan_rate = 0.105):
        structure = [0.0] * self.YOJANA_LENGTH
        emi_amount = (loan_size * bank_loan_rate)/(1 - (1 + bank_loan_rate)**(-1*pay_emi_in))

        for i in range(pay_emi_in):
            structure[i] = emi_amount
        
        #Creating a dictionary for exit
        dictionary = {'Year': np.arange(1, 26), 'EMI': structure}
        emi_structure = pd.DataFrame.from_dict(dictionary)

        return emi_structure
    
    def nominal_return(self, bid_rate: float, project_size: float, loan_size: float, pay_emi_in: int):
        total_return = self.total_return(bid_rate=bid_rate, project_size=project_size)
        emi_pay = self.emi_payment(loan_size=loan_size, pay_emi_in=pay_emi_in)

        nominal_return = total_return
        nominal_return['Nominal Return'] = total_return['Gross Return'] - emi_pay['EMI']

        return nominal_return[['Year', 'Nominal Return']]
    
    def inflation_rate(self, ):
        inflation_adjust = [1.0] * self.YOJANA_LENGTH
        for i in range(len(inflation_adjust)):
            inflation_adjust[i] *= (1 + self.INFLATION)**(i+1)

        dictionary = {'Year': np.arange(1, 26), 'Inflation': inflation_adjust}
        inflation_by_year = pd.DataFrame.from_dict(dictionary)

        return inflation_by_year
    
    def real_return(self, bid_rate: float, project_size: float, loan_size: float, pay_emi_in: int):
        #get nominal returns
        nominal_return = self.nominal_return(bid_rate=bid_rate, project_size=project_size, loan_size=loan_size, pay_emi_in=pay_emi_in)
        
        #turn it into real returns
        real_return = nominal_return

        #inflation
        inflation = self.inflation_rate()

        real_return['Real Return'] = nominal_return['Nominal Return'] / inflation['Inflation']

        return real_return[['Year', 'Real Return']]
