import numpy as np
from sklearn.preprocessing import OrdinalEncoder


class MyHMM:
    def __init__(self, hidden_status_num=None, visible_status_num=None, pi=None, A=None, B=None):
        """
        初始化HMM模型的主要参数
        :param hidden_status_num: 可能的状态数
        :param visible_status_num: 可能的观测数
        :param pi: 初始概率分布
        :param A: 状态转移概率分布
        :param B: 观测概率分布
        """
        self.hidden_status_num = hidden_status_num
        self.visible_status_num = visible_status_num
        self.pi = pi
        self.A = A
        self.B = B

    def forward(self, visible_seq, want_t=None):
        """
        前向算法
        :param visible_seq: 观测序列
        :param want_t: \alpha_t(i)中的t
        :return: P(O|\lambda)或\alpha_t(i)
        """
        if want_t is None:
            want_t = len(visible_seq)+1
        alpha = self.pi * self.B[:, [visible_seq[0]]]  # 计算初值
        if want_t == 1:
            return alpha
        for step in range(1, len(visible_seq)):
            """递推"""
            alpha = self.A.T.dot(alpha) * self.B[:, [visible_seq[step]]]
            if step+1 == want_t:
                return alpha
        return np.sum(alpha)  # 求和

    def backward(self, visible_seq, want_t=None):
        """
        后向算法
        :param visible_seq: 观测序列
        :param want_t: \beta_t(i)中的t
        :return: P(O|\lambda)或\beta_t(i)
        """
        beta = np.ones_like(self.pi)  # 初始化
        if want_t == len(visible_seq):
            return beta
        for step in range(len(visible_seq) - 1, 0,  -1):
            """递推"""
            beta = self.A.dot(self.B[:, [visible_seq[step]]] * beta)
            if step == want_t:
                return beta
        return np.sum(self.pi * self.B[:, [visible_seq[0]]] * beta)  # 求和

    def gamma_t(self, visible_seq, t, state):
        """
        给定模型\lambda和观测O,计算在时刻t处于状态q_i的概率
        :param visible_seq: 观测序列
        :param t: 时刻(从1开始)
        :param state:状态
        :return: P(i_t=q_i|O,\lambda)
        """
        alpha = self.forward(visible_seq, t)  # alpha_t(i)
        beta = self.forward(visible_seq, t)  # \beta_t(i)
        part_above = (alpha * beta)[state].item()
        part_below = 0
        part_below = np.sum(alpha * beta)
        return part_above / part_below

    def xi_t(self, visible_seq, t, pre_state, next_state):
        """
        给定模型\lambda和观测O,在时刻t处于状态q_i且在时刻t+1处于状态q_j的概率
        :param visible_seq: 观测序列
        :param t: 时刻(从1开始)
        :param pre_state: 时刻t的状态
        :param next_state: 时刻t+1的状态
        :return: P(i_t=q_i,i_{t+1}=q_j|O,\lambda)
        """
        alpha = self.forward(visible_seq, t)
        beta = self.forward(visible_seq, t+1)  # \beta_{t+1}(i)
        part_above = alpha[pre_state] * self.A[pre_state, next_state] * self.B[next_state, visible_seq[t]] * beta[next_state]
        part_below = np.sum(alpha * (self.A * (self.B[:, visible_seq[t]].reshape(-1, 1) * beta).reshape(1, -1)))  # 利用了不同形状下数组的广播机制
        return part_above / part_below

    def baum_welch(self, visible_seq, n_iter=50, p=0.5):
        """
        Baum-Welch算法
        :param visible_seq:观测序列
        :param n_iter:迭代次数
        :param p:停止迭代条件(模型参数含0率大于p时退出循环)
        :return:模型的\pi,A,B
        """
        # 模型初始化
        if self.pi is None:
            self.pi = abs(np.random.normal(0, 1, size=(self.hidden_status_num, 1)))
            self.pi = self.pi / np.sum(self.pi)
        if self.A is None:
            self.A = abs(np.random.normal(0, 1, size=(self.hidden_status_num, self.hidden_status_num)))
            self.A = self.A / np.sum(self.A, axis=0)
        if self.B is None:
            self.B = abs(np.random.normal(0, 1, size=(self.hidden_status_num, self.visible_status_num)))
            self.B = self.B / np.sum(self.B, axis=0)
        T = len(visible_seq)

        for _ in range(n_iter):
            for i in range(self.hidden_status_num):
                new_p_i = self.gamma_t(visible_seq, 1, i)
                self.pi[i] = new_p_i  # 更新参数self.pi

            for j in range(self.hidden_status_num):
                for k in range(self.visible_status_num):
                    part_above = 0
                    part_below = 0
                    for t in range(1, T+1):
                        if visible_seq[t-1] == k:
                            part_above += self.gamma_t(visible_seq, t, j)
                        part_below += self.gamma_t(visible_seq, t, j)
                    new_B_jk = part_above / part_below
                    self.B[j, k] = new_B_jk  # 更新参数self.B

            for m in range(self.hidden_status_num):
                part_below = 0
                for t in range(1, T):
                    part_below += self.gamma_t(visible_seq, t, m)
                for n in range(self.hidden_status_num):
                    part_above = 0
                    for t in range(1, T):
                        part_above += self.xi_t(visible_seq, t, m, n)
                    new_A_ij = part_above / part_below
                    self.A[m, n] = new_A_ij  # 更新参数self.A

            # 概率需要进行归一化
            self.pi = self.pi / np.sum(self.pi)
            self.A = self.A / np.sum(self.A, axis=0)
            self.B = self.B / np.sum(self.B, axis=0)

            zero_pro = (np.sum(self.pi == 0) + np.sum(self.A == 0) + np.sum(self.B == 0)) /\
                       (self.hidden_status_num * (self.hidden_status_num + self.visible_status_num + 1))
            if zero_pro > p:
                break

    def supervision(self, visible_seq, hidden_seq):
        """
        监督学习方法
        :param visible_seq: 观测序列
        :param hidden_seq: 对应的状态序列
        :return:模型的\pi,A,B
        """
        self.pi = np.zeros(shape=(self.hidden_status_num, 1)) + 1e-8
        self.A = np.zeros(shape=(self.hidden_status_num, self.hidden_status_num)) + 1e-8
        self.B = np.zeros(shape=(self.hidden_status_num, self.visible_status_num)) + 1e-8
        for i in range(len(visible_seq)):
            """最大似然估计法估计\pi,A,B"""
            visible_status = visible_seq[i]
            hidden_status = hidden_seq[i]
            self.pi[hidden_status[0]] += 1
            for j in range(len(hidden_status) - 1):
                self.A[hidden_status[j], hidden_status[j + 1]] += 1
                self.B[hidden_status[j], visible_status[j]] += 1
        # 归一化
        self.pi = self.pi / np.sum(self.pi)
        self.A = self.A / np.sum(self.A, axis=0)
        self.B = self.B / np.sum(self.B, axis=0)

    def viterbi(self, visible_seq):
        """
        维特比算法求解最优路径
        :param visible_seq: 整个观测序列
        :return: 最优路径
        """
        # 初始化
        delta = self.pi * self.B[:, [visible_seq[0]]]
        Psi = [[0] * self.hidden_status_num]

        # 递推
        for visible_index in range(2, len(visible_seq)+1):  # 即t=2,3,...T
            new_delta = np.zeros_like(delta)
            new_Psi = []
            for i in range(0, self.hidden_status_num):
                best_pre_index_i = -1
                best_pre_index_value_i = 0
                delta_i = 0
                for j in range(0, self.hidden_status_num):
                    delta_i_j = delta[j][0] * self.A[j, i] * self.B[i, visible_seq[visible_index-1]]
                    if delta_i_j > delta_i:
                        """寻找最大的\delta_i"""
                        delta_i = delta_i_j
                    best_pre_index_value_i_j = delta[j][0] * self.A[j, i]
                    if best_pre_index_value_i_j > best_pre_index_value_i:
                        """寻找最大的\Psi"""
                        best_pre_index_value_i = best_pre_index_value_i_j
                        best_pre_index_i = j

                new_delta[i, 0] = delta_i  # 更新\delta_i
                new_Psi.append(best_pre_index_i)

            delta = new_delta
            Psi.append(new_Psi)

        bset_hidden_status_pro = np.max(delta)  # 最优路径的概率
        best_hidden_status = [np.argmax(delta)]  # 最优路径的终点

        # 最优路径回溯
        for Psi_index in range(len(visible_seq) - 1, 0, -1):
            next_status = Psi[Psi_index][best_hidden_status[-1]]
            best_hidden_status.append(next_status)
        best_hidden_status.reverse()
        return best_hidden_status, bset_hidden_status_pro


