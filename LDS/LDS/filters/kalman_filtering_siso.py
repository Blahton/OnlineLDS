"""Implements Kalman filter prediction.
Originates from function Kalman_filtering_SISO from onlinelds.py."""

import numpy as np
from LDS.filters.filtering_siso import FilteringSiso

class KalmanFilteringSISO(FilteringSiso):
    """
    Subclass of class FilteringSiso.

                                                        WaveFilteringSisoPersistent
                                                            ^
                                                            |
    Filtering(ABC) --> FilteringSiso(ABC) -->  WaveFilteringSisoAbs(ABC) -->WaveFilteringSisoFtlPersistent
                                     |                 |                |
                    KalmanFilteringSISO    WaveFilteringSISO  WaveFilteringSisoFtl
    """

    def __init__(self, sys, G, f_dash,proc_noise_std, obs_noise_std, t_t, Y):
        """
        Inherits init method of FilteringSiso.
        Created to easily find the Kalman filter prediction.

        Args:
            sys: Linear Dynamical System.
            t_t: Time horizon.
        """
        super().__init__(sys, t_t)
        self.G = G
        self.f_dash = f_dash
        self.proc_noise_std = proc_noise_std
        self.obs_noise_std = obs_noise_std
        self.Y = Y
        #a, b = self.predict()
        self.parameters() #?

    def predict(self):
        pass

    def parameters(self):
        """
        The above part is create by me. The below part is created by prof.Marecek.

        Creates G - State transition matrix, square identity matrix 4x4.
                n - number of rows of G
                F - Observation matrix, matrix 4x1 of 0.5.
                Id - identity matrix 4x4
                m_prev - 0
                c_prev - matrix nxn of zeros

                R - 
                
                Kalman filter recursive equations:
                a = G.m_prev
                R, Q, matrix_a

                F
                RF

        Returns:
            y_pred_full: Predicted output.
            pred_error:  Error prediction.

        Raises:
            Q can't be zero.
        """

        self.n = self.G.shape[0]   #input vector
        self.m = self.f_dash.shape[0] #observation vector

        self.W = self.proc_noise_std ** 2 * np.matrix(np.eye(self.n))  #covariance matrix of process noise
        self.V = self.obs_noise_std ** 2 * np.matrix(np.eye(self.m))   #observation noise covariance

        # m_t = [np.matrix([[0],[0]])]
        self.matrix_c = [np.matrix(np.eye(2))]
        self.R = []
        self.Q = []
        self.matrix_a = []
        self.Z = []

        for t in range(self.t_t):
            self.R.append(self.G * self.matrix_c[-1] * self.G.transpose() + self.W)
            # if t == 1:
            #     print('muj')
            #     print(self.R)
            #     print('Kalman')
            self.Q.append(self.f_dash * self.R[-1] * self.f_dash.transpose() + self.V)

            #LaTeX A_t &=& R_t F  / Q_t
            self.matrix_a.append(self.R[-1] * self.f_dash.transpose() * np.linalg.inv(self.Q[-1]))

            #C_t &=& R_t - A_t Q_t A'_t
            self.matrix_c.append(self.R[-1] - self.matrix_a[-1] * self.Q[-1] *\
               self.matrix_a[-1].transpose())

            #In general, set $Z_t = G(I-F\otimes A_t)$ and $Z = G(I-F \otimes A)$.
            self.Z.append(self.G * (np.eye(2) - self.matrix_a[-1] * self.f_dash))

        #return n, m, W, V, matrix_c, R, Q, matrix_a, Z

        #Y_pred = prediction(t_t, f_dash, G, matrix_a, sys, s, Z, Y)
        #Y_kalman = prediction_kalman(t_t, f_dash, G, matrix_a, sys, Z, Y)

    def prediction_new(self,s):

        self.Y_kalman = []
        for t in range(self.t_t):
            Y_pred_term1 = self.f_dash * self.G * self.matrix_a[t] * self.sys.outputs[t]
            if t == 0:
                self.Y_kalman.append(Y_pred_term1)
                continue

            self.accKalman = 0
            #We don't have range(min(t,s)+1) as we do for prediction function
            for j in range(min(t,s) + 1):
                for i in range(j + 1):
                    if i == 0:
                        ZZ = self.Z[t - i]
                        continue
                    ZZ = ZZ * self.Z[t - i]
                self.accKalman += ZZ * self.G * self.matrix_a[t - j - 1] * self.Y[t - j - 1]
            self.Y_kalman.append(Y_pred_term1 + self.f_dash * self.accKalman)

        return self.Y_kalman


        

        # sys = self.sys                       #LDS
        # t_t = self.t_t                       #time horizon

        # #G = np.diag(np.array(np.ones(4)))    #$G \in \RR^{n\times n}$ is the state transition 
        #                                      #matrix which defines the system dynamics
        
        # #G = np.matrix([[0.999,0],[0,0.5]])   #state transition matrix

        # #def pre_comp_filter_params(G, f_dash, proc_noise_std, obs_noise_std, t_t):
        # n = G.shape[0] #
        # m = f_dash.shape[0] #new
        # #No noise covariance matrix was written yet.
        # matrix_c = [np.matrix(np.eye(2))] #new
        # W = proc_noise_std ** 2 * np.matrix(np.eye(n))  #new, covariance matrix of process noise
        # V = obs_noise_std ** 2 * np.matrix(np.eye(m))   #new, observation noise covariance
        # #R = []
        # #Q = []
        # #matrix_a = []
        # #Z = []

        # F = np.ones(n)[:, np.newaxis] / np.sqrt(n)

        # #Take the example
        # f_dash = np.matrix([[1,1]])  #new                  #is the observation direction
        
        # Id = np.eye(n)
        # m_prev = 0                           #m_{t-1} is the last hidden state
        # c_prev = np.zeros((n, n))            #C_{t-1} is the covariance matrix of $\phi_{t-1}$ 
        #                                      #given $Y_0,\ldots,Y_{t-1}$. 

        # y_pred_full = [0]
        # pred_error = [sys.outputs[0]]
        
        # for t in range(t_t):                #Changed from range(1,t_t)

        #     a = np.dot(G, m_prev)
        #     #R.append(G * matrix_c[-1] * G.transpose() + W) #new

        #     #R = np.dot(G, np.dot(c_prev, G.t_t)) + W
        #     R = np.dot(G, np.dot(matrix_c[-1], G.transpose())) + W

        #     """Result from the main file. We need to make it the same
        #     [matrix([[1.248001, 0.      ],
        #     [0.      , 0.5     ]]), matrix([[ 0.71753214, -0.15600005],
        #     [-0.15600005,  0.34371873]])]"""
        #     if t == 0:
        #         print(R) 

        #     f = np.dot(f_dash, a)           #f_t = F' a_t.   
        #     RF = np.dot(R, F)               #R_tF
        #     Q = np.dot(f_dash, RF)  # + V   

        #     matrix_a = RF                   
        #     try:
        #         matrix_a = RF / Q           #LaTeX A_t &=& R_t F  / Q_t
        #     except:
        #         print("Zero Q? Check %s" % str(Q))

        #     # thats on purpose in a bit slower form, to test the equations
        #     y_pred = np.dot(F.t_t, np.dot(G, m_prev)) #Same as Kalman filter 
        #                                               #f = np.dot(F.t_t, a)

        #     #m_t = A_t Y_t + (I - F \otimes A_t) a_t
        #     m_prev = y_pred * matrix_a + np.dot((Id - np.dot(matrix_a, F.t_t)), a) 
        #     #Why do we use here y_pred instead of sys.outputs[t]? We don't have them?

        #     #C_t &=& R_t - A_t Q_t A'_t
        #     c_prev = R - Q * np.dot(matrix_a, matrix_a.t_t)   
        #     #Why is Q not in the middle of multiplication

        #     y_pred_full.append(y_pred)

        #     # $The loss function (Y_t-y_pred)^2$.
        #     loss = pow(np.linalg.norm(sys.outputs[t] - y_pred), 2) 

        #     pred_error.append(loss)
        # #print(y_pred_full)
        # return y_pred_full, pred_error
