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

    def loan_amount(self, project_size: float, DCR_status: bool, loan_size: float, subsidy_size:float):
        '''
        If the loan_size is a percent, this function simply converts it to an amount.
        For example, if you type in loan_size = 70, this will calculate 70% of the project cost.
        '''
        if loan_size <= 100:
            if DCR_status:
                return ((self.DCR * project_size) - subsidy_size) * (loan_size/100)
            else:
                return ((self.NON_DCR * project_size) - subsidy_size) * (loan_size/100)
        else:
            return loan_size


    def total_amount(self, bid_rate: float, project_size: float):
        '''
        The absolute return without any cost involved. Calculates the gross number.
        '''
        nominal_per_year = project_size * 4500 * 365 * bid_rate #Return in Rupees/per year      
        dictionary = {'Year': np.arange(1, 26), 'Gross Return': [nominal_per_year] * self.YOJANA_LENGTH}
        absolute_structure = pd.DataFrame.from_dict(dictionary)       

        return absolute_structure


    def emi_payment(self, project_size: float, loan_size: float, pay_emi_in: int, subsidy_size: float, bank_loan_rate = 0.105, DCR_status=True):
        '''
        EMI Payment structure for the specified length.
        '''
        structure = [0.0] * self.YOJANA_LENGTH

        #loan in percent
        loan_size = self.loan_amount(project_size=project_size, DCR_status=DCR_status, loan_size=loan_size, subsidy_size=subsidy_size)

        emi_amount = (loan_size * bank_loan_rate)/(1 - (1 + bank_loan_rate)**(-1*pay_emi_in))

        for i in range(pay_emi_in):
            structure[i] = emi_amount
        
        #Creating a dictionary for exit
        dictionary = {'Year': np.arange(1, 26), 'EMI': structure}
        emi_structure = pd.DataFrame.from_dict(dictionary)

        return emi_structure
    
    def nominal_amount(self, bid_rate: float, project_size: float, loan_size: float, pay_emi_in: int, subsidy_size:float, DCR_status=True):
        '''
        Nominal amount = Total amount - EMI Payment
        '''
        total_amount = self.total_amount(bid_rate=bid_rate, project_size=project_size)
        emi_pay = self.emi_payment(project_size=project_size, loan_size=loan_size, pay_emi_in=pay_emi_in, subsidy_size=subsidy_size, DCR_status=DCR_status)

        nominal_amount = total_amount
        nominal_amount['Nominal Amount'] = total_amount['Gross Return'] - emi_pay['EMI']

        return nominal_amount[['Year', 'Nominal Amount']]
    
    def inflation_rate(self, ):
        '''
        Calculates the effects of inflation for 25Y.
        '''
        inflation_adjust = [1.0] * self.YOJANA_LENGTH
        for i in range(len(inflation_adjust)):
            inflation_adjust[i] *= (1 + self.INFLATION)**(i+1)

        dictionary = {'Year': np.arange(1, 26), 'Inflation': inflation_adjust}
        inflation_by_year = pd.DataFrame.from_dict(dictionary)

        return inflation_by_year
    
    def real_amount(self, bid_rate: float, project_size: float, loan_size: float, pay_emi_in: int, subsidy_size: float, DCR_status=True):
        '''
        Nominal amount realized by the inflation factor.
        '''
        #get Nominal Amounts
        nominal_amount = self.nominal_amount(bid_rate=bid_rate, project_size=project_size, loan_size=loan_size, pay_emi_in=pay_emi_in, subsidy_size=subsidy_size, DCR_status=DCR_status)
        
        #turn it into Real Amounts
        real_amount = nominal_amount

        #inflation
        inflation = self.inflation_rate()

        real_amount['Real Amount'] = nominal_amount['Nominal Amount'] / inflation['Inflation']

        return real_amount[['Year', 'Real Amount']]
    
    def annualized_return(self, bid_rate: float, project_size: float, loan_size: float, pay_emi_in: int, subsidy_size: float, realized=True, DCR_status=True):
        if realized:
            amount = self.real_amount(bid_rate=bid_rate, project_size=project_size, loan_size=loan_size, subsidy_size=subsidy_size, pay_emi_in=pay_emi_in)
            overall_val = sum(amount['Real Amount'])
        else:
            amount = self.nominal_amount(bid_rate=bid_rate, project_size=project_size, loan_size=loan_size, subsidy_size=subsidy_size, pay_emi_in=pay_emi_in)
            overall_val = sum(amount['Nominal Amount'])
        if DCR_status:
            overall_investment = (project_size * self.DCR) - self.loan_amount(project_size=project_size, subsidy_size=subsidy_size, DCR_status=DCR_status, loan_size=loan_size)
            if realized:
                print(f'{round((((overall_val/overall_investment)**(1/25))-1)*100, 2)}% return over {self.INFLATION*100}% inflation over {self.YOJANA_LENGTH} years.')
            else:
                print(f'{round((((overall_val/overall_investment)**(1/25))-1)*100, 2)}% return over {self.YOJANA_LENGTH} years.')
        else:
            overall_investment = (project_size * self.NON_DCR) - self.loan_amount(project_size=project_size, subsidy_size=subsidy_size, DCR_status=DCR_status, loan_size=loan_size)
            if realized:
                print(f'{round((((overall_val/overall_investment)**(1/25))-1)*100, 2)}% return over {self.INFLATION*100}% inflation over {self.YOJANA_LENGTH} years.')
            else:
                print(f'{round((((overall_val/overall_investment)**(1/25))-1)*100, 2)}% return over {self.YOJANA_LENGTH} years.')
            
        
        return 

    def figure(self, bid_rate: float, project_size: float, loan_size: float, pay_emi_in: int, subsidy_size: float):
        '''
        Draw everything.
        '''
        emi_amount = self.emi_payment(project_size=project_size, loan_size=loan_size, subsidy_size=subsidy_size, pay_emi_in=pay_emi_in)
        nominal_amount = self.nominal_amount(bid_rate=bid_rate, project_size=project_size, loan_size=loan_size, subsidy_size=subsidy_size, pay_emi_in=pay_emi_in)
        real_amount = self.real_amount(bid_rate=bid_rate, project_size=project_size, loan_size=loan_size, subsidy_size=subsidy_size, pay_emi_in=pay_emi_in)

        plt.plot(emi_amount['Year'], emi_amount['EMI']/1e5)
        plt.plot(emi_amount['Year'], nominal_amount['Nominal Amount']/1e5)
        plt.plot(emi_amount['Year'], real_amount['Real Amount']/1e5)

        plt.scatter(emi_amount['Year'], emi_amount['EMI']/1e5)
        plt.scatter(emi_amount['Year'], nominal_amount['Nominal Amount']/1e5)
        plt.scatter(emi_amount['Year'], real_amount['Real Amount']/1e5)

        plt.legend(['EMI', 'Nominal Amount', 'Real Amount'])
        plt.xlabel('Year')
        plt.ylabel('In Lakhs')
        plt.grid(True)

        return