if __name__ == '__main__':
    test_forward_backwwar_gamma_xi_viterbi = 1
    if test_forward_backwwar_gamma_xi_viterbi:
        A = np.array([[0.5, 0.2, 0.3],
                      [0.3, 0.5, 0.2],
                      [0.2, 0.3, 0.5]])
        B = np.array([[0.5, 0.5],
                      [0.4, 0.6],
                      [0.7, 0.3]])
        pi = np.array([[0.2, 0.4, 0.4]]).T
        visible_seq_init = np.array(['红', '白', '红'], dtype=object).reshape(-1, 1)

        enc = OrdinalEncoder(categories=[['红', '白']])
        visible_seq = enc.fit_transform(visible_seq_init).astype(np.int).reshape(-1, )

        # forward_test = MyHMM(hidden_status_num=3, visible_status_num=2, pi=pi, A=A, B=B)
        # print(forward_test.forward(visible_seq=visible_seq)) # 前向算法测试
        # print(forward_test.forward(visible_seq=visible_seq, want_t=1))
        # print(forward_test.forward(visible_seq=visible_seq, want_t=2))
        # print(forward_test.forward(visible_seq=visible_seq, want_t=3))
        #
        # backward_test = MyHMM(hidden_status_num=3, visible_status_num=2, pi=pi, A=A, B=B)
        # print(backward_test.backward(visible_seq=visible_seq)) # 后向算法测试
        # print(backward_test.backward(visible_seq=visible_seq, want_t=1))
        # print(backward_test.backward(visible_seq=visible_seq, want_t=2))
        # print(backward_test.backward(visible_seq=visible_seq, want_t=3))
        #
        # gamma_test = MyHMM(hidden_status_num=3, visible_status_num=2, pi=pi, A=A, B=B)
        # print(gamma_test.gamma_t(visible_seq=visible_seq, t=1, state=0)) # \gamma计算测试
        # print(gamma_test.gamma_t(visible_seq=visible_seq, t=1, state=1))
        # print(gamma_test.gamma_t(visible_seq=visible_seq, t=1, state=2))
        #
        # xi_test = MyHMM(hidden_status_num=3, visible_status_num=2, pi=pi, A=A, B=B)
        # print(xi_test.xi_t(visible_seq=visible_seq, t=1, pre_state=0, next_state=1)) # \xi计算测试
        # print(xi_test.xi_t(visible_seq=visible_seq, t=2, pre_state=0, next_state=0)) # \xi计算测试
        # print(xi_test.xi_t(visible_seq=visible_seq, t=2, pre_state=2, next_state=0)) # \xi计算测试

        # vitiver_test = MyHMM(hidden_status_num=3, visible_status_num=2, pi=pi, A=A, B=B)
        # best_hidden_status, bset_hidden_status_pro = vitiver_test.viterbi(visible_seq=visible_seq)
        # print("最优路径:", best_hidden_status, '最优路径概率:', bset_hidden_status_pro)

    test_Baum_Welch = 1
    if test_Baum_Welch:
        O = [
            [1, 2, 3, 0, 1, 3, 4],
            [1, 2, 3],
            [0, 2, 4, 2],
            [4, 3, 2, 1],
            [3, 1, 1, 1, 1],
            [2, 1, 3, 2, 1, 3, 4]
        ]
        I = O

        hmm_supervision = MyHMM(hidden_status_num=5, visible_status_num=5)
        hmm_supervision.supervision(visible_seq=O, hidden_seq=I)
        print(hmm_supervision.pi)
        print(hmm_supervision.A)
        print(hmm_supervision.B)

        # hmm_no_supervision = MyHMM(hidden_status_num=5, visible_status_num=5)
        # hmm_no_supervision.baum_welch(O[0] + O[1] + O[2] + O[3] + O[4] + O[5])
        # print(hmm_no_supervision.pi)
        # print(hmm_no_supervision.A)
        # print(hmm_no_supervision.B)
