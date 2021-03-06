#### 标识系统
1. 小标题标识,如:<font color='red' size=4>定理:</font>;<font color='red' size=4>定义:</font>;<font color='red' size=4>证明:</font> $ ...... $
2. 算法伪代码标识,如:**for**  $ i=1,2,\dots, n $ **do**
3. 重要程度标识
   1. 非常重要:★★★★★
   2. 很重要:★★★★
   3. 重要:★★★
   4. 相对重要:★★


####   符号系统
$ x $: 标量      
$ \mathbf{x}$:  向量/序列 
$ X $: 矩阵/随机变量/数据集   
$ \mathcal{X} $: 样本空间或状态空间,也可以用来表示概率分布,如$\mathcal{D}$     
$ \mathbb{I}(*) $:  指示函数,在$*$为真/假时分别取值为1/0   
$ \mathrm{sign}(*) $:  符号函数,在$*$<,=0,>0时分别取值为-1,0,1  
$ E_{* \sim \mathcal{D}} [f( * )] $: 函数$f( * )$对$ * $在分布$\mathcal{D}$下的数学期望;明确意义时将省略$\mathcal{D}$和/或$ * $


#### 模块使用习惯
1. numpy模块
    * 函数功能以np.\*为模板(统一,推荐),如np.array,np.sort,np.argmax......
    * 除\*.flatten,\*.ravel;\*.reshape外
2. pandas模块
    * 函数功能以$*.*$为模板(统计,推荐),如df.rename,df.fillna,df.replace......
    * 除定义功能函数外,如:
        * pd.DataFrame
        * pd.Series
        * pd.date_range
        * pd.read_excel
        * ......       
3. pytorch模型
    1. 基本功能
        * 函数功能以torch.\*为模板(统一,推荐),如torch.[tensor;ones;arange;topk;var;sqrt;matmul;round;randint;sort;cat]
        * 除t.[to;tolist;numpy;item;clone;detach;in-place操作;reshape;transpose;flatten;重复元素操作;backward;retain_grad;requires_grad_]
    2. 其他(参考具体库),如
        * torch.autograd
        * torch.nn
        * torch.nn.functional
        * torch.cuda
        * torch.optim
        * ......
     

#### 额外安装(初始安装为Anconda)
1. 额外安装的模块
	* xgboost: pip install xgboost
	* PyTorch: https://pytorch.org/ 查看
	* graphviz: pip install graphviz
	* jieba: pip install jieba
	* spacy: https://spacy.io/usage 查看
2. jupyter notebook目录功能安装及其配置
	1. pip install jupyter_contrib_nbextensions   
	2. pip install jupyter_nbextensions_configurator    
	3. jupyter contrib nbextension install --user    


#### 项目主要参考(排名不分先后)
* 统计学习方法(李航)
* 西瓜书
* 花书
* 神经网络与深度学习(邱锡鹏)
* 利用Python进行数据分析(Wes Mckinney)
* 深度学习入门-基于Python的理论与实现(斋藤康毅)
* Pattern Recognition and Machine Learning(Christopher M. Bishop)
* 数学分析(华东师范大学)
* 高等数理统计(茆诗松)
* 算法导论第三版
* 统计推断
* 矩阵分析与应用
* 白板推导(B站)
* 数据结构与算法-Python语言实现
* 深入浅出PyTorch
* 百面机器学习
* 万门大学-数据结构与算法进阶班
* 龙龙pytorch
* 斯坦福CS224n
* 吴恩达-机器学习
* 吴恩达-深度学习工程师
* 唐启迪-Python数据分析
* python/numpy/pandas/matplotlib/seaborn/sklearn/pytorch等官网
* ......
