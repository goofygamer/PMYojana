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
        if loan_size <= 100000:
            if DCR_status:
                return ((self.DCR * project_size - subsidy_size)) * (loan_size/100)
            else:
                return ((self.NON_DCR * project_size - subsidy_size)) * (loan_size/100)
        else:
            return loan_size


    def total_amount(self, bid_rate: float, project_size: float):
        '''
        The absolute return without any cost involved. Calculates the gross number.
        '''
        nominal_per_year = project_size * 4500 * 365 * bid_rate #Return in Rupees/per year
        total_return = [nominal_per_year] * self.YOJANA_LENGTH
        solar_breakdown = [1.0]*25
        solar_breakdown[0] = 0.98
        for i in range(1, len(solar_breakdown)):
            solar_breakdown[i] *= solar_breakdown[i-1]*0.994
        for j in range(len(total_return)):
            total_return[j] *= solar_breakdown[j]
        dictionary = {'Year': np.arange(1, 26), 'Gross Return': total_return}
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
            overall_investment = (project_size * self.DCR) - self.loan_amount(project_size=project_size, subsidy_size=subsidy_size, DCR_status=DCR_status, loan_size=loan_size) - subsidy_size
            if realized:
                print(f'Realized return of {round(overall_val, 0)} INR on {round(overall_investment, 2)} investment.')
                print(f'{round((((overall_val/overall_investment)**(1/25))-1)*100, 2)}% return over {self.INFLATION*100}% inflation over {self.YOJANA_LENGTH} years.')
            else:
                print(f'Nominal return of {round(overall_val, 0)} INR on {round(overall_investment, 2)} investment.')
                print(f'{round((((overall_val/overall_investment)**(1/25))-1)*100, 2)}% return over {self.YOJANA_LENGTH} years.')
        else:
            overall_investment = (project_size * self.NON_DCR) - self.loan_amount(project_size=project_size, subsidy_size=subsidy_size, DCR_status=DCR_status, loan_size=loan_size) - subsidy_size
            if realized:
                print(f'Realized return of {round(overall_val, 0)} INR on {round(overall_investment, 2)} investment.')
                print(f'{round((((overall_val/overall_investment)**(1/25))-1)*100, 2)}% return over {self.INFLATION*100}% inflation over {self.YOJANA_LENGTH} years.')
            else:
                print(f'Nominal return of {round(overall_val, 0)} INR on {round(overall_investment, 2)} investment.')
                print(f'{round((((overall_val/overall_investment)**(1/25))-1)*100, 2)}% return over {self.YOJANA_LENGTH} years.')
            
        
        return 

    def figure_total(self, bid_rate: float, project_size: float, loan_size: float, pay_emi_in: int, subsidy_size: float, realized=True, DCR_status=True):
        '''
        Draw total, nominal, and emi payments.
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

        self.annualized_return(bid_rate=bid_rate, project_size=project_size, loan_size=loan_size, pay_emi_in=pay_emi_in, subsidy_size=subsidy_size, realized=realized, DCR_status=DCR_status)
        return
    
    def _annualized_return(self, bid_rate: float, project_size: float, loan_size: float, pay_emi_in: int, subsidy_size: float, realized: bool, DCR_status: bool):
        if realized:
            amount = self.real_amount(bid_rate=bid_rate, project_size=project_size, loan_size=loan_size, subsidy_size=subsidy_size, pay_emi_in=pay_emi_in)
            overall_val = sum(amount['Real Amount'])
        else:
            amount = self.nominal_amount(bid_rate=bid_rate, project_size=project_size, loan_size=loan_size, subsidy_size=subsidy_size, pay_emi_in=pay_emi_in)
            overall_val = sum(amount['Nominal Amount'])
        if DCR_status:
            overall_investment = (project_size * self.DCR) - self.loan_amount(project_size=project_size, subsidy_size=subsidy_size, DCR_status=DCR_status, loan_size=loan_size) - subsidy_size
        else:
            overall_investment = (project_size * self.NON_DCR) - self.loan_amount(project_size=project_size, subsidy_size=subsidy_size, DCR_status=DCR_status, loan_size=loan_size) - subsidy_size
        
        return (((overall_val/overall_investment)**(1/25))-1)*100

    def _figure_return(self, bid_rate: float, project_size: float, loan_size: float, pay_emi_in: int, subsidy_size: float, compare: str, realized: bool, DCR_status: bool):
        if compare == 'bid_rate':
            if type(bid_rate) != list:
                x = np.linspace(0.5*bid_rate, 1.5*bid_rate, 10)
            else:
                x = np.linspace(bid_rate[0], bid_rate[-1], 10)
            #output
            y = []
            for val in x:
                y.append(self._annualized_return(bid_rate=val, project_size=project_size, loan_size=loan_size, pay_emi_in=pay_emi_in, subsidy_size=subsidy_size, realized=realized, DCR_status=DCR_status))
            plt.plot(x, y)
            plt.scatter(x, y)
            plt.grid(True)
            plt.xlabel('Bid Rate')
            if realized:
                plt.ylabel(f'Realized Return over {round(self.INFLATION*100, 2)}% inflation')
            else:
                plt.ylabel('Nominal Return')
        elif compare == 'project_size':
            if type(project_size) != list:
                x = np.linspace(0.5*project_size, 1.5*project_size, 10)
            else:
                x = np.linspace(project_size[0], project_size[-1], 10)
            #output
            y = []
            for val in x:
                y.append(self._annualized_return(bid_rate=bid_rate, project_size=val, loan_size=loan_size, pay_emi_in=pay_emi_in, subsidy_size=subsidy_size, realized=realized, DCR_status=DCR_status))
            plt.plot(x, y)
            plt.scatter(x, y)
            plt.grid(True)
            plt.xlabel('Project Size in MW')
            if realized:
                plt.ylabel(f'Realized Return over {round(self.INFLATION*100, 2)}% inflation')
            else:
                plt.ylabel('Nominal Return')
        elif compare == 'loan_size':
            if type(loan_size) != list:
                x = np.linspace(0.75*loan_size, 1.25*loan_size, 10)
            else:
                x = np.linspace(loan_size[0], loan_size[-1], 10)
            #output
            y = []
            for val in x:
                y.append(self._annualized_return(bid_rate=bid_rate, project_size=project_size, loan_size=val, pay_emi_in=pay_emi_in, subsidy_size=subsidy_size, realized=realized, DCR_status=DCR_status))
            plt.plot(x, y)
            plt.scatter(x, y)
            plt.grid(True)
            plt.xlabel('Loan Amount')
            if realized:
                plt.ylabel(f'Realized Return over {round(self.INFLATION*100, 2)}% inflation')
            else:
                plt.ylabel('Nominal Return')
        elif compare == 'pay_emi_in':
            if type(pay_emi_in) != list:
                x = np.arange(int(0.5*pay_emi_in), int(1.5*pay_emi_in), 1)
            else:
                x = np.arange(pay_emi_in[0], pay_emi_in[-1], 1)
            #output
            y = []
            for val in x:
                y.append(self._annualized_return(bid_rate=bid_rate, project_size=project_size, loan_size=loan_size, pay_emi_in=val, subsidy_size=subsidy_size, realized=realized, DCR_status=DCR_status))
            plt.plot(x, y)
            plt.scatter(x, y)
            plt.grid(True)
            plt.xlabel('EMI Duration')
            if realized:
                plt.ylabel(f'Realized Return over {round(self.INFLATION*100, 2)}% inflation')
            else:
                plt.ylabel('Nominal Return')
        elif compare == 'subsidy_size':
            if type(subsidy_size) != list:
                x = np.linspace(0.5*subsidy_size, 1.5*subsidy_size, 10)
            else:
                x = np.linspace(subsidy_size[0], subsidy_size[-1], 10)
            #output
            y = []
            for val in x:
                y.append(self._annualized_return(bid_rate=bid_rate, project_size=project_size, loan_size=loan_size, pay_emi_in=pay_emi_in, subsidy_size=val, realized=realized, DCR_status=DCR_status))
            plt.plot(x, y)
            plt.scatter(x, y)
            plt.grid(True)
            plt.xlabel('Subsidy Size')
            if realized:
                plt.ylabel(f'Realized Return over {round(self.INFLATION*100, 2)}% inflation')
            else:
                plt.ylabel('Nominal Return')
        else:
            print('Error! Get better idiot (Check Spelling).')
        return
    
    def full_roi(self, bid_rate: float, project_size: float, loan_size: float, pay_emi_in: int, subsidy_size: float, realized=True, DCR_status=True):
        real_amount = list(self.real_amount(bid_rate=bid_rate, project_size=project_size, loan_size=loan_size, pay_emi_in=pay_emi_in, subsidy_size=subsidy_size, DCR_status=DCR_status)['Real Amount'])
        if DCR_status:
            overall_investment = (project_size * self.DCR) - self.loan_amount(project_size=project_size, subsidy_size=subsidy_size, DCR_status=DCR_status, loan_size=loan_size) - subsidy_size
        else:
            overall_investment = (project_size * self.NON_DCR) - self.loan_amount(project_size=project_size, subsidy_size=subsidy_size, DCR_status=DCR_status, loan_size=loan_size) - subsidy_size
        print(f'Investment of {round(overall_investment, 0)} INR.')
        total_real_return = 0
        for i in range(len(real_amount)):
            total_real_return += real_amount[i]
            if total_real_return >= overall_investment:
                diff = overall_investment - (total_real_return - real_amount[i])
                ratio_to_add = diff/real_amount[i]
                year = i-1
                break
        print(f'{round(year+1+ratio_to_add, 1)} years to get a full ROI.')      
        return

    def compare(self, bid_rate: float, project_size: float, loan_size: float, pay_emi_in: int, subsidy_size: float, compare: str, realized=True, DCR_status=True):
        if compare == 'DCR_status':
            print('DCR Case')
            self.annualized_return(bid_rate=bid_rate, project_size=project_size, loan_size=loan_size, pay_emi_in=pay_emi_in, subsidy_size=subsidy_size, realized=realized, DCR_status=True)
            print('-'*10)
            print('Non-DCR Case')
            self.annualized_return(bid_rate=bid_rate, project_size=project_size, loan_size=loan_size, pay_emi_in=pay_emi_in, subsidy_size=subsidy_size, realized=realized, DCR_status=False)
        elif compare == 'realized':
            print('Nominal Return')
            self.annualized_return(bid_rate=bid_rate, project_size=project_size, loan_size=loan_size, pay_emi_in=pay_emi_in, subsidy_size=subsidy_size, realized=False, DCR_status=DCR_status)
            print('-'*10)
            print('Realized Return')
            self.annualized_return(bid_rate=bid_rate, project_size=project_size, loan_size=loan_size, pay_emi_in=pay_emi_in, subsidy_size=subsidy_size, realized=True, DCR_status=DCR_status)
        else:
            self._figure_return(bid_rate=bid_rate, project_size=project_size, loan_size=loan_size, pay_emi_in=pay_emi_in, subsidy_size=subsidy_size, compare=compare, realized=realized, DCR_status=DCR_status)
        return
