import hvplot
import hvplot.pandas
import numpy as np
import pandas as pd
import param

import panel as pn


class GBM(param.Parameterized):
    # interface
    mean = param.Number(default=5, bounds=(.0, 25.0))
    volatility = param.Number(default=5, bounds=(.0, 50.0))
    maturity = param.Integer(default=1, bounds=(0, 25))
    n_observations = param.Integer(default=10, bounds=(2, 100))
    n_simulations = param.Integer(default=20, bounds=(1, 500))
    refresh = pn.widgets.Button(name="Refresh", button_type='primary')

    def __init__(self, **params):
        super(GBM, self).__init__(**params)

    # update the plot for every changes
    # @param.depends('mean', 'volatility', 'maturity', 'n_observations', 'n_simulations', watch=True)
    # refresh the plot only on button refresh click
    @param.depends('refresh.clicks')
    def update_plot(self, **kwargs):
        df_s = pd.DataFrame(index=range(0, self.n_observations))

        for s in range(0, self.n_simulations):
            name_s = f"stock_{s}"
            df_s[name_s] = self.gbm(spot=100,
                                    mean=self.mean/100,
                                    vol=self.volatility/100,
                                    dt=self.maturity / self.n_observations,
                                    n_obs=self.n_observations)

        return df_s.hvplot(grid=True, colormap='Paired', value_label="Level", legend=False)

    @staticmethod
    def gbm(spot: float, mean: float, vol: float, dt: float, n_obs: int) -> np.ndarray:
        """ Geometric Brownian Motion

        :param spot: spot value
        :param mean: mean annualised value
        :param vol: volatility annualised value
        :param dt: time steps
        :param n_obs: number of observation to return
        :return: a geometric brownian motion np.array()
        """
        # generate normal random
        rand = np.random.standard_normal(n_obs)
        # initialize the parameters
        S = np.zeros_like(rand)
        S[0] = spot
        # loop to generate the brownian motion
        for t in range(1, n_obs):
            S[t] = S[t - 1] * np.exp((mean - (vol ** 2) / 2) * dt + vol * rand[t] * np.sqrt(dt))
        # return the geometric brownian motion
        return S
