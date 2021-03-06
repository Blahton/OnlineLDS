""""""

import numpy as np
from LDS.filters.wave_filtering_siso_abs import WaveFilteringSisoAbs

class WaveFilteringSisoPersistent(WaveFilteringSisoAbs):
    """
    Subclass of abstract class WaveFilteringSisoAbs.
                                                        WaveFilteringSisoPersistent
    Hierarchy tree ((ABC)):                                 ^
                                                            |
    Filtering(ABC) --> FilteringSiso(ABC) -->  WaveFilteringSisoAbs(ABC) -->WaveFilteringSisoFtlPersistent
                                     |                 |                |
                    KalmanFilteringSISO    WaveFilteringSISO  WaveFilteringSisoFtl
    """

    def __init__(self, sys, t_t, k, eta, r_m):
        """
        Inits all the attributes of its superclass(see WaveFilteringSisoAbs) and
        adds attributes eta and r_m.
        """
        super().__init__(sys, t_t, k)
        self.eta = eta
        self.r_m = r_m

        super().var_calc()
        self.y_pred_full, self.M,\
             self.pred_error, self.pred_error_persistent = self.predict()

    def predict(self):
        """
        Returns:
            y_pred_full:
            M:
            pred_error:
            pred_error_persistent:
        """

        t_t = self.t_t
        k = self.k
        H = self.H
        sys = self.sys
        M = self.M
        eta = self.eta
        r_m = self.r_m

        y_pred_full = []
        pred_error = []
        pred_error_persistent = []

        for t in range(1, t_t):
            X = []
            for j in range(k):
                scaling = pow(H.V[j], 0.25)
                conv = 0
                for u in range(0, t):
                    conv += H.matrix_d[u, j] * sys.inputs[t - u]
                X.append(scaling * conv)

            X.append(sys.inputs[t - 1])
            X.append(sys.inputs[t])
            X.append(sys.outputs[t - 1])

            X = np.matrix(X).reshape(-1, 1)

            y_pred = np.real(M * X)
            y_pred = y_pred[0, 0]
            y_pred_full.append(y_pred)
            # loss = pow(np.linalg.norm(sys.outputs[t] - y_pred), 2)
            loss = pow(np.linalg.norm(sys.outputs[t] + y_pred), 2)
            M = M - 2 * eta * (sys.outputs[t] - y_pred) * X.transpose()
            frobenius_norm = np.linalg.norm(M, 'fro')
            if frobenius_norm >= r_m:
                M = r_m / frobenius_norm * M

            pred_error.append(loss)
            pred_error_persistent.append(pow(np.linalg.norm(sys.outputs[t] - sys.outputs[t - 1]),\
                 2))

            # print(loss)

        return y_pred_full, M, pred_error, pred_error_persistent
